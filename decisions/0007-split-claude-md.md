# ADR-0007: Split the workspace CLAUDE.md into reference doc + decisions/ (ADRs) + status-log.md

**Status:** Accepted
**Date:** 2026-09-13
**Deciders:** Sam

## Context

By 2026-09-13 the workspace-root `CLAUDE.md` had grown from a same-day design doc (written 2026-09-02) to roughly 225 lines / 46KB, entirely by appending dated narrative sections: "Status as of ..." updates, an incident post-mortem (`sync.sh pull` deleting `homework/module_01/`), a pre-commit audit and its correction, a follow-up verification pass, and per-module verification writeups. Meanwhile `decisions/` already existed at the workspace root as a working ADR pattern (0001, 0002) but was scoped only to cross-module architectural choices (auth, sync model) — workspace/governance decisions (repo structure, git rules, module-2 scoping) had nowhere to go but into `CLAUDE.md`'s prose. `CLAUDE.md`'s own instruction #1 tells every fresh session to read it in full before doing anything else, so its growth directly taxed every future session, and its own instruction #5 ("update this file when workspace-level layout changes... don't let it drift into describing history") was being violated by its own accumulated content.

## Decision

Split the workspace documentation into three files with distinct, non-overlapping jobs:

- **`CLAUDE.md`** — stable reference only: workspace purpose, repo layout, naming conventions, sync mechanics rules, governance rules, submission workflow, learning-in-public/FAQ conventions. Points to the other two files rather than duplicating their content.
- **`decisions/`** — ADRs for choices with real trade-offs worth keeping for future projects (already the established pattern for architecture; extended here to cover workspace/governance decisions too — see ADR-0003 through ADR-0006).
- **`status-log.md`** — the append-only narrative: dated status updates, incident reports, audit/verification writeups. Read when a session needs "what's the current state," not needed to understand "how does this workspace work."

`decisions/` starts syncing into the actual git repo via `sync.sh` (removed from the exclude list) since ADRs explain why the code is built a certain way and belong next to it. `status-log.md` stays Cowork-only, same treatment as `CLAUDE.md` and `workflow.md` — it's Cowork's own working notes about running the process, not part of the graded submission.

## Options Considered

### Option A: Three-file split (reference / ADRs / status log)
| Dimension | Assessment |
|---|---|
| Complexity | One new file, one folder's scope widened, one sync.sh line removed |
| Cost | None |
| Scalability | `CLAUDE.md` stays roughly constant size going forward; only `status-log.md` and `decisions/` grow |
| Team familiarity | N/A (solo), reuses a pattern already proven at 0001/0002 |

**Pros:** Every future session pays a bounded, small cost to read `CLAUDE.md` in full (as its own instruction #1 requires) instead of a cost that grows every session. Decisions and incident history stop competing for the same document, so each stays legible on its own terms. Reuses infrastructure (the ADR template) that already works rather than inventing something new.
**Cons:** Three files to keep straight instead of one; a session has to know which file to write into for a given kind of update (mitigated by making that explicit in `CLAUDE.md`'s own instructions).

### Option B: Leave `CLAUDE.md` as a single growing file
| Dimension | Assessment |
|---|---|
| Complexity | None extra (status quo) |
| Cost | Growing per-session read cost, already visible at 46KB after 11 days |
| Scalability | Gets worse every session, with no natural end |
| Team familiarity | N/A (solo) |

**Pros:** Nothing to restructure now.
**Cons:** Directly contradicts `CLAUDE.md`'s own stated purpose (a routing/reference doc, not a journal); makes it progressively harder to find the current rule versus a superseded one, since corrections were already being layered on top of corrections in place (e.g. the pre-commit audit's own follow-up correction).

## Trade-off Analysis

The deciding factor is that `CLAUDE.md` has one very specific, very high-frequency reader contract (every fresh session, in full, before anything else) that a growing journal is structurally unsuited to serve. Splitting costs a small amount of bookkeeping discipline in exchange for keeping that contract cheap indefinitely.

## Consequences

- All narrative content from `CLAUDE.md`'s "Status as of..." sections onward, plus the incident/audit/verification writeups, moved verbatim into `status-log.md`.
- Workspace-level decisions previously described only in prose (two-repo split, homework-in-course-repo, human-in-loop git, Module 2 scoping) now have their own ADRs (0003–0006) with alternatives and trade-offs actually recorded, not just a stated outcome.
- Going forward: a genuine choice-with-alternatives gets a new ADR in `decisions/`; anything else worth recording (what happened, what got verified, what broke) goes in `status-log.md`; `CLAUDE.md` itself only changes when the workspace's actual layout or rules change.

## Action Items

- [x] `decisions/0003` through `0006` written, covering decisions previously only in `CLAUDE.md` prose
- [x] `status-log.md` created with the moved narrative
- [x] `CLAUDE.md` trimmed, with pointers to both other files
- [x] `sync.sh` updated to stop excluding `decisions/`
- [ ] Apply the same split to the CLIO Findings Explorer project's own `CLAUDE.md`, if it develops the same growth pattern (not done here — out of scope, that file is owned by the project subfolder's own governance)
