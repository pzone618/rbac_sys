# Start Development Servers

Start the full-stack development environment (backend + frontend).

## Steps

1. Check that dependencies are installed:
   - Backend: verify `backend/.venv` exists, if not run `cd backend && uv sync`
   - Frontend: verify `frontend/node_modules` exists, if not run `cd frontend && npm install`

2. Start the backend server:
   ```bash
   cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 28000
   ```

3. Start the frontend dev server:
   ```bash
   cd frontend && npm run dev
   ```

4. Report the URLs:
   - Backend API: http://localhost:28000
   - API Docs: http://localhost:28000/docs
   - Frontend: http://localhost:5173

Run both servers in background tasks so the user can continue working.
