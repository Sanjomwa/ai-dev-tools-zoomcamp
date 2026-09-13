# ADR-0005: Human-in-the-loop git governance extends to the course-materials repo

**Status:** Accepted
**Date:** 2026-09-07
**Deciders:** Sam

## Context

The CLIO Findings Explorer project already runs on a governance pattern where Cowork plans, Claude Code executes file/code changes, and Sam alone runs `git commit`/`git push` — enforced in that repo with hooks like `block-autonomous-git`. Once the course-materials repo became a real git repo (2026-09-07, `github.com/Sanjomwa/ai-dev-tools-zoomcamp`), the open question was whether that same discipline should apply there too, or whether ungraded coursework could reasonably run looser (Claude Code committing and pushing on its own).

## Decision

The no-autonomous-git rule carries over to the course-materials repo in full. Claude Code stages and describes changes; Sam alone commits and pushes. First recorded in-repo as decision 5 in `homework/module_01/_docs/decisions.md`; this ADR is the workspace-level record of the same decision, since it governs the whole repo, not just Module 1.

## Options Considered

### Option A: Same human-in-the-loop rule as CLIO
| Dimension | Assessment |
|---|---|
| Complexity | None extra — same pattern already in use |
| Cost | Slightly slower iteration (a human step every commit) |
| Scalability | Proven already on the CLIO project |
| Team familiarity | N/A (solo), but consistent habit across both repos |

**Pros:** One mental model across every repo Sam works in with Cowork + Claude Code, instead of remembering which repo is "the strict one." Catches a self-review gap even on ungraded work — this course's own retrospective (Module 1) explicitly names "no agent grades its own work" as a rule learned the hard way.
**Cons:** Adds a manual step to work that isn't graded on process, only on the final submission.

### Option B: Looser rule for course work (Claude Code can commit/push autonomously)
| Dimension | Assessment |
|---|---|
| Complexity | Lower friction per commit |
| Cost | None directly, but see Cons |
| Scalability | Two different governance models to remember and not confuse |
| Team familiarity | N/A (solo) |

**Pros:** Faster iteration on work that isn't itself being graded for process rigor.
**Cons:** A public, graded repo is exactly the wrong place to relax review — this workspace's own history already includes one incident where an automated `sync.sh pull` deleted 47 tracked files (see status-log.md, 2026-09-10); looser git discipline compounds that kind of risk rather than mitigating it.

## Trade-off Analysis

The deciding factor: this repo is public and graded, and the workspace has already had one real close call from insufficiently-supervised automation (the `sync.sh` deletion incident). A slightly slower commit cadence is a small cost against a repeat of that class of failure landing directly in git history on a public repo.

## Consequences

- Every commit message reaching this repo going forward is drafted by Cowork or Claude Code and reviewed/executed by Sam — this is now the standing convention for both course-materials and CLIO repos.
- Independent post-hoc verification (reading the actual pushed diff from GitHub, not trusting a session's self-report) remains the compensating control for anything Claude Code builds between commits.

## Action Items

- [x] Recorded as decision 5 in `homework/module_01/_docs/decisions.md`
- [x] Applied consistently through Module 2's backend build, docs, and sha1 fix (all drafted, reviewed, then committed by Sam — see status-log.md)
