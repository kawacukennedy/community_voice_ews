# Getting Started

## Prerequisites

- Python 3.12+
- pip

## Installation

```bash
git clone https://github.com/kawacukennedy/community_voice_ews.git
cd community_voice_ews
cp .env.example .env
make install
```

## Running the Backend

```bash
make dev-backend
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Running the Frontend

The frontend is served automatically by the backend at `http://localhost:8000`.

To run the frontend standalone (useful for development):

```bash
python3 -m http.server 5500 -d frontend/
```

## Running Everything Together

```bash
make dev
```

## Verifying It Works

```bash
curl http://localhost:8000/api/health
# {"status":"ok","version":"1.0.0","database":"connected","timestamp":"..."}
```

## Next Steps

- [Architecture](architecture.md) — understand the system design
- [API Reference](api.md) — explore all endpoints
- [Deployment Guide](deployment.md) — deploy to production
- [Examples](../examples/) — runnable API usage scripts
