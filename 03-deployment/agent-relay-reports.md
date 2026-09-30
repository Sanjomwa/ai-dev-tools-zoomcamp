# Agent Relay (hw03) — cumulative progress log

**Purpose:** Claude Code's `reports.md` inside `~/Projects/agent-relay` is scratch space — it
gets **overwritten** each step, not appended to (repo stays clean, no report-file history in
git). This file is the durable record instead: every time Sam pastes a `reports.md` dump here,
it gets appended below under its own dated/step heading. Read this file for the full history;
`reports.md` in the repo only ever holds the *latest* step's findings.

Related: `module-03-lessons.md` in this same folder (technique lessons from the Module 3
lesson content, not hw03-specific); `status-log.md` at the workspace root (workspace-wide
narrative, not this project's step-by-step detail).

---

## 2026-09-17 — Steps 1–3 (environment check, clone verification, Question 1 exploration)

### Step 1 — Environment check

Ubuntu-on-WSL2. Results:

| Tool | Status | Version |
|---|---|---|
| docker | already installed, reachable (`docker ps` succeeded, empty list, no error) | Docker version 29.8.0, build 88096ef |
| uv | already installed | uv 0.11.25 (x86_64-unknown-linux-gnu) |
| kind | installed this session — no sudo available, binary placed in `~/.local/bin` (already on PATH) instead of `/usr/local/bin` | kind v0.30.0 |
| kubectl | already installed | Client v1.36.1, Kustomize v5.8.1 |
| act | installed this session via nektos/act's official install script, targeted at `~/.local/bin` | act v0.2.89 |

Docker confirmed reachable via `docker ps`. kind and act live in `~/.local/bin` rather than `/usr/local/bin` since sudo needs an interactive password prompt in this environment — move with `sudo mv` later if a system path is ever needed.

### Step 2 — Clone the fork

`~/Projects/agent-relay` exists, clean git repo on `main`, up to date with `origin/main`. Remotes: `origin` → Sanjomwa/agent-relay, `upstream` → alexeygrigorev/agent-relay. Verified both existing commits (`c82b354`, `0a2895b`) are authored by Alexey Grigorev and match `upstream/main` exactly — confirmed untouched starter, not prior work.

### Step 3 — Question 1: architecture

`uv sync` (32 packages), server started with `uv run uvicorn main:app --reload`, running at http://127.0.0.1:8000/. `/health` → ok, `/ready` → ready.

Ran a full task exchange via curl: registered alice (sender) and uppercase (recipient) agents, alice posted a task, uppercase claimed it (`/tasks/claim`), completed it (`/tasks/{id}/complete`), alice fetched the result (`output: "HELLO AGENT RELAY"`). Both agents show correct `last_seen_at`; dashboard root returns 200.

**Architecture finding:** plain HTTP REST API backed by a shared SQLite database acting as a job queue — not a message broker, not pub/sub, not peer-to-peer, no WebSocket push (the `websockets` package is only a transitive uvicorn dependency, unused for messaging). Key mechanics found:

- Agents never talk to each other directly — everything routes through the relay over HTTP/JSON.
- SQLite (WAL mode) is the single source of truth; `storage.py` handles claim/complete/fail/recovery, `database.py` has the SQLAlchemy models plus a `BEGIN IMMEDIATE` transaction helper substituting for SQLite's lack of `FOR UPDATE SKIP LOCKED` (SPEC.md flags this as the seam a Postgres port would replace with row locking).
- "Delivery" is agent-initiated long-polling: `POST /tasks/claim` takes `wait_seconds` (0–30, default 30) and holds the connection until work appears or the wait expires. The relay never pushes.
- Claims are leased (60s default, `RELAY_LEASE_SECONDS`) with their own single-use `claim_token`, separate from the agent's auth token. Heartbeats extend the lease; a background recovery loop expires stale leases and requeues (up to `RELAY_MAX_ATTEMPTS`, default 5) or fails with `attempts_exhausted`.
- Delivery is at-least-once, not exactly-once (SPEC.md explicit) — side-effecting agents are expected to use the task ID as their own idempotency key.
- Terminal actions and task creation (`Idempotency-Key` header) are idempotent by design.
- Everything but registration requires `Authorization: Bearer <agent_token>` — the token is the identity.

**Notes relevant to later questions (from SPEC.md):**

- SPEC.md calls itself a "v1 starter," explicitly missing Docker/K8s/CI/broker/LLM/Postgres on purpose, framed as later "deployment/porting" exercises — directly foreshadows this homework.
- Storage layer intentionally seamed for a PostgreSQL port: protocol, credential rules, lifecycle, delivery guarantees expected to stay unchanged — relevant to Question 4.
- Config already via env vars (`RELAY_DATABASE_URL`, `RELAY_ENROLLMENT_SECRET`, `RELAY_LEASE_SECONDS`, `RELAY_MAX_ATTEMPTS`) — maps cleanly to k8s ConfigMap/Secret later.
- `/health` (liveness) vs `/ready` (readiness, checks real DB schema) already split — maps directly to k8s probes.
- SQLite is a single file (`./agent-relay.db`) — for kind, means either a PersistentVolume or accepting pod-restart data loss; a decision point for a later step.
- The included worker (`uv run python main.py worker ...`) is a separate long-running client process, self-registers, persists creds to a mode-0600 JSON file — a second workload that may need its own deployment later.
- SPEC.md lists 10 acceptance scenarios (basic exchange, offline recipient, multi-worker distribution, lease expiry/redelivery, stale-token rejection, heartbeat-blocks-others, idempotency, attempt-limit exhaustion, cross-agent access denial, restart durability) — good checklist for later correctness questions.

Test suite (`uv run pytest -q`) and the worker script were not run this step (Q1 only asked for hands-on API/dashboard exploration) — noted here in case a later step wants them.

## 2026-09-17 — Step 4 (Question 2: integration test)

**Test location:** `test_agent_relay.py`, new function `test_full_task_exchange_sender_sees_completed_result`, placed before `test_dashboard_is_asset_and_invalid_input_is_documented_error`. Follows existing file conventions: the autouse `empty_database` fixture (real SQLite scratch DB at `/tmp/agent-relay-test.db`, isolated from the manually-run dev server's `./agent-relay.db`), the existing `register(client, name)` helper, `TestClient(main.app)` (real app + real DB, no mocking, matching the rest of the file), `wait_seconds: 0` on claim since the task is already queued.

**What it does:** alice (sender) and uppercase (recipient) register → alice posts a task (asserts `201`, `status == "queued"`) → uppercase claims it (asserts `200`, captures `claim_token`) → uppercase completes it with `output: "HELLO AGENT RELAY"` (asserts `200`, `status == "completed"`) → alice reads the task back (asserts `200`, `status == "completed"`, `output` matches, `error is None`, `finished_at` set).

**Run output:** targeted run — `1 passed, 4 deselected` in 1.29s. Full suite — `5 passed` in 1.75s, no regressions against the 4 pre-existing tests.

**Direct answer:** task status from the sender's point of view after the recipient submits its result is the literal string `"completed"` (returned by `GET /api/v1/tasks/{task_id}`). The parallel failure-path terminal state is `"failed"` per SPEC.md, not exercised by this test since the recipient succeeded.

## 2026-09-17 — Step 5 (Question 3: containerization)

**Dockerfile** (repo root):

```dockerfile
FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

# Install dependencies first so this layer is cached unless pyproject/uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Application code.
COPY main.py database.py errors.py schemas.py storage.py worker.py dashboard.py dashboard.html ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Approach:** `python:3.11-slim` base (matches `.python-version`/`pyproject.toml`'s `>=3.11`). Dependencies installed via `uv sync --frozen --no-dev` against the committed `uv.lock` (exact resolved versions, dev group like pytest/httpx excluded from runtime image). `pyproject.toml`+`uv.lock` copied and synced before app code, so the dependency layer caches across code-only rebuilds; a second `uv sync --frozen --no-dev` after the code copy installs the project itself. `CMD` uses the plain venv `uvicorn` binary (via `PATH` pointed at `/app/.venv/bin`) rather than `uv run`, no `--reload` (dev-only). **`--host 0.0.0.0` explicit** — uvicorn's `127.0.0.1` default would make a published port connect-refuse from the host despite the process being healthy; confirmed avoided. Added `.dockerignore` (`.venv`, `.git`, `.pytest_cache`, `__pycache__/`, `*.db*`, `*-credentials.json`, `reports.md`). `RELAY_DATABASE_URL` left unset — container uses its default SQLite file inside the writable layer (`/app/agent-relay.db`), ephemeral, lost on `docker rm` — flagged as the natural candidate for a k8s PersistentVolume later.

**Build:** `docker build -t agent-relay:local .` — succeeded, ~40s.

**Run:** `docker run -d --name agent-relay-local -p 18000:8000 agent-relay:local` — **host port 18000** (chosen to avoid clashing with the bare `uv run` dev process still on host `8000`). `docker ps` confirmed `0.0.0.0:18000->8000/tcp`; container logs showed clean `Uvicorn running on http://0.0.0.0:8000`.

**Verification against http://127.0.0.1:18000/:** `/health` ok, `/ready` ready, dashboard root 200. Repeated the full Q2 task-exchange flow through the container (register alice/uppercase, send/claim/complete a task, sender reads back `status: "completed"`, correct output, `error: null`, `finished_at` set) — identical behavior to the bare-process runs in Steps 3–4.

Container (`agent-relay-local`) left running on host port 18000 for manual dashboard check if wanted.

## 2026-09-17 — Step 6 (Question 4: Postgres + Compose)

**DB-swap approach:** codebase was already mostly DB-agnostic (SQLAlchemy Core/ORM throughout, `psycopg[binary]>=3.3.5` already a dependency). One real blocker: `database.immediate_transaction()` issued raw `BEGIN IMMEDIATE` (SQLite-only writer-lock syntax, invalid on Postgres), used by `authenticate()`, `create_task()`, `claim_one()`, `heartbeat()`, `commit_terminal()`. Fixed by branching on `_is_sqlite(DATABASE_URL)`: SQLite still gets `BEGIN IMMEDIATE`, Postgres relies on SQLAlchemy's normal autobegin. SQLite support left fully intact, selected purely by `RELAY_DATABASE_URL` scheme.

**compose.yaml:** two services — `postgres` (postgres:16-alpine, healthcheck via `pg_isready`, named volume for data) and `app` (build: ., port 8010→8000, `depends_on: postgres: condition: service_healthy`). App connects via `postgresql+psycopg://agent_relay:agent_relay@postgres:5432/agent_relay` — hostname is the **Compose service name** (`postgres`), resolved via Docker's embedded DNS, not `localhost` (which inside the app container would mean the app container itself) and not a published host port (5432 was never published — postgres only reachable from other Compose services). `+psycopg` scheme suffix needed explicitly since the project uses psycopg3, not psycopg2.

**Build & start:** `docker compose up --build -d`. Confirmed startup order — postgres created→started→Waiting→**Healthy**, only then app created/started — proving `depends_on: condition: service_healthy` actually gated startup, not just container-started.

**Verification 1 (really using Postgres, not silent SQLite fallback):** checked the resolved SQLAlchemy engine URL from inside the running app process (not just the env var) — confirmed `postgresql+psycopg://...@postgres:5432/agent_relay`; confirmed no `/app/*.db` file exists in the container.

**Verification 2 (task flow via http://127.0.0.1:8010):** full register→send→claim→complete→read-back flow, identical to prior steps, `status: completed`, correct output.

**Verification 3 (direct Postgres query):** `docker compose exec postgres psql` confirmed 2 agents, 1 task (status completed, correct output), 1 attempt row actually persisted in the real `agent_relay` Postgres database.

**Verification 4 (pytest integration test from Q2, against Postgres):** created a second logical DB (`agent_relay_test`) in the same Postgres instance to avoid the `empty_database` fixture wiping the just-verified demo data; ran the test from inside the `app` container (so `postgres` hostname resolves the same way the real app sees it) with `RELAY_DATABASE_URL` pointed at `agent_relay_test`. **1 passed.** Confirmed demo data in the main DB untouched afterward. Also re-ran the full local suite (defaults to SQLite) — still 5 passed, no regression from the `immediate_transaction()` change.

**Scope note — real finding, deliberately not fixed this step:** running the *full* suite against Postgres (not just the Q2 test) fails `test_sqlite_atomic_claims_distribute_without_overlap` (16 concurrent claims, asserts zero overlap) with a duplicate-key IntegrityError. SQLite's `BEGIN IMMEDIATE` gives this test a whole-database writer lock for free; Postgres's default autobegin has no equivalent, so two threads can select the same queued task before either commits. This is exactly the seam SPEC.md flags as needing `SELECT ... FOR UPDATE SKIP LOCKED` for a real Postgres port. Not required by Question 4 (DB swap + Compose orchestration only) — flagged in case a later step needs concurrency-safety hardening.

**Current state:** three independent ways to reach the API are running simultaneously — bare `uv run` dev process (port 8000), Q3's standalone container `agent-relay-local` (port 18000), and the Compose stack's `app` service (port 8010, backed by real Postgres). Compose stack left up for manual dashboard check if wanted.

## 2026-09-17 — Step 7 (Question 5: Kubernetes via kind)

**Cluster:** `kind create cluster --name agent-relay`, single-node. Confirmed via `kubectl cluster-info`/`get nodes` (Ready). kind's default `StorageClass` (`standard`, `rancher.io/local-path`, `WaitForFirstConsumer`) is what the Postgres PVC binds to.

**Manifests (`k8s/`, 3 files):** `secret.yaml` (one Secret holding Postgres creds + the fully-composed `RELAY_DATABASE_URL` — Kubernetes Secrets can't cross-reference keys, so it's written out in full, same flat approach as `compose.yaml`), `postgres.yaml` (PVC + Deployment + Service, one logical unit), `app.yaml` (Deployment + Service).

**Key decisions:**
- **Postgres: Deployment (not StatefulSet) + PVC**, since a single instance doesn't need StatefulSet's multi-replica ordering guarantees. Set `strategy: type: Recreate` — default `RollingUpdate` would try starting a replacement pod before killing the old one, which can't work against a `ReadWriteOnce` PVC. Data dir mounted at `subPath: pgdata` (not the PVC mount root) — local-path-provisioner volumes can have pre-existing content like `lost+found` at their root, which breaks Postgres's `initdb`.
- **App finds Postgres via the Service name as DNS hostname** — `postgres:5432`, resolved by CoreDNS — same pattern as Question 4's Compose service name, not localhost, not a pod IP. Verified directly from inside the running app process.
- **Probes:** app readinessProbe → `/ready` (real DB check), livenessProbe → `/health` (DB-independent, so a DB blip doesn't get the app container killed, only marked not-ready). Postgres: exec probe `pg_isready` for both, using the same Secret-sourced env vars via `envFrom` (real configured user/db, not hardcoded).
- **`imagePullPolicy: Never`** on the app container, since `agent-relay:local` is loaded directly into the kind node rather than pulled from a registry — makes a missing image fail with a clear scheduling error instead of a silent pull attempt.

**Image load:** rebuilt `agent-relay:local` first (Question 3's image predated Question 4's Postgres fix in `database.py`) and verified the rebuild actually picked up the fix by inspecting the running container's source. Then `kind load docker-image agent-relay:local --name agent-relay` — output confirmed the image wasn't already on the node and had to be explicitly pushed in (kind's containerd is a separate image store from the host Docker daemon).

**Apply & readiness:** `kubectl apply -f k8s/secret.yaml -f k8s/postgres.yaml -f k8s/app.yaml`. The app pod briefly `CrashLoopBackOff`'d while waiting for Postgres's pod to finish pulling `postgres:16-alpine` (a real registry pull, unlike the kind-loaded app image) — expected, since **Kubernetes Deployments have no native dependency-wait gate** the way Compose's `depends_on: condition: service_healthy` does; the app just retries via its restart policy until Postgres is reachable. `kubectl wait --for=condition=Ready` confirmed both, and `kubectl get pods` showed both **1/1 READY** (app's 5 restarts fully explained by the startup race, stable since).

**Port-forward:** `kubectl port-forward svc/agent-relay-app 8020:8000` → dashboard at **http://127.0.0.1:8020/**.

**Verification:** confirmed the app's resolved DB URL points at `postgres:5432` from inside the running pod (not a fallback). Ran the full Q2 task-exchange flow through the forwarded port — register, send, claim, complete, read-back, all correct — then cross-checked directly against in-cluster Postgres via `kubectl exec deploy/postgres -- psql`, confirming 2 agents / 1 task actually persisted there.

**Final state:** `kubectl get deploy,svc,pvc` shows both Deployments 1/1 available, both Services ClusterIP, PVC Bound 1Gi RWO. Five things are now running simultaneously: bare dev server (8000), Question 3 container (18000), Question 4 Compose stack (8010), and now the kind cluster reachable via port-forward (8020).

## 2026-09-17 — Step 8 (Question 6: CI/CD with act) — final of the six questions

**Pre-flight, tested in isolation before building the real workflow:**
1. Docker socket → `kind load docker-image`: act mounts `/var/run/docker.sock` by default; confirmed the job container's `docker ps` shows the *host's* real containers (not nested Docker-in-Docker), and `kind load docker-image` from inside the job container genuinely reached and modified the real kind cluster.
2. Reaching the kind API server: act's `--network` defaults to `host`, and since Docker runs natively inside this WSL2 VM (no Docker-Desktop VM boundary), `--network host` means the job container shares the literal WSL2 network namespace — `127.0.0.1:<kind's API port>` means the same thing inside the job container as outside it. **Decision: keep default host networking, just mount `~/.kube` read-only into the job container**, rather than the Docker-Desktop-style fix (rewrite kubeconfig to the `kind` Docker network's internal address) — that fix solves a VM-boundary problem that doesn't exist in this environment. Verified with `kubectl get pods -A` from inside the job container listing every real pod.

`kind`/`kubectl` aren't preinstalled in act's runner image — installed via curl as an early workflow step. These downloads were consistently the slowest part of every run (3–20 min) due to memory/swap pressure from the many demo services left running since Questions 3–5; stopped the no-longer-needed ones (bare dev server, standalone container, Compose stack) mid-step to relieve it. The kind cluster + port-forward stayed up throughout since Question 5's deployment is what this step builds on.

**`.github/workflows/ci.yml`** — one job, in order: checkout → compute unique tag (`short-SHA + unix-timestamp`, timestamp added specifically because this session never commits, so the SHA alone would collide across repeated `act` runs against the same uncommitted tree) → install uv → start ephemeral Postgres via plain `docker run` (not GitHub Actions' `services:` block, to avoid an untested second networking path after just validating `--network host`) → install deps → run test suite incl. Q2's integration test against real Postgres, excluding `test_sqlite_atomic_claims_distribute_without_overlap` (documented inline — that test asserts a guarantee that's specifically a SQLite `BEGIN IMMEDIATE` property, not something Postgres has without the `FOR UPDATE SKIP LOCKED` hardening flagged as out-of-scope in Step 6/7) → stop ephemeral Postgres (`if: always()`) → build image tagged `agent-relay:<tag>` → install kubectl/kind → `kind load docker-image` → `kubectl set image` + `kubectl rollout status` (waits for the rollout to actually finish, not just for the apply to return). No explicit `if:` gating needed for "don't deploy on failure" — GitHub Actions/act's default behavior already skips all steps after a failure; **verified empirically, not assumed from the YAML shape** (next section).

**Deliberate test-failure verification:** captured before-state (deployed image tag, pod name+start time, list of local `agent-relay:*` images), broke `test_full_task_exchange_sender_sees_completed_result` to assert a nonsense status string, ran the full workflow. Result: pytest correctly failed (`1 failed, 3 passed`), and the job log jumped straight from the `if: always()` Postgres-cleanup step to job failure — `Build Docker image`, `Load image into kind`, `Deploy` never ran. Confirmed on the cluster side too, not just the log: deployed image tag unchanged, same pod/same start time (never replaced), no new local Docker image was even built, and `curl /health` on the live app still returned ok — the old version kept serving, completely untouched. Reverted the deliberate breakage, confirmed no leftover trace.

**v2 heading change:** confirmed the currently-deployed app still served the old `<h1>Agent Relay</h1>` first, then changed `dashboard.html`'s heading to "Agent Relay v2" and re-ran the workflow. Result: `4 passed`, new image built/tagged, `kind load` succeeded, `kubectl rollout status` → "successfully rolled out". **Did not stop at the workflow's own success status** — restarted the port-forward (expected to die on every rollout, since it binds to a specific pod not the Service) and independently curled the live page: new image tag confirmed via `kubectl get deployment`, new pod confirmed via start time, and `curl .../ | grep h1` → `<h1>Agent Relay v2</h1>`, genuinely served by the new running pod.

**Iteration notes:** four real hiccups along the way, none needing more than one retry to resolve, none recurring after being fixed (the "stop after 2 loops on the same error" condition never triggered) — act's first-run interactive runner-image prompt (fixed permanently via `~/.config/act/actrc`), a self-inflicted observation bug where piping `act`'s output through `tail` in the background silently buffered it (fixed by redirecting to a file and `tail -f`-ing that instead), two `port-forward` restarts that silently failed to bind (fixed by always confirming PID + a real curl rather than trusting a reused `nohup` invocation), and using `act -r`/`--reuse` throughout to avoid re-paying the slow kubectl/kind download cost on every iteration.

**Final state — all six homework questions now complete:** kind cluster running the v2 image, reachable at http://127.0.0.1:8020/ via port-forward. `.github/workflows/ci.yml` is the only new file under `.github/` (the throwaway `_probe.yml` was deleted). `test_agent_relay.py` back to its Q2 state, `dashboard.html` carries the permanent v2 heading, `database.py` still has the Q4 Postgres fix. Next: submission prep (reflection answer, learning-in-public, FAQ, homework_url) — not started.

## 2026-09-17 — Correction to Step 8's networking claim (found while investigating C: disk space)

Step 8's note above ("Docker runs natively inside this WSL2 VM (no Docker-Desktop VM boundary)") was **wrong**. A disk-space investigation this same day (`docker context ls`, `docker info`, `wsl.exe -l -v`) confirmed this machine runs Docker Desktop with WSL2 integration: `docker info` reports `Operating System: Docker Desktop` / `Name: docker-desktop`, and `wsl.exe -l -v` lists a separate `docker-desktop` distro alongside `Ubuntu`. There genuinely is a VM boundary — the earlier claim's premise doesn't hold.

The Q6 fix itself (mount `~/.kube` read-only, keep default host networking) still worked and is still correct — `127.0.0.1:<kind's API port>` really does resolve the same way inside act's job container as outside it — but the *reason* is Docker Desktop's own WSL2-integration networking (it proxies/forwards ports across the VM boundary transparently), not the absence of a VM boundary. Leaving the original note above unedited (preserving what was actually verified and reasoned at the time) and recording the correction here instead.

## 2026-09-17 — C: drive space investigation (not part of hw03, general machine hygiene)

Prompted by the Phase 2 teardown's ~10.9GB Docker reclaim not showing up on `C:\` or in `df -h /` inside WSL. Diagnostics (`docker context ls`, `docker info`, `df -h /` + `df -h /var/lib/docker`, `docker system df -v`, `wsl.exe -l -v`, a search for `*.vhdx` files under `/mnt/c/Users`, `df -h /mnt/c`) found the actual cause:

- Docker Desktop's WSL2 integration stores all real container/image/volume data inside a separate `docker-desktop-data`-equivalent distro, not inside the Ubuntu distro's own filesystem — confirmed by `/var/lib/docker` not existing at all from Ubuntu's shell, and `df -h /` showing an unrelated 1TB volume (`/dev/sdd`) with 943G free throughout. This is why reclaiming Docker space never showed up in `df -h /`: that data was never counted there.
- The actual data lives in `C:\Users\HP\AppData\Local\Docker\wsl\disk\docker_data.vhdx` — found to be **18.28GB on disk** even though `docker system df -v` shows the daemon now holds ~0 images/containers/build-cache and only the pre-existing 48MB CLIO volume. This is the real cause: `docker_data.vhdx` is a dynamically-expanding virtual disk. Deleting data inside it frees logical space (why Docker's own accounting shows ~0), but the file's physical size on the Windows NTFS filesystem doesn't shrink automatically — it stays at its high-water mark until manually compacted.
- `df -h /mnt/c` confirmed the actual squeeze: 195G total, 189G used, only 6.1G free (97% full). Compacting `docker_data.vhdx` down toward its real ~50MB logical content would recover most of that missing ~18GB.

**Not fixed this session** — compaction requires shutting down WSL (`wsl --shutdown`) and either the Docker Desktop UI's own disk-cleanup option or `diskpart`/`Optimize-VHD` from Windows PowerShell, none of which this session's tools (device bridge, WSL shell) can safely do without killing their own connection mid-operation. Left for Sam to run directly on the Windows side; full report and exact commands given in chat, not filed here since no code/config in either repo needs to change.
