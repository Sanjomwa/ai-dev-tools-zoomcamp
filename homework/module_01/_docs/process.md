# Process

The issue is the unit of work. Every issue lives in GitHub, on `Sanjomwa/ai-dev-tools-zoomcamp`, labeled `MVP` or `post-MVP` (see `_docs/backlog.md` for how the current set was seeded).

Lifecycle:

1. Groomed — PM rewrites the issue into the `_docs/task-template.md` structure. See `_docs/team/pm.md`.
2. Implemented — an engineer builds exactly what the groomed issue specifies, no more. See `_docs/team/software-engineer.md`.
3. QA'd — QA checks the implementation against the issue's Acceptance Criteria only and returns PASS or FAIL. See `_docs/team/qa-engineer.md`.
4. Closed — a PASS closes the issue. A FAIL routes back to step 2, to the engineer — QA does not fix what it finds.

Commits close their issue with `Closes #N` in the message, so the GitHub issue closes automatically when the commit lands on the default branch.

Nothing here is automated yet — no CI, no test suite runs any of this. Grooming, implementation, and QA are each done by reading the issue and the code by hand.
