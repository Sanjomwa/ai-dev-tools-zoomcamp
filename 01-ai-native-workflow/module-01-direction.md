# Module 1 — Opus pass: direction for the workshop and homework

*AI Dev Tools Zoomcamp, 2026 cohort. Written for Sam, 2026-09-07. Verified against the live repo in-browser same day — see update note below.*

---

## Update, 2026-09-07 (same day, after live verification) — two things that need attention before anything else in this document

**1. Module 1 homework is due today.** Confirmed directly from `cohorts/2026/README.md`: *"Module 1: AI-Native Developer Workflow — due 2026-09-07."* That's today's date. This supersedes every sequencing suggestion below that assumes unhurried time (e.g. "watch the workshop first" in §1) — if the deadline is hard, submit something correct over something thorough. Check the actual submission mechanics (late-submission policy, whether the leaderboard/certificate track cares) at https://courses.datatalks.club/ai-dev-tools-2026/homework/hw1 before deciding how much of §1-§4 below you have time for.

**2. The course's real 2026 module structure does not match what the CLIO Findings Explorer plan assumes, and the mismatch is bigger than the "module count" flag in the original §5 gotcha below suggested.** Verified live from the repo root and `cohorts/2026/`:

| # | Real 2026 module (verified 2026-09-07) | What CLIO's plan (§4) assumed for that slot |
|---|---|---|
| 1 | AI-Native Developer Workflow | Module 1 — AI tools overview ✓ close enough |
| 2 | Build and Ship an AI-Assisted Full-Stack App | Module 2 — end-to-end (Snake) — roughly matches in spirit |
| 3 | Test, Containerize, and Deploy an AI-Assisted App | Module 3 — **MCP** ✗ no match. Testing/containers/deploy, not MCP |
| 4 | DevOps and Observability for AI-Built Apps | Module 4 — **build a custom coding agent** ✗ no match. This is Module 5's content, not Module 4's |
| 5 | **Coding Agent Capabilities: MCP, Skills, Plugins, and Custom Agents** — MCP *and* custom agents *and* subagents, combined into one module | Module 5 — CI/CD & DevOps ✗ that's real Module 4's content |
| — | *(no 2026 module visible for this)* | Module 6 — n8n / low-code — **no corresponding 2026 module exists in the repo as of this check** |

Concretely: the plan's Week 3 exit criterion ("MCP server built and used") and Week 4 exit criterion ("evidence-reviewer subagent built") both actually belong to the *same* real module (Module 5), and that module comes appreciably later in the sequence than either assumed week. The plan's Week 5 (CI/CD/DevOps content) is real Module 4, one slot earlier than planned. And there's currently no real Module 6 to hang the n8n freshness-check workflow on — that piece of the plan may need to become unpaced bonus work rather than a course-paced milestone, unless a Module 6 appears later (the repo's own banner says 2026 materials are "currently being finalized... may change before the cohort starts").

**This document does not attempt to fix the CLIO plan's §4 milestone table — that's a separate, deliberate edit Sam should make (or ask for) once the real module list stops moving.** Treat the version notice above as the reason to re-verify each module's real content close to when it's about to start, rather than trusting the original CLIO plan's guesses at this point. Everything below this notice (the five calls, the execution plan, the process guidance) is about Module 1 specifically and is unaffected by the mismatch — it's the *later* weeks of the CLIO plan that need revisiting, not this document.

**3. §2's repo-structure recommendation below is superseded.** Sam gave explicit direction, 2026-09-07: course-following work and homework live in the **same** repo — `~/Projects/ai-dev-tools-zoomcamp`, the existing course WSL repo — not a separate third repo as originally recommended below. "Same way I did for the llm zoomcamp course." Verified live against his own precedent, [`Sanjomwa/LLM-ZOOMCAMP-2026`](https://github.com/Sanjomwa/LLM-ZOOMCAMP-2026). See the correction note at the top of §2 for the full replacement structure and reasoning — the original §2 is left below it for the reasoning trail, not as current direction.

---

## Submission checklist and time budget — added after a second review pass, 2026-09-07 ~10:00 UTC (~12h to deadline)

**This section didn't exist in the first version of this document — it was the biggest gap a critical re-review found.** Read this before Q2.

**What's actually graded, verified directly from `homework.yaml` and the course README:** a repo URL, `time_spent_lectures`, `time_spent_homework`, `faq_contribution` (yes/no), up to 7 learning-in-public links (`learning_in_public_cap: 7`), and one free-form `reflection` question worth **0 points**. There are no graded entries for the Q1-Q6 self-check questions in the machine-readable form — Appendix B's MCQs appear to be self-check only (one caveat: the actual web form at courses.datatalks.club wasn't opened to confirm — check it once, it's 60 seconds, before assuming). **Homework does not affect certificate eligibility or peer review** — confirmed from the root README: *"Homework helps you stay on track, but the certificate is based on the final project and peer review requirements."* Real reason to timebox hard today rather than over-invest in homework polish.

**Minimum viable submission**, derived from `homework.md`: a public repo containing `.gitignore`, `README.md`, `_docs/plan.md`, `backlog.md`, a Django project with an app registered, a server that runs, and at least one test. No grooming, no role files, no GitHub issues, no QA session required to satisfy the homework's own instructions — everything past that is rehearsal value for CLIO, deliberately layered on top (see §1). Know what you're protecting when you start cutting.

**Checkpoint schedule (UTC), with an explicit cut rule at each step:**

| By | State | If behind, cut |
|---|---|---|
| 11:00 | Brainstorm done, `plan.md` saved | — |
| 12:30 | Repo set up, plan.md/.gitignore/README committed+pushed | — |
| 14:00 | Django bootstrapped, rocket page confirmed | Skip the stack conversation (§3a) — take this doc's recommended stack directly |
| 15:30 | `AGENTS.md`, `CLAUDE.md`, `process.md`, 3 role files, task-template written | Trim role files to ~10 lines each instead of retroloop's 27-50 |
| 17:00 | `backlog.md` written + reviewed, issues created | Cut the `/goal` grooming loop — groom by hand. Cut GitHub issues if needed; `backlog.md` alone satisfies the homework |
| 19:00 | Task #1 implemented via PM→engineer→QA (separate sessions) | Cut the PM session; keep engineer + a separate QA session — QA-in-its-own-session is the one rule not to cut, see §4 |
| 20:30 | Tests written and passing | Cut to one happy-path test |
| 21:00 | Learning-in-public post(s), FAQ contribution, reflection drafted | — |
| **21:15** | **Submit** — ~45min buffer before the 21:59 deadline | — |

**Hard rule: at 18:00 UTC, whatever hasn't started gets cut, not compressed.** Half-finishing three things is worse than finishing one cleanly.

**Schedule the learning-in-public post deliberately today, not as an afterthought** — `learning_in_public_cap: 7` is the single largest points lever in the whole submission (the reflection question is worth 0), and your own posting convention (root `CLAUDE.md`) takes real drafting time. Put it in the 21:00 slot, not squeezed in at 21:50.

**One free FAQ candidate already in hand:** this morning's GitHub password-auth failure (`git push` rejected, fixed via `gh auth login` OAuth instead of a PAT) is a real, common gotcha other students will hit — worth writing up once the homework itself is done, per the sequencing rule in root `CLAUDE.md`.

---

## TL;DR — the five calls

1. **Don't rebuild retroloop.** Watch the workshop, then *read* retroloop as a reference artifact for its file conventions. The homework is your hands-on rep. Rebuilding it would be the same exercise twice.
2. ~~The homework repo gets its own top-level WSL folder and its own GitHub repo, outside both existing mirrors, with no third `sync.sh`.~~ **Superseded 2026-09-07 — see the update note above and the correction at the top of §2.** The homework lives *inside* the existing course repo (`~/Projects/ai-dev-tools-zoomcamp`, under `homework/module_01/`), synced by the existing root `sync.sh` — matching Sam's own LLM Zoomcamp precedent. No separate repo, no third sync script.
3. **Follow the homework's own paths literally** — `_docs/plan.md`, `backlog.md` — not the workshop's `docs/`. (Convenient: retroloop actually uses `_docs/` too. Verified below.)
4. **Scale the graph down: build all three role files, run the full PM→engineer→QA loop on exactly one issue, and use `/goal` only for grooming.** Full orchestration over the whole backlog is disproportionate at 4-5x tokens for a homework nobody grades past task #1.
5. **The artifacts are the point, not the chores app.** `AGENTS.md`, `_docs/process.md`, `_docs/team/pm.md` and a working QA-verdict contract are what transfer to CLIO Findings Explorer. Write them deliberately; the Django app is scaffolding to hang them on.

---

## 1. How the workshop and the homework relate

They are the same process applied to two different deliberately-vague one-liners:

| | Workshop | Homework |
|---|---|---|
| Vague idea | "a tool for weekly feedback for projects" | "a tool for managing shared household chores" |
| Bad path (shown) | `weekly-feedback/` — one-shot prompt, agent invents a git-log CLI | *(you don't do this)* |
| Good path | `retroloop` — brainstorm → plan → stack → backlog → issues → context → PM/eng/QA | Your repo, questions 2-6 |
| Stack | Django | Django (fixed by the homework) |

Same framework, same process, same six steps. The homework text even reuses the workshop's framing verbatim in spirit: *"We will work on a project with a very vague idea... most of you will finish with different projects."* The divergence between students' outputs **is the lesson** — it's the empirical proof that the spec, not the prompt, is what determines what gets built.

### Do you need to build retroloop yourself?

**No. Explicitly no.** Watching is sufficient; reading the repo is where the actual value is.

Reasoning:

- The transferable content is *process and file conventions*, and both are identical between the two projects. Building retroloop would give you a second Django CRUD app and zero new process reps.
- Both are Django. There isn't even a framework delta to learn from doing both.
- Your token budget matters here (see §4). The full process costs 4-5x per issue. Spending that twice on the same lesson is the wrong trade when CLIO is the thing that actually needs the budget.

**What to do instead**, in this order, before you touch the homework:

1. **Watch the workshop** — [Workshop 1: AI-Native Developer Workflow](https://www.youtube.com/watch?v=VUJxJGpaDEs). Pause and transcribe at exactly three moments: when he writes `AGENTS.md`, when he writes the PM persona, and when he sets the `/goal`. Those three are the CLIO-relevant payload; everything else you already know conceptually from the article.
2. **Skim `weekly-feedback/`** in the course repo for five minutes. It's the negative control. Seeing concretely how far off-target an unspecified agent lands is worth more than another paragraph of theory about why specs matter.
3. **Read `retroloop`'s convention files** (github.com/alexeygrigorev/retroloop) — specifically `AGENTS.md`, `CLAUDE.md`, `_docs/process.md`, `_docs/decisions.md`, `_docs/team/pm.md`. See Appendix A: I checked these and the mature repo diverges from the transcript in ways worth knowing before you copy the transcript's structure.

Then do the homework as your single hands-on rep.

### Why this matters more for you than for most students

Your CLIO Findings Explorer plan already commits to this exact machinery — an `AGENTS.md` context file, a PM/engineer/QA-style split, an `evidence-reviewer` subagent, hooks, and a milestone sequence synced to these modules. That's a plan written *before* you'd practiced any of it. This homework is the cheapest possible place to find out which parts of that plan survive contact with reality — on a throwaway chores app where a bad `AGENTS.md` costs you an hour, not on a repo carrying real Kenya civil-liberties findings where it costs you rework and trust.

Two specific things to carry back:

- **`evidence-reviewer` is a domain-specialized QA node.** Writing a generic `qa.md` here — with a strict binary pass/fail contract and no authority to fix what it finds — is a direct rehearsal of its parent pattern. If you can't make the generic one return clean binary verdicts on "does this chore rotate to the next housemate," you won't get clean verdicts on evidence provenance either.
- **The instructor's "no agent grades its own work" is the single load-bearing rule.** If everything else in your CLIO plan gets cut for time, keep that one. It's also the cheapest to implement: it costs one extra session, not a whole orchestrator.

---

## 2. Repo and folder structure — the call

> **Correction, 2026-09-07 — superseded by Sam's explicit direction, verified against his own GitHub precedent.** The recommendation immediately below (a third, unmirrored WSL repo, e.g. `choreboard`) does not stand. Sam's instruction: course-following work and homework live in the **same repo** as each other — `~/Projects/ai-dev-tools-zoomcamp`, the existing course WSL repo already wired to this workspace's root `sync.sh` — "same way I did for the llm zoomcamp course." Verified live in-browser against his own precedent repo, [`Sanjomwa/LLM-ZOOMCAMP-2026`](https://github.com/Sanjomwa/LLM-ZOOMCAMP-2026):
>
> ```
> LLM-ZOOMCAMP-2026/            (one repo, one GitHub remote)
> ├── 01-agentic_rag/           # course-following work, per module — notebooks/scripts, ungraded
> ├── 02-vector-search/
> ├── 03-orchestration/
> ├── 04-evaluation/
> ├── 05-monitoring/
> ├── dlt_workshop/
> └── homework/                 # the actual graded deliverable, per module
>     ├── module_01/
>     ├── module_02/
>     ├── module_03/
>     ├── module_04/
>     └── module_05/
> ```
>
> Mapped onto this course:
>
> ```
> ~/Projects/ai-dev-tools-zoomcamp/     (existing course WSL repo — git init happens here)
> ├── 01-ai-native-workflow/            # course-following notes/exploration — ungraded
> ├── 02-development/
> ├── 03-deployment/
> ├── 04-devops/
> ├── 05-agent-capabilities/
> └── homework/
>     └── module_01/                   # the Module 1 homework — this is what homework_url points at
> ```
>
> **No third repo. No third `sync.sh`.** The existing root `sync.sh` (Cowork workspace root ↔ `~/Projects/ai-dev-tools-zoomcamp`) already targets exactly this repo; its exclude list has been extended (`*.sqlite3`, `db.sqlite3`, `staticfiles/`, `media/`, `.coverage`) for the Django app's build/runtime churn, alongside the `.venv/`/`__pycache__/`/etc. excludes already there — an extension to the existing mechanism, not a new one.
>
> The four reasons below still name real effects. Here's how the single-repo structure actually answers each, rather than avoiding them:
>
> - **"The submission is a repo link."** Still true, still satisfied: `homework_url` on the submission form points at `.../ai-dev-tools-zoomcamp/tree/main/homework/module_01`, not the repo root. GitHub deep-links to a folder correctly, and this is exactly what Sam's own LLM Zoomcamp submissions already did — it's a working, already-graded pattern, not a guess.
> - **`CLAUDE.md` inheritance.** Still a real effect — Claude Code launched inside `homework/module_01/` will walk up and inherit the root `CLAUDE.md`. The mitigation is keeping that root file a thin pointer (the retroloop `AGENTS.md`-pointer convention this workspace already plans to use — see the root `CLAUDE.md`'s "This folder is not part of CLIO" note in the project's own file for the same pattern applied elsewhere) rather than avoiding the nesting altogether. Sam's own precedent repo already lives with this tradeoff day to day; it isn't hypothetical risk.
> - **Nested `.git` inside an rsync `--delete` mirror.** Doesn't arise — there is exactly one `.git`, at the course repo's root, already excluded from `sync.sh` in both directions (see "Sync mechanics" in the root `CLAUDE.md`). No nested repo is created by this structure.
> - **Working-tree churn.** Real, and solved by the exclude-list extension above rather than by segregating into an unmirrored repo — same fix already used for `.venv/`/`__pycache__/`/`node_modules/` elsewhere in this same script.
>
> The "Repo naming" and "One caveat" subsections below were written for the now-superseded third-repo plan (they assume a fresh top-level repo needing its own product name and a possible later split into `~/Projects/zoomcamp-homework/`) and don't apply as written under the single-repo structure — left in place for the reasoning trail, not as current direction. If a later module's homework genuinely warrants its own separate repo for a real reason (not just habit), that's a fresh decision to make explicitly then, not a default to fall back into.

**Recommendation (superseded — see correction above): a third top-level WSL repo, outside both existing mirrors, with its own GitHub remote and *no* third `sync.sh`.**

```
WSL
├── ~/Projects/ai-dev-tools-zoomcamp/          # course materials    ← mirrored (existing sync.sh)
├── ~/Projects/CLIO-Findings-Explorer-course-project/   # final project ← mirrored (existing sync.sh)
└── ~/Projects/choreboard/                     # HOMEWORK — NOT mirrored, GitHub-backed only

Cowork (connected folder: ai-dev-tools-zoomcamp)
├── (root)                                     # course materials + root CLAUDE.md
├── CLIO-Findings-Explorer-course-project/     # excluded from root sync.sh
└── module-01-homework/                        # brainstorm notes ONLY — rides the existing course mirror
```

**No change to either existing `sync.sh`. No new exclude entry. No third sync script.**

### Why not nest it in the course repo

Four independent reasons, any one of which is sufficient:

1. **The submission is a repo link.** A reviewer opens the URL and expects `README.md`, `.gitignore`, `_docs/plan.md`, `manage.py`, `backlog.md` at the root. Nesting means you either submit the course repo (wrong — it contains everything else) or a submodule (fragile; reviewers frequently see an empty pointer). Neither is worth explaining in a submission.
2. **`CLAUDE.md` inheritance.** Claude Code walks up the directory tree collecting context files. Launch it in `~/Projects/ai-dev-tools-zoomcamp/choreboard/` and it inherits the course repo's `CLAUDE.md` — course-notes instructions leaking into a Django build's context. This is precisely the context pollution the workshop's "fresh session per task" rule exists to prevent, and you'd be building it into the directory layout. This is the decisive argument for me.
3. **Nested `.git` inside an rsync full-mirror with `--delete` is genuinely dangerous**, not just untidy. rsync doesn't understand git internals; a partial sync of `.git/` produces a repo in an inconsistent state, and `--delete` can remove objects the index still references. Your existing course `sync.sh` already excludes the CLIO subfolder — presumably for this reason. Same logic, and the homework repo has *far* more churn (`.venv/`, `__pycache__/`, `db.sqlite3`) than a docs folder.
4. **Working-tree churn.** A live Django tree generates thousands of files you'd be mirroring pointlessly on every sync.

### Why not a third `sync.sh` either

This is the part that departs from the established pattern, so here's the reasoning explicitly.

The pattern exists because *Cowork can't reach WSL*, and both existing folders are **docs that Cowork authors and WSL consumes**. The homework repo is the opposite: **code that WSL authors**, and it has a GitHub remote from question 2 onward. Once it's on GitHub, Cowork can read it directly. rsync would be a second, weaker transport for something git already carries — with `--delete` semantics on a live working tree, which is the highest-risk configuration you could pick.

Concretely: adopting the pattern reflexively here would mean full-mirroring a Django working tree with `--delete` in both directions, over the Windows/WSL boundary, against a folder whose contents `manage.py` rewrites. That's the setup that eats a `db.sqlite3` mid-write or flips file modes on every file.

**So the transport is:**

- **Plan (Cowork → WSL), one time:** you brainstorm in Cowork; the plan lands in `module-01-homework/plan.md`. Run the existing course `sync.sh`; it arrives at `~/Projects/ai-dev-tools-zoomcamp/module-01-homework/plan.md`. Then a single `cp` into the real repo:
  ```bash
  cp ~/Projects/ai-dev-tools-zoomcamp/module-01-homework/plan.md ~/Projects/choreboard/_docs/plan.md
  ```
  Zero new machinery, and it's a nice first real exercise of a `sync.sh` you've never run. (If the sync feels risky on day one, just paste the file — it's one markdown file.)
- **Code (WSL → Cowork), ongoing:** `git push`. Cowork reads GitHub.

### Repo naming

Name it as a product, not as an assignment. The instructor named his `retroloop`, not `workshop-1-demo` — and there's a real reason beyond taste: the agent reads the repo name as context, and `hw1` tells it nothing while `choreboard` tells it what it's building. `choreboard`, `choresplit`, `roundrobin` — pick one and put the course/module reference in the README instead.

**Make it public.** `gh repo create` will happily default to private and your submission link will 404 for reviewers.

### One caveat on this recommendation

If later modules' homeworks turn out to *extend* the Module 1 project rather than start fresh, this structure is still correct — it just becomes a longer-lived repo. If instead every module wants its own throwaway repo, revisit at Module 3: five standalone repos in `~/Projects/` is clutter, and a `~/Projects/zoomcamp-homework/` parent (with each module a separate git repo inside, and the parent *not* a git repo and *not* mirrored) is the right refactor at that point. Don't pre-build it now.

---

## 3. Step-by-step execution plan

> **Note, 2026-09-07:** Q2's repo-creation commands below have been updated in place (not left as a stale reference) to match the single-repo structure from §2's correction — the homework is created inside the existing course repo, at `~/Projects/ai-dev-tools-zoomcamp/homework/module_01/`, not in a new standalone `choreboard` repo. Everywhere else in this section that implicitly assumes "repo root," read that as `homework/module_01/` inside the course repo.

### A note on paths before you start

The homework specifies `_docs/plan.md` and `backlog.md`. The workshop transcript says `docs/plan.md` and `tasks.md`. **Follow the homework literally for anything graded.**

Two things make this painless:

- I checked: **retroloop actually uses `_docs/` too** — the transcript's `docs/` was loose speech. So the homework's paths and the instructor's real convention agree.
- The homework's phrasing is `_docs/plan.md` (path-qualified) but bare `backlog.md` (not path-qualified). That contrast is deliberate enough to read as **`backlog.md` at repo root**. Put it at the root. If you'd rather keep docs together, put it at the root anyway and leave a one-line pointer in `_docs/`. Don't optimize tidiness against a graded path.

Everything else — `process.md`, `decisions.md`, `team/pm.md` — goes under `_docs/`, matching retroloop. **Do not create a second `docs/` folder.** One docs root.

---

### Q1 — Pick an agent

**Claude Code.** Not a close call for you:

- Your whole workspace is already built around it (root `CLAUDE.md`, Cowork, the CLIO plan's subagents and hooks).
- The CLIO plan specifies subagents and hooks, which are Claude Code primitives. Switching agents for the homework would mean practicing on machinery you won't use.
- `/goal` — the loop mechanism the workshop leans on — is a Claude Code feature. Codex has an equivalent; Gemini CLI and Aider don't.

Record the choice in your `README.md` (one line — the homework asks you to commit to one tool, and writing it down is how you hold yourself to it). Verify `/goal` exists in your installed version before you plan around it: run `/help` in a Claude Code session. If it's absent, the fallback per the instructor is a stop-hook or an external re-prompt loop; for grooming five issues, honestly, just re-prompt manually — see §4.

---

### Q2 — Brainstorm the spec, then create the repo

**Run the brainstorm in Cowork, not in Claude Code.** Cowork is your planning environment and this is planning. But there's an adaptation the instructor didn't have to make:

> **The instructor's rationale for using a chat assistant is that it *can't touch files*, which forces it to stay conceptual.** Your Cowork session **does** have file access via the connected folder. So state the constraint explicitly instead of relying on the tool to enforce it: append *"Don't create or edit any files during this conversation — we're only talking."* to the prompt, and hold it to that.

Use the homework's prompt **verbatim** (it's the controlled variable across the cohort):

> I want to build a tool for managing shared household chores. Help me set the scope for this project precisely. I want to brainstorm with you and understand how the tool should work. Give me options. Ask me one question at a time and keep your output short.

Then:

- **Keep thinking effort low or medium.** High reasoning modes are too slow and verbose for a rapid one-question-at-a-time exchange — the instructor calls this out specifically, and it's right.
- **Answer in two or three sentences, not one word.** The output quality tracks the volume of real context you supply. The instructor used voice dictation for exactly this reason. If you have dictation available, use it; if not, deliberately over-answer.
- **Push back on scope creep.** It will offer you gamification, points, mobile push notifications. Every feature you accept is a feature you have to implement or explicitly defer.
- **Close the loop deliberately.** The homework's deliverable is *"which 2-4 features did the spec settle on."* Don't infer it afterwards from prose — end the conversation with: *"List the final MVP feature set as 2-4 bullets, then write the whole thing out as a single markdown document I can save."* Now `plan.md` has an unambiguous features section and your submission answer is a copy-paste.

Save to `01-ai-native-workflow/plan.md` on the Cowork side — this module's existing course-following folder, not a separate `module-01-homework/` folder (that name is superseded, see §2's correction).

**Then set up the repo, in WSL — the *course* repo, not a new one.** It doesn't exist as a git repo yet (confirmed 2026-09-02), so this first run initializes it in place and creates the homework subfolder, rather than `gh repo create --clone`-ing a fresh standalone repo:

```bash
cd ~/Projects/ai-dev-tools-zoomcamp
gh auth status                      # do this FIRST — see §5
git status                          # confirm it really isn't a repo yet before the next line
git init
gh repo create ai-dev-tools-zoomcamp --public --source=. --remote=origin \
  --description "AI Dev Tools Zoomcamp — course work + homework, DataTalksClub 2026 cohort"
mkdir -p homework/module_01
cd homework/module_01
```

**From here on, every command in §3 that assumes "repo root" means this folder** — `~/Projects/ai-dev-tools-zoomcamp/homework/module_01/` — not a standalone repo. `git add -A && git commit` still targets the one repo at `~/Projects/ai-dev-tools-zoomcamp` (git finds it by walking up from cwd), so committing from inside `homework/module_01/` behaves normally; it just means a `git status` here will only show you what's changed under this subfolder plus anything else dirty elsewhere in the repo.

```bash
mkdir _docs
cp ~/Projects/ai-dev-tools-zoomcamp/01-ai-native-workflow/plan.md _docs/plan.md
```

Write `.gitignore` **before the first commit** — at minimum `.venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, `.env`, `staticfiles/`, `.pytest_cache/`, `.ruff_cache/`. Getting `db.sqlite3` into history is annoying to undo and it's the single most common mistake in this exact homework.

Write `README.md`: what the tool is, the agent you committed to, how to run it (you'll fill the commands in after Q3).

```bash
git add -A && git commit -m "Initial: plan, README, gitignore" && git push
```

The workshop's instruction is *"commit regularly"* and it's not decoration — it's what makes an agent's mistakes cheap to undo. Commit after every question below, minimum.

---

### Q3 — Django bootstrap (plus the two workshop steps the homework skips)

The homework jumps straight from plan to Django. The workshop has two steps in between that are worth doing — they're most of what makes this a rehearsal for CLIO rather than a Django tutorial.

**3a. Stack conversation (workshop step 3).** Django is fixed, but real choices remain: `uv` vs pip, SQLite vs Postgres, server-rendered templates vs DRF+React, auth approach, Python version. New Claude Code session:

> Read `_docs/plan.md`. Propose 2-3 options for each open stack decision — dependency management, database, frontend approach, auth — and explain the tradeoffs. Don't write any code yet.

**Push back on what it proposes.** The instructor's warning about knowledge cutoffs is concrete and immediate here: Django's major version and `uv`'s idioms have both moved recently, and the agent will confidently cite whatever it was trained on. After you install, check what you actually got and read *those* docs:

```bash
uv run python -c "import django; print(django.get_version())"
```

**My recommendation for this project: `uv`, SQLite, Django templates, no DRF, no React, Django's built-in auth (or no auth at all if the plan doesn't need it).** Reasoning: the homework grades process, not architecture, and CLIO is where your FastAPI/React/Postgres complexity belongs. Duplicating that stack here doubles the yak-shaving and teaches you nothing you won't learn on the real project. Deliberately picking a *different, simpler* stack also proves the process is stack-independent — which is the actual claim being tested.

Save the decisions to `_docs/decisions.md`. (Note: retroloop names this `decisions.md`, not `architecture.md` as the transcript says. Match the real repo — "decisions" is the better name anyway, since it's a log you append to, not a static description.)

**3b. Bootstrap.**

```bash
uv init --python 3.12          # then delete the main.py/hello.py it scaffolds
ls -a                          # check: uv init can create its own .git/ — if you see one here, remove it
                                # (rm -rf .git), you don't want a repo-inside-a-repo swallowing the homework
uv add django
uv run django-admin startproject config .
uv run python manage.py startapp chores
```

**Note, added after review:** `manage.py` lives at `homework/module_01/manage.py`, and `uv` resolves the active project from the nearest `pyproject.toml` walking upward — so every `uv run`/`manage.py` command below must be run from inside `homework/module_01/`, never from the course repo root. Worth one line in `AGENTS.md` (§3c) so an agent session doesn't get this wrong.

Then register the app. **One file, one list.** Find it yourself — that's Q3's question, and hunting for it once is why the question exists.

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Open it in your Windows browser at `http://127.0.0.1:8000/` and confirm the rocket. See §5 if it doesn't load.

**3c. Context engineering (`AGENTS.md` + `CLAUDE.md`) — workshop step 6, and the highest-value item in the whole homework for you.**

**Location, confirmed after review: both files go inside `homework/module_01/`, not at the course repo root.** Under the single-repo layout, Claude Code walks *up* the directory tree collecting context files — a root-level `CLAUDE.md` would be inherited by every homework build session, which is exactly the context pollution §2's correction flagged as a real (not hypothetical) risk of nesting. Don't create one at the course repo root today; launch Claude Code with its working directory set to `homework/module_01/` so it only picks up the files described below. Also add one line to `AGENTS.md` itself: all commands run from `homework/module_01/` (see the `uv`/working-directory note in §3b above).

`CLAUDE.md` is one line. Verified: retroloop's `CLAUDE.md` is literally `@AGENTS.md` — an import directive, nothing else. Copy that exactly. It's how the same context serves Claude Code and any other agent.

`AGENTS.md` — plain facts, no markdown decoration, no headers needed at this size. Aim for **under 30 lines to start.** Cover:

- Stack, in one line (Django + SQLite + uv + templates)
- Commands: install, migrate, runserver, test
- Conventions: what belongs in the `chores` app, template location
- Where tasks live: GitHub issues, labeled MVP / post-MVP
- Pointers, not content: "process is in `_docs/process.md`", "decisions in `_docs/decisions.md`"

Two rules from the transcript that you should actually enforce:

- **Trim ruthlessly.** The agent will pad it and will write things that aren't true yet ("we use pytest with 90% coverage"). Delete anything aspirational. A context file that lies is worse than no context file.
- **Point, don't inline.** Topic docs live in `_docs/` and get linked, so each task pulls in only what it needs. This is the mechanism that keeps `AGENTS.md` from becoming a 2,000-word wall — which, for the record, is exactly what retroloop's has become as the project matured (I checked: ~2,000 words, sections for Documents / Commands / Rules / Background tasks / CI). That's a mature repo's end state, not a starting point. **Start at 30 lines and let it grow only when a real mistake proves a line is missing.**

Commit.

---

### Q4 — Backlog, and push it to GitHub issues

New session:

> Read `_docs/plan.md` and `_docs/decisions.md`. The Django project and the `chores` app are already bootstrapped and migrations run — do not include setup tasks. Propose a backlog for implementing the MVP. Each task must be independent and small enough to finish in one session. Mark each MVP or post-MVP. Write it to `backlog.md`. Don't write any code.

**The "bootstrap is already done" clause is load-bearing.** Left to itself the agent will make task #1 "set up the Django project" — which you've already done, which makes Q4's deliverable trivial and Q5's implementation hollow. You want task #1 to be a real user-facing slice (e.g. "create a chore with a name and a recurrence").

**Then review it with a PM hat on**, as the workshop instructs. Concretely, check each task for: is it a real feature with a concrete goal? Is it independent, or does it secretly depend on three others? Is it too granular ("add a field to the model" is not a task)? Is it too vague ("build the UI")? Rewrite in place — don't just accept the list.

Aim for **6-10 issues**, maybe 4-6 of them MVP. More than that and you've over-decomposed a chores app.

**Push to GitHub issues** (workshop step 5). The homework doesn't require this. Do it anyway — it's cheap, and it's the piece your CLIO plan depends on, since the whole PM/engineer/QA graph is built on issues as the unit of work. Files can't carry a state machine; issues can.

```bash
gh label create MVP --color 0E8A16
gh label create post-MVP --color C5DEF5
gh issue create --title "..." --body-file /tmp/issue-body.md --label MVP
# use --body-file, not --body "..." — agent-generated bodies commonly contain
# newlines/backticks that break a shell-quoted --body string
```

Have the agent generate the `gh issue create` calls from `backlog.md` and run them — but read them before executing. Note task #1's title; that's Q4's deliverable.

Commit `backlog.md`.

---

### Q5 — Implement task #1 and run the server

**Fresh session.** This is workshop step 9 and it's not ceremony — carrying the backlog-generation context into implementation is exactly the token bloat and context pollution the practice exists to prevent.

If task #1 is user-facing (it should be, per Q4), run it through the PM persona first — see §4 for the role files. Groom the issue: explicit goal, checkable acceptance criteria, explicit out-of-scope list. **"Checkable" has a specific test**: someone should be able to point at the screen and say yes or no. "Chores are easy to add" fails. "Submitting the new-chore form with a name and a weekly recurrence creates the chore and shows it in the list" passes.

Then implement, against the groomed issue only. Then:

```bash
uv run python manage.py runserver
```

and actually click through the acceptance criteria yourself. Q5's question is about this command; you'll have typed it twice by now.

Commit, push, close or leave the issue open pending QA.

---

### Q6 — Tests

The homework specifies a two-phase approach and the review step is the point — don't collapse it into one prompt.

**Phase 1, scenarios only:**

> For issue #N, list the test scenarios worth covering. Don't write any test code yet.

**Sanity-check the list yourself.** This is the homework explicitly asking you to not rubber-stamp. Look for: the happy path, the obvious invalid input, the boundary case that the acceptance criteria implies. Look also for *absent* scenarios and *pointless* ones — agents reliably propose tests for Django's own ORM behaviour, which test nothing you wrote. Cut those.

**Phase 2, implement and run:**

```bash
uv run python manage.py test
```

**Use Django's built-in test runner, not pytest-django, for this project.** Fewer moving parts, no extra config, and `manage.py test` is the command you should know cold regardless of what you later prefer. (retroloop does use a richer setup with a dedicated `config/settings_test.py` — that's a mature project's answer, not a first-week one.)

This is also where the QA persona earns its keep: separate session, reads the groomed acceptance criteria, checks each one, returns pass or fail. Not "mostly working." Binary.

Push. Submit the repo link at https://courses.datatalks.club/ai-dev-tools-2026/homework/hw1.

---

## 4. Where the full graph earns its keep here — and where it doesn't

**Verdict: build all the role artifacts, run the full loop exactly once, and skip the orchestrator.**

The instructor's own stated tradeoff is the right lens: the full process burns **4-5x the tokens per issue** (groom + implement + test + possible fail-and-retry, versus just implement), and he explicitly does *not* run technical bootstrap tasks — docker-compose, scaffolding — through PM/QA. He reserves it for user-facing features, where QA catches real bugs.

Apply that rule honestly to a chores app with 6-10 issues and you get:

| Work | Process |
|---|---|
| `uv init`, `uv add django`, `startproject`, `startapp`, `.gitignore`, settings, base template, migrations | **Direct implementation.** No grooming, no QA. This is exactly the instructor's bootstrap exemption. |
| Backlog task #1 (user-facing) | **Full loop: PM → engineer → QA, separate sessions each.** This is the required rep. |
| Backlog tasks #2-N | Direct implementation, or stop entirely once the homework is submitted. |
| Whole-backlog orchestration | **Skip.** |

### Why skip the orchestrator specifically

Not because orchestration is bad — because there's nothing here for it to orchestrate. Its value is *amortized*: it pays off across many issues, when the cost of manually driving each handoff exceeds the cost of the extra tokens. Across four MVP issues in a throwaway repo, you'd pay 4-5x on tasks nobody grades, to save maybe twenty minutes of typing, and you'd be debugging your orchestrator rather than learning the handoffs. That's the definition of disproportionate.

There's a second reason, and it's the more important one: **the orchestrator is the piece you most want to get right on CLIO, and it's the piece that benefits most from having felt the handoffs manually first.** Run PM→engineer→QA by hand once and you'll know exactly what the orchestrator needs to pass between nodes. Automate it before you've felt it and you'll be writing an orchestrator from the transcript's description rather than from experience.

### But do run `/goal` once — on grooming

Loop engineering is a real concept you should have hands on, and grooming is where it's cheapest to practice. Grooming is text-only: no code generation, no test runs, no fail-and-retry cycles. It's the lowest-token-cost demonstration of the exact mechanism.

> `/goal` Groom all issues labeled MVP. For each: read it, rewrite it using the template in `_docs/team/pm.md`, make the acceptance criteria checkable, list edge cases, and put anything out of scope into a separate follow-up issue rather than expanding this one. Resolve loose ends yourself and document each decision in the issue. Stop when every MVP issue is groomed.

Note the two features that make this a *loop* rather than a prompt: a standing goal, and a checkable stop condition. Both must be present or the harness has nothing to terminate on. (`/loop` — the scheduled re-prompt — exists but the instructor uses `/goal` far more; skip `/loop` here, there's nothing long-running to poll.)

### What to actually write, and where

Write these — they're cheap (one text-only session), and they're the deliverables that transfer:

- **`_docs/process.md`** — the workflow: tasks are GitHub issues, MVP/post-MVP labels, the lifecycle from grooming through QA to close, commit conventions, and the rule that QA failures route back to the engineer.
- **`_docs/team/pm.md`, `_docs/team/software-engineer.md`, `_docs/team/qa-engineer.md`** — three short separate role files (retroloop's are 27-50 lines each), not one consolidated file. See the correction just below — this document originally got this wrong.
- **`_docs/task-template.md`** — the four-section issue template (Goal / Acceptance criteria / Out of scope / Constraints) that `pm.md` rewrites issues into, kept separate from `pm.md` itself.
- **`AGENTS.md`** links to `_docs/process.md`. That's what makes it reproducible in every future session instead of something you re-explain.

**Correction (2026-09-07, re-verified live in-browser): the earlier version of this document had this backwards.** All three role files exist in retroloop, separately: `_docs/team/pm.md`, `_docs/team/software-engineer.md`, `_docs/team/qa-engineer.md`. `_docs/process.md`'s "Roles" section is a **three-line pointer** to those files ("PM — grooms a task, follows `_docs/team/pm.md`", etc.), not the role definitions themselves. There's also a separate `_docs/task-template.md` (Goal / Acceptance criteria / Out of scope / Constraints — four sections, ~15 lines) that `pm.md` points to rather than embedding. So: **build all three role files** (pm.md, software-engineer.md, qa-engineer.md), each short (retroloop's are 27-50 lines), plus a separate task-template.md, and keep `process.md` itself to workflow/labels/lifecycle — matching the actual mature repo, not the "consolidate into one file" advice this document gave before verification. The QA file's contract is worth copying near-verbatim: strict PASS/FAIL, one line per acceptance criterion, the test command and its result included, and an explicit "ignore what the implementation claims, only the acceptance criteria and the running code count."

The single rule to preserve above all others: **QA runs in a separate session from the engineer.** Everything else in the graph is optimization. This one is the mechanism — an agent that reviews its own output confirms its own assumptions, and you get a green check on a broken feature. If you strip the process down to nothing else, keep this.

**Added after review — "separate session" made operational, since the doc never actually said what that means in your setup:** PM, engineer, and QA are three separate Claude Code sessions/invocations in WSL (not three different tools, not Cowork playing one of the roles) — call them A, B, C. Session C (QA) receives only the groomed issue text and the repo state, never session B's (engineer's) transcript or reasoning — that's what "separate" has to mean for the rule to actually hold. Cowork's role stays what it's been all along: it can help specify (e.g. drafting `pm.md`/`qa.md` content, or the brainstorm in Q2) but it never adjudicates whether the work passes — if the same session both writes acceptance criteria and later blesses the result, the rule is broken while looking satisfied.

### CLIO carry-over

When you get to CLIO, `evidence-reviewer` slots into the QA node position. The generic `qa.md` you write here is its template: reads criteria it didn't write, returns binary, has no authority to fix what it finds. Write it that way now.

One thing you'll see in retroloop's `_docs/process.md` that you should *not* build yet: it has grown sections for parallel waves, git worktrees with isolated databases, and a serial merge queue — up to five agents working concurrently. That's where this goes at scale, and it's a plausible CLIO end state. It is not a Module 1 pattern. Note it and move on.

---

## 5. Risks and gotchas specific to your setup

**Ordered roughly by likelihood of actually biting you.**

1. **Neither `sync.sh` has ever been run — and as of 2026-09-07 ~10:00 UTC this is now actively dangerous, not just untested.** Originally both WSL targets were empty; that's no longer true. WSL `~/Projects/ai-dev-tools-zoomcamp` now holds a real git clone (`.git/`, `README.md`, `.gitignore`, `LICENSE`, two pushed commits); the Cowork mirror holds this document and other course-following content. **The two sides are now disjoint — a full-mirror `--delete` in either direction destroys whichever side it overwrites** (`pull` wipes the WSL clone, `.git/` included, if it isn't excluded; `push` wipes the Cowork-side docs). **Don't run `sync.sh` today.** Copy `plan.md` by hand instead (it's one file) — the escape hatch this document already offered below is now the right default, not the fallback. Dry-run both directions and confirm the exclude list (especially `.git/`) on a calmer day before trusting it with anything real.

2. **`gh` may not be installed or authenticated in WSL.** Check `gh auth status` before Q2, not during it. If it's missing: `sudo apt install gh` then `gh auth login`. Several steps depend on it (repo creation, labels, issues) and discovering this mid-flow is a needless interruption.

3. **The repo must be public.** `gh repo create` without `--public` makes it private, and your submitted link 404s for reviewers. Check with `gh repo view --web` after creating.

4. **`db.sqlite3` and `.venv/` in git.** Write `.gitignore` before the first commit. This is the single most common failure mode in this specific homework and it's irreversible-ish once pushed.

5. **`runserver` not reachable from your Windows browser.** WSL2 usually forwards `localhost`, but not always — after a Windows update, or with certain VPN clients, it breaks. Fallback: `uv run python manage.py runserver 0.0.0.0:8000`, get the WSL IP with `hostname -I`, and browse to that. **Correction: the original advice here was wrong about when this matters.** Even with `DEBUG=True`, Django only auto-allows `localhost`/`127.0.0.1`/`[::1]`/`.localhost` — a raw WSL IP like `172.x.x.x` still hits `DisallowedHost` regardless of `DEBUG`. If you need the IP fallback, add it to `ALLOWED_HOSTS` in `config/settings.py` no matter what `DEBUG` is set to.

6. **Line endings and file modes across the Windows/WSL boundary.** The sync bridge crosses filesystems. Symptom: `git status` shows every file modified after a sync. Prevention, in the homework repo:
   ```bash
   git config core.autocrlf input
   git config core.fileMode false
   printf '* text=auto eol=lf\n' > .gitattributes
   ```
   Under my §2 recommendation the homework repo isn't mirrored at all, so this mostly won't arise — but set it anyway, and *definitely* set it in the CLIO repo, which is mirrored.

7. **Two writers on one file.** Full-mirror `--delete` resolves conflicts by clobbering, not merging. Adopt one rule: **one writer per file.** For the homework, `plan.md` is Cowork-authored, copied into WSL once, and never edited on the Cowork side again. For CLIO, decide this explicitly per file before you have a conflict, not after.

8. **`/goal` may not exist in your Claude Code version.** Verify with `/help` before planning around it. The instructor's fallback is a stop-hook or a scripted re-prompt loop (he uses tmux); for grooming four or five issues, just re-prompt manually — building a tmux loop to save four prompts is not a good trade. Also: `/goal` is a Claude Code *CLI* mechanism. Cowork is not Claude Code CLI; don't expect it there.

9. **The instructor's setup is not yours.** He drives a remote machine over tmux; you have WSL local plus a manual rsync bridge. Anything in the workshop that depends on a long-running detached session — background loops, scheduled re-prompts, agents left running — doesn't transfer directly. Your `sync.sh` runs are manual and synchronous, so **nothing crosses the Cowork/WSL boundary while an agent is mid-task.** Don't design a workflow that assumes it does.

10. **Token budget.** The 4-5x multiplier is real and it compounds with retries. If you're on a plan with weekly caps, running the full graph across a whole backlog on a *homework* project is how you arrive at CLIO's week with no budget. §4's scoping is partly a token-budget decision, not just a pedagogical one.

11. **Knowledge-cutoff drift on Django and `uv`.** Both have moved recently. The agent will confidently produce `settings.py` patterns or `uv` invocations from an older version. Always check the installed version and read those docs. This is the workshop's push-back instruction made concrete — it's not a general disclaimer, it's the specific failure mode you'll hit in Q3.

12. **Module count mismatch — worth resolving before you hard-code CLIO milestones.** The course repo's root README currently presents **four** workshops, while your CLIO plan maps Week 1-6 to Modules 1-6. That may just be a stale public README versus the cohort page, but your project plan's milestone sequence is pinned to a module count. Confirm against the 2026 cohort page before those milestones become commitments — a six-week plan against a four-module course is a scheduling problem you'd rather find now.

13. **Don't let habits from this repo leak into CLIO.** Django generates a `SECRET_KEY` directly in `settings.py`, and committing it is fine for a throwaway chores app — nothing is behind it. It is not fine for CLIO. Note the distinction now, because the agent will happily reproduce the pattern it saw you accept.

14. **Homework timing.** No deadline is stated in the homework file, but the cohort started 2026-08-31 and these stack — Module 2 assumes Module 1's habits. Check the cohort page for the actual cutoff and don't let it drift; the value of Module 1 as *rehearsal for CLIO* decays sharply if you're doing it while Module 3 is live.

---

## Appendix A — Verified retroloop conventions

I checked these against the live repo (github.com/alexeygrigorev/retroloop) rather than relying on the transcript. Where they differ, trust these.

**Root:** `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore`, `.env.example`, `manage.py`, `pyproject.toml`, `uv.lock`, `compose.yaml`, `Dockerfile`, `.dockerignore`, `package.json`, `vite.config.js`, plus Django apps (`accounts/`, `board/`, `cycles/`, `meetings/`, `projects/`, `retro/`, `ai/`), `config/`, `templates/`, `static/`, `assets/`, `tests/`, `deploy/`, `demo/`, `.github/workflows/`.

**Confirmed and worth copying:**

- **`_docs/`, not `docs/`** — matches the homework's required path. The transcript's `docs/` was loose speech.
- **`CLAUDE.md` is a single line: `@AGENTS.md`.** An import, nothing more. Copy this literally.
- **`_docs/decisions.md`**, not `architecture.md`. Better name — it's an append-only log.
- **`_docs/process.md`** carries the workflow: Labels / Background / Roles / Orchestrator / Working in parallel / Worktrees / Integration / Lifecycle / Rules. ~2,500 words *at maturity* — confirmed by direct read, and it's a genuinely sophisticated operations doc at this point (parallel waves of up to 5 agents, one git worktree + isolated Postgres database per issue, a merge queue, explicit rules against ever running destructive commands because they stall an unattended agent waiting on human approval). This is real end-state content, not something to imitate for a homework repo — noted correctly below, keep ignoring it for Module 1.
- **Corrected 2026-09-07 (was wrong before verification): all three role files exist separately** — `_docs/team/pm.md`, `_docs/team/software-engineer.md`, `_docs/team/qa-engineer.md` — plus a standalone `_docs/task-template.md`. `process.md`'s "Roles" section is only a 3-line pointer to the three files, not their content. See the corrected guidance in §4.
- **No `_docs/plan.md` and no `backlog.md` in the current repo.** `process.md`'s Background section references "archived plans." These are *scaffolding for the start of a project*, and retroloop has moved past needing them — the backlog now lives entirely in GitHub issues. Reassuring: your homework's `plan.md` and `backlog.md` are supposed to be superseded by issues, not maintained forever.
- **`AGENTS.md` at maturity: ~2,000 words**, sections for Documents / Commands / Rules / Background tasks / CI, pointing to `_docs/process.md` and `_docs/decisions.md`. This is an end state reached by accretion. Start at 30 lines.
- **No `.claude/agents/` in the repo.** The role definitions are plain markdown docs, not Claude-Code-specific subagent configs — which is why they survive the `AGENTS.md`/`CLAUDE.md` portability trick. Worth noting for CLIO: your `evidence-reviewer` will be more portable as a doc the agent reads than as a tool-specific config.

---

## Appendix B — MCQ self-check

**Don't read this before doing the work.** All three answers fall out of Q3, Q5 and Q6 as a matter of course — you will have typed two of the commands several times and edited the file in question by hand. That's the design of the exercise: the questions verify you actually ran the thing.

Use this only to confirm after the fact:

- **Q3 (register an app):** the file you edited lives in the project package alongside `wsgi.py` and `asgi.py`, and contains `INSTALLED_APPS`.
- **Q5 (dev server):** whatever you actually ran to get the rocket page. Django's runserver subcommand goes through `manage.py`; under `uv`, prefixed with `uv run`.
- **Q6 (tests):** Django's built-in runner is a `manage.py` subcommand. If you added `pytest-django` instead, you'd have answered differently — which is a reason to stick with the stock runner for this one.

If any of these three feel like guesses rather than recall, that's a signal you skipped a step and should go back and run it.

---

## Retrospective — carried over from the original `README.md`

*Everything above this line is prospective: direction and an execution plan written **before** the
Module 1 build. This section is the reverse — post-hoc findings from actually **running** the
AI-native process on the chores app. It was the substantive half of the original
`01-ai-native-workflow/README.md` (still readable via
`git show HEAD:01-ai-native-workflow/README.md`), folded in here in its original wording when that
file was replaced, so the findings and the rule they produced don't get lost in the swap.*

### The one load-bearing rule

> **No agent grades its own work.**

This is the cheapest part of the whole process to implement — it costs one extra session, not
an orchestrator, not tooling, not a framework. It is also the one part that must not be cut
under time pressure. Everything else in `process.md` can be compressed if the schedule slips;
this can't, because without it "QA'd" means nothing more than the engineer re-reading its own
diff.

### What held up when the process was run

Two findings from actually running the build. These are the substantive part of this document.

#### Finding 1 — the isolation rule fails visibly the one time it's skipped

A QA pass was run in the same chat session that had just written the code under review.

It returned a clean **PASS** on every acceptance criterion. Then, unprompted, it flagged itself:
it still had the full implementation in its own context, so its verdict couldn't count as
review. It had checked the criteria against its own memory of building the thing, not against
the code as a stranger would find it.

The pass was re-run from a genuinely fresh session. That session confirmed, at the very start of
its own output, that it had no memory of the implementation. Same issue, same acceptance
criteria — and this time it caught real edge cases that the contaminated pass's confidence had
glossed straight over.

**Takeaway:** a PASS from a reviewer that wrote the code is a measurement of that reviewer's
memory, not of the code. The isolation rule isn't bureaucracy; it's the thing that makes the
verdict mean something.

#### Finding 2 — a groomed issue is not the same as an independently buildable one

Two backlog issues were each, on their own, well-formed: checkable acceptance criteria, an
explicit out-of-scope section, stated constraints. By the template, both were ready.

Together they were circular. One issue's acceptance criteria required an endpoint that the
other issue was responsible for building. That other issue's own constraints required the first
issue's guard to already exist. Neither could be built alone as written — each one's
precondition sat on the other side of the pair.

**Takeaway:** buildability is a property of the issue *graph*, not of any single issue. A
grooming pass that only ever looks at one issue at a time can't catch this. The fix is
re-grooming — decide which issue owns the shared piece, consolidate it there, and re-link the
dependency one way; or merge the two if they're really one slice of work. It is *not* something
to work around during implementation.

This became a course FAQ contribution, filed under the `ai-dev-tools-zoomcamp` course:
[`github.com/DataTalksClub/faq/issues/387`](https://github.com/DataTalksClub/faq/issues/387).
