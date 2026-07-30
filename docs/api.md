# API Reference

Base URL: `http://localhost:8000` (local) or `https://community-voice-ews.onrender.com` (production)

Interactive docs available at `/docs` when the server is running.

## Health

```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2026-07-30T12:00:00Z"
}
```

## Reports

### Submit a Report

```http
POST /api/reports
Content-Type: application/json

{
  "message": "Heavy flooding in the village near the river",
  "latitude": -1.315,
  "longitude": 36.785,
  "location_name": "Nairobi River Basin",
  "source": "sms"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "report_type": "flood",
  "severity": "high",
  "confidence": 0.92,
  "status": "pending",
  "submitted_at": "2026-07-30T12:00:00Z"
}
```

### List Reports

```http
GET /api/reports?report_type=flood&severity=high&region=Nairobi&limit=20&offset=0
```

### Get Report by ID

```http
GET /api/reports/{report_id}
```

## Classification

```http
POST /api/classify?text=flooding+water+entering+homes
```

**Response:**
```json
{
  "report_type": "flood",
  "severity": "high",
  "confidence": 0.95,
  "keywords_found": ["flood", "water"]
}
```

## Alerts

### List Alerts

```http
GET /api/alerts?active_only=true
```

### Create Alert (broadcasts via SMS)

```http
POST /api/alerts
Content-Type: application/json

{
  "title": "Flood Warning",
  "message": "Heavy rainfall expected in Nairobi region",
  "severity": "high",
  "region": "Nairobi"
}
```

## Communities

### List Communities

```http
GET /api/communities
```

### Register Community

```http
POST /api/communities
Content-Type: application/json

{
  "name": "Kibera Community",
  "phone": "+254712345678",
  "region": "Nairobi",
  "country": "Kenya",
  "latitude": -1.315,
  "longitude": 36.785
}
```

## Stats

```http
GET /api/stats
```

**Response:**
```json
{
  "total_reports": 42,
  "total_alerts": 7,
  "total_communities": 3,
  "reports_by_type": {"flood": 20, "drought": 10, "pest": 8, "disease": 4},
  "reports_by_severity": {"low": 5, "moderate": 15, "high": 18, "critical": 4},
  "active_alerts": 2,
  "recent_reports": [...]
}
```

## SMS Webhook

```http
POST /api/webhooks/sms
Content-Type: application/x-www-form-urlencoded

from=+254712345678&text=flood+water+in+my+house
```

## ICPAC Sync

```http
POST /api/icpac/sync
```

**Response:**
```json
{
  "status": "success",
  "alerts_created": 5,
  "source": "icpac"
}
```
