# Community Voice Early Warning System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

A two-way early warning platform for the IGAD region that combines official forecasts from ICPAC with crowdsourced SMS reports from local communities. Built for the IGAD Hackathon 2026.

🌐 **Live Demo**: [https://community-voice-ews.vercel.app](https://community-voice-ews.vercel.app)
📖 **API Docs**: [https://community-voice-ews-api.onrender.com/docs](https://community-voice-ews-api.onrender.com/docs)
📂 **Source**: [github.com/kawacukennedy/community_voice_ews](https://github.com/kawacukennedy/community_voice_ews)

## Problem

In East Africa, communities face increasing climate disasters — floods, droughts, pests, and disease outbreaks. Warning systems exist, but they often fail to reach the most vulnerable. Community Voice EWS bridges this gap by turning local knowledge into actionable alerts.

## Architecture

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
│   Supabase DB    │       │   Web Dashboard   │
│   PostgreSQL     │       │   Leaflet Map     │
│   + PostGIS      │       │   Reports/Alerts  │
└──────────────────┘       └───────────────────┘
```

### Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Frontend | HTML, CSS, JS + Leaflet | No frameworks needed, fast load on slow connections |
| Backend | Python FastAPI | High performance, async, auto-docs |
| Database | Supabase (PostgreSQL + PostGIS) | Free 500MB, spatial queries, real-time |
| SMS | Africa's Talking / Twilio | Free sandbox, works without internet |
| NLP | Keyword matching (EN + SW) | No ML training needed, works offline |
| Hosting | Render (backend) + Vercel (frontend) | Both free tiers |
| CI/CD | GitHub Actions | Automated testing and deployment |

## Quick Start (5 minutes)

### 1. Clone & Setup

```bash
git clone https://github.com/kawacukennedy/community_voice_ews.git
cd community_voice_ews
cp .env.example .env
```

### 2. Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 3. Run Frontend

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500` in your browser.

## API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/reports` | Submit a new report |
| GET | `/api/reports` | Get all reports (with filters) |
| GET | `/api/reports/:id` | Get single report |
| GET | `/api/alerts` | Get active alerts |
| POST | `/api/alerts` | Create an alert (broadcasts via SMS) |
| POST | `/api/webhooks/sms` | SMS webhook receiver |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/communities` | List communities |
| POST | `/api/communities` | Register a community |
| POST | `/api/classify` | Classify a message |
| POST | `/api/icpac/sync` | Sync ICPAC forecasts |

## Deployment

### Backend → Render.com

1. Create account at [render.com](https://render.com)
2. Create new Web Service, connect GitHub repo
3. Set root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (see `.env.example`)

### Frontend → Vercel

1. Create account at [vercel.com](https://vercel.com)
2. Import GitHub repo, set root: `frontend`
3. Deploy — zero configuration needed

### Database → Supabase

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to SQL Editor, paste and run `backend/schema.sql`
4. Copy connection string for `DATABASE_URL`

### SMS → Africa's Talking

1. Create account at [africastalking.com](https://africastalking.com)
2. Go to Sandbox, get API key
3. Set callback URL: `https://your-backend.onrender.com/api/webhooks/sms`

## Features

- **SMS Reporting**: Community members send SMS to report floods, droughts, pests, disease — no smartphone required
- **NLP Classification**: Messages are automatically classified and prioritized in English and Swahili
- **Live Map**: Interactive map with color-coded markers and severity indicators
- **Two-way Alerts**: Authorities can broadcast alerts to all communities via SMS
- **ICPAC Integration**: Automatically pulls official forecasts for cross-validation
- **Offline-capable**: Frontend works with service workers; SMS doesn't need internet
- **Dark mode**: Automatically adapts to system preference
- **Responsive**: Works on phones, tablets, and desktops

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

## Project Structure

```
community_voice_ews/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with all endpoints
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── services/
│   │   │   ├── nlp.py           # Message classification
│   │   │   ├── sms.py           # SMS sending (Africa's Talking / Twilio)
│   │   │   └── icpac.py         # ICPAC data integration
│   │   └── utils/
│   │       └── config.py         # Environment config
│   ├── tests/
│   │   ├── test_api.py           # API endpoint tests
│   │   └── test_db.py            # NLP classification tests
│   ├── schema.sql                # Full database schema
│   ├── requirements.txt
│   ├── render.yaml
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js                # Main application logic
│       ├── api.js                # API service layer
│       ├── map.js                # Leaflet map management
│       └── sms-demo.js           # SMS simulation
├── .github/workflows/
│   ├── deploy.yml
│   └── ci.yml
├── docker-compose.yml
├── Makefile
├── .env.example
├── README.md
└── CONTRIBUTING.md
```

## License

MIT — free and open source for all. See [LICENSE](LICENSE) for details.

---

Built with ❤️ for the IGAD Hackathon 2026 by **kawacukennedy**.
