# Deployment Guide

## Render (recommended)

The project includes a `render.yaml` blueprint for one-click deployment.

### Automatic (Blueprint)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/kawacukennedy/community_voice_ews)

### Manual

1. Create account at [render.com](https://render.com)
2. Click **New +** → **Blueprint**
3. Connect `kawacukennedy/community_voice_ews`
4. Render auto-reads `render.yaml` and provisions the web service

### Environment Variables

Set these in the Render dashboard:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./ews.db` | PostgreSQL connection string for production |
| `SECRET_KEY` | No | auto-generated | JWT / encryption key |
| `SMS_API_KEY` | For SMS | — | Africa's Talking API key |
| `SMS_USERNAME` | For SMS | `sandbox` | Africa's Talking username |
| `TWILIO_ACCOUNT_SID` | For Twilio | — | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | For Twilio | — | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | For Twilio | — | Twilio sender number |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### PostgreSQL in Production

To use PostgreSQL instead of SQLite:

1. Create a PostgreSQL database (Render offers free managed Postgres)
2. Set `DATABASE_URL` to the connection string:
   ```
   postgresql://user:password@host:5432/ews
   ```
3. The app auto-creates tables on startup

## Docker

```bash
docker-compose up -d
# App at http://localhost:8000
```

## CI/CD

The project uses GitHub Actions:

- **CI** (`.github/workflows/ci.yml`) — runs on PR/push to `develop`: lint, test, validate frontend
- **Deploy** (`.github/workflows/deploy.yml`) — runs on push to `main`: test, deploy to Render

## SMS Provider Setup

### Africa's Talking

1. Sign up at [africastalking.com](https://africastalking.com)
2. Go to **Sandbox** → get API key
3. Set callback URL to `https://your-app.onrender.com/api/webhooks/sms`
4. Set `SMS_API_KEY` and `SMS_USERNAME` environment variables

### Twilio

1. Sign up at [twilio.com](https://twilio.com)
2. Get Account SID and Auth Token
3. Get a phone number
4. Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
