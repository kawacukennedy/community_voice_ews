# AI Agent Guidance

## Build & Test

```bash
# Backend
make install      # Install Python dependencies
make dev-backend  # Start FastAPI dev server on :8000
make test         # Run pytest suite
make lint         # flake8 + black --check
make format       # black auto-format

# Frontend (standalone)
python3 -m http.server 5500 -d frontend/

# Full stack
make dev          # Backend :8000 + Frontend :5500
```

## Architecture

```
frontend/          # Static HTML/CSS/JS (Leaflet map)
backend/app/
  main.py          # FastAPI router + lifespan
  models.py        # SQLAlchemy ORM models
  schemas.py       # Pydantic request/response schemas
  services/
    nlp.py         # Keyword classification (EN + SW)
    sms.py         # SMS provider abstraction
    icpac.py       # ICPAC geospatial data fetch
  utils/
    config.py      # Pydantic Settings
backend/tests/     # pytest suite
```

## Where New Code Goes

| Change type | Directory |
|-------------|-----------|
| New API endpoint | `backend/app/main.py` (or new router file) |
| New DB model | `backend/app/models.py` |
| New Pydantic schema | `backend/app/schemas.py` |
| New SMS provider | `backend/app/services/sms.py` |
| New classification category | `backend/app/services/nlp.py` |
| New data source integration | `backend/app/services/` |
| Frontend feature | `frontend/js/` (app.js / api.js / map.js) |
| Frontend styling | `frontend/css/style.css` |
| Tests | `backend/tests/` (mirror source structure) |
| Documentation | `docs/` |
| Examples | `examples/` |

## Commit Convention

```
type: description

Types: feat, fix, docs, style, refactor, test, chore, ci
```

## PR Convention

- One PR = one logical change
- Title matches commit convention
- Description links to issue and summarizes changes
- All CI checks must pass before merge
- Squash-merge preferred

## Test File Naming

Tests mirror source: `backend/app/services/nlp.py` → `backend/tests/test_nlp.py`

## Documentation Sync

- API changes → update README API table + docs/api.md
- Model changes → update docs/architecture.md
- Config changes → update .env.example + docs/getting-started.md
