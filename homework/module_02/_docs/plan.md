# Leagueboard — Project Plan

*Module 2 homework, AI Dev Tools Zoomcamp 2026. Brainstormed in Cowork, 2026-09-10, following the module's article/lesson.md workflow.*

## The idea

A shared, no-login scoreboard for one sports league — its teams, its games, and standings computed from results. Anyone with the link can add teams, schedule games, and record scores.

## MVP feature set (4)

1. **Open access, single league.** No accounts, no passwords — anyone with the link can view and edit. Exactly one league per deployment; no multi-league or multi-tenant support. Updates are refresh-based (view again / reload to see someone else's change) — no live push (WebSocket/polling) in this version.

2. **Teams roster.** View the list of teams. Add a new team (name only — no logo, no roster of players). Supporting/unscored functionality the rest of the app depends on.

3. **Games and results.** Schedule a game between two existing teams — status starts as `scheduled`, no score yet. Record a score for a scheduled game, which marks it `completed`. View the list of games, both scheduled and completed, most recent first.

4. **Standings, computed.** A standings table ranked by points, derived from completed games only — win = 3, draw = 1, loss = 0 — showing played / won / drawn / lost / points per team. Not stored directly; recomputed from recorded results.

## Explicitly out of scope for the MVP

- Real authentication (usernames, passwords, sessions)
- Live/real-time sync (WebSocket or polling-based push) — refresh is enough for this version
- Multiple leagues per deployment
- Editing or deleting a recorded score once saved
- Game scheduling conflicts / validation beyond "both teams exist"
- Notifications or reminders of any kind
- Player-level rosters or stats — teams only

## Working name

**Leagueboard.** Other candidates considered: PitchTable, ScoreKeep, MatchTrack.

## Screens (wireframe)

A UI wireframe for the three core screens (Standings, Games, Teams) was mocked up in Cowork before frontend build, in place of Claude Design (the account this ran under didn't expose that artifact type) — see the published mockup link shared in that session.
