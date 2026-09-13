# ADR-0003: Course-materials and CLIO Findings Explorer live in separate repos, each with its own full-mirror sync.sh

**Status:** Accepted
**Date:** 2026-09-02
**Deciders:** Sam

## Context

This Cowork workspace covers two things at once: general course-following for the AI Dev Tools Zoomcamp, and planning for CLIO Findings Explorer, the course's required final project. Both live under one Cowork connected folder (`ai-dev-tools-zoomcamp`) so that what's learned module-by-module can directly inform the project (the project plan's own Module 3 MCP server, Module 4 custom subagent, etc. are sequenced against the course modules). The question this ADR settles: given one Cowork folder, should the WSL/execution side also be one repo, with one sync script, or two?

## Decision

Two separate WSL repos, never merged:
- `~/Projects/ai-dev-tools-zoomcamp` — course exercises and homework.
- `~/Projects/CLIO-Findings-Explorer-course-project` — the actual scored final-project codebase (FastAPI + React/TS + Postgres).

Each gets its own `sync.sh`, built to the same mechanism: full mirror in both directions (not a curated file list), manual (`pull`/`push` run by Sam in WSL, never autonomously by Cowork or Claude Code), fail loudly on a missing side rather than silently no-op. The course-side script additionally excludes `CLIO-Findings-Explorer-course-project/` (the project's own sibling Cowork mirror) so the two mechanisms never sweep up each other's content.

## Options Considered

### Option A: Two repos, two sync.sh, same mechanism
| Dimension | Assessment |
|---|---|
| Complexity | Two scripts to maintain, but they're near-identical in shape |
| Cost | None |
| Scalability | Each repo's structure can evolve independently |
| Team familiarity | N/A (solo) |

**Pros:** Course homework isn't part of what the final-project rubric grades, and the project's repo layout is dictated entirely by the rubric's expected contents (`frontend/`, `backend/`, `openapi.yaml`, etc.), not by the course repo's structure. Keeping them separate keeps both clean. A curated single sync also has a known failure mode in this exact workflow's own history (the Evidence Pipeline SDK project's curated push list silently dropped real code changes on a later pull).

**Cons:** Two scripts, two exclude lists to keep from drifting apart; a shared Cowork root means both mechanisms root at the same Windows folder and could in principle cross-contaminate if either exclude list is wrong.

### Option B: One combined repo for course + project
| Dimension | Assessment |
|---|---|
| Complexity | Lower (one script) |
| Cost | None |
| Scalability | Couples two things that don't share a grading rubric |
| Team familiarity | N/A (solo) |

**Pros:** One less script to maintain.
**Cons:** Mixes ungraded coursework with the scored capstone in one repo/history — makes neither one clean, and the two have genuinely different required structures.

## Trade-off Analysis

The deciding factor is that the two things being synced don't share a purpose: one is ungraded practice, the other is a rubric-scored deliverable with its own mandated layout. Sharing a Cowork *workspace* is fine (the module-by-module learning genuinely feeds the project plan); sharing a *repo* would not be, since it would force one repo to satisfy two unrelated structural requirements at once.

## Consequences

- Any session working in this workspace must check which repo/mirror a task actually touches before editing — CLAUDE.md's own instruction #1 exists partly to prevent conflating the two.
- Both scripts must be kept in sync on shape (exclude-list conventions, permission-flag fixes) even though they point at different repos — a fix found in one (e.g. the DrvFs permission-preservation bug, see status-log.md) should be checked against the other.

## Action Items

- [x] Course-side `sync.sh` built at the workspace root, project-side `sync.sh` built in `CLIO-Findings-Explorer-course-project/`
- [x] Course-side script excludes the project's sibling mirror folder
- [ ] Re-check the project's own `sync.sh` for the same permission-flag fix applied here (see status-log.md, 2026-09-10)
