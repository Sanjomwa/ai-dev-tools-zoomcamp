# Module 1 — The AI-Native Workflow

This repo keeps two kinds of material apart. Graded work lives under `homework/module_NN/`.
Course-following notes live in numbered folders at the root (`01-`, `02-`, …). This is one of
those: notes on Module 1 itself — the workshop, the process it teaches, and what actually held
up when that process was run on real work.

It is **not** a write-up of the homework's answers. Those are in
[`homework/module_01/_docs/homework-answers.md`](../homework/module_01/_docs/homework-answers.md)
and are not repeated here.

---

## Same sentence, different software

The workshop and the homework are the same exercise pointed at two different, deliberately
vague one-liners:

- Workshop: *"a tool for weekly feedback for projects"*
- Homework: *"a tool for managing shared household chores"*

The homework's own text makes the point explicitly: different students starting from the same
vague sentence ship different software, because they write different specs. The spec is what
determines the output — not the prompt, and not the one-liner. Two people can hand an agent the
identical sentence and, if their specs differ, get back two unrelated applications.

The instructor's reference implementation of the workshop one-liner is
[`github.com/alexeygrigorev/retroloop`](https://github.com/alexeygrigorev/retroloop).

## The process it teaches

```
brainstorm
  → plan (_docs/plan.md)
  → pick a stack
  → backlog (backlog.md)
  → one GitHub issue per backlog item
  → context files (AGENTS.md, _docs/process.md, role docs)
  → PM → engineer → QA loop, run as genuinely separate sessions
```

The loop at the end is the part that carries the method: a PM session grooms an issue, an
engineer session builds exactly what the groomed issue specifies, and a QA session checks the
result against that issue's acceptance criteria — each one a separate Claude Code session, not
one session switching hats.

## File conventions

Checked against retroloop's live repository, not just the workshop transcript — the transcript
is looser than the repo about several of these.

| Convention | Detail |
| --- | --- |
| `_docs/` | Project docs directory — leading underscore, **not** `docs/`. |
| `CLAUDE.md` | A single line: `@AGENTS.md`. It exists only to import `AGENTS.md`. |
| `_docs/decisions.md` | Append-only log. Entries are added, not edited or removed. |
| `_docs/process.md` | How the project is worked — the issue lifecycle and the isolation rule. |
| `_docs/team/` | One file per role (PM, engineer, QA). |
| `_docs/task-template.md` | The shape every groomed issue takes: **Goal / Acceptance Criteria / Out of Scope / Constraints**. |

## The one load-bearing rule

> **No agent grades its own work.**

This is the cheapest part of the whole process to implement — it costs one extra session, not
an orchestrator, not tooling, not a framework. It is also the one part that must not be cut
under time pressure. Everything else in `process.md` can be compressed if the schedule slips;
this can't, because without it "QA'd" means nothing more than the engineer re-reading its own
diff.

## Decisions made before building

Recorded here for the reasoning, not just the outcome.

- **Don't rebuild retroloop.** It's the same framework teaching the same lesson; re-implementing
  it start to finish adds no new reps. Reading its conventions does.
- **Follow the homework's required paths literally**, even where the workshop transcript is
  looser about them. When the transcript and the assignment disagree on a path or a filename,
  the assignment wins.
- **Scale the loop down by running it, not by skipping it.** The homework's PM→engineer→QA loop
  is run deliberately on real tasks rather than orchestrated across the entire backlog at once.
  Fewer passes, each one real — not a driver script that fans the whole backlog out to
  sub-agents.
- **The artifacts are the point.** `AGENTS.md`, `process.md`, the role docs, and a QA-verdict
  contract that actually holds are the deliverable. The Django app is scaffolding to hang them
  on.
- **One explicit reversal.** The plan originally put the homework in its own separate
  repository. The reasoning: a root-level context file would leak into agent sessions started
  in subfolders. That was reversed the same day. The homework now nests under
  `homework/module_01/` — matching this account's existing convention from a prior course — and
  the leakage concern is solved directly, by creating no root-level context file at all. The
  context file is scoped to `homework/module_01/` and nothing above it.

---

## What held up when the process was run

Two findings from actually running the build. These are the substantive part of this document.

### Finding 1 — the isolation rule fails visibly the one time it's skipped

A QA pass was run in the same chat session that had just written the code under review.

It returned a clean **PASS** on every acceptance criterion. Then, unprompted, it flagged itself:
it still had the full implementation in its own context, so its verdict couldn't count as
review. It had checked the criteria against its own memory of building the thing, not against
the code as a stranger would find it.

The pass was re-run from a genuinely fresh session. That session confirmed, at the very start of
its own output, that it had no memory of the implementation. Same issue, same acceptance
criteria — and this time it caught real edge cases that the contaminated pass's confidence had
glossed straight over.

**Takeaway:** a PASS from a reviewer that wrote the code is a measurement of that reviewer's
memory, not of the code. The isolation rule isn't bureaucracy; it's the thing that makes the
verdict mean something.

### Finding 2 — a groomed issue is not the same as an independently buildable one

Two backlog issues were each, on their own, well-formed: checkable acceptance criteria, an
explicit out-of-scope section, stated constraints. By the template, both were ready.

Together they were circular. One issue's acceptance criteria required an endpoint that the
other issue was responsible for building. That other issue's own constraints required the first
issue's guard to already exist. Neither could be built alone as written — each one's
precondition sat on the other side of the pair.

**Takeaway:** buildability is a property of the issue *graph*, not of any single issue. A
grooming pass that only ever looks at one issue at a time can't catch this. The fix is
re-grooming — decide which issue owns the shared piece, consolidate it there, and re-link the
dependency one way; or merge the two if they're really one slice of work. It is *not* something
to work around during implementation.

This became a course FAQ contribution, filed under the `ai-dev-tools-zoomcamp` course:
[`github.com/DataTalksClub/faq/issues/387`](https://github.com/DataTalksClub/faq/issues/387).

---

## Where things live

| Path | What it is |
| --- | --- |
| [`../homework/module_01/`](../homework/module_01/) | The graded deliverable — the chores app and its docs. |
| [`../homework/module_01/_docs/homework-answers.md`](../homework/module_01/_docs/homework-answers.md) | The six homework questions and their answers. |
| [`../homework/module_01/_docs/plan.md`](../homework/module_01/_docs/plan.md) | The product spec that came out of the brainstorm. |
| [`../homework/module_01/_docs/backlog.md`](../homework/module_01/_docs/backlog.md) | MVP and post-MVP backlog items. |
| [`../homework/module_01/_docs/decisions.md`](../homework/module_01/_docs/decisions.md) | Append-only stack/decision log. |
| [`../homework/module_01/_docs/process.md`](../homework/module_01/_docs/process.md) | The issue lifecycle and the session-isolation rule. |
| [`../homework/module_01/_docs/team/`](../homework/module_01/_docs/team/) | One context file per role — PM, engineer, QA. |
| [`github.com/alexeygrigorev/retroloop`](https://github.com/alexeygrigorev/retroloop) | The instructor's reference implementation of the workshop one-liner. |
| [`github.com/DataTalksClub/faq/issues/387`](https://github.com/DataTalksClub/faq/issues/387) | The FAQ contribution from Finding 2. |

For orientation notes written before implementation, see
[`_reference/direction-notes.md`](_reference/direction-notes.md) — superseded by this document
wherever the two disagree.
