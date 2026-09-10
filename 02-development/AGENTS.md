# Leagueboard — Agent notes

A shared, no-login scoreboard for one sports league. Full product spec: `plan.md` in this folder.

## Status

- `frontend/` — done for this pass: React + TypeScript + Vite, all "backend" calls centralized in `frontend/src/api/client.ts` against an in-memory mock store. Swapping in the real API later means changing only that file.
- `backend/` — not started. Next steps, in order:
  1. Derive an OpenAPI spec from `frontend/src/api/client.ts` and `frontend/src/types.ts` (that mock layer *is* the contract).
  2. Build the FastAPI backend against that spec, in-memory store first.
  3. Point `frontend/src/api/client.ts` at the real backend (expect a CORS step — add the frontend's dev origin to FastAPI's allowed origins).
  4. Swap the in-memory store for SQLite + SQLAlchemy.

## Conventions

- Backend: uv-managed, Python.
- Commit regularly — after each working step, not just at the end.
- Standings are computed from recorded game results, never stored directly.
- No auth in this version — open access is a deliberate spec choice, not an oversight.
