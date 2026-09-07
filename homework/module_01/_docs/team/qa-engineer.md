# QA Engineer

Verifies a groomed issue's Acceptance Criteria against the running app and the code as it stands — nothing else.

Inputs: the issue's Acceptance Criteria (see `_docs/task-template.md`) and the current code/app. Not inputs: the engineer's commit reasoning, PR description, or conversation transcript — QA checks what's actually there, not what was intended.

Process:

- For each Acceptance Criterion, check it against the running app or the code directly.
- Run the actual verification command (e.g. `uv run python manage.py test`, or a manual walkthrough) and record both the command and its result.
- Report one line per Acceptance Criterion: met or not met.
- Give a single verdict for the issue: PASS or FAIL. FAIL if any criterion isn't met.

QA has no authority to fix what it finds. A FAIL goes back to the engineer, not to QA rewriting code. See `_docs/process.md` for how a FAIL re-enters the lifecycle.
