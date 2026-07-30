# Contributing to Community Voice EWS

## Code of Conduct

This project is committed to providing a welcoming, inclusive, and harassment-free experience for everyone.

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Use the issue template and provide as much detail as possible
- Include steps to reproduce, expected behavior, and actual behavior

### Feature Requests

- Describe the problem you're solving, not just the solution
- Explain how it helps communities in the IGAD region
- Keep scope focused and practical

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `make test`
5. Run linting: `make lint`
6. Commit with clear messages: `git commit -m "feat: add X feature"`
7. Push: `git push origin feature/your-feature`
8. Open a Pull Request

## Coding Standards

### Python (Backend)

- Follow PEP 8
- Line length: 120 characters
- Use type hints for all functions
- Docstrings for public functions
- Use `black` for formatting: `black app/ --line-length=120`
- Use `flake8` for linting: `flake8 app/ --max-line-length=120`

### JavaScript (Frontend)

- Use ES6+ syntax
- No external libraries beyond Leaflet and its plugins
- All functions in camelCase
- Comments for non-obvious logic

### CSS

- Use CSS custom properties (variables)
- Mobile-first approach
- Follow the existing design system in `:root`
- Support dark mode via `prefers-color-scheme`

## Testing Requirements

- All new features must include tests
- API endpoints: test success and error cases
- NLP: test English and Swahili keywords
- Run `make test` before submitting
- Minimum 80% code coverage for new code

## Branch Strategy

- `main` - production-ready code
- `develop` - integration branch
- `feature/*` - new features
- `fix/*` - bug fixes
- `docs/*` - documentation

## Commit Convention

```
type: description

Types: feat, fix, docs, style, refactor, test, chore
```

## Building for Communities

This project serves vulnerable communities. When contributing:
- Keep the UI simple and accessible (WCAG 2.1 AA)
- Support low-bandwidth environments
- Design for users with basic phones
- Support English and Swahili
- Never require JavaScript for critical paths
