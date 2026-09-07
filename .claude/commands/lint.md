# Lint and Format Code

Run linting and formatting tools on the codebase.

## Input

The user may provide: $ARGUMENTS

Parse from arguments:
- Scope: `backend`, `frontend`, `all` (default: all)
- Mode: `check` (report only) or `fix` (auto-fix, default)

## Backend (Python)

Format with ruff:
```bash
cd backend && uv run ruff format .
```

Lint with ruff:
```bash
cd backend && uv run ruff check . --fix
```

Type check with mypy (check only, no auto-fix):
```bash
cd backend && uv run mypy app/
```

## Frontend (TypeScript/React)

Lint with ESLint:
```bash
cd frontend && npm run lint
# or with fix:
cd frontend && npm run lint -- --fix
```

Format with Prettier:
```bash
cd frontend && npx prettier --write "src/**/*.{ts,tsx,css}"
```

Type check:
```bash
cd frontend && npx tsc --noEmit
```

## Steps

1. Determine scope and mode from arguments
2. Run formatters first (they may fix lint issues)
3. Run linters
4. Run type checkers
5. Report issues found and fixed
6. If issues remain that can't be auto-fixed, show them with file locations
