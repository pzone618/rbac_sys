# Database Migration

Run Alembic database migration commands.

## Input

The user may provide: $ARGUMENTS

Parse the action from arguments (default: upgrade to latest):
- `generate <message>` — auto-generate a new migration from model changes
- `upgrade` or no args — apply all pending migrations
- `downgrade` — rollback one migration
- `history` — show migration history
- `current` — show current migration revision

## Commands

Based on the parsed action, run:

### Generate new migration
```bash
cd backend && uv run alembic revision --autogenerate -m "{message}"
```
After generating, read the migration file and verify it looks correct before applying.

### Upgrade (apply migrations)
```bash
cd backend && uv run alembic upgrade head
```

### Downgrade (rollback)
```bash
cd backend && uv run alembic downgrade -1
```

### Show history
```bash
cd backend && uv run alembic history --verbose
```

### Show current revision
```bash
cd backend && uv run alembic current
```

## Post-steps

- After generating: review the migration file for correctness
- After upgrade/downgrade: confirm the current revision matches expectations
- Warn the user if there are pending model changes that haven't been migrated
