# Module 2 Homework — Questions & Answers

*AI Dev Tools Zoomcamp 2026. Answers below correspond to the seven questions in the official `homework.md` (DataTalksClub/ai-dev-tools-zoomcamp, `cohorts/2026/homework/02-development/homework.md`), in the same order, for pasting into the submission form.*

## Question 1: Pick your project

**Sports-league scoreboard.** Built as Leagueboard in `homework/module_02/` — teams, scheduled/completed games, and standings computed from recorded results.

## Question 2: Spec first

**"Leagueboard."** Spec at `_docs/plan.md`, which also records the name candidates considered and rejected (PitchTable, ScoreKeep, MatchTrack).

## Question 3: GitHub Repository

**`<commit sha — fill in after Sam commits and pushes this change>`.** As of this commit, `_docs/plan.md` (this project's spec file — named `plan.md` rather than the homework's suggested `specs.md`, consistent with `homework/module_01/`'s own convention), the repo-root `.gitignore`, `AGENTS.md`, and `README.md` are all in place under `homework/module_02/`.

## Question 4: Frontend prototype

**`npm run dev`** (after `npm install`). Confirmed against `frontend/package.json`'s `scripts.dev`, which runs `vite`.

## Question 5: Backend

**`uv run uvicorn app.main:create_app --factory --port 8000`** (after `uv sync`). Confirmed against `backend/app/main.py`'s `create_app(database_url: str | None = None)` factory function and `AGENTS.md`'s documented backend start command.

## Question 6: Connect frontend and backend

**`http://localhost:8000/api`.** Confirmed against the `BASE_URL` constant in `frontend/src/api/client.ts`, which every backend call in the frontend goes through.

## Question 7: Database

**`uv run pytest`** (run from `backend/`). Confirmed passing — 15 passed — against the SQLAlchemy/SQLite-backed store as of this commit.
