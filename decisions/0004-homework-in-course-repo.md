# ADR-0004: Homework lives inside the course-materials repo (`homework/module_NN/`), not a separate third repo

**Status:** Accepted
**Date:** 2026-09-07
**Deciders:** Sam

## Context

`01-ai-native-workflow/module-01-direction.md` originally recommended a separate third repo for graded homework, distinct from both the course-following-notes repo and the CLIO Findings Explorer project repo. Before that was built, Sam had a directly comparable precedent from a prior course: [`Sanjomwa/LLM-ZOOMCAMP-2026`](https://github.com/Sanjomwa/LLM-ZOOMCAMP-2026), verified live rather than assumed, which uses numbered module folders for course-following work plus a sibling top-level `homework/` folder containing `module_01`–`module_05` subfolders — one repo, not three.

## Decision

Homework lives inside the same course-materials repo as course-following notes, under `homework/module_NN/`. No separate repo for homework. `homework_url` on each module's submission form points at the specific `homework/module_NN/` subfolder (GitHub deep-links to a folder correctly), not the repo root.

## Options Considered

### Option A: Homework inside the course-materials repo, `homework/module_NN/`
| Dimension | Assessment |
|---|---|
| Complexity | Lowest — one repo, one clone, one auth setup |
| Cost | None |
| Scalability | Matches a verified working precedent (LLM Zoomcamp) |
| Team familiarity | N/A (solo), but matches Sam's own established habit |

**Pros:** One less repo to init, auth, and keep straight; directly matches a precedent Sam already runs elsewhere, so submission-form conventions (deep link to a subfolder) are already known to work.
**Cons:** Course-following notes and graded homework share history/commits in one repo, so a homework-only reviewer sees unrelated notes commits too (not disqualifying — the LLM Zoomcamp precedent works the same way).

### Option B: Separate third repo just for homework
| Dimension | Assessment |
|---|---|
| Complexity | Higher — a third repo to create, clone, and auth |
| Cost | None |
| Scalability | No existing precedent for it working well |
| Team familiarity | N/A (solo) |

**Pros:** Cleanest possible separation between notes and graded work.
**Cons:** Extra setup for a separation the LLM Zoomcamp precedent shows isn't actually necessary; `module-01-direction.md`'s original recommendation of this option was made before checking that precedent.

## Trade-off Analysis

The deciding factor was a live, verified precedent rather than a guess: Sam's own LLM Zoomcamp repo already runs course-notes-plus-homework in one repo successfully, including the exact deep-link submission pattern this course's forms need. Inventing a third repo would have added setup cost to solve a separation problem that precedent shows doesn't actually cause issues.

## Consequences

- `module-01-direction.md` §2 and the workspace root `CLAUDE.md` were both corrected to match (the original separate-third-repo recommendation was retracted).
- The course-materials `sync.sh` carries homework too — no separate sync script exists or is needed for it (see ADR-0003).
- Homework's own build/runtime artifacts (Module 1's Django `.venv/`, `db.sqlite3`, migration caches) had to be added to that one script's exclude list rather than a homework-specific script's.

## Action Items

- [x] `module-01-direction.md` §2 corrected
- [x] Root `CLAUDE.md` naming-convention table updated to match
- [x] Module 1 (`homework/module_01/`) and Module 2 (`homework/module_02/`) both built under this convention
