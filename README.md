# Community Voice Early Warning System

[![CI](https://github.com/kawacukennedy/community_voice_ews/actions/workflows/ci.yml/badge.svg)](https://github.com/kawacukennedy/community_voice_ews/actions/workflows/ci.yml)
[![Deploy](https://github.com/kawacukennedy/community_voice_ews/actions/workflows/deploy.yml/badge.svg)](https://github.com/kawacukennedy/community_voice_ews/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)
[![GitHub Issues](https://img.shields.io/github/issues/kawacukennedy/community_voice_ews)](https://github.com/kawacukennedy/community_voice_ews/issues)
[![Last Commit](https://img.shields.io/github/last-commit/kawacukennedy/community_voice_ews)](https://github.com/kawacukennedy/community_voice_ews/commits/main)

A two-way early warning platform for the IGAD region — combining official ICPAC forecasts with crowdsourced SMS reports from local communities. No smartphone required.

```bash
git clone https://github.com/kawacukennedy/community_voice_ews.git
cd community_voice_ews
make install && make dev-backend
# Open http://localhost:8000
```

[Live Demo](https://community-voice-ews.onrender.com) · [API Docs](https://community-voice-ews.onrender.com/docs) · [Report a Bug](https://github.com/kawacukennedy/community_voice_ews/issues/new?labels=bug&template=bug_report.yml) · [Request Feature](https://github.com/kawacukennedy/community_voice_ews/issues/new?labels=enhancement&template=feature_request.yml)

---

## Why

- **No connectivity required** — community members report via SMS (Africa's Talking / Twilio); internet not needed on their end
- **Bilingual NLP** — automatically classifies reports in English and Swahili (flood, drought, pest, disease, fire, conflict, health)
- **Official + Crowdsourced** — merges ICPAC satellite forecasts with on-the-ground reports
- **Two-way communication** — authorities broadcast alerts back to all registered communities via SMS
- **Free tier deploy** — costs nothing to run on Render free plan + SQLite; zero-config to start

## Features

- **SMS Reporting** — community members text floods, droughts, pests, disease outbreaks — no smartphone required
- **NLP Classification** — messages automatically categorized and prioritized in English and Swahili
- **Live Map** — interactive Leaflet map with color-coded severity markers
- **Two-way Alerts** — authorities broadcast SMS alerts to all communities in a region
- **ICPAC Integration** — pulls official flood/drought/rainfall forecasts for cross-validation
- **Offline-capable** — frontend works without internet after first load
- **Dark mode** — automatically adapts to system preference
- **Responsive** — works on phones, tablets, and desktops

## Quick Start

### Prerequisites

- Python 3.12+
- pip

### Install & Run

```bash
# Clone
git clone https://github.com/kawacukennedy/community_voice_ews.git
cd community_voice_ews

# Backend
make install
make dev-backend
```

Open **http://localhost:8000** — the frontend is served automatically. API docs at **http://localhost:8000/docs**.

```python
# Or use the API directly
import requests

r = requests.post("http://localhost:8000/api/reports", json={
    "message": "Heavy flooding in the village near the river",
    "latitude": -1.315,
    "longitude": 36.785,
    "source": "demo"
})
print(r.json())
# {'id': '...', 'report_type': 'flood', 'severity': 'high', ...}
```

### Run Tests

```bash
make test
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/reports` | Submit a community report |
| GET | `/api/reports` | List reports (filter by type, severity, region) |
| GET | `/api/reports/{id}` | Get a single report |
| POST | `/api/classify` | Classify a message without storing |
| GET | `/api/alerts` | List active alerts |
| POST | `/api/alerts` | Create alert (broadcasts via SMS) |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/communities` | List registered communities |
| POST | `/api/communities` | Register a community for alerts |
| POST | `/api/webhooks/sms` | SMS webhook receiver |
| POST | `/api/icpac/sync` | Sync official ICPAC forecasts |

Full interactive docs at `/docs` when the server is running.

## Project Structure

```
community_voice_ews/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + all endpoints
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   └── services/
│   │       ├── nlp.py         # Message classification (EN + SW)
│   │       ├── sms.py         # SMS provider abstraction
│   │       └── icpac.py       # ICPAC data integration
│   ├── tests/                 # pytest suite
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Single-page app
│   ├── css/style.css          # Styles (dark mode, responsive)
│   └── js/
│       ├── app.js             # Main UI logic
│       ├── api.js             # API service layer
│       ├── map.js             # Leaflet map management
│       └── sms-demo.js        # SMS simulation UI
├── docs/                      # Extended documentation
├── examples/                  # Runnable API usage examples
├── scripts/                   # Automation helpers
├── .github/                   # CI/CD, templates, labels
├── render.yaml                # Render blueprint
├── Makefile                   # Developer entry points
├── docker-compose.yml         # Docker setup
└── .env.example               # Environment config template
```

## Deployment

### One-click Render Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/kawacukennedy/community_voice_ews)

Or connect the repo manually:

1. Create account at [render.com](https://render.com)
2. **New +** → **Blueprint** → connect `kawacukennedy/community_voice_ews`
3. Render auto-reads `render.yaml` and deploys

### Environment Variables

See [.env.example](.env.example) for all options. Key variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./ews.db` | Database connection string |
| `SMS_API_KEY` | No | — | Africa's Talking API key |
| `SMS_USERNAME` | No | `sandbox` | Africa's Talking username |
| `SECRET_KEY` | No | `change-me` | JWT / session secret |

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- How to set up the dev environment
- Coding standards (PEP 8, black, flake8)
- Commit and PR conventions
- Testing requirements

Browse [good first issues](https://github.com/kawacukennedy/community_voice_ews/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) to get started.

## License

MIT — free and open source. See [LICENSE](LICENSE).
