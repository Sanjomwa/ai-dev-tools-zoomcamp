# ADR-0002: Refresh-based updates over WebSocket/live sync (Module 2)

**Status:** Accepted
**Date:** 2026-09-10
**Deciders:** Sam

## Context

Leagueboard is a shared, multi-editor app (anyone with the link can add teams, schedule games, record scores). Open question: does a change made by one visitor need to appear live in another visitor's open tab, or is "reload to see it" good enough for v1?

The course's own Module 2 workshop is direct evidence here: the instructor's live demo (a different app — a multi-user AI-system-design interview canvas) added WebSocket-based real-time sync and hit a real, time-consuming bug — updates flowed from interviewer to interviewee but not the reverse — that visibly ate a meaningful chunk of the session before being fixed by trial and error.

## Decision

Leagueboard uses refresh-based updates. No WebSocket, no polling loop. A visitor sees another visitor's change on their next reload, not live.

## Options Considered

### Option A: Refresh-based (reload to see changes)
| Dimension | Assessment |
|---|---|
| Complexity | Low — no persistent connections, no sync protocol |
| Cost | None |
| Scalability | Trivial — every request is stateless |
| Team familiarity | N/A (solo) |

**Pros:** Nothing to get wrong; matches a scoreboard's actual usage pattern (checked periodically, not watched live like a chat app).
**Cons:** Not "live" — a visitor mid-session won't see someone else's update until they reload.

### Option B: WebSocket / live push
| Dimension | Assessment |
|---|---|
| Complexity | Medium-High — connection lifecycle, fan-out, directionality bugs |
| Cost | Low but nonzero (persistent connections) |
| Scalability | Needs more thought (connection limits, reconnect logic) |
| Team familiarity | N/A (solo) |

**Pros:** Feels responsive; genuinely necessary for collaborative/live use cases (the interview-canvas example is one — everyone needs to see the same canvas move in real time).
**Cons:** Directly observed to be a real source of hard-to-debug asymmetric-sync bugs in this exact course's own live demo; that complexity buys nothing for a scoreboard, where results are recorded after a game ends, not watched live.

## Trade-off Analysis

The deciding factor is what the product actually needs: a scoreboard's value proposition doesn't depend on liveness the way a live drawing canvas or an interview tool does. Live sync is the right call when *staleness itself breaks the product* (two people drawing on the same canvas); it's pure risk when staleness is merely mildly inconvenient (a score updates a few minutes before someone else refreshes).

## Consequences

- Leagueboard's spec (`02-development/plan.md`) lists this as an explicit non-goal, not a gap.
- If a future module's spec genuinely requires liveness (the interview-canvas pattern, a chat feature, anything collaborative-by-nature), don't default to this ADR — evaluate fresh, and budget real debugging time for the sync-direction class of bug this ADR's Context section documents.

## Action Items

- [x] Leagueboard frontend prototype built refresh-based (see `02-development/frontend`)
- [ ] Carry this criterion forward explicitly when scoping any future module with multi-user real-time requirements
