# Process

The issue is the unit of work. Every issue lives in GitHub, on `Sanjomwa/ai-dev-tools-zoomcamp`, labeled `MVP` or `post-MVP` (see `_docs/backlog.md` for how the current set was seeded).

Lifecycle:

1. Groomed — PM rewrites the issue into the `_docs/task-template.md` structure. See `_docs/team/pm.md`.
2. Implemented — an engineer builds exactly what the groomed issue specifies, no more. See `_docs/team/software-engineer.md`.
3. QA'd — QA checks the implementation against the issue's Acceptance Criteria only and returns PASS or FAIL. See `_docs/team/qa-engineer.md`.
4. Closed — a PASS closes the issue. A FAIL routes back to step 2, to the engineer — QA does not fix what it finds.

Commits close their issue with `Closes #N` in the message, so the GitHub issue closes automatically when the commit lands on the default branch.

## Session isolation

Before pasting any role's prompt (PM, engineer, or QA), run `/clear` in this terminal, or start a genuinely new Claude Code session in a fresh terminal — not `claude --continue` or `--resume`. This applies every time the role changes, even mid-task: reusing a session's conversation history across roles defeats the isolation this section exists for. A session that already discussed the implementation is not a valid QA session for it, even if it's told to "act as QA now."

PM, engineer, and QA are three separate Claude Code sessions — never the same session playing more than one role on the same issue. Concretely:

- Session A (PM) grooms the issue into `_docs/task-template.md` shape and stops. It does not touch code.
- Session B (engineer) receives only the groomed issue and implements it. It does not review its own work.
- Session C (QA) receives only the groomed issue and the repo state — never session B's transcript or reasoning — and checks the implementation against the issue's Acceptance Criteria only, returning PASS or FAIL.

This is the one rule in the whole process that must not be skipped under time pressure: it's what makes "QA'd" mean something other than the engineer re-reading its own diff. Everything else in this file can be compressed if we're behind schedule; this can't.

Nothing here is automated yet — no CI, no test suite runs any of this. Grooming, implementation, and QA are each done by reading the issue and the code by hand.
