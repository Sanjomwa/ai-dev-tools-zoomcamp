# ADR-0008: Curated adoption of the firstmate/no-mistakes/quota-axi/lavish-axi/treehouse workflow

**Status:** Accepted (approved as drafted, no amendments)
**Date:** 2026-09-13
**Deciders:** Sam
**Applies to:** This workspace as a whole — both the course-materials repo (homework, `01-ai-native-workflow/`, etc.) and the CLIO Findings Explorer capstone project. A workspace-level decision, hence filed at the workspace root rather than inside the project subfolder.

## Context

Sam watched a demo by Kun Chen (ex-Meta/Microsoft/Atlassian) of his personal agentic workflow, built on five of his own open-source tools (`github.com/kunchenguid`): `firstmate` (an orchestrator "agent distro" that dispatches bounded tasks to autonomous "crewmate" agents, each in an isolated git worktree, reporting back PRs/merges/investigation reports), `no-mistakes` (a local git push-time validation gate: review→test→docs→lint in a disposable worktree, auto-fix mechanical issues, escalate real judgment calls, open a clean PR once green), `quota-axi` (a data-only CLI reporting quota/usage windows across many AI-provider CLIs, feeding routing decisions), `lavish-axi` / Lavish Editor (a local browser tool for annotating a single agent-generated HTML artifact — element-level feedback, Mermaid diagram editing — sent back to the agent), and `treehouse` (a reusable git-worktree pool, avoiding repeated clone/dependency-install cost per agent session).

All five repos were read directly (not taken from the video's framing) to confirm current, real behavior — see the verification notes below. Two corrections to the original description: `no-mistakes` never auto-merges anything itself, it stops at opening a PR (the auto-merge behavior is firstmate's own separate `+yolo` flag, layered on top); and `lavish-axi` is single-artifact annotation, not a side-by-side multi-variant comparison board.

That workflow's design assumes: multiple simultaneous paid model subscriptions with independently renewing quota (what `quota-axi` routes across), cheap parallelism, and often a public community supplying external work (what firstmate's Relay answers). Sam asked whether **this project** actually shares those conditions before adopting anything, since if it doesn't, several patterns are actively wrong to copy, not just unnecessary overhead.

**Answers to the diagnostic questions, from Sam directly (2026-09-13):**
- **Target:** both the course homework and the CLIO Findings Explorer capstone — this whole workspace, not one project in isolation.
- **External funder/client/compliance oversight of scale or cost:** none. Self-directed.
- **Team:** solo.
- **Git autonomy policy:** unchanged — same as this workspace's existing rule (`decisions/0005-human-in-loop-git-course-repo.md`): Claude Code stages and describes, Sam alone commits and pushes, always. Confirmed as the answer even when explicitly offered a more permissive middle option, so this is treated as a values position, not a convenience default open to reconsideration as validation tooling improves.

**Two more facts drawn from Sam's own tooling profile, not re-asked because the evidence is already clear:** Sam's AI subscription is Claude Pro — a single vendor, a single renewing (not depleting/grant) quota pool, not the multiple-simultaneous-subscription situation `quota-axi` is built to route across. And this workspace's artifacts are markdown docs, ADRs, and code judged against a written spec or an OpenAPI contract (Leagueboard, CLIO Findings Explorer) — correctness-judged, not open-ended visual/design exploration with genuine throwaway variants to compare by eye.

## Decision

Curated, per-pattern adoption — not wholesale copy, not blanket rejection. Each pattern is sorted below with reasoning tied to the facts above, not generic pros/cons.

### ADOPT — transfers cleanly, costs nothing extra, no new tooling

| Pattern | Why it transfers as-is |
|---|---|
| Single point of contact | Already the structure: Sam talks to Cowork; Cowork plans, drafts Claude Code prompts, and reports outcomes. No change needed. |
| Bounded dispatch to a sub-agent for investigation/verification, reporting back a plain result | This is firstmate's "scout" task shape, and Cowork already has it natively (the `Agent` tool, including an Opus-model second-opinion pass — used minutes ago for the `sync.sh` safety review). Formalize as a standing habit: any judgment-heavy or verification-heavy step gets dispatched to an independently-scoped sub-agent rather than self-reviewed, matching this workspace's existing "no agent grades its own work" rule. Zero marginal cost — the tool is already here. |
| An on-demand "what's shipped / in progress / waiting on your decision" digest | Mirrors firstmate's `/bearings` and `/ahoy`. The raw material already exists (`status-log.md`, `decisions/`, each `homework/module_NN/`'s own `AGENTS.md`/README). Adopt the shape by producing this digest on request, read live from those files — no new tool, no new file format. |
| A written validation checklist before handing work back to Sam | Already the de facto practice (the Module 2 pre-commit audit, the sync-safety review, independent GitHub verification after every push) — worth naming explicitly as a standing checklist analogous to `no-mistakes`' review→test→docs→lint gate, run by a sub-agent or manually, never by the agent that built the thing being checked. |
| A disposable, isolated environment per task | Structurally already true: Claude Code works in its own WSL clone, separate from Cowork's OneDrive mirror; Cowork's own `Agent` tool supports an `isolation: "worktree"` mode for cloud-side sub-tasks. `treehouse`'s specific pooling optimization isn't needed to get this property (see REJECT below) — it's already had for free. |

### ADOPT THE SHAPE, REJECT THE MECHANISM

| Pattern | Shape kept | Mechanism rejected, and why |
|---|---|---|
| `no-mistakes`'s validation gate | Auto-fix mechanical issues, escalate only real judgment calls, keep a green-before-it-leaves-the-worktree bar | Not installing the actual tool. It ends by pushing to the real remote and opening a PR itself — a semi-autonomous git action that goes further than "Sam alone commits and pushes," even though it never merges. It's also a Go binary + local git proxy to trust and maintain for a benefit (mechanical auto-fix) that's small at this project's current scale. **Reopen if:** PR/commit volume grows enough that manually opening PRs becomes a real bottleneck, or Sam decides he wants a tool to hold git-push authority. |
| firstmate's trust-tier concept (`no-mistakes` / `direct-PR` / `local-only`, optional `+yolo`) | The idea of a named, explicit, per-project autonomy level is sound in general | Not adopting any tier above "local-only, human commits/pushes" here — this project's tier is fixed at the strictest setting by policy, not by current validation confidence. **Reopen:** never, for this project, unless Sam changes the underlying policy himself — this is stated as a values position, not a circumstance. |
| firstmate's dispatch-and-report loop (talk to one agent, get back a finished result without watching the mechanics) | Already adopted, see ADOPT above | Not installing firstmate itself, and not adopting its multi-crewmate fleet (parallel workers in separate tmux windows/worktrees dispatched concurrently). Solo work with a naturally sequential shape (one module's homework at a time, one CLIO Findings Explorer milestone at a time) has no coordination problem for a fleet to solve, and Cowork's own `Agent` tool already gives the single-dispatch property without a second orchestration layer on top of the one already in use. **Reopen if:** this workspace's work genuinely becomes parallel (e.g., multiple independent workstreams needed at once on CLIO Findings Explorer). |

### REJECT — stated with the specific reason and the specific reopening condition

| Pattern | Why not now | Reopen when |
|---|---|---|
| `quota-axi` (multi-vendor quota-aware routing) | Single vendor (Claude Pro), single renewing pool — there is nothing to route between. Its entire value is choosing among multiple simultaneous paid subscriptions with independent reset windows. | Sam starts running multiple paid AI subscriptions (e.g. adds Codex, Cursor, Grok) for this work. |
| `lavish-axi` / Lavish Editor (interactive HTML annotation) | This workspace's artifacts are judged by correctness against a spec or contract, not by visual/design judgment calls needing element-level annotation. Even the one real UI (Leagueboard's frontend) is spec-driven from `openapi.yaml`, not an open-ended visual exploration. | A module or CLIO Findings Explorer enters a genuine visual-design exploration phase with real competing variants to look at. |
| firstmate's Relay (public Discord/X mention handling) | No public community or external inbound stream exists for course homework or CLIO Findings Explorer at this stage — nothing for a relay to act on. | CLIO Findings Explorer (or its future users) stands up a real public Discord/X presence generating actual inbound requests. |
| firstmate's secondmates (persistent second mates, multi-machine fleets) | Solo work, single machine (WSL + Cowork) — no cross-person or cross-machine coordination problem to solve. | This becomes a team project, or work needs to run across multiple physical machines that must stay coordinated. |
| `treehouse`'s worktree-pool reuse | Its whole point is amortizing the clone/dependency-install cost of running *many* parallel, short-lived agent sessions against one repo — a cost that only exists once genuinely parallel crewmates exist, which this project doesn't have (see the fleet-dispatch rejection above). | Reopen together with the fleet-dispatch item, if parallel dispatch ever becomes real. |
| firstmate's multi-harness dispatch profiles (routing tasks across Claude/Grok/Pi/Codex by which fits best) | One harness in active use here (Claude Code, via Cowork) — no multi-harness fleet to route across. | Multiple different AI CLIs are actually in play for this project. |

## Options Considered

### Option A: Wholesale adoption (install firstmate + treehouse + no-mistakes + quota-axi + lavish-axi as demoed)
**Pros:** Matches a working reference implementation exactly; nothing to design.
**Cons:** Assumes conditions this project doesn't have (multi-vendor quota to route, parallel crew coordination to solve, a community to relay). Its own trust-tier defaults and PR/merge automation go further than this workspace's explicit, values-based human-in-the-loop git rule. Real setup and trust cost (a Go binary with local git-proxy privileges, a multi-tool install) for benefits mostly aimed at a different economic situation.

### Option B: Curated per-pattern adoption (chosen)
**Pros:** Keeps the genuinely transferable ideas (bounded dispatch, a validation checklist, an on-demand digest) at zero marginal cost, since Cowork's own tools already provide them. Explicitly declines the parts that solve problems this project doesn't have, each with a stated reopening condition so the decision doesn't have to be relitigated from scratch if circumstances change. Respects the fixed git-autonomy policy rather than treating it as negotiable.
**Cons:** More design work up front than either wholesale adoption or flat rejection; requires actually naming and using the "shape" patterns (the digest, the checklist) rather than getting them for free from an installed tool.

### Option C: Reject everything, change nothing
**Pros:** Zero effort.
**Cons:** Throws away genuinely free wins already sitting in Cowork's existing tool set (bounded sub-agent dispatch, an on-demand digest) that cost nothing to start using deliberately.

## Trade-off Analysis

The deciding factor is that this project's actual constraints — solo, single-vendor renewing quota, no external funder, a fixed (not negotiable) human-in-the-loop git policy, correctness-judged artifacts, no public community — overlap with only part of what the source workflow was built for. Copying it wholesale would import automation (auto-PR, auto-merge tiers, multi-vendor routing, a relay bot) built for a different economic situation; rejecting all of it would also throw away the parts that transfer for free through tools already in hand. Curated adoption captures the free wins, declines the mismatched parts with reasons anchored to this project's actual facts rather than generic caution, and states plainly which rejections are circumstantial (reopen if X) versus which are fixed policy (never, unless Sam changes the policy itself).

## Consequences

If accepted:
- No new tool gets installed. Nothing about how Claude Code, `sync.sh`, or git access works changes.
- Bounded sub-agent dispatch for verification/investigation becomes a named, standing habit rather than an ad hoc choice — used already (the Opus `sync.sh` safety review), continued deliberately going forward.
- An on-demand "shipped / in progress / awaiting your decision" digest becomes something Sam can ask for directly, assembled live from `status-log.md`, `decisions/`, and each module's own docs.
- The validation-before-handoff checklist gets named explicitly rather than implied by practice.
- Six specific patterns (quota-axi, lavish-axi, Relay, secondmates, treehouse's pooling, multi-harness dispatch) are declined with stated reopening conditions, not permanently foreclosed — a future session should check this ADR before re-proposing any of them, and reopen only if the stated condition has actually changed.
- The `+yolo`/autonomous-merge pattern is declined as fixed policy, not a circumstance — a future session should not re-propose it based on improved validation confidence alone; only Sam changing the underlying policy reopens it.

## Action Items

- [x] Sam reviews, amends, or rejects this proposal — approved as drafted, no amendments (2026-09-13)
- [x] Mark this ADR's Status as `Accepted` — `CLAUDE.md` itself left untouched, since nothing about `sync.sh`, git policy, or tooling changes (confirmed against the "if it changes anything CLAUDE.md currently states" test above: it doesn't)
- [ ] Use the bounded-dispatch and on-demand-digest habits deliberately going forward — no separate implementation step, since both ride on tools already in place; this is an ongoing practice, not a one-time task
- [ ] Revisit the REJECT table's reopening conditions if this workspace's circumstances change (team forms, multiple AI subscriptions get used, a public community appears, visual-design exploration work begins)
