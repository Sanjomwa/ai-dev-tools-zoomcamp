# Chores App — Project Plan

*Module 1 homework, AI Dev Tools Zoomcamp 2026. Brainstormed in Cowork, 2026-09-07, following the homework's own prompt.*

## The idea

A tool for managing shared household chores — one household, several people, chores that rotate among them automatically.

## MVP feature set (4)

1. **Household + simple identity.** A household has multiple members. Each member picks their name from the household's roster to identify themselves when using the app — no password, no login. Adding a member to the household is basic supporting functionality this depends on, not a separately scored feature.

2. **Recurring chores with an expected cadence.** A chore is created once — a name and a cadence (e.g. "take out trash — daily," "vacuum — weekly") — and repeats indefinitely. There's no such thing as a one-off chore in this app; if it's not recurring, it doesn't belong here.

3. **Completion-driven rotation.** Each chore is currently "with" one household member. It stays with them — no matter how much time passes — until they mark it done. Only then does it advance to the next person. Rotation never advances on a fixed calendar schedule regardless of completion; a skipped chore is not silently reassigned to someone else.

   *Default rotation order:* the order members were added to the household. Not a scored decision, just needs a sane default — first-in-first-out is the simplest one that needs no extra input from the user.

4. **Overdue tracking, visual only.** Based on a chore's cadence, the app shows whether it's currently overdue (e.g. a "daily" chore not marked done within its expected window). This is a status you see when you check the app — a flag in the list, nothing more. No notifications, no reminders, no push/email — considered during the brainstorm and explicitly cut for time.

## Explicitly out of scope for the MVP

- Real authentication (usernames, passwords, sessions beyond picking a name)
- Active reminders or notifications of any kind
- One-off / non-recurring chores
- Gamification, points, streaks
- Reassigning a chore to someone other than the next person in rotation
- Multiple households (this app manages exactly one)

The exact mechanics of "overdue" (measured from what timestamp, what counts as the cadence window) are a Q3 stack/implementation decision, not a product-spec one — that belongs in `_docs/decisions.md`, not here.
