Stack: Vite + React 19 + TypeScript frontend; FastAPI backend (in-memory store first, then SQLite + SQLAlchemy) built against `openapi.yaml`. No login — open access is a deliberate spec choice (see `_docs/plan.md`).

All paths below are relative to this directory (`homework/module_02/`), not the repo root.

Frontend — run from `frontend/`:

Install deps: `npm install`
Start dev server: `npm run dev`
Build: `npm run build`
Lint: `npm run lint`
Tests: none yet.

Backend — not yet built. It will live in `backend/` as a uv-managed FastAPI service satisfying `openapi.yaml`: in-memory store first, then SQLite + SQLAlchemy. Its install/run/test commands get added here once it exists.

`frontend/` is the React prototype: every "backend" call is centralized in `frontend/src/api/client.ts` against an in-memory mock, so swapping in the real API touches only that file.
`openapi.yaml` is the REST contract derived from that mock layer; the backend is built to satisfy it.

Standings are always computed from recorded game results, never stored directly.

Tasks are tracked as GitHub issues, labeled `MVP` / `post-MVP`. Not created yet.

See `_docs/plan.md` for the full product spec (goals and non-goals) and `../../02-development/AGENTS.md` for the build-sequence notes (not repeated here).
