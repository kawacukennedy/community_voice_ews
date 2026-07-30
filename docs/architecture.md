# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Community Members                      │
│          (SMS / USSD - No internet needed)               │
└───────────┬──────────────────────────┬──────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────┐    ┌──────────────────────────┐
│  Africa's Talking   │    │  ICPAC (Official Data)   │
│  SMS Gateway        │    │  Flood/Drought Forecasts │
└──────────┬──────────┘    └───────────┬──────────────┘
           │                            │
           ▼                            ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ NLP      │  │ SQLAlchmy│  │ SMS/Alert Service    │  │
│  │ Classify │  │ ORM      │  │ Broadcast Engine     │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
┌──────────────────┐       ┌───────────────────┐
│   SQLite / PG    │       │   Web Dashboard   │
│   (Reports,      │       │   Leaflet Map     │
│    Alerts,       │       │   Reports/Alerts  │
│    Communities)  │       └───────────────────┘
└──────────────────┘
```

## Components

### Backend (`backend/app/`)

| Module | Responsibility |
|--------|---------------|
| `main.py` | FastAPI application, route definitions, request handling, static file serving |
| `models.py` | SQLAlchemy ORM models (Report, Alert, Community) |
| `schemas.py` | Pydantic models for request validation and response serialization |
| `services/nlp.py` | Keyword-based message classification in English and Swahili |
| `services/sms.py` | SMS provider abstraction (Africa's Talking / Twilio) |
| `services/icpac.py` | HTTP client for ICPAC geospatial data endpoints |
| `utils/config.py` | Environment configuration via Pydantic Settings |

### Frontend (`frontend/`)

| File | Responsibility |
|------|---------------|
| `index.html` | Single-page application shell |
| `css/style.css` | Responsive design, dark mode, severity colors |
| `js/app.js` | UI state management, tab switching, data binding |
| `js/api.js` | HTTP client for all backend API endpoints |
| `js/map.js` | Leaflet map rendering with clustered markers |
| `js/sms-demo.js` | SMS simulation UI for testing |

### Database

The app uses SQLAlchemy ORM with SQLite by default (zero-config). For production, switch to PostgreSQL by setting `DATABASE_URL`.

**Models:**

- **Report** — community-submitted reports with classification, location, and severity
- **Alert** — official alerts broadcast to communities
- **Community** — registered groups with contact details and region

### Data Flow

1. **Report submission**: SMS → Africa's Talking webhook → FastAPI → NLP classify → store → broadcast alert if high severity
2. **Alert broadcast**: API create → SMS provider → all communities in region
3. **ICPAC sync**: Cron/API → HTTP fetch → parse features → store as alerts
4. **Dashboard**: Frontend → API → DB → Leaflet map + stats

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Pydantic |
| Frontend | HTML5, CSS3, JavaScript (ES6+), Leaflet |
| Database | SQLite (dev), PostgreSQL (production) |
| SMS | Africa's Talking, Twilio |
| Hosting | Render (blueprint deploy) |
| CI/CD | GitHub Actions |
