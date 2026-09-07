# Run Tests

Run the test suite for backend, frontend, or both.

## Input

The user may provide: $ARGUMENTS

Parse from arguments:
- Scope: `backend`, `frontend`, `all` (default: all)
- Specific test file or pattern (optional)
- Options: `--coverage`, `--watch`, `--verbose`

## Backend Tests

```bash
cd backend && uv run pytest {args}
```

Common variations:
- All tests: `uv run pytest`
- With coverage: `uv run pytest --cov=app --cov-report=term-missing`
- Specific file: `uv run pytest tests/test_{name}.py`
- Verbose: `uv run pytest -v`
- Stop on first failure: `uv run pytest -x`

## Frontend Tests

```bash
cd frontend && npm run test {args}
```

Common variations:
- All tests: `npm run test`
- Watch mode: `npm run test -- --watch`
- With coverage: `npm run test -- --coverage`
- Specific file: `npm run test -- {pattern}`

## Steps

1. Determine scope from arguments
2. Run the appropriate test command(s)
3. Report results summary: passed, failed, skipped
4. If tests fail, show the failure details and suggest fixes
