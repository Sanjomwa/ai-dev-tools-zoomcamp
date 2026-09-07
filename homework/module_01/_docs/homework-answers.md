# Module 1 Homework — Questions & Answers

*AI Dev Tools Zoomcamp 2026. Answers below correspond to the six questions in the official `homework.md` (DataTalksClub/ai-dev-tools-zoomcamp, `cohorts/2026/01-overview/homework.md`), in the same order, for pasting into the submission form.*

## Question 1: Select your coding agent

**Claude Code.** Used consistently through the whole build — spec brainstorming, and then every implementation, PM-grooming, and QA pass on the actual codebase.

## Question 2: Turn the idea into a spec

Four features (see `_docs/plan.md`):

1. **Household + simple identity.** Members pick their name from the household's roster to identify themselves — no password, no login.
2. **Recurring chores with an expected cadence.** A chore is created once (name + cadence, e.g. "vacuum — weekly") and repeats indefinitely. No one-off chores.
3. **Completion-driven rotation.** A chore stays "with" one member — regardless of elapsed time — until they mark it done, then it advances to the next member in order.
4. **Overdue tracking, visual only.** The chore list flags whether a chore is currently overdue based on its cadence. No notifications, no reminders.

## Question 3: Django project

**`settings.py`** — that's where a newly created app gets registered, in `INSTALLED_APPS`.

## Question 4: Backlog

Task 1 (see `_docs/backlog.md`):

> **Household & Member models.** `Household(name)`, `Member(household FK, name, order)` — `order` is the rotation position, set by creation order. Migration + Django admin registration (roster management is unscored supporting functionality — admin is enough, no custom UI needed).

## Question 5: First version

**`uv run python manage.py runserver`**

## Question 6: Tests

**`python manage.py test`** (run in this project via `uv run python manage.py test`, per the project's `uv`-managed setup).
