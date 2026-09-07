# Build for Production

Build the project for production deployment.

## Input

The user may provide: $ARGUMENTS

Parse from arguments:
- Target: `frontend`, `backend`, `all` (default: all)
- Environment-specific options if any

## Frontend Build

```bash
cd frontend && npm run build
```

After build:
- Verify `frontend/dist/` was created
- Report bundle size if available
- Check for any build warnings

## Backend Preparation

```bash
cd backend && uv run python -m compileall app/
```

Checks:
- Verify all migrations are applied
- Verify .env.example is up to date with required variables
- Run type checking: `uv run mypy app/`

## Docker Build (if Dockerfile exists)

```bash
docker compose build
```

## Steps

1. Run frontend build
2. Run backend checks
3. Report build status and any warnings
4. If Docker is configured, offer to build containers
