Stack: Vite + React 19 + TypeScript frontend; FastAPI backend (SQLite + SQLAlchemy) built against `openapi.yaml`. No login — open access is a deliberate spec choice (see `_docs/plan.md`).

All paths below are relative to this directory (`homework/module_02/`), not the repo root.

Frontend — run from `frontend/`:

Install deps: `npm install`
Start dev server: `npm run dev` (Vite; defaults to `http://localhost:5173`)
Build: `npm run build`
Lint: `npm run lint`
Tests: none yet.

Backend — run from `backend/`:

Install deps: `uv sync`
Start dev server: `uv run uvicorn app.main:create_app --factory --port 8000`
Run tests: `uv run pytest`

`backend/` is a uv-managed FastAPI service satisfying `openapi.yaml`, all under `/api`. Storage is SQLite via SQLAlchemy Core/ORM (`app/db.py`, `app/models.py`), chosen so a later move to Postgres is a `DATABASE_URL` change (default `sqlite:///./leagueboard.db`; tests use `sqlite:///:memory:` for isolation). `app/store.py` is the repository layer — seeded once, on first use of an empty database, with data shaped like `frontend/src/api/mockData.ts` (same teams, same games, same ids) so manual testing against the frontend looks the same as it did against the mock. CORS is restricted to `http://localhost:5173` (`app/main.py`'s `FRONTEND_ORIGIN`), the frontend's actual Vite dev origin.

`frontend/src/api/client.ts` now calls the real backend at `http://localhost:8000/api` via `fetch()` instead of the in-memory mock — it's still the only file that talks to the backend, per the original design. `frontend/src/api/mockData.ts` is unused now but left in place as a reference for the backend's seed shape.
`openapi.yaml` is the REST contract derived from that former mock layer; the backend satisfies it (see `_docs/decisions.md`-equivalent notes below for the two intentional deviations).

Known deviations from `openapi.yaml`:
- Pydantic's automatic 422 validation errors are normalized to a single string `detail` message (FastAPI's default is a list of error objects); this keeps every error response — 404/409/422 alike — matching the `Error` schema's `{"detail": string}` shape exactly.
- `POST /teams` also returns 422 (not just empty-name) for a duplicate team name. `Team.name` is the identifier other endpoints match against, so silently allowing duplicates (as the mock does) breaks that invariant once persisted; 422 is the only error code the spec already defines for this endpoint.

Standings are always computed from recorded game results, never stored directly.

Tasks are tracked as GitHub issues, labeled `MVP` / `post-MVP`. Not created yet.

See `_docs/plan.md` for the full product spec (goals and non-goals) and `../../02-development/AGENTS.md` for the build-sequence notes (not repeated here).
