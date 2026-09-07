# Chores App — Backlog

*Module 1 homework, AI Dev Tools Zoomcamp 2026. See `_docs/plan.md` for the product spec and `_docs/decisions.md` for the stack. Django project and `chores` app are already bootstrapped; migrations already run — no setup tasks here.*

## MVP

1. **Household & Member models.** `Household(name)`, `Member(household FK, name, order)` — `order` is the rotation position, set by creation order. Migration + Django admin registration (roster management is unscored supporting functionality — admin is enough, no custom UI needed).
2. **Chore model.** `Chore(household FK, name, cadence, current_holder FK to Member, last_completed_at nullable)`. Migration + admin registration.
3. **Identity-pick view.** Page listing the household's members by name; clicking one stores `member_id` in the session and redirects to the chore list.
4. **Session-identity guard.** Any view that needs "who am I" redirects to the identity-pick page if `member_id` isn't in the session yet.
5. **Chore list view.** Template showing every chore, its cadence, and its current holder.
6. **Mark-done action.** POST endpoint: sets `last_completed_at` to now and advances `current_holder` to the next member in `order` (wrapping to the first). Requires a picked session identity.
7. **Overdue flag on chore list.** Compute overdue from `cadence` + `last_completed_at` (or chore creation time if never completed); show a visual flag per chore in the list. No notifications — display only.

## Post-MVP

8. **Restrict mark-done to the current holder.** Reject (or hide the control) if the session identity isn't the chore's current holder — MVP only requires *some* picked identity, not a matching one.
9. **Household/member management UI.** Replace admin-only roster editing with in-app pages.
10. **Chore management UI.** Replace admin-only chore creation/editing with in-app pages.
11. **Switch-identity link.** Clear the session and return to the identity-pick page without needing to clear cookies manually.
12. **Basic styling pass.** The MVP views ship unstyled; pass a stylesheet over them once the flows are proven.
