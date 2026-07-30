import pytest
from datetime import datetime, timezone, timedelta
from app.services.nlp import classify_message


class TestNLPClassification:
    def test_flood_keywords_en(self):
        result = classify_message("Severe flooding reported near the river bank")
        assert result["report_type"] == "flood"
        assert result["confidence"] > 0

    def test_drought_severity_high(self):
        result = classify_message("Severe drought, livestock dying, no water for crops")
        assert result["report_type"] == "drought"
        assert result["severity"] in ("high", "critical")

    def test_pest_infestation(self):
        result = classify_message("Locust swarm destroying all crops in the region")
        assert result["report_type"] == "pest"
        assert result["confidence"] > 0.3

    def test_mixed_keywords(self):
        result = classify_message("There is flooding and heavy rain but also some pests")
        assert result["report_type"] in ("flood", "pest")

    def test_swahili_only(self):
        result = classify_message("Maji yamefurika barabarani na nyumba zimezama")
        assert result["report_type"] == "flood"

    def test_case_insensitive(self):
        result = classify_message("FLOOD WARNING - HEAVY RAIN EXPECTED")
        assert result["report_type"] == "flood"

    def test_unicode_text(self):
        result = classify_message("Mafuriko makubwa yameleta uharibifu mkubwa")
        assert result["report_type"] == "flood"

    def test_empty_text(self):
        result = classify_message("")
        assert result["report_type"] == "other"
        assert result["severity"] == "low"
        assert result["confidence"] == 0.0

    def test_whitespace_text(self):
        result = classify_message("   ")
        assert result["report_type"] == "other"

    def test_health_related(self):
        result = classify_message("People are sick with malaria, need medicine at the clinic")
        assert result["report_type"] == "disease"

    def test_conflict_related(self):
        result = classify_message("Violence erupted in the village, people are fleeing")
        assert result["report_type"] == "conflict"

    def test_critical_flood(self):
        result = classify_message("EMERGENCY! Drowning people need evacuation immediately")
        assert result["report_type"] in ("flood", "health")
        assert result["severity"] == "critical"

    def test_keywords_found(self):
        result = classify_message("Heavy rain and flooding")
        assert len(result["keywords_found"]) > 0

    def test_no_match_returns_other(self):
        result = classify_message("The weather is nice today, everything is normal")
        assert result["report_type"] == "other"

    def test_confidence_never_exceeds_095(self):
        flood_msg = " ".join(["flood"] * 50)
        result = classify_message(flood_msg)
        assert result["confidence"] <= 0.95
