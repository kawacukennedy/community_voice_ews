# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. Email the maintainer directly at [kawacukennedy](https://github.com/kawacukennedy)
3. Provide a detailed description and steps to reproduce

We will respond within 48 hours and work on a fix promptly.

## Best Practices

This project follows these security practices:
- All environment variables are loaded from `.env` (never committed)
- Row Level Security enabled on all database tables
- Input validation on all API endpoints
- CORS restricted to known origins
- No secrets in client-side code
