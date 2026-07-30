import pytest
from fastapi.testclient import TestClient
from app.main import app, memory_db
from app.services.nlp import classify_message

client = TestClient(app)


def setup_module(module):
    memory_db.communities.clear()
    memory_db.reports.clear()
    memory_db.alerts.clear()


class TestHealth:
    def test_health_endpoint(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestReports:
    def test_create_report_minimal(self):
        resp = client.post("/api/reports", json={
            "message": "Heavy rain causing flooding in my area"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["report_type"] == "flood"
        assert data["source"] == "web"
        assert "id" in data

    def test_create_report_with_location(self):
        resp = client.post("/api/reports", json={
            "message": "Drought conditions severe, crops failing",
            "latitude": -1.2833,
            "longitude": 36.8167,
            "location_name": "Nairobi, Kenya",
            "source": "web"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["latitude"] == -1.2833
        assert data["longitude"] == 36.8167
        assert data["report_type"] == "drought"

    def test_create_report_invalid_lat(self):
        resp = client.post("/api/reports", json={
            "message": "Test report",
            "latitude": 100
        })
        assert resp.status_code == 422

    def test_get_reports(self):
        resp = client.get("/api/reports")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_reports_filtered(self):
        resp = client.get("/api/reports?report_type=flood")
        assert resp.status_code == 200
        data = resp.json()
        assert all(r["report_type"] == "flood" for r in data)

    def test_get_report_by_id(self):
        all_resp = client.get("/api/reports")
        if all_resp.json():
            report_id = all_resp.json()[0]["id"]
            resp = client.get(f"/api/reports/{report_id}")
            assert resp.status_code == 200
            assert resp.json()["id"] == report_id

    def test_get_report_not_found(self):
        resp = client.get("/api/reports/nonexistent-id-here")
        assert resp.status_code == 404


class TestAlerts:
    def test_create_alert(self):
        resp = client.post("/api/alerts", json={
            "title": "Flood Warning",
            "message": "Heavy flooding expected in Nairobi region",
            "alert_type": "flood",
            "severity": "high",
            "region": "Nairobi"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Flood Warning"
        assert data["status"] == "active"

    def test_get_alerts(self):
        resp = client.get("/api/alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_active_alerts(self):
        resp = client.get("/api/alerts?status=active")
        assert resp.status_code == 200
        data = resp.json()
        assert all(a["status"] == "active" for a in data)


class TestCommunities:
    def test_create_community(self):
        resp = client.post("/api/communities", json={
            "name": "Test Community",
            "phone": "+254700000001",
            "region": "Nairobi",
            "country": "Kenya",
            "latitude": -1.2833,
            "longitude": 36.8167
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Community"
        assert data["phone"] == "+254700000001"

    def test_create_community_duplicate_phone(self):
        resp = client.post("/api/communities", json={
            "name": "Duplicate",
            "phone": "+254700000001",
        })
        assert resp.status_code == 409

    def test_get_communities(self):
        resp = client.get("/api/communities")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_create_community_invalid_phone(self):
        resp = client.post("/api/communities", json={
            "name": "Bad Phone",
            "phone": "not-a-phone"
        })
        assert resp.status_code == 422


class TestSMSWebhook:
    def test_sms_webhook_flood(self):
        resp = client.post("/api/webhooks/sms", json={
            "from": "+254712345678",
            "text": "There is heavy flooding in our village, water is everywhere"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_sms_webhook_drought_swahili(self):
        resp = client.post("/api/webhooks/sms", json={
            "from": "+254723456789",
            "text": "Kuna ukame mkubwa, mazao yote yamekauka"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"


class TestStats:
    def test_get_stats(self):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_reports" in data
        assert "total_alerts" in data
        assert "total_communities" in data
        assert "reports_by_type" in data
        assert "active_alerts" in data


class TestClassification:
    def test_classify_flood(self):
        result = classify_message("Heavy rain causing flooding near the river")
        assert result["report_type"] == "flood"
        assert result["severity"] in ("low", "moderate", "high", "critical")

    def test_classify_drought(self):
        result = classify_message("No rain for months, crops dying, drought severe")
        assert result["report_type"] == "drought"

    def test_classify_pest(self):
        result = classify_message("Locusts have invaded our farms")
        assert result["report_type"] == "pest"

    def test_classify_disease(self):
        result = classify_message("Many people sick with cholera outbreak")
        assert result["report_type"] == "disease"

    def test_classify_fire(self):
        result = classify_message("Forest fire spreading rapidly")
        assert result["report_type"] == "fire"

    def test_classify_empty(self):
        result = classify_message("")
        assert result["report_type"] == "other"
        assert result["confidence"] == 0.0

    def test_classify_swahili_flood(self):
        result = classify_message("Mafuriko makubwa yamejaa nyumbani kwetu")
        assert result["report_type"] == "flood"

    def test_classify_swahili_drought(self):
        result = classify_message("Hakuna mvua, njaa inatuesha")
        assert result["report_type"] == "drought"

    def test_classify_endpoint(self):
        resp = client.post("/api/classify?text=Flooding in the streets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["report_type"] == "flood"

    def test_classify_confidence(self):
        result = classify_message("Heavy rain and flooding with water rising fast")
        assert result["confidence"] > 0.3
        assert len(result["keywords_found"]) > 0


class TestICPAC:
    def test_sync_icpac(self):
        resp = client.post("/api/icpac/sync")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            data = resp.json()
            assert "status" in data
