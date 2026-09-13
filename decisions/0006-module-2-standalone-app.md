# ADR-0006: Module 2 (Leagueboard) built as its own standalone app, not folded into CLIO Findings Explorer

**Status:** Accepted
**Date:** 2026-09-10 (question opened 2026-09-07)
**Deciders:** Sam

## Context

Module 5 ("Coding Agent Capabilities") has no graded homework of its own — it's assessed by an "Agent Extension Pack" deliverable that the course explicitly frames as extending "the app you built in Modules 2 and 3." That raised a real strategic question once Module 2 started: build Module 2's app (Leagueboard) as a genuinely separate exercise, or fold "Modules 2 and 3" work directly into CLIO Findings Explorer, so the eventual Module 5 extension pack and the final-project rubric's own "Agent Extension Pack" scoring item could be satisfied by the same artifact.

## Decision

Leagueboard is built as its own separate app (`homework/module_02/`), not folded into CLIO Findings Explorer. Module 5's Agent Extension Pack will extend Leagueboard when that module arrives, not the capstone project.

## Options Considered

### Option A: Leagueboard as its own separate app
| Dimension | Assessment |
|---|---|
| Complexity | Lower per-module — each module's app is scoped to what that module actually teaches |
| Cost | None |
| Scalability | Keeps CLIO Findings Explorer's scope defined entirely by its own rubric, not stretched to also satisfy Module 2/3/5's requirements |
| Team familiarity | N/A (solo) |

**Pros:** CLIO Findings Explorer's repo layout and milestones are already dictated by the final-project rubric (see ADR-0003's reasoning) — grafting Module 2/3 homework requirements onto it would pull it in a direction the rubric doesn't ask for. Each homework module stays a clean, standalone demonstration of that module's own workflow (frontend prototype → contract → backend, per `workflow.md`).
**Cons:** Module 5's eventual Agent Extension Pack extends a smaller, homework-only app rather than the actual capstone — some of that later work may not transfer to CLIO Findings Explorer.

### Option B: Fold Module 2 (and by extension Module 3) into CLIO Findings Explorer
| Dimension | Assessment |
|---|---|
| Complexity | Higher — CLIO's own scope has to absorb Module 2/3's requirements too |
| Cost | Real risk of scope creep on the graded capstone |
| Scalability | Couples two rubrics (course-module grading and final-project grading) that don't otherwise need to match |
| Team familiarity | N/A (solo) |

**Pros:** Module 5's Agent Extension Pack would extend the actual capstone, which is arguably the more meaningful target for that deliverable.
**Cons:** CLIO Findings Explorer's architecture (plan §2.5) is dictated by the final-project rubric, not by what Module 2/3 happen to teach that week — forcing them into one artifact risks compromising both.

## Trade-off Analysis

The deciding factor is the same one behind ADR-0003 (keeping the course-materials and CLIO repos separate): the two things being combined don't share a rubric. Module 2/3's grading criteria and CLIO Findings Explorer's final-project rubric are independent; satisfying both with one artifact would mean designing to the intersection of two unrelated specs instead of either one cleanly.

## Consequences

- `homework/module_02/` (Leagueboard) is a fully independent FastAPI + React/TS/SQLite app with its own `openapi.yaml`, no dependency on CLIO Findings Explorer's codebase.
- The CLIO Findings Explorer plan's own §4 milestone table has NOT been revised to reflect any of this — that's a separate, deliberate edit still open for Sam to make or request, scoped entirely to that project's own `CLAUDE.md`/plan (not touched by this ADR).
- When Module 5 arrives, its Agent Extension Pack will target Leagueboard (or whatever Module 2/3 app exists by then), not CLIO Findings Explorer.

## Action Items

- [x] Module 2 built as `homework/module_02/`, independent of the CLIO Findings Explorer repo (the `hw02` submission form itself is still open as of 2026-09-13 — see `status-log.md`)
- [ ] Revisit whether Module 3's app is also Leagueboard (extending it) or a fresh module-scoped app, when Module 3 starts
