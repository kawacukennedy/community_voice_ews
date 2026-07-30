# Contributing to Community Voice EWS

First off, thank you for considering contributing! This project aims to help communities in the IGAD region respond to climate disasters — every contribution, big or small, makes a difference.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Convention](#commit-convention)
- [Branch Strategy](#branch-strategy)
- [Project Areas](#project-areas)

## Code of Conduct

This project is committed to providing a welcoming, inclusive, and harassment-free experience. By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. **Find an issue** — browse [good first issues](https://github.com/kawacukennedy/community_voice_ews/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) or [help wanted](https://github.com/kawacukennedy/community_voice_ews/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
2. **Comment on the issue** — let others know you're working on it
3. **Fork & branch** — create a feature branch from `develop`
4. **Code** — follow the standards below
5. **Test** — ensure tests pass and add new ones
6. **PR** — open a pull request against `develop`

## How to Contribute

### Reporting Bugs

- Check existing issues first
- Use the [bug report template](https://github.com/kawacukennedy/community_voice_ews/issues/new?labels=bug&template=bug_report.yml)
- Include steps to reproduce, expected vs actual behavior
- Add relevant logs, screenshots, or API responses

### Suggesting Features

- Use the [feature request template](https://github.com/kawacukennedy/community_voice_ews/issues/new?labels=enhancement&template=feature_request.yml)
- Describe the problem you're solving, not just the solution
- Explain how it helps communities in the IGAD region

### Improving Documentation

- Documentation lives in `docs/` and the README
- API changes must update the API table in README
- Model changes must update `docs/architecture.md`

### Adding Translations

- NLP keywords for additional languages go in `backend/app/services/nlp.py`
- UI translations go in `frontend/js/app.js`

## Development Setup

### Prerequisites

- Python 3.12+
- pip

### Local Setup

```bash
git clone https://github.com/kawacukennedy/community_voice_ews.git
cd community_voice_ews
cp .env.example .env
make install
```

### Start Developing

```bash
# Terminal 1: Backend API
make dev-backend

# Terminal 2: Frontend (optional — backend serves frontend too)
python3 -m http.server 5500 -d frontend/

# Or both together
make dev
```

Open http://localhost:8000 — API docs at http://localhost:8000/docs.

## Coding Standards

### Python (Backend)

| Rule | Standard |
|------|----------|
| Style | [PEP 8](https://peps.python.org/pep-0008/) |
| Line length | 120 characters |
| Formatting | [black](https://black.readthedocs.io) `--line-length=120` |
| Linting | [flake8](https://flake8.pycqa.org) `--max-line-length=120 --extend-ignore=E203` |
| Types | Use type hints for all function signatures |
| Imports | Standard library → third-party → local (alphabetical) |

```bash
make lint    # Check formatting + linting
make format  # Auto-format with black
```

### JavaScript (Frontend)

- ES6+ syntax
- camelCase for functions and variables
- No external libraries beyond Leaflet + Leaflet.markercluster
- Comments for non-obvious logic

### CSS

- Use CSS custom properties (variables in `:root`)
- Mobile-first responsive design
- Support dark mode via `prefers-color-scheme`

## Testing

- All new features must include tests
- API endpoints: test success and error cases
- NLP: test English and Swahili keywords
- Tests mirror source structure:

```
backend/app/services/nlp.py  →  backend/tests/test_nlp.py
```

```bash
make test    # Run full suite
```

```bash
# Run specific test file
cd backend && python -m pytest tests/test_nlp.py -v

# Run with coverage
cd backend && python -m pytest tests/ -v --cov=app
```

## Pull Request Process

1. Create a feature branch from `develop`: `git checkout -b feat/your-feature develop`
2. Make changes with descriptive commits
3. Run `make lint && make test`
4. Push and open a PR against `develop`
5. Ensure CI checks pass
6. Request review from a maintainer
7. Squash-merge when approved

### PR Checklist

- [ ] `make lint` passes
- [ ] `make test` passes
- [ ] New tests added for new code
- [ ] Documentation updated (README, docs/, or inline)
- [ ] PR title follows commit convention

## Commit Convention

```
<type>: <short description>

Types: feat, fix, docs, style, refactor, test, chore, ci
```

Examples:
- `feat: add Kiswahili SMS keyword matching`
- `fix: handle empty report body in NLP classifier`
- `docs: update API endpoint table in README`
- `test: add integration test for SMS webhook`

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production — deployable at all times |
| `develop` | Integration — PRs merge here |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation |
| `refactor/*` | Code restructuring |

## Project Areas

| Area | Description | Key Files |
|------|-------------|-----------|
| Backend API | FastAPI endpoints, models, schemas | `backend/app/main.py`, `models.py`, `schemas.py` |
| NLP | Message classification engine | `backend/app/services/nlp.py` |
| SMS | SMS provider integration | `backend/app/services/sms.py` |
| ICPAC | Official forecast data integration | `backend/app/services/icpac.py` |
| Frontend | Web dashboard, map, SMS demo | `frontend/` |
| Infra | CI/CD, Docker, Render deploy | `.github/`, `render.yaml`, `Dockerfile` |
| Docs | Guides, API reference | `docs/` |

## Need Help?

- Open a [Discussion](https://github.com/kawacukennedy/community_voice_ews/discussions)
- Tag `@kawacukennedy` in issues or PRs
- Check existing issues and PRs for context
