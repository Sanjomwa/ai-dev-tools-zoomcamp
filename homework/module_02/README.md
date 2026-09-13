# Leagueboard

A shared, no-login scoreboard for one sports league — teams, scheduled and completed games, and standings computed from recorded results.

Module 2 homework, AI Dev Tools Zoomcamp 2026 cohort.

- **Agent used:** Claude Code
- **Spec:** see `_docs/plan.md`
- **Contract:** see `openapi.yaml`
- **How to run:**
  - Frontend (`frontend/`): `npm install`, then `npm run dev` (Vite, `http://localhost:5173`)
  - Backend (`backend/`): `uv sync`, then `uv run uvicorn app.main:create_app --factory --port 8000`
  - Backend tests: `uv run pytest`

See `_docs/plan.md` for the full feature set and what's explicitly out of scope for the MVP.
