# Scaffold Project Structure

Initialize or verify the full project structure for this FastAPI + React monorepo.

## Expected Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings/config (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine, session, Base
│   │   ├── dependencies.py      # Shared Depends() functions
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   └── __init__.py
│   │   └── services/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── conftest.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/           # API client functions
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── router.tsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── storage/
│   └── db/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── CLAUDE.md
```

## Steps

1. Check which parts of the structure already exist
2. Create missing directories and files with sensible defaults
3. For backend:
   - Init pyproject.toml with uv if not exists (include fastapi, sqlalchemy, alembic, uvicorn, pytest, ruff, mypy)
   - Set up SQLAlchemy Base and session management
   - Set up Alembic configuration
   - Create a health check endpoint in main.py
4. For frontend:
   - Init Vite + React + TypeScript project if not exists
   - Set up routing (react-router-dom)
   - Set up API client (axios or fetch wrapper)
   - Configure proxy to backend in vite.config.ts
5. Create .env.example with documented variables
6. Create docker-compose.yml for postgres + redis (matching .mcp.json config)
7. Create CLAUDE.md with project conventions

## Important

- Do NOT overwrite existing files — only create missing ones
- Use the database connection from .mcp.json as reference for docker-compose
- Ask before making choices that aren't specified (e.g., CSS framework)
