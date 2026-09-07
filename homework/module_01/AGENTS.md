Stack: Django 6.1 + SQLite + uv + server-rendered templates, session-cookie identity (no real auth).

All commands below run from this directory (`homework/module_01/`), not the repo root.

Install deps: `uv sync`
Run migrations: `uv run python manage.py migrate`
Start dev server: `uv run python manage.py runserver`
Run tests: `uv run python manage.py test`

`chores/` is the Django app: models, views, templates, tests for the household/chore/rotation domain.
`config/` is Django project config only: settings, root urlconf, wsgi/asgi — no domain logic goes here.

Tasks are tracked as GitHub issues, labeled `MVP` / `post-MVP`. Not created yet.

See `_docs/decisions.md` for stack rationale and `_docs/process.md` for how this project is worked (not repeated here).
