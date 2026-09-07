# Chores App — Stack Decisions

*Module 1 homework, AI Dev Tools Zoomcamp 2026. See `_docs/plan.md` for the product spec.*

1. **Dependency management: uv.** Fast, single tool for env + deps + lockfile, and the modern default for new Python projects.

2. **Database: SQLite.** Single-household, no-concurrent-writer scope needs no DB server — a file is enough.

3. **Frontend: Django templates (server-rendered).** The full MVP is CRUD-shaped (view list, mark done, see overdue flag) — no SPA needed, and Django gives templates, ORM, and sessions in one framework.

4. **Identity: Django session cookie.** `request.session['member_id']` after picking a name persists identity server-side with zero extra code — it's session framework Django already enables by default, not new "auth," and it doesn't require bridging client-side storage back to the server on every request the way localStorage would.

5. **Git commit/push: human-only, never autonomous.** Same convention as the CLIO capstone project. Claude Code stages and describes changes; Sam alone runs `git commit` and `git push`. Applies to every task in this repo going forward, not just this one.
