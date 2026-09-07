# Direction notes — Module 1

*Dated 2026-09-07. Written during orientation, before any implementation. Superseded by
[`../README.md`](../README.md) wherever the two conflict — read that first.*

## retroloop file conventions

Checked against the live reference repo
([`github.com/alexeygrigorev/retroloop`](https://github.com/alexeygrigorev/retroloop)), not
just the workshop transcript — the transcript is looser about these:

- `_docs/`, with a leading underscore — not `docs/`.
- `CLAUDE.md` is one line, `@AGENTS.md`; it only imports `AGENTS.md`.
- `_docs/decisions.md` is an append-only log.
- `_docs/process.md` holds the workflow.
- `_docs/team/` holds one file per role.
- `_docs/task-template.md` is structured Goal / Acceptance Criteria / Out of Scope / Constraints.

## Repo-isolation reversal

**Original plan:** put the homework in its own separate repository. Reasoning — a shared
root-level context file would leak into agent sessions started in subfolders, so keeping the
homework in its own repo was the way to keep contexts clean.

**What was done instead:** no separate repo. The homework nests under `homework/module_01/`,
matching this account's existing convention from a prior course. The leakage concern is solved
directly: no root-level context file is created at all. The context file is scoped to
`homework/module_01/`, so there is nothing above it to leak downward.
