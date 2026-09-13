# ADR-0001: No authentication in v1 prototypes — pick-yourself identity instead

**Status:** Accepted
**Date:** 2026-09-10
**Deciders:** Sam

## Context

Every homework spec so far (Module 1's chores app, Module 2's Leagueboard) needs *some* notion of identity — who's marking a chore done, who's recording a score — but building real authentication (accounts, passwords, sessions) at prototype stage spends time on infrastructure the spec doesn't actually need yet, and neither module's grading criteria requires it.

## Decision

Default v1 specs to no real authentication. Where identity matters at all, use the cheapest model that satisfies the spec: picking a name from a known roster (chores app), or, where even that isn't needed, no identity concept at all (Leagueboard — anyone with the link can edit).

## Options Considered

### Option A: No auth / pick-yourself identity
| Dimension | Assessment |
|---|---|
| Complexity | Low — no session/password infra |
| Cost | None |
| Scalability | Fine for single-household / single-league scope |
| Team familiarity | N/A (solo) |

**Pros:** Ships fast, keeps the prototype focused on the actual product question, matches "learn the tool workflow" as the real goal of the homework.
**Cons:** Not remotely production-safe — anyone with the link/app has full write access.

### Option B: Real auth (accounts, sessions)
| Dimension | Assessment |
|---|---|
| Complexity | Medium-High |
| Cost | Low but nonzero (session storage, password handling) |
| Scalability | Needed for any real multi-tenant deployment |
| Team familiarity | N/A (solo) |

**Pros:** Actually deployable to strangers.
**Cons:** Pure overhead at prototype stage — nothing in either homework's grading criteria asks for it.

## Trade-off Analysis

The deciding factor is scope, not difficulty: these are single-tenant prototypes (one household, one league) built to learn a workflow, not to launch. Auth is real work with zero payoff until a spec actually needs isolation between untrusted parties.

## Consequences

- Every v1 spec in this course explicitly lists "no login" as a non-goal, not an oversight — worth stating out loud in each module's own spec so it reads as a decision, not a gap.
- Revisit (supersede) this ADR the moment a module's spec genuinely requires isolating one user's data from another's.

## Action Items

- [x] Module 1: chores app uses pick-a-name-from-roster identity
- [x] Module 2: Leagueboard uses no identity concept at all (fully open)
- [ ] Reassess if/when a later module's spec needs real multi-tenancy
