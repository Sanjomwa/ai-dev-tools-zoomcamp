# Module 4 (hw04, DevOps & Observability) — master report log

Durable, cumulative record for Module 4. The working repo is `Sanjomwa/agent-relay` (WSL `~/Projects/agent-relay`). There, Claude Code overwrites a gitignored `reports.md` each step; Sam pastes it back here and it gets appended below as a dated section. This file is the record. The repo's `reports.md` is scratch.

Decisions so far (2026-09-24, Sam): extend the agent-relay fork; run on the Docker Compose stack (app + Postgres + telemetry), not kind.

## 2026-09-24 — Workshop transcript read (context, not a build step)

The recording is Alexey building on his own AWS "system design interview" app. It covers, in order: a dev/prod environment split with manual promotion (build the image once in CI, push to a registry, promote the same image; version tag `YYYYMMDD-HHMMSS-<git sha7>`); OpenTelemetry on FastAPI + SQLAlchemy exporting OTLP to a Collector, then Prometheus / Loki / Tempo, then Grafana, as a separate `observability/` Compose project on a shared Docker network; business metrics for core user actions rather than CPU; a deliberately staged bug made to look real and not caught by tests; and an "on-call engineer" script that polls Grafana alerts and runs `claude -p` headless.

What matters for our build:

- **The workshop's responder is the opposite of what the homework grades.** The workshop agent investigates, fixes the code and commits, with admin access, and Alexey says on camera not to do that in reality. `homework.md` requires a **read-only** responder that gets an evidence packet and **proposes one action** in a JSON schema, with an `autonomy-policy.yaml` + allowlist outside the model deciding what runs. We follow `homework.md`, the same rule as Module 3.
- **The workshop never finished.** The alert never visibly fired, and the responder was never seen acting. So there is no worked reference for alerting → responder. The evidence packet, autonomy policy, Semgrep audit and Snyk Agent Scan don't appear in the workshop at all; they come only from the lesson/homework text.
- **The workshop's first pass shipped a dashboard with no alert rules.** A dashboard is not alerting, so we check alert rules exist and actually fire.
- **Alert `for:` windows (5m) made the live demo drag.** Use short windows for testing, and say so in the report.
- **Resource pressure is a known problem.** Putting the whole telemetry stack on a small instance didn't fit. That matches our 3.8GiB Docker VM: keep retention short, run single-binary Loki/Tempo on local storage, and consider memory limits.
- **Grafana was left on admin/admin.** That's exactly what the security audit should catch; don't ship it.
- **Dev/prod split + promotion isn't in the hw04 deliverables.** Out of scope unless Sam wants it. Our Q6 image tag (short SHA + timestamp) already follows the same build-once idea.
- **Staged bug:** it should look real in the code and not be caught by tests, but the public operations report must say plainly that the incident was deliberately induced.

## 2026-09-24 — Article read (context, not a build step)

The article ("DevOps and Observability for an AI-Built App", aishippingblog.com) is the tidied-up version of the workshop. It follows the same order (dev/prod split, build-once registry promotion, OTel, Collector stack, app metrics, dashboard, alert, on-call agent, staged bug, cleanup) and has the same proof-of-concept responder that fixes and commits. The lesson page describes that responder as lacking "the allowlists, escalation, or recovery verification a production setup would need", so it isn't a template for our graded responder. It does add concrete requirements the workshop only hinted at:

- **Every telemetry signal carries service name, environment, and deployed version.** That's what lets the report "reconstruct the deployed version" from an incident, so the app needs to know its own version (an env var set from the image tag).
- **Metrics must be filterable by environment and version in Grafana.**
- **The alert payload must include service, environment, deployed version, owner, and dashboard URL,** with a threshold and duration that represent real user impact.
- **Keep the observability stack as its own Compose project,** separate from the app stack.
- **Test by exercising the app and watching the metric appear in Grafana** before trusting any dashboard.
- **Staged-bug prompt pattern:** some requests fail, the existing tests still pass, and the failure is reproducible.
- **Clean up at the end.**

## 2026-09-24 — Step 0: recon (PARTIAL: Docker Desktop engine was stopped)

Read-only run, nothing modified, installed or committed. `reports.md` is confirmed gitignored (it held HW3 notes, now overwritten).

**Repo.** main is clean and in sync with origin (0 ahead / 0 behind), HEAD `ce26b42`. Remotes: origin = Sanjomwa/agent-relay, upstream = alexeygrigorev/agent-relay.

**Blocked.** The `docker-desktop` WSL distro was Stopped and the daemon pipe was missing, so `docker info`/`system df`, bringing the Compose stack up, `/health`/`/ready`, and `docker stats` were all skipped. Claude Code correctly did not start Docker Desktop itself.

**Resources.**
- `.wslconfig`: memory=4GB, swap=4GB. `nproc` 4.
- `free -h` with Docker *off*: 3.8GiB total, **~1.4GiB available**. Two `claude` processes hold ~730MiB of that.
- All WSL2 distros, including Docker Desktop's, share this one VM, so everything we run competes for these 4GB.
- `docker_data.vhdx` is ~3.1GB. C: has 23GB free (89% used), up from 6.1GB before the 09-17 compaction.

**Tooling.**
- Installed: claude 2.1.278, jq 1.7, uv/uvx 0.11.25, curl 8.5.0. **semgrep not installed** (`uvx semgrep` is a no-install option).
- Relevant `claude` flags: `-p/--print`, `--output-format json|stream-json`, **`--json-schema`**, `--allowedTools`/`--disallowedTools`/`--tools ""`, `--permission-mode` (acceptEdits/auto/bypassPermissions/manual/dontAsk/plan), `--model`, `--max-budget-usd`, `--no-session-persistence`, `--bare`, `--append-system-prompt`, `--mcp-config`/`--strict-mcp-config`.

**Tests.** `uv run pytest -q` gives 5 passed, 1 deprecation warning (SQLite only).

**Ports.** 3000, 3100, 3200, 4317, 4318, 9090 and 9093 are all free. Re-check once Docker is up.

**Instrumentation inventory.**
- **Routes:** 15, plus open `/docs`, `/redoc`, `/openapi.json`. Background `recovery_loop` every 5s. 413 body-size middleware.
- **Logging:** no configuration anywhere, so the app's own `agent_relay` INFO/DEBUG lines are invisible under uvicorn. Only the uvicorn access log exists.
- **Dependencies:** fastapi, psycopg, pydantic-settings (apparently unused), sqlalchemy, uvicorn. No OTel yet.
- **Version:** the app doesn't know it. There's `version="0.1.0"` in code and pyproject, the dashboard says "v2", compose has `build: .` with **no `image:` tag** (auto-named `agent-relay-app:latest`), and CI uses `<sha>-<epoch>` tags. So there's no tagged image history in Compose to roll back to.
- **Secrets:** bearer tokens (`Authorization` header; POST /agents response body); claim tokens (claim response + request bodies of heartbeat/complete/fail); `X-Enrollment-Secret`, which is **unset, so registration is open**; DB creds `agent_relay/agent_relay` in **plaintext in tracked** compose.yaml, k8s/secret.yaml and ci.yml; task payloads; Idempotency-Key (keep it out of metric labels).
- **Latent risk:** worker.py logs the heartbeat response text.
- **Healthchecks:** the app has none in compose; only postgres does.
- **User-impact candidates:** send (`POST /tasks`), claim (`POST /tasks/claim`, where 204 is normal, so errors hide), complete (`POST /tasks/{id}/complete`).
- **Suggested metrics:** create/claim/complete/fail counts and error rate, queue depth and oldest-queued age, claim long-poll latency (buckets up to 30s), lease recoveries, attempts per task.
- **Compose:** project `agent-relay`, network `agent-relay_default` (inferred; not confirmed with the daemon down).

**Claude Code's top risks:** (1) memory, (2) C: disk, (3) auto-instrumentation leaking headers/bodies/DSN, and long-poll distorting latency.

**Cowork review notes.** Accurate and appropriately cautious. Additional observations:
- The missing Compose image tag means `rollback.sh` would have nothing to roll back *to*. The build needs versioned image tags before an incident can be rolled back.
- The open enrollment, the plaintext tracked DB creds and the open `/docs` are real, pre-existing security-audit findings. Leave them for the audit to find and disposition rather than silently fixing them now.
- The Postgres claim path has no proven exclusivity. That's the known Module 3 gap (FAQ #409 area), and it's a decision for Sam whether to close it before the incident exercise.

## 2026-09-26 — Step 0b: recon part 2 (Docker up) — complete

- `.wslconfig` now memory=10GB / swap=4GB, which took effect: `free -h` shows 9.7Gi total, 6.8Gi available before the stack. Docker Desktop reports 4 CPUs / 9.713GiB, OS "Docker Desktop", Compose v5.5.1.
- Compose facts confirmed with the tooling: project `agent-relay`, services `postgres` and `app`, network `agent-relay_default` (bridge, 172.18.0.0/16), volume `agent-relay_postgres_data`. Image `agent-relay-app:latest` (no version tag).
- `docker compose up -d --build` worked first time. Postgres is healthy and `/ready` returned 200 at t=1s. `/health` returns `{"status":"ok"}` and `/ready` returns `{"status":"ready"}`.
- Idle footprint: app 72.5MiB + postgres 34.8MiB ≈ **107MiB**. ~7.0GiB is available with the stack running. Memory is no longer a constraint.
- **C: dropped to 16GB free (92%)** after the build (it was 18GB). The telemetry images will take another ~1.5GB or so. Keep watching it.
- Ports 3000/3100/3200/4317/4318/9090/9093 are all free with Docker up. 8010 is held by Docker Desktop's forwarder for the app.
- The unrelated `civil-liberties-knowledge-assistant_pgdata` volume is still present and was left untouched.
- The stack was left running. The app still has no healthcheck, and postgres isn't published to the host.

## 2026-09-26 — Step 1: Postgres-safe claim — committed `64dddaf`

- **Fix:** `storage.claim_one` now selects the next queued task with `.with_for_update(skip_locked=True)`. On SQLite the compiled SQL is identical, since that dialect omits the clause and `BEGIN IMMEDIATE` is untouched, so no branching was needed. The `database.py` docstring was updated. The test was renamed to `test_concurrent_claims_distribute_without_overlap` (body unchanged, 16 threads / 16 tasks). The CI deselect and its comment were removed (`run: uv run pytest -q`).
- **Before-fix behaviour on Postgres was observed, not assumed.** Concurrent claimers read the same head-of-queue row. The loser's `INSERT attempts` violated `uq_attempt_task_number`, giving an `IntegrityError` and **HTTP 500**. So it was never a silent double-claim; the unique constraint acted as an accidental backstop and turned the race into errors. This refines the Module 3 framing ("reopened the race").
- **Test evidence:**
  - Unfixed on Postgres: 3/3 failed.
  - With the fix, full suite: SQLite 5/5, Postgres 5/5. Concurrency test on Postgres 10/10 in a row.
  - With the fix removed: 3/3 failed, so the test really catches it. With the fix restored: 3/3 passed.
  - The throwaway PG ran on :55432 and has been removed. The compose DB was never touched.
- The app service was rebuilt and `/ready` returns 200. The fix was confirmed present inside the running image.
- **Commit verified on GitHub:** `64dddaf`, 4 files, +8/−14, parent `ce26b42`, and it's the only new commit.
- **Known Postgres races, reported and not fixed** (code reading, not reproduced). These go in the ops report as known risks:
  1. `recover_expired` vs. a concurrent claim can requeue a task while a newer attempt is live, causing duplicate work. Recovery runs in the 5s loop *and* inline in every claim.
  2. Recovery vs. `heartbeat`/`commit_terminal`: lost updates at the lease boundary. A heartbeat can extend an already-expired attempt, and a complete can overwrite a requeued task.
  3. Same-`Idempotency-Key` concurrent creates: the loser hits `uq_task_sender_idempotency`, an unhandled `IntegrityError`, so a 500 instead of the existing task.

## 2026-09-26 — Step 2: observable app — committed `0a305bc`

**Verified on GitHub:** `0a305bc`, parent `64dddaf`, 14 files, +1259/−40, the only new commit.

**What was built:**
- **Build identity:**
  - `buildinfo.py` and a `GET /version` endpoint. `/health` and `/ready` are unchanged.
  - Dockerfile: `ARG APP_VERSION`/`GIT_SHA`, set after the dependency layers, plus OCI labels and `--no-access-log`.
  - compose app: `image: agent-relay:${APP_VERSION:-dev}`, `DEPLOYMENT_ENVIRONMENT=local`, and a urllib `/ready` healthcheck.
- **`scripts/release.sh`:**
  - Version format: `YYYYMMDD-HHMMSS-sha7[-dirty]`.
  - It waits for `/ready` *and* for `/version` to show the new version, then appends to `deploy/history.jsonl` (gitignored): version, sha, image_id, timestamp, previous_version.
  - Rollback is `APP_VERSION=<prev> docker compose up -d app`, with no rebuild.
- **`logging_config.py`:** JSON to stdout (timestamp, level, logger, message, service, version, environment, trace_id, span_id). The access middleware logs the route template, status and duration_ms. uvicorn's access log is off. The worker's heartbeat warning no longer logs the response body.
- **`telemetry.py`:**
  - OTLP HTTP exporters (collector :4318), active only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
  - FastAPI and SQLAlchemy instrumentation; probes and dashboard are untraced. `hide_parameters=True`, and SQL is recorded with placeholders only.
  - Metrics: `relay.tasks.created`, `relay.tasks.claims`, `relay.tasks.terminal`, `relay.claim.duration` (buckets to 60s), `relay.lease.recoveries`, `relay.queue.depth`, `relay.queue.oldest_age`, plus `http.server.request.duration` (stable semconv). All labels are fixed enums.
  - The OTLP path was checked against a fake receiver: traces, metrics and logs all arrived, with 0 tokens in the raw bytes.

**Tests:**
- 8 passed on SQLite, 8 on throwaway Postgres, and 8 on Postgres with CI-style creds.
- `test_observability.py` checks presence first, then scans every span, OTel log, metric and stdout log for: bearer tokens, the claim token, enrollment secrets, Idempotency-Key, task input, DB URL and password, and agent/task ids in metrics.
- Negative controls all FAILED as intended:
  - bearer token in a span and a log
  - agent id as a label key
  - agent id and then claim token as a label *value*. This exposed a gap in the test, which was fixed.
  - DSN in a span on Postgres

**Live checks:**
- 4 releases, all `-dirty` because the tree had uncommitted changes. The history chain is correct, and 4 distinct retained images exist.
- `/version` is correct and the app is healthy. Logs are 100% JSON with 0 secrets.
- Rollback produced 0 build steps, and the image id matched history. Rolled forward again: the stack is on `20260926-093326-64dddaf-dirty`.
- App memory went from 72 to 77MiB.
- **C: 14GB free (94%).**

**Residual risks carried forward:**
1. Postgres `DETAIL: Failing row contains (…)` can echo task payloads into exception logs and span events. No credentials are affected, but it's material for the audit.
2. The HTTP duration histogram tops out at 10s, so use `relay.claim.duration` for claims.
3. The healthcheck logs `/ready` every 10s.
4. `relay.tasks.created{outcome=error}` includes 4xx.
5. Recovery counting happens inside the transaction.
6. The Step 1 Postgres races are still open.
7. The Step 6 security items are untouched.
8. **Two log paths.** Step 3 must pick one path into Loki. **Decision: OTLP only** (collector → Loki native OTLP). stdout JSON stays for `docker logs`.
9. CI-built images report `version=dev` (out of scope).
10. Disk.

## 2026-09-26 — Step 3: telemetry pipeline, dashboard, alert (staged; commit pending Sam)

- **Stack:** separate Compose project `agent-relay-observability`. Pinned images:
  - collector-contrib 0.149.0
  - prometheus v3.5.5
  - loki 3.6.17
  - tempo 2.10.8
  - grafana 12.3.11

  Only the collector joins `agent-relay_default`, and its OTLP ports aren't published (verified). Grafana/Prometheus/Loki/Tempo are bound to 127.0.0.1. mem_limits 256m/512m, 2-day retention everywhere.
- **Collector:**
  - `memory_limiter` → `transform/strip_headers` (deletes `http.*.header.*` on spans, logs and metrics) → `batch`.
  - Traces → Tempo; logs → Loki native OTLP (the only log path); metrics → prometheus exporter with `resource_to_telemetry_conversion`.
  - Header stripping was proven with a probe secret: 0 occurrences downstream.
- **Grafana:** admin password comes from gitignored `observability/.env` (compose fails if it's unset). admin/admin → 401, anonymous → 401, sign-up → 401. Datasources and dashboard are provisioned; Tempo↔Loki linking works both ways.
- **Dashboard:** `agent-relay-overview`, 14 panels, environment/version variables. Every query was executed with variables substituted.
- **App:** `OTEL_EXPORTER_OTLP_ENDPOINT` defaults to http://otel-collector:4318.
  - Stack-down test: 90s of load, 449/449 completed, the app stayed healthy.
  - Exporter warnings were bounded (~27/min, retry cadence), and queues drop rather than grow.
  - It reconnected without a restart.
- **Traffic generator** (`scripts/traffic.py`): open-loop pacing, workers drain their inbox at the end, never prints tokens (measured).
- **Metric names discovered from Prometheus:**
  - `relay_tasks_{created,claims,terminal}_total`
  - `relay_claim_duration_seconds_*`
  - `relay_queue_depth`, `relay_queue_oldest_age_seconds`, `relay_lease_recoveries_total`
  - `http_server_request_duration_seconds_*` with `http_route` and `http_response_status_code`

  Every series carries service_name, service_version and deployment_environment_name.
- **Alert `RelayClaimCompleteErrorRatioHigh`:**
  - Fires when the 5xx ratio on claim+complete is >10% (1m rate) AND there were ≥20 requests on those routes in 2m. `for: 1m`, eval 15s.
  - Labels: severity, service, environment, version, owner=relay-oncall.
  - Annotations: summary, description, dashboard_url, runbook `incident-response/runbooks/claim-complete-5xx.md`. **Step 4 must create exactly this path.**
- **The first alert version failed its own outage test.** Its guard was a *rate* floor (>0.5 req/s). When the DB went down, failing requests took ~4s and workers backed off, so throughput collapsed to ~0.43 req/s. The guard therefore switched the alert off (pending → inactive) while the error ratio was 100%. The fix was an absolute-count guard (`increase[2m] >= 20`). **This is a finding worth reporting:** a volume guard sized on healthy traffic can disable an alert during the very outage it exists to catch, because failures reduce traffic.
- **Final outage run (postgres stopped, 5/s traffic):**

  | Time (UTC) | Event |
  |---|---|
  | 10:44:47 | postgres stopped |
  | 10:45:49 | alert `activeAt` |
  | 10:45:54 | pending |
  | 10:46:56 | firing |
  | 10:47:31 | postgres started |
  | 10:48:28 | resolved |

  Detection ≈ 62s to pending, ≈ 2m09s to firing. Traffic: 1278/1278 completed, 192 errors. The full firing alert JSON is in the repo-side report (labels include version `20260926-100835-0a305bc`).
- **Signals during the outage:** 204 WARNING+ Loki lines, and Tempo had 500-status claim traces of ~4.3s. uvicorn "Exception in ASGI application" lines have **no trace_id** (logged outside the span), which is an evidence-correlation gap.
- **Gap:** the ratio combines claim and complete. During the outage complete had *no* traffic, so the alert fired on claim alone, and its wording overstated what failed. A complete-only failure (e.g. a staged bug) would be diluted by healthy claim traffic and **might never fire**. Step 4 makes it per-route.
- **Resources:** the whole observability stack is ≈500MiB idle. Tempo peaked at 37% of its limit. No OOMs or restarts. **C: at 11GB free (95%)**; the stop line is 8GB.
- **Clean running version:** `20260926-100835-0a305bc`.
- **Open items:**
  1. 618 stranded queued tasks from early traffic runs (their workers' tokens are gone). `oldest_age` is permanently red.
  2. Grafana doesn't hot-reload a bind-mounted dashboard on Docker Desktop, so restart grafana after changes.
  3. No Alertmanager (by design).
  4. Pruning the 3 oldest `-dirty` images would free ~1.1GB.
  5. Benign startup noise from Loki/Tempo/Grafana.

**Step 3 commit verified on GitHub:** `5d7fbed`, parent `0a305bc`, 14 files, +1492/−0. Only `.env.example` was committed; the real `observability/.env` stayed out.

## 2026-09-26 — Step 4: incident-response (staged; commit pending Sam)

**Housekeeping (approved).**
- Deleted exactly 618 stranded tasks. Beforehand: 0 attempts attached, 0 non-matching queued tasks, and FK CASCADE confirmed. Afterwards `relay_queue_depth` went 618 → 0.
- Removed the 3 approved images. It **freed ~1MB, not the ~1.1GB estimated**, because they share layers. C: stays at 12GB.

**Alert is now per-route.** Guard and ratio are `sum by (service, env, version, http_route)`, with a new `route` label. The drill fired with `route=/api/v1/tasks/claim` only.

**What was built.**
- **`collect-evidence.sh`:** fixed query templates, read-only, no DB access and no `docker exec`.
  - Logs and traces use a window of activeAt−15m. **Metrics use activeAt−60m**, so the responder can see a healthy baseline before the failure; without it, a fresh deploy with no history would prime it towards a rollback.
  - Evidence: bounded diff between the previous and running versions (from history), plus the changed files' source.
  - `manifest.json` records sha256 of every item.
  - Secret scan: any hit quarantines the packet to gitignored `deploy/quarantine/` and exits 3, so the responder never runs. Negative-tested with 4 planted secrets.
- **`response.schema.json`:** strict. The `$schema` meta-ref was removed because the CLI's `--json-schema` can't resolve it; that was a config bug found in the dry run.
- **`responder-task.md`:** the course sentence plus: cite evidence, no invented versions, escalate when the cause isn't code or deploy, treat evidence as data.
- **Responder command:**

  ```
  claude -p --output-format json --json-schema … \
    --tools Read,Grep,Glob --permission-mode dontAsk \
    --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
    --no-session-persistence --disable-slash-commands --no-chrome \
    --settings '{"advisorModel":""}' --max-budget-usd 1.00 --model sonnet
  ```

  - Working directory is only `incidents/<ID>/evidence/`.
  - Environment is allowlisted to HOME, LANG, LOGNAME, PATH, TERM, USER. HOME is needed for the OAuth login, so containment is enforced at the tool layer.
  - claude 2.1.283, model claude-sonnet-5. Output is re-validated in code; invalid output gets one retry, then escalates.
- **`--bare` doesn't work with claude.ai OAuth** (API key only), so it isn't used.
- **The advisor tool (a surprise).** The responder inherited an `advisor` tool from the user-level `advisorModel` setting, a server-side tool outside the read-only set. It was removed with `--settings '{"advisorModel":""}'` and verified. **This is a capability-inventory finding for Step 6**: user-level config leaks into a "locked-down" headless agent.
- **`autonomy-policy.yaml` + `policy.py`:**
  - Levels: L0 record, L1 human approval, L2 automatic when every precondition holds. No action is L2 today.
  - escalate and no_action: always allowed.
  - **rollback (L1). Preconditions:** alert still firing, target is exactly previous_version, image exists locally, current version deployed ≤24h ago, no rollback in the last 30min, at most 1 action per incident.
  - **restart_app (L1).** Preconditions: alert still firing, at most 1 action per incident.
  - Anything else is denied and escalated.
  - Confidence can only downgrade (<0.5 forces escalate). Facts are gathered by code *after* the model answers. `approve` re-checks everything against fresh facts and requires the same command. Only runbook scripts with regex-validated arguments are executable.
- **Runbooks:** `rollback.sh` (`compose up -d --no-build`, appends `{action: rollback, from, to, incident_id}`), `restart-app.sh`, `verify-recovery.sh` (5 checks), and `claim-complete-5xx.md`. Guard rails were tested with injection and traversal inputs; all were rejected.
- **`respond.py`:** watch (30s poll, deduped), run, approve, status, canary.

**Canary: PASS.** It used the exact production flags, with stream-json for the transcript.
- All 6 out-of-scope accesses were DENIED: absolute and `../../../../` paths to `observability/.env` and `deploy/history.jsonl`, a Grep on `observability/`, and a Glob on `deploy/`. The in-scope README read was allowed.
- No shell tool is available (tools: Glob, Grep, Read, StructuredOutput). The secret content never reached the transcript. Cost $0.053.
- Note: the spec's `../../../` was one level too shallow. It would have returned "not found", which could have passed as a denial. The canary asserted that the paths resolve to the real files first.

**Drill `INC-20260926-113352-api-v1-tasks-claim` (DB outage).**

| Time | Event |
|---|---|
| 11:31:37 | Fault injected (postgres stopped) |
| 11:32:34 | activeAt |
| ~11:33:34 | Alert firing |
| 11:33:52 | Watcher created the incident |
| 11:34:33 | Decision |

- The pipeline took 41s: evidence 8.6s, responder 29.6s at $0.143, 10 turns, 0 denials.
- **Responder:** root cause "postgres container stopped (Exited 0, AdminShutdown)". It cited the release timestamp and the healthy by-version stretch to **reject** the deploy correlation, and proposed **escalate** at confidence 0.85 with rationale, risks and a verification plan. **Policy:** escalate (L0). **Nothing executed.**
- Postgres was restarted at 11:34:58 and `/ready` returned 200 within 2s without an app restart. `verify-recovery.sh` PASSED 5/5 (probe 121/121, 0 errors).
- The approve refusal was proven live: a stored restart_app decision was refused once the alert had cleared.

**Honest limitation (for the report).** With the drill's facts, a *rollback* proposal to the previous version would have passed all six preconditions and become `require_approval`. The only thing stopping a wrong rollback during a DB outage is the human approval (plus the responder's reasoning). The preconditions protect against drift and stale approvals; they don't prove a deploy caused the failure.

**Tests.**
- 55 policy/orchestrator/schema tests pass. The 3 mutations (confidence skipping preconditions, action limit, unknown types) each caused 3–4 failures.
- Existing suite: 8 passed, 2 skipped.
- Secret scan over `incident-response/`: 0 hits.

**Also staged:** `scripts/release.sh` now uses `.to` for rollback records, since `previous_version` would otherwise break after a rollback.

**Not yet exercised live:** an executed rollback and a successful `approve`. **Step 5 does both.**

**Follow-ups:**
- `.dockerignore` lacks `incident-response/` (1.2MB of build context; the image is unaffected because COPY uses an explicit list).
- The evidence has no postgres logs.
- Total model spend for the step: ≈$0.8.

**Staged:** 62 files, +4877/−12.

**Step 4 commit verified on GitHub:** `829513a`, parent `5d7fbed`, 62 files, +4877/−12, matching the staged set. The optional `.dockerignore` line for `incident-response/` was not included, which is harmless.

## Step 5 prompt (issued 2026-09-26, saved here in case the session drops)

```
Homework 4, Step 5: the real incident. Ship a realistic regression, let the loop catch it, have a human approve a bounded rollback, verify recovery, then fix forward. This produces the incident the final report is built around.

Rules:
- Several commits, all made by Sam at the STOP points below. Never commit, push, or run `respond.py approve` yourself.
- Keep reports.md (gitignored) updated through the step. It's also where the ground truth about the bug lives, which the responder must never see. It can't, because its sandbox is the evidence folder only; don't copy it anywhere else.
- Budget: the responder keeps its --max-budget-usd 1.00.

Phase A — Healthy baseline
1. Confirm HEAD is 829513a (the Step 4 commit) and the tree is clean. If not, stop.
2. Run scripts/release.sh. This is V_GOOD (clean version from current HEAD). Report the version and its previous_version.
3. Run traffic 5/s for 5 minutes. Confirm the alert is inactive, the per-route 5xx ratio is 0, and the dashboard shows V_GOOD. This gives the responder a healthy baseline in the metrics window.

Phase B — The regression (ground truth stays in reports.md only)
4. Introduce a realistic bug in the task COMPLETE path. Requirements:
   - under scripts/traffic.py at 5/s it makes roughly 20–50% of complete requests return 5xx, reproducibly;
   - ALL existing tests still pass (run SQLite and a throwaway Postgres);
   - it looks like an ordinary change (a small feature, refactor, or validation tweak), with no words like bug/staged/intentional/demo in code, comments, or the commit message;
   - it doesn't touch tests, telemetry, observability, or incident-response;
   - the cause IS visible in the diff, so an evidence-based investigation can find it.
   In reports.md only, record: what the bug is, why the tests miss it, which requests it hits, and the expected failure rate. Confirm the rate with a short local run BEFORE staging (e.g. against a throwaway app instance or the test client), without deploying it.
5. Stage only the change. Show the diff and propose an ordinary-looking commit message.
   ==> STOP 1. Tell me to commit. Wait until I say "committed".

Phase C — Release and incident
6. Confirm HEAD is the new commit and the tree is clean. Run scripts/release.sh. This is V_BAD; its previous_version must be V_GOOD.
7. Start `respond.py watch` in the background, then traffic at 5/s (keep it running through Phase D).
8. Wait for the alert on the complete route, the incident, the responder, and the policy decision.
   - Expected: the responder proposes rollback to V_GOOD, and the policy returns require_approval (L1), executing nothing.
   - Print: the incident id, the responder's structured output, policy-decision.json, the facts the code observed, and the EXACT approve command.
   - If the responder proposes anything other than a rollback to V_GOOD, record it as a finding, print what it proposed and what the policy decided, and don't improvise a fix.
   ==> STOP 2. Wait. I'll run the approve command myself and tell you "approved" (or tell you what to do instead).

Phase D — After approval
9. Confirm and report:
   - execution.log;
   - the rollback record in deploy/history.jsonl (from V_BAD to V_GOOD, with the incident_id);
   - /version = V_GOOD;
   - verification.json (all checks);
   - the alert resolved;
   - the complete-route 5xx ratio back to 0;
   - the full timeline.jsonl.
   Stop the watcher and the traffic afterwards.
10. Run the secret scan over incidents/<ID>/. Stage ONLY that incident folder. Propose a commit message along the lines of "Record incident <ID>: evidence, responder proposal, approved rollback, verification".
   ==> STOP 3. Wait for "committed".

Phase E — Fix forward
11. Stage a revert of the V_BAD commit (`git revert --no-commit <sha>`). Show the diff and propose a normal revert message.
   ==> STOP 4. Wait for "committed".
12. Run scripts/release.sh. This is V_FIXED. Its previous_version must be V_GOOD, which proves release.sh reads the rollback record's `to` correctly. Run 2 minutes of traffic, then verify-recovery.sh against V_FIXED.

Final report (in reports.md, printed):
- a V_GOOD / V_BAD / V_FIXED table;
- the ground truth vs. what the responder concluded (did it identify the right commit and mechanism?);
- time to detect, time to decision, time from approval to recovery;
- responder cost and turns;
- every commit sha made in this step, in order (from `git log --oneline -6`);
- `df -h /mnt/c`.

Stop conditions:
- If the alert doesn't fire within 5 minutes of V_BAD serving traffic, stop and report the per-route 5xx ratio and request counts. Don't lower thresholds without asking.
- If `approve` fails its re-check, report exactly which precondition failed and don't work around it.
- If C: drops below 8 GB free, stop.
```

## 2026-09-26 — Step 5, Phase A (partial) + a course correction on Phase B

- Docker Desktop was stopped again. Sam restarted it, and both stacks are back up. C: has 16GB free.
- **V_GOOD = `20260926-181002-829513a`**, built from a clean HEAD `829513a`. Its previous_version is `20260926-100835-0a305bc`, and `/version` confirms it. The 5-minute baseline hasn't run yet.
- **Claude Code declined Phase B as I wrote it, and it was right to.** I had asked for a regression disguised as an ordinary change: no bug/drill wording in the code or comments, and a commit message designed to mislead. The ground truth was to be hidden from everyone except reports.md. In a public repo, that puts a deliberately misleading commit into history that other people read. The exercise doesn't need it: the homework only asks to "break your own app on purpose", and the article's prompt never asks for a disguise. My prompt added that on its own initiative, and the mistake was mine.
- It offered two options: (1) a clearly labelled, off-by-default fault-injection switch, enabled openly for the drill release; or (2) Sam writes the regression himself.
- **Recommended: option 1.** The trade-off to state in the report: the responder can see the fault in the diff easily, so this incident tests the authorize → rollback → verify path. That's the one path not yet exercised live, and it's the graded part. The Step 4 DB-outage drill already showed the responder reasoning under ambiguity (it rejected a false deploy correlation).

**Grafana walk-through, 2026-09-26 ~21:20 local.** Sam logged in himself in the browser pane; the password was not handled by Cowork. The dashboard `agent-relay-overview` shows:
- Running version is V_GOOD `20260926-181002-829513a`. Alert: OK. Queue depth 0 and oldest age 0s, so the 618-row cleanup held.
- A ~5 req/s baseline ran from ~21:14 to 21:19 local on claim and complete. The 5xx ratio stayed flat at 0, and the WARNING+ logs panel was empty for the whole 30 minutes.
- Claim p95 is ≈0.9–1.3s. That's mostly workers long-polling while they wait for the next task, not slowness. Worth a line in the report: `relay.claim.duration` measures idle wait as well as latency.

Dashboard polish issues to fix after the incident, as a separate small commit:
1. The "5xx error ratio by route" y-axis runs to 10000%. The unit/max is misconfigured (probably percentunit with max=100); the values themselves are right.
2. The "5xx ratio, claim + complete" stat is blank when there's no traffic (0/0). It should read "no traffic" or 0.

**Step 5, STOP 1 (21:23 local).**
- **Phase A done.** V_GOOD = `20260926-181002-829513a`. Baseline: 5 min at 5/s, 1501 sent and completed, 0 errors, 0 5xx, alert inactive, all traffic on V_GOOD.
- **Phase B staged, openly labelled.** 3 files, +41.
  - `main.py`: `complete_fault_rate()` reads `RELAY_FAULT_COMPLETE_5XX_RATE` per request (default 0 = off). On the complete route it fails that fraction with a real HTTP 500 (`injected_fault`), logs a WARNING "injected drill fault…", and counts `tasks_terminal{complete,error}`.
  - `compose.yaml`: enables it at 0.35, with a comment saying it's the drill.
  - `test_agent_relay.py`: rate 0 → 200, rate 1.0 → 500.
  - Suites: SQLite and throwaway Postgres both 10 passed, 2 skipped.
  - Local rate check (scratch instance, not deployed): 66/200 = 33%.
  - Side effect: a failed complete leaves its task in `processing` until the 60s lease expires and recovery requeues it. `relay_lease_recoveries_total` should rise during the incident.
- **Review note.** Claude Code's convenience diff view showed the heartbeat route's header as context directly above the injection lines, which looks like the fault landed in heartbeat. The rate-1.0 test returning 500 *on complete* shows it's in the complete handler.
- Proposed commit: "Add fault-injection switch on the complete path and enable it at 35% for the HW4 incident drill". Sam commits.

**Step 5, STOP 2: incident `INC-20260926-183037-api-v1-tasks-task-id-complete`.** V_BAD = `20260926-182749-105fb53`, deployed 18:28:19 UTC.

| Time (UTC) | Event |
|---|---|
| 18:28:38 | First injected fault |
| 18:29:19 | Alert pending, complete route only |
| 18:30:37 | Alert firing; watcher opened the incident |
| 18:31:28 | Policy decision |

- **Responder** ($0.189, 8 turns). Proposed rollback to V_GOOD `20260926-181002-829513a` at confidence 0.9, with `suspected_change` = `105fb53`, **which is correct**. It named the mechanism (`complete_fault_rate()`, 0.35 in compose.yaml) and matched it to the 35.5% ratio it observed. It also noted that a restart wouldn't help and that the next release from main would bring the fault back.
- **Policy:** require_approval, L1, all 6 preconditions pass. Command: `rollback.sh 20260926-181002-829513a`. Code-observed facts: alert firing, running V_BAD, previous V_GOOD, no prior rollbacks, 0 actions executed.
- **Cowork check before approval:** it matches the ground truth, so approval is recommended.
- **Grafana screenshots taken while firing** (sent to Sam in chat): running version V_BAD, alert FIRING, combined ratio 15.2%, complete-route ratio ~30–40% against the 10% line, **queue 1.44K, and oldest queued 5.16 min and growing**, with the injected-fault WARN lines in Loki. Real user impact was building: failed completes sit until the 60s lease expires, and the backlog grows.

**Step 5, STOP 3: approved rollback executed and verified.**
- **Approval.** Sam approved at 18:44:13 UTC. The re-check against fresh facts passed all 6 preconditions.
- **Rollback.** `rollback.sh 20260926-181002-829513a` exited 0 with no build. History record: `{"action":"rollback","from":"20260926-182749-105fb53","to":"20260926-181002-829513a","timestamp":"2026-09-26T18:44:21Z","incident_id":"INC-20260926-183037-api-v1-tasks-task-id-complete"}`. `/version` shows V_GOOD.
- **Verification.** `verification.json` passed 5/5 at 18:45:25: ready, version, probe 121/121 with 0 errors, 5xx rate 0, alert cleared. Prometheus shows 0 alerts and a complete-route ratio of 0. `timeline.jsonl` has 14 events.
- **Timings:**
  - Deploy (18:28:19) → pending (18:29:19): 60s.
  - Deploy → firing (18:30:37): 2m18s.
  - Deploy → decision (18:31:28): 3m09s.
  - **Decision → approval: 12m45s.** That was human latency, including the Cowork review and screenshots.
  - Approval → rollback done: 8s. Approval → verified: 72s.
  - **Total time V_BAD served traffic: ~16 min.**
- **Lasting user impact:**
  - **25 tasks ended `failed`** after exhausting their attempts. That work is actually lost.
  - **746 tasks stranded** in the queue, addressed to traffic-worker agents that no longer exist because the generator was stopped.
  - The 1730 queue-gauge reading is a stale series from the dead V_BAD instance and ages out of Prometheus in ~5 min.
- **Finding for the report:** `verify-recovery.sh` passed while the backlog the incident created was still stranded. It checks new-traffic health (a fresh probe, the 5xx rate, the alert), not whether the backlog is draining. In production those tasks belong to live agents and would drain. The check should still assert that queue depth and oldest age are trending down. Separately, the human gate dominated time-to-recovery (12m45s of ~16 min), which is the price of L1.
- Secret scan over the incident folder: 0 matches for all 8 patterns. Staged only that folder: 44 files, +1453. Proposed commit: "Record incident INC-20260926-183037-api-v1-tasks-task-id-complete: evidence, responder proposal, approved rollback, verification".

**Step 5, STOP 4: backlog cleanup and revert staged.**
- **Cleanup:** `DELETE 746`, only the queued tasks addressed to `traffic-worker-*` agents, with the FK cascade confirmed. The queue is empty.
- **Kept:** all **25 failed tasks**, the record of lost work. All were created in the incident window, between the V_BAD deploy and the rollback.
- **Revert of `105fb53` staged:** it removes the switch in `main.py`, the 0.35 activation in `compose.yaml`, and the fault-switch test. The three files are identical to their V_GOOD state. SQLite suite: 8 passed, 2 skipped.
- **Proposed message:** `Revert "Add fault-injection switch…"`. The body references `INC-20260926-183037-api-v1-tasks-task-id-complete` and the 18:44Z production rollback, and says this makes the next release from main clean.
- **Next:** Sam commits the revert. Then `release.sh` produces V_FIXED, whose previous_version must be V_GOOD (a live test of the `.to` logic for rollback records), followed by 2 min of traffic and `verify-recovery.sh` against V_FIXED.

**Step 5: COMPLETE (2026-09-26 ~19:02 UTC).**

| | Version | Previous | Result |
|---|---|---|---|
| V_GOOD | 20260926-181002-829513a | 20260926-100835-0a305bc | baseline 1501/1501, 0 errors |
| V_BAD | 20260926-182749-105fb53 | V_GOOD | ~35% of completes returned 500; rolled back after Sam's approval |
| V_FIXED | 20260926-185716-0a7a1fb | **V_GOOD** | 601/601, verify 5/5 |

- V_FIXED's previous_version is **V_GOOD, not V_BAD**, which proves `release.sh` reads the rollback record's `to` live. The fix-forward verification (`INC-20260926-185738-fix-forward-verify/verification.json`) passed 5/5 at 19:01:40. That folder is untracked, and it's Sam's call whether to commit it.
- **Commits:** `105fb53` fault switch → `853f931` incident record → `0a7a1fb` revert. Pushing is pending from Sam.
- **Incident cost:**
  - 1583 errors reached clients.
  - **25 tasks permanently failed.**
  - 746 stranded tasks were deleted, as approved.
- **Timings:**
  - Detection (incident opened): 2m18s after deploy.
  - Incident → decision: 52s.
  - Approval → rollback: 8s. Approval → verified recovery: 1m11s.
  - Responder: $0.189, 8 turns.
- **Caveat:** the fault was openly labelled, so this incident tests the *loop*: detect → evidence → propose → authorize → rollback → verify → fix forward. It doesn't test the model's diagnostic difficulty. The Step 4 DB drill is the ambiguity test.
- **Screenshots** (Cowork, sent to Sam):
  - 2 taken during firing at STOP 2.
  - 3 after: the complete-route 5xx ratio arc (≈30–45% from ~21:28 local, dropping to 0 at the 21:44 rollback, 10% threshold line); the request-rate arc (baseline, incident, a ~15 req/s complete burst at ~21:45 as requeued tasks drained after the rollback, then V_FIXED traffic); and final state V_FIXED + alert OK.
- **Chart artifact to note or fix:** the ratio panel draws a diagonal ramp from ~21:20 to 21:28. That's line interpolation across the no-traffic gap between baseline and V_BAD, not real errors. Fix: set "connect null values" to never. Added to the dashboard-polish list, with the 10000% axis and the blank stat at 0/0.
- C: is at 10GB free.

## Step 6 prompt (drafted 2026-09-26, saved here in case the session drops)

```
Homework 4, Step 6: security audit. Build security-audit/ with a deterministic scanner (Semgrep), a model review, human validation, and an inventory of the responder's own capabilities. Course principle: the model reviews, but a human validates every finding, and the responder itself is attack surface.

Rules:
- ONE commit for the audit artifacts. Any fixes Sam chooses later are separate commits. Don't commit or push; stage and report.
- Don't install anything globally. Semgrep runs via `uvx semgrep ... --metrics=off`, so code never leaves the machine except for the model review below.
- No accounts, no API keys, no third-party uploads. If a tool needs any of these, record that and skip it.
- Don't fix anything in this step. Findings get dispositions from Sam first.
- Overwrite reports.md (gitignored) with this step's results and print it at the end.

1. security-audit/audit-brief.md: the brief the model reviewer receives.
   - Scope: app code (main.py, storage.py, database.py, schemas.py, worker.py, telemetry.py, logging_config.py, buildinfo.py), Dockerfile, compose.yaml, observability/*.yaml, .github/workflows/ci.yml, k8s/, incident-response/ (orchestrator, policy engine, runbooks, collect-evidence.sh, responder flags).
   - A short threat model: who can reach what (the app on :8010, Grafana/Prometheus/Loki/Tempo bound to 127.0.0.1, the collector only on the Docker network); what's sensitive (agent tokens, claim tokens, enrollment secret, DB creds, Grafana admin password, the Claude OAuth session); and what the responder and orchestrator can do.
   - Instructions: cite file and line for every finding; distinguish exploitable from theoretical; don't invent findings to fill space.

2. security-audit/findings.schema.json: a strict schema for one finding. Fields: id, title, severity (critical/high/medium/low/info), category, file, line, evidence, source (semgrep | model), confidence, recommendation, and disposition (null until a human sets it: confirmed / false_positive / accepted_risk / fix_now / fix_later), with disposition_rationale.

3. Semgrep run → security-audit/runs/<UTC date>/semgrep.json
   - `uvx semgrep scan --metrics=off` with explicit registry rulesets relevant to this repo, e.g. p/python, p/secrets, p/dockerfile, p/github-actions, and a docker-compose ruleset if one exists. Record the exact command and version.
   - Summarize the counts by rule and severity.

4. Model review → security-audit/runs/<UTC date>/model-review.json
   - Use headless Claude with the same lockdown as the responder: read-only tools only, --permission-mode dontAsk, empty strict MCP config, no session persistence, --settings '{"advisorModel":""}', --max-budget-usd 2.00, --model sonnet, output constrained with --json-schema.
   - Its working directory is a SNAPSHOT of tracked files only: `git ls-files` copied into a gitignored folder, e.g. security-audit/runs/<date>/snapshot/, so it can never see observability/.env, deploy/, or reports.md. Confirm those three are absent from the snapshot before running.
   - Record the exact command, the model, the cost, and the turns. Validate the output against the schema.

5. security-audit/capability-table.md: inventory of the incident responder AND the orchestrator. One row per capability:
   - built-in tools available; file read scope; shell (none); MCP servers (none); network (the Anthropic API only);
   - credentials in reach: the claude.ai OAuth session lives under HOME. The model can't read it through its tools, but the process runs with it. Note that honestly;
   - model and CLI version and where the CLI is installed from (provenance);
   - user-level settings that leak into headless runs (the advisorModel finding from Step 4, and anything else in ~/.claude/settings.json that affects headless runs; list keys only, never values);
   - what the ORCHESTRATOR can execute after approval (runbooks → docker compose → Docker socket access, which is effectively root on the Docker VM. Say so plainly);
   - budget caps.
   Mark each row: needed / could be removed / risk accepted.

6. Snyk Agent Scan (the successor to Invariant's mcp-scan)
   - Find the current official way to run it without an account (e.g. via uvx), and run it against this machine's agent configuration.
   - Its output may list ALL of Sam's personal MCP servers, plugins, and skills. Do NOT commit the raw output. Save it only under a gitignored path, and put a short responder-relevant summary in capability-table.md.
   - If it needs an account/API key or fails, record exactly why and rely on the manual inventory instead.

7. Human-validation prep → security-audit/runs/<UTC date>/triage.md
   - One table merging the Semgrep and model findings, deduplicated. Columns: id, source, severity, file:line, one-line description, and your suggested disposition with a one-line reason. Leave the actual disposition column EMPTY for Sam.
   - Make sure these known items are present, found by the tools or added as "known, pre-existing" with source=manual:
     - open agent enrollment (no RELAY_ENROLLMENT_SECRET);
     - plaintext DB creds in tracked compose.yaml, k8s/secret.yaml and ci.yml;
     - public /docs, /redoc and /openapi.json;
     - Postgres `DETAIL: Failing row contains` echoing task payloads into logs/span events;
     - the 3 Postgres races from Step 1 (recovery vs claim, recovery vs heartbeat/terminal, idempotency IntegrityError);
     - the advisorModel settings leak;
     - verify-recovery not checking backlog drain (Step 5 finding);
     - an L1 rollback during a non-deploy outage would pass every precondition, so the human approval is the only gate (Step 4 finding).
   Mark which ones the tools missed.

8. Secret scan over security-audit/ (excluding the gitignored snapshot and raw Snyk output). `git add` only the committable audit files. Show `git status` and `git diff --cached --stat`, and propose one commit message.

Stop conditions:
- If the snapshot contains any of observability/.env, deploy/, or reports.md, stop before running the model review.
- If any tool tries to upload code or requires login, skip it and record why.
- If C: drops below 8 GB free, stop.
```

**Step 5 commits verified on GitHub, in order:** fault switch → incident record → revert → fix-forward verification (`6b32e9e`).

## 2026-09-27 — Step 6: security audit (staged; dispositions pending Sam)

Run folder: `security-audit/runs/20260926/`. A usage-limit pause split it across two days.

**Semgrep 1.178.0** (`uvx`, `--metrics=off`, no login). Rulesets: p/python, p/secrets, p/dockerfile, p/github-actions, p/docker-compose, p/kubernetes. 152 files, 223 rules. It had to run from the repo root, because it only scans git-tracked files and so found nothing inside the gitignored snapshot. **8 results:**
- Dockerfile missing-user (ERROR)
- `gha-curl-pipe-shell` in ci.yml (ERROR)
- mutable action tag (WARN)
- k8s writable-fs ×2 (WARN)
- run-as-non-root ×2 (INFO)
- `python-logger-credential-disclosure` at worker.py:171. It logs the agent id and file path, not the token, so the suggested disposition is false positive.

p/secrets found nothing.

**Model review:** same lockdown as the responder, cwd = snapshot of `git ls-files` (`.env`, `deploy/` and `reports.md` confirmed absent). sonnet-5, $0.590, 32 turns, 115s. It returned **10 findings**, schema-valid. Claude Code reproduced 3 new ones on a scratch instance:
- **M-002:** a chunked request bypasses the body-size limit (413 with Content-Length, but it parses when chunked).
- **M-003:** a non-ASCII `X-Enrollment-Secret` causes a 500 TypeError.
- **M-004:** committed incident evidence (`INC-…183037…/evidence/changed-files/compose.yaml:6`) contains `POSTGRES_PASSWORD`, even though that packet's secret scan "passed". The value is the public dev default, already in tracked compose.yaml, so there's no new exposure. **But the Step 4/5 "0 secrets" scan claims were narrower than they sounded:** the scan covered token, URL and Grafana patterns, not `KEY: value` secrets. **The report must correct this.**

**Capability table:** responder rows A1–A13, orchestrator rows B1–B8.
- Confinement is enforced by Claude Code's permission layer, **not the OS**.
- The process runs with the developer's claude.ai OAuth session.
- CLI 2.1.283 (native installer). It **changed version during the week without a pin.**
- User settings keys: advisorModel, theme. Recommendation: `--setting-sources ""`.
- After approval the orchestrator has Docker-socket access, which is **effectively root on the Docker VM.**
- Budgets: $1/responder call, $2/review.

**Snyk Agent Scan 0.6.4 was NOT run.** It requires a Snyk account + `SNYK_TOKEN`, uploads tool/skill descriptions, and starts the stdio MCP servers it finds, so it was skipped per the rules.

**Triage:** `runs/20260926/triage.md`, 21 deduplicated rows with suggested dispositions and an empty column for Sam.
- **Suggested fix_now:** open enrollment (K-001/M-001), non-ASCII 500 (M-003), evidence-scan gap (K-011/M-004), `--setting-sources ""` (K-008/M-006).
- **The tools missed:** public /docs, the Postgres DETAIL echo, the 3 races, the backlog-drain gap, and the L1-rollback gate. Semgrep also missed the plaintext creds and all app-logic issues.

**Staged:** `.gitignore` + 13 audit files (+722). `snapshot/` and `local-only/` are gitignored. The dev-default password is masked in committed findings; the raw versions are in `local-only/` with their sha256. The secret rescan found 0 hits.

**Note:** `.dockerignore` still lacks `security-audit/` and `incident-response/` (build context only).

## 2026-09-27 — Step 6b: dispositions (`0e69e2f`) and the four fix_now items (staged)

- **Part A committed as `0e69e2f`:** dispositions in `triage.md` (21 rows) and in all 29 findings across the 3 JSON files. Only the two disposition fields were touched.
- **Part B staged:** 19 files, +673/−15.
  - **K-001:**
    - `RELAY_ENROLLMENT_SECRET` via `${…:?}` from a gitignored root `.env` (mode 600, token_urlsafe(32)), plus `.env.example`.
    - Port is now `127.0.0.1:8010:8000`, and `.env*` is in `.dockerignore`.
    - traffic.py and verify-recovery.sh read the secret from the environment or `.env`, and never print it. The evidence scan looks for the secret's actual value.
  - **M-003:** bytes compare. The new test sends the raw 0xE9 byte and gets 401 (the old code gave a TypeError).
  - **K-011:**
    - `redact_secrets.py`: key-like names in `KEY: value` / `KEY=value` form in config files, string literals only in code. Skips placeholders, numbers and bind params. 20 tests.
    - The collector redacts before writing, and the backstop uses the same rules. Negative tests passed (redaction works, planted secrets get quarantined).
    - **Found and fixed:** the first backstop version would have quarantined real packets, because of `token_hash = %(token_hash_1)s` in SQL spans and `input_tokens` in usage JSON. Committed evidence was NOT edited.
  - **K-008:** `--setting-sources ""` added to the responder and the model review. **Canary re-run PASS** (`canary-20260927`): tools exactly Glob/Grep/Read/StructuredOutput, 6/6 denials, auth OK, $0.095.
- **Verification:**
  - SQLite 36 passed / 2 skipped; Postgres the same; incident-response tests 82 passed.
  - Registration: none → 401, wrong → 401, non-ASCII → 401, correct → 201.
  - `:8010` is loopback-only (docker port, Windows netstat).
  - Release `20260927-101902-0e69e2f-dirty`.
  - **The observability stack had silently died** (Exited 127 when Docker Desktop stopped). **The first verify-recovery correctly FAILED** its Prometheus checks ("unknown"), so it fails closed when monitoring is blind. After a restart, `INC-20260927-102600-fixnow-verify` PASSED 5/5. The secret appears 0 times in logs, Loki and the verification output.
- **Found:** pytest recursed into the gitignored audit `snapshot/` ("import file mismatch"). Claude Code deleted the snapshot (reproducible with `git archive`). Follow-up: move the snapshot outside the repo or set `testpaths`.
- **Next:** Sam commits Part B and pushes. Then run a clean release (no `-dirty`) and verify-recovery against it; commit that verification instead of the `-dirty` one. Then the report.

**Step 7 (report) prompt issued 2026-09-27**, after the fix_now commit. It asks for docs/operations-and-security-report.md built only from artifacts, with a clean release + post-audit verify first, 9 sections (summary, loop, primary incident, DB drill, alerting lessons, audit, corrections/limitations, reproduce, deliverable map), optional screenshots in docs/images, and a README pointer section. The full text is in the chat. Remaining for 2026-09-28: Q1–Q8 answers, course-repo pointer docs (04-devops/README.md + homework/module_04/), submission, LIP posts.

---

### Step 7 prompt, revised 2026-09-27 (full text)

Revised because INC-20260927-102600-fixnow-verify/ turned out to be staged, not untracked. The first issue's full text only existed in chat, so this is the complete version to send. It supersedes the first issue.

```
Step 7: operations and security report (docs/operations-and-security-report.md)

Context: Module 4 homework on the agent-relay fork. Steps 1–6b are done and on main, including the fix_now commit (K-001/M-001, M-003, K-011/M-004, K-008/M-006). This step writes the report that ties it together.

Build every claim from artifacts in the repo: incident folders, security-audit/runs/20260926/, deploy/history.jsonl, observability config, runbooks, policy files. The figures I give below are my notes, so treat them as a checklist, not a source. Where an artifact disagrees, the artifact wins, and you list the mismatch in your final summary.

Ground rules (unchanged):
- You stage only. No git commit, push, tag, reset --hard, rebase or stash. Sam commits and pushes.
- Don't touch the civil-liberties-knowledge-assistant_pgdata volume or any other project's containers or volumes.
- Never print secret values (.env contents, RELAY_ENROLLMENT_SECRET, Grafana admin password, DB password) to the terminal, the report or your summary. Refer to them by name only.
- Don't edit committed incident evidence (manifest.json hashes must stay valid). Quote from it; don't rewrite it.
- If Docker Desktop is stopped, stop and tell Sam. Don't try to start it.

0. Clean state first (revised: the fixnow-verify folder is STAGED, not untracked)
   a. Show `git log --oneline -5`, `git status`, then `git fetch` and `git status -sb`. Confirm HEAD is the fix_now commit and main is level with origin/main.
      Expected staged: incident-response/incidents/INC-20260927-102600-fixnow-verify/ (at least its verification.json) and nothing else.
      Expected untracked: the five docs/images/inc-*.jpg screenshots Sam copied in.
      If anything else is staged, modified or untracked, stop and report before changing anything.
   b. Before removing it, record what the superseded folder says. Print only the non-secret result fields of INC-20260927-102600-fixnow-verify/verification.json (version, overall pass/fail, per-check results, timestamp). Keep that summary for §7.
   c. Unstage it: `git restore --staged incident-response/incidents/INC-20260927-102600-fixnow-verify`. Show `git status`. It must now be untracked, with nothing staged.
   d. Remove it: `rm -r incident-response/incidents/INC-20260927-102600-fixnow-verify`.
      Why: it verified build 20260927-101902-0e69e2f-dirty, which no commit can reproduce, so it isn't valid evidence for the fix. It's your own Step 6b output and was never committed, so nothing in history references it.
      §7 of the report says it existed, what it showed, and why it was replaced.
      Leave its line in deploy/history.jsonl alone. That file is gitignored and is an accurate record of what was deployed.
   e. Check how scripts/release.sh decides "-dirty". `git describe --dirty` ignores untracked files; `git status --porcelain` counts them. If untracked files would make the build -dirty, move docs/images/inc-*.jpg to /tmp/relay-images/ for the release and move them back straight after. Stage nothing before the release.
   f. Confirm the tree is clean: `git status --porcelain` is empty, or shows only the untracked images if (e) showed they don't count.
   g. Confirm the stack is up: `docker compose ps` shows app, db, collector, prometheus, loki, tempo and grafana running and healthy.
   h. Run scripts/release.sh. The printed version must have no -dirty suffix, and its sha7 must equal HEAD. If it's -dirty, stop.
   i. Run incident-response/runbooks/verify-recovery.sh with a new id INC-<UTC YYYYMMDD-HHMMSS>-post-audit-verify against that version. It must PASS. If it fails, stop and report. Don't write the report on top of a failing verify. Keep the new folder for staging in step 11.

1. Summary. One paragraph covering:
   - what was built: observability, alerting, versioned release and rollback, a read-only responder under an autonomy policy, and a security audit
   - the headline incident result
   - what is still open
   No hype.

2. System and loop.
   - Architecture: app → OTLP/HTTP → collector → Prometheus / Loki (native OTLP, the only log path) / Tempo → Grafana; the alert rule; release.sh and deploy/history.jsonl; the responder. Use a Mermaid or plain-text diagram.
   - The loop: observe → alert → evidence → propose → authorize → rollback → verify → fix-forward. For each stage, say which component does it and at what autonomy level.
   - The responder's actual invocation flags, taken from respond.py, with one line on what each flag confines.
   - The autonomy policy (L0/L1/L2). Quote the rollback and restart_app preconditions from autonomy-policy.yaml.
   - Confidence can only downgrade (below 0.5 forces escalate). Model text is never executed. `approve` re-checks every precondition against fresh facts.
   - Evidence collection is bounded and allowlisted, with a manifest.json of sha256 hashes, a quarantine path, and redaction.
   - The canary results: 6/6 out-of-scope accesses denied, before and after `--setting-sources ""`.

3. Primary incident: INC-20260926-183037-api-v1-tasks-task-id-complete. Build the timeline table from artifacts, UTC with local time in brackets. Checklist to confirm against the artifacts:
   - Versions:
     - V_GOOD 20260926-181002-829513a
     - V_BAD 20260926-182749-105fb53, a fault injected through the openly labelled RELAY_FAULT_COMPLETE_5XX_RATE switch
     - V_FIXED 20260926-185716-0a7a1fb
   - Timings:
     - incident opened 2m18s after deploy
     - decision 52s later
     - approval wait 12m45s
     - approval → rollback 8s
     - approval → verified 1m11s
   - Responder: $0.189 over 8 turns. It named commit 105fb53 and the mechanism correctly.
   - Impact: 1583 errors; 25 tasks permanently failed; 746 stranded tasks deleted with Sam's approval.
   - Fix-forward: verified in INC-20260926-185738-fix-forward-verify.
   Be explicit about which actions the human took and which the automation took.
   Embed the docs/images/inc-*.jpg screenshots with captions. The 5xx-ratio and request-rate panels show a ramp before about 21:28 local (18:28 UTC). That's line interpolation across a gap in the data, not real traffic, and the caption must say so.

4. DB drill: INC-20260926-113352-api-v1-tasks-claim. Cover what was broken, what the responder decided (escalate), and why that's the correct outcome under the policy.

5. Alerting lessons.
   - A rate-based guard switched itself off during the outage, because failures cut traffic below the threshold. It was replaced with an absolute-count guard (increase over 2m ≥ 20).
   - A combined claim+complete ratio could dilute a failure on one route. The ratio became per-route.
   - Quote the final RelayClaimCompleteErrorRatioHigh rule, with its labels and annotations, from the config.
   - Say what it still doesn't catch.

6. Security audit.
   - Method: Semgrep via uvx with metrics off; a locked-down model review on a git ls-files snapshot; human triage; the capability table.
   - Snyk Agent Scan was skipped, because it needs an account and uploads data.
   - Counts by disposition, from triage.md.
   - The fix_now items and the commit sha that fixed them.
   - accepted_risk items with their reasons; the false positive; the fix_later list.
   - A short summary of capability-table.md.

7. Corrections and limitations. State these plainly.
   Corrections:
   - The first Step 5 prompt asked for a covertly disguised fault with a misleading commit message. It was declined and replaced with an openly labelled switch.
   - The evidence secret scan was narrower than claimed. Committed evidence contains the public dev-default DB password. It wasn't rewritten, to keep the manifest hashes valid, and redact_secrets.py was added for future evidence.
   - The redactor's first backstop false-positived on token_hash and input_tokens, and was fixed.
   - pytest recursed into the gitignored audit snapshot.
   - The observability stack died silently when Docker Desktop stopped, and verify-recovery correctly failed closed.
   - The superseded -dirty verification from step 0: what it showed, and that the fix build was re-verified on clean release <version> in INC-…-post-audit-verify.
   Limitations:
   - The L1 human gate is the only protection against a wrong rollback.
   - verify-recovery has no backlog-drain check.
   - Docker socket access is effectively root on the VM.
   - The OAuth session is reachable from the responder's process.
   - The Claude CLI version is unpinned.
   - The Postgres races are still open.
   - M-002 (chunked body-limit bypass) is still open.

8. How to reproduce. Give the commands from a fresh clone:
   - .env from .env.example
   - compose up
   - release.sh
   - traffic.py
   - the fault switch
   - respond.py and approve
   - rollback, verify-recovery
   - the tests
   Include only commands that exist in the repo, and check each path.

9. Deliverable map. A table mapping each homework requirement to the file paths that satisfy it, including every incident folder.

10. README. Add a short "Homework 4: Operations and Security" section that links the report and the key directories. Don't rewrite other sections.

11. Checks and staging.
   a. Run the test suite scoped so it can't recurse into any audit snapshot, and report the results.
   b. Run redact_secrets.py and the secret scan over the report, README and new verify folder. Also check for the actual secret values by count only, never printing them.
   c. Stage exactly these:
      - docs/operations-and-security-report.md
      - docs/images/inc-*.jpg
      - README.md
      - the INC-…-post-audit-verify folder
   d. Show `git status` and `git diff --cached --stat`, and propose a commit message. Don't commit.

Report style: plain and specific, numbers from artifacts, tables for timelines. No hype. Avoid the "wasn't X, it was Y" construction and heavy em-dash use.

Final summary back to Sam:
- the released version and the verify result
- the step-0b summary of the superseded folder
- any mismatches between this checklist and the artifacts
- test and secret-scan results
- the staged file list
- the proposed commit message
```

### Step 7 result, 2026-09-27 ~20:32 EAT (staged, not committed)

- fix_now commit daa54c1 is confirmed on GitHub as the top of main. Checked in the browser.
- The fixnow-verify folder was untracked, not staged; Claude Code's git status showed nothing staged. It was deleted. It had passed 5/5 on 20260927-101902-0e69e2f-dirty (10:28:56–10:30:02Z), and §7 of the report records that.
- Clean release 20260927-172131-daa54c1. INC-20260927-172205-post-audit-verify passed 5/5 (121/121, 0 errors). The images went to /tmp during the release, because release.sh counts untracked files as dirty.
- Checklist vs artifacts:
  - errors: the server-side count is 1529 (one Loki warning per injected 500). 1583 is the client-side count from the generator and isn't committed. The report uses 1529.
  - 746 stranded: this is only in gitignored notes, and the report says so. 25 permanently failed is confirmed in the DB.
  - request-rate panel: no interpolation ramp; it shows real zeros. My prompt was wrong here and the caption was corrected. Only the 5xx-ratio panel has the ramp.
  - all timings, $0.189/8 turns and the versions matched to the second.
- New limitations in the report:
  - Four app tests fail with 401 when RELAY_ENROLLMENT_SECRET is exported in the shell (it was exported in the Claude Code session env).
  - Quarantine leaves an empty incident dir behind. Claude Code removed the empty INC-20260927-000000-kvscantest itself, which the prompt didn't ask for.
  - The CLI drifted from 2.1.278 to 2.1.283.
  - Replaying 105fb53 re-exposes 0.0.0.0:8010 with open enrollment. That's noted in §8.
- Tests: app 9/9 on SQLite and 9/9 on throwaway Postgres (variable unset); incident-response 82/82. Secret scans clean.
- Staged 8 files (+453):
  - report
  - 5 images
  - README (+11, append only)
  - post-audit verification.json
- Before committing: Cowork reviews the report text.

### Step 7 report review (Cowork), 2026-09-27

- Read all 403 lines of the report through a copy in Claude outputs/.
- The timeline arithmetic checks out against the timestamps:
  - 18:28:19 → 18:30:37.2 = 2m18s
  - → 18:31:28.9 = 51.7s
  - → 18:44:13.6 = 12m45s
  - → 18:44:21.8 = 8.2s
  - approval → 18:45:25.1 = 71.5s
- The impact figures are consistent: 1529/4382 ≈ 35%. The dispositions total 21 rows / 29 ids, and fix_now = 7 ids.
- Two wording fixes before commit:
  1. Line 5 says every figure comes from a file in the repo. But 1529 (Loki), ~4382 (Prometheus) and 25 (DB) are live queries, and Loki/Prometheus keep only 2 days. The qualifier should say so.
  2. The request-rate caption says the "requeued backlog drained", which contradicts the 746 stranded tasks in §3.5/§7.
- The §9 deliverable map will be cross-checked against homework.md tomorrow, since homework.md is still [DRAFT].

### Step 7 pushed and verified live, 2026-09-27

- The commit "Add Module 4 operations and security report" is at the top of main on GitHub.
- The report is live with both wording fixes:
  - the line-5 qualifier is there
  - the caption now says "requeued tasks were completed (746 others stayed stranded"
  - "backlog drained" is gone
- In GitHub's rendered view, all 5 screenshots load (800px wide) and the Mermaid diagram renders.
- README.md has the "Homework 4: Operations and Security" section.
- INC-20260927-172205-post-audit-verify/verification.json is on main: passed=true, version 20260927-172131-daa54c1.
- The superseded fixnow-verify folder returns 404, as intended.
- Sam deleted the temporary Claude outputs/ copy.
- Build work for Module 4 is done.
- Remaining for 2026-09-28:
  - re-check homework.md
  - Q1–Q8 answers and the reflection
  - the course-repo pointer docs
  - submit
  - LIP posts
- Optional: dashboard polish, .dockerignore, a test fixture that clears RELAY_ENROLLMENT_SECRET.

---

### Step 8 prompt: agent-relay wrap-up, issued 2026-09-27 (full text)

Context:
- Sam confirmed the published hw4 answers don't come from agent-relay.
- Before starting Order Tracker, finish agent-relay: loose ends, a full README rewrite following Alexey's article, and Docker cleanup.
- Sam left the cleanup choices to Cowork:
  - stop the stacks
  - remove old release images, dangling images, build cache and the kind cluster
  - keep all volumes, since the report says the postgres volume holds the 25 failed tasks as the record of lost work, and the observability volumes expire on their own

```
Step 8: agent-relay wrap-up (loose ends, README rewrite, Docker cleanup)

Context: agent-relay is finished as a Module 3 + Module 4 project. The graded hw4 was published on 2026-09-26 around a different app (alexeygrigorev/order-tracker), and that will be a separate repo. This step leaves agent-relay as a clean portfolio repo before we move on. Work in ~/Projects/agent-relay.

Ground rules (unchanged):
- You stage only. No git commit, push, tag, reset --hard, rebase or stash. Sam commits and pushes.
- Never print secret values. Refer to them by name.
- Don't edit committed incident evidence or security-audit run outputs (hashes must stay valid).
- Don't touch any other project's containers, images or volumes, especially civil-liberties-knowledge-assistant_pgdata. No `docker system prune -a`, no `docker volume prune`, and no `down -v` anywhere in this step.
- If Docker Desktop is stopped, stop and tell Sam.
- There are three STOPs. At each one, stage the files, report and wait. Sam commits between parts.

PART A: loose ends (code and config)

A1. Test isolation. test_agent_relay.py fails with 401 when RELAY_ENROLLMENT_SECRET is exported in the shell. Fix it in the fixture: clear the variable (monkeypatch.delenv, raising=False) for tests that don't set it, and have the enrollment tests set it explicitly. Prove it: the suite must pass both with the variable exported to a dummy value and with it unset.

A2. pytest collection. Configure [tool.pytest.ini_options] in pyproject.toml so a plain `uv run pytest -q` can never collect security-audit/runs/** or other generated folders. Use norecursedirs and/or testpaths. The incident-response tests need extra deps (pyyaml, jsonschema), so either add them as a dev dependency group or keep the `--with` command, and say which you chose and why.

A3. .dockerignore. Keep security-audit/, incident-response/, docs/, observability/, deploy/, k8s/, .github/, .env and tests out of the app image, unless the Dockerfile or the app needs one of them (check first). Rebuild with `docker compose build app`. Don't run release.sh; the tree is dirty. Show the image size before and after.

A4. Quarantine leftovers. A quarantined evidence packet leaves an empty incidents/<ID>/ directory behind. Remove that directory only if it's empty after the move, and add a test.

A5. Dashboard polish (observability/dashboard.json), three known issues:
   - the 5xx-ratio axis shows 10000%: the unit is wrong for a 0–1 ratio, so use percentunit
   - the "5xx ratio, claim + complete" stat is blank at 0/0: give it an explicit no-traffic display instead of empty
   - time series draw ramps across gaps: set spanNulls/connect nulls to never, and insert nulls where the panel supports it
   Restart only Grafana to reload provisioning, and confirm through the Grafana API that the dashboard loads with the new settings. Sam will look at it himself.

A6. Report header. Add one line under the title of docs/operations-and-security-report.md: "Built against the draft of Module 4's homework. The published homework (2026-09-26) uses a different starter app, Order Tracker; this repo is the extended version." Change nothing else in the report.

Run everything:
- app tests on SQLite, with the variable exported and unset
- app tests on a throwaway Postgres (remove the container afterwards)
- incident-response tests
- a plain `uv run pytest -q`, which must not touch the audit runs
Stage A1–A6 and show `git diff --cached --stat`. Propose a commit message.

STOP 1. Wait for Sam to commit and push.

PART B: README rewrite

Follow Alexey Grigorev's "How to Write a Good README" (aishippingblog.com). The reader is three people at once: a peer reviewer looking for evidence, a hiring engineer deciding in 10 seconds, and Sam in six months. The first screen must say what this is, who it's for and what it shows. Everything after that is evidence and detail, with links to where the depth lives. Include only sections that fit, in this order:

1. Title and a two-sentence description in the article's formula: "[Project] is a [system] that helps [user] do [outcome]", plus the main obstacle. Don't open with a list of technologies.
   Status line: built for AI Dev Tools Zoomcamp 2026, Modules 3 and 4, as a fork of alexeygrigorev/agent-relay. Graded hw4 lives in a separate Order Tracker repo (leave a TODO link for Sam to fill in).
2. Problem. A short paragraph. Agents hand work to each other through the relay. When a release breaks it, the damage is silent and piles up (stranded tasks), and a coding agent that responds to incidents must be kept from doing damage itself.
3. Demo. The existing screenshots in docs/images/, the firing dashboard and the 5xx-ratio arc, each with a one-line caption. Add a short text walkthrough of the incident: deploy → alert → evidence → proposal → approval → rollback → verified, with real timings.
4. Does it work? Evidence, not adjectives:
   - Tests: what they cover, counts and the one-line commands, including anything the tests need.
   - Incidents: a table of the drills. Primary incident, DB drill, fix-forward and post-audit verify, each with its outcome, a key number and a link to its folder.
   - Monitoring: what the dashboard panels show, what the alert fires on, and a link to the rule.
   - Security audit: method in one line, disposition counts, what was fixed and in which commit, and a link to triage.md.
5. Quickstart. Prerequisites (Docker Desktop/Compose, uv, and the Python version from .python-version), then the shortest reliable path: clone, the two .env copies, release.sh, the observability stack, traffic, the Grafana URL.
6. Configuration. A table of every env var the app, compose, observability and responder read: required or optional, what it controls, the default. Take it from the code, not memory.
7. Architecture. Reuse the report's Mermaid diagram, simplified, plus 3–4 sentences on what each part is responsible for.
8. Project structure. A short annotated tree of the paths that matter, not a full `tree`.
9. Decisions and trade-offs. 5–7 entries in the article's form, "I chose X over Y because Z. The downside is A. I accepted it because B." Candidates, each checked against the artifacts:
   - a read-only responder with an L1 human gate instead of an agent that fixes code
   - policy in code instead of in the prompt
   - Loki native OTLP as the only log path
   - an absolute-count alert guard and a per-route ratio
   - a Prometheus rule plus a watcher instead of Alertmanager
   - Compose instead of kind for Module 4
   - leaving committed evidence unredacted to keep hashes valid
   - skipping Snyk Agent Scan
10. CI/CD. Describe what .github/workflows actually does: its triggers, checks and deploy target, and that it was run with act against kind. Read the workflow, don't guess. If it doesn't run on GitHub-hosted runners, say so.
11. Limitations. From report §7, one line each, with the practical effect.
12. Future work. From the fix_later list, prioritised, 4–6 items, each with the reason.
13. Evidence map (self-evaluation). A table with a row for each Module 3 homework question (Q1–Q6, using the commit messages) and each Module 4 capability (observe, alert, evidence, authorize, rollback, verify, audit). Each row points at the file or folder that proves it. Nothing without evidence.
14. Credits: the course and the upstream starter, as plain fact.

Move the starter's protocol, worker and storage documentation (the current "Run it", "Run the deterministic worker", "Storage and delivery behavior" and "Verify" text) into docs/protocol.md. Fix what's stale there, for example "does not include Docker, Kubernetes, CI…" and the `uv run uvicorn` dev path if it no longer matches. Link it from the README.

Rules for the README:
- Present tense only for what exists.
- Every number from an artifact.
- No hype.
- No "wasn't X, it was Y" construction.
- Few em-dashes.
- Tables and short paragraphs, not walls of text.
- Keep it scannable, with the depth in the report and docs/.

Verify before staging:
- Fresh-clone check without Docker: `git clone ~/Projects/agent-relay /tmp/agent-relay-readme-check`, then in it run `uv sync`, the .env copy steps and the test commands exactly as the README writes them. Confirm every relative link and path in README.md and docs/protocol.md exists. Delete /tmp/agent-relay-readme-check afterwards.
- Docker commands: run the quickstart's Docker commands in ~/Projects/agent-relay, not in the clone, and confirm the app /ready, /version, Grafana and Prometheus respond. Don't run release.sh on a dirty tree. If a command needs a clean tree, say so rather than work around it.
- Secret scan: run redact_secrets.py over README.md and docs/protocol.md.

Stage README.md and docs/protocol.md. Show the diff stat, and propose a commit message and a GitHub "About" description (one sentence, 350 characters max) plus 5–8 topics for Sam to set on GitHub himself.

STOP 2. Wait for Sam to send the README for review, then commit and push.

PART C: Docker cleanup (after STOP 2 is cleared)

C1. Record `docker system df` and free space on C: (`df -h /mnt/c`) before starting.
C2. Stop both stacks: `docker compose -f observability/compose.yaml down`, then `docker compose down`. No -v.
C3. Images:
   - List the `agent-relay` image tags. Remove every release tag except the current release in deploy/history.jsonl (20260927-172131-daa54c1, unless a later clean release exists), including any -dirty tags from A3.
   - Then `docker image prune` (dangling only; no -a).
   - Then `docker builder prune`. Show the reclaimable size first.
C4. kind: `kind get clusters`. If the Module 3 cluster exists, delete it. Remove the kindest/node image only if no kind clusters remain.
C5. Keep all agent-relay volumes. The postgres volume holds the 25 failed tasks that the report says were kept as the record of lost work, and the observability volumes expire their data on their own. List them with their sizes for the record.
C6. Record `docker system df` and `df -h /mnt/c` after, and confirm that ports 3000, 3100, 3200, 4317, 4318, 8000, 8001, 8010 and 9090 are free for Order Tracker.

STOP 3. Report before/after sizes, what was removed and what was kept.
```

### Step 8, STOP 1 (Part A staged), 2026-09-27 ~21:24 EAT

- Setup: this ran in a new Claude Code session. `env | grep -c` showed RELAY_ENROLLMENT_SECRET was exported in a fresh VS Code terminal, but no profile or direnv sets it; it's most likely the VS Code Python extension loading .env. Sam unset it before starting.
- A1: the secret is cleared per test; 4 tests used to fail when it was exported. A2: testpaths and norecursedirs set, pyyaml and jsonschema in the dev group, and a decoy test under the audit runs wasn't collected. A3: .dockerignore; the image is unchanged at 376.6 MB because the Dockerfile copies an explicit list, and the build context shrank. A4: an empty incident dir is removed after quarantine, with a 2-case test that fails on the old script. A5: spanNulls false plus insertNulls 5m on all 8 time series, and "no traffic" mapping for the NaN stat. A6: the header line was added.
- Tests: SQLite 9/9 and throwaway Postgres 9/9, with the secret exported and unset; incident-response 84; plain pytest 93.
- Its own throwaway Postgres left an anonymous volume, which it removed by exact ID. civil-liberties pgdata wasn't touched.
- The "10000% axis" wasn't reproduced. The file and live Grafana both use percentunit, and the screenshots show 0–50%. It came from a note I made during Step 5 with no screenshot behind it. Withdrawn, no change.
- Cowork checked live Grafana (26 Sep 18:15–19:05Z window): the ratio line now rises vertically at 21:28 with no ramp, the stat shows "no traffic", and the axis runs 0–50%. Confirmed fixed.

### Step 8, STOP 2 (README staged), review 2026-09-27 ~21:45 EAT

- Sam pasted README.md and docs/protocol.md into chat, so no copy was needed. 71dac87 is the Part A commit.
- Numbers check out: the test table adds up (6+3+44+27+11+2 = 93); 16 min bad-release window; fix-forward verification 64 s; timeline matches the report.
- Fixes requested:
  - Drop the Order Tracker TODO link until that repo exists.
  - Module 3 Q1 row: in the published hw3, Q1 was "fork, run and understand the architecture" (MCQ, no code). Point it at the fork, SPEC.md and docs/protocol.md, without stating the answer.
  - Q4 row wrongly credits 64dddaf (SKIP LOCKED, which came at the start of Module 4) to Q4.
  - The Snyk "starts stdio MCP servers" clause isn't in the report; source it or remove it.
  - Tighter two-sentence description.
  - Report erratum in the same commit: 82 → 84; two §7 limitations marked fixed in 71dac87; §8 test commands updated.
- Claude Code asked about Alertmanager and Compose-vs-kind; both are left out rather than given invented reasons.

### Step 8 closed: README pushed, Docker cleaned (STOP 3), 2026-09-27 ~21:56 EAT

Live check on GitHub:
- 70a9e31 "Rewrite README; move protocol docs to docs/protocol.md" is on main.
- The About description is set. No topics are set yet.
- README:
  - no TODOs
  - the Q1 row points to the fork, SPEC.md and protocol.md without stating the answer
  - the Q4 row credits 1f2a30b and notes 64dddaf as added later
  - both demo images load and the Mermaid diagram renders
  - docs/protocol.md is live
- Report erratum is in: "82 pass" is gone, and both limitations say "fixed in 71dac87".
- The Snyk "starts the stdio MCP servers" clause I flagged is sourced after all: it's in security-audit/capability-table.md §C. My flag was wrong, and the clause stays.

Docker (STOP 3):
- Both stacks are down, with no -v.
- 7 agent-relay tags removed: dev, two -dirty, V_BAD, V_GOOD, V_FIXED, 0a305bc. Only 20260927-172131-daa54c1 remains.
- No dangling images. Build cache prune freed 191.8 MB. There was no kind cluster.
- All 6 volumes kept: postgres 80 MB with the 25 failed tasks, observability ~93 MB, civil-liberties untouched.
- Images went from 3.27 to 3.17 GB (the tags shared layers). C: is still at 11 GB free until the vhdx is compacted.
- All 9 ports are free.
- Rollback now needs a rebuild, because only the current image is left. That's fine with the stacks down.

agent-relay is done. Optional: GitHub topics, and compacting docker_data.vhdx. Next: Order Tracker, Step 0 recon.

---

## Order Tracker (the published hw4): setup, 2026-09-27

- Published homework: cohorts/2026/homework/04-devops/homework.md, commit "Publish Homework 4 incident response exercise", 2026-09-26.
- Starter app: alexeygrigorev/order-tracker.
- due_at: 2026-10-05T23:00:00Z, which is 6 Oct 02:00 EAT (checked live against homework.yaml).
- The form has 6 questions plus a reflection question ("Describe one practical idea you took from this module"), homework_url, time spent, faq_contribution, and up to 7 LIP links.

Questions:
- Q1: /healthz output.
- Q2: status code in the console metric for standard-1001.
- Q3: status code Grafana shows for standard-1002.
- Q4: Grafana 5xx alert state.
- Q5: the last line of the agent's reply to a test alert at POST :8001/alerts.
- Q6: what the problem was after express-1002 fires the alert. Grafana sends a webhook, the agent fixes, restarts and verifies.

Submission: repo link, with the telemetry and alert config, responder, incident evidence and the agent's fix committed.

Sam's decisions (2026-09-27):
- Fork Order Tracker and port the agent-relay patterns. agent-relay stays as the portfolio repo.
- Responder autonomy:
  - the agent may edit code
  - the orchestrator runs the tests and a replay of the failing request, and restarts only if both pass, otherwise it escalates
  - the agent never runs git
  - test alerts never lead to code changes
- The README follows Alexey's "How to Write a Good README", with a demo GIF of the alert → fix → verify cycle, an evidence map per question, decisions, limitations, and a link to agent-relay. It's the last step.

Rule for every Order Tracker session: nobody requests express-* orders or looks for the express bug before Q6. Finding it is the responder's job.

### Order Tracker Step 0 prompt (recon), full text, updated 2026-09-27

Prerequisite: Sam forks alexeygrigorev/order-tracker on GitHub as Sanjomwa/order-tracker (public), then starts a fresh Claude Code session in ~/Projects.

```
Module 4, Order Tracker, Step 0: recon only (no feature code yet)

Context: the published hw4 (cohorts/2026/homework/04-devops/homework.md, published 2026-09-26, due 2026-10-05T23:00:00Z) uses Order Tracker, not agent-relay. We fork it and reuse the patterns from ~/Projects/agent-relay:
- the OTel setup, collector config and Grafana provisioning
- evidence collection
- the responder lockdown flags
- secret redaction
agent-relay stays untouched as a separate, finished repo; read from it, never write to it.

Ground rules:
- You stage only. No git commit, push, tag, reset --hard or rebase. Sam commits and pushes.
- Don't touch any other project's containers or volumes (agent-relay_*, agent-relay-observability_*, civil-liberties-knowledge-assistant_pgdata). Never use `down -v`.
- Never print secret values.
- Do NOT request /api/orders/express-1002 or any express-* order, and don't read the code looking for the express-order bug. Finding it is the responder's job in Q6. If you notice it by accident, say so and don't describe it.

1. Preconditions:
   - `env | grep -c '^RELAY_ENROLLMENT_SECRET='` must print 0. Print the count only.
   - `docker ps` should show no agent-relay containers; they were stopped on 2026-09-27.
   - Confirm nothing is listening on ports 3000, 3100, 3200, 4317, 4318, 8000, 8001 or 9090.

2. Clone: `git clone https://github.com/Sanjomwa/order-tracker.git ~/Projects/order-tracker`. Add upstream https://github.com/alexeygrigorev/order-tracker.git as a fetch-only remote. Show `git log --oneline` and `git remote -v`.

3. Map the starter, and report:
   - the file tree
   - app framework and entry point
   - how routes are defined
   - DB access and schema
   - how sample orders are seeded (list their ids and types only)
   - compose.yaml services, healthcheck, volume and the ORDER_TRACKER_PORT variable
   - the Dockerfile
   - the Python version
   - dependencies in pyproject.toml
   - the test layout and how the tests isolate the DB
   - any existing logging
   Keep to what's there, and don't propose code yet.

4. Run it exactly as the homework says:
   - `docker compose up --build -d --wait`
   - `curl -s http://localhost:8000/healthz`, and show the raw output. This is Q1.
   - `curl -i http://localhost:8000/api/orders/standard-1001`
   - `uv run --frozen pytest -q`, with results
   Then leave the app running.

5. Porting assessment. For each item below, say what carries over from agent-relay as-is, what needs adapting, and what's new:
   - Q2: OTel instrumentation, exported to the console first. The request metric must carry route and status code.
   - Q3: collector, Prometheus, Loki, Tempo and Grafana added to this repo's compose.yaml, so a single `docker compose up --build -d --wait` brings everything up. A dashboard for request counts and errors.
   - Q4: a Grafana-managed alert, not a Prometheus rule. It must include the endpoint, time window and dashboard link, and handle no-data.
   - Q5/Q6: a responder in incident-response/ serving POST /alerts on :8001, which receives Grafana webhooks, saves evidence and starts Claude Code headless. Decide whether the responder runs on the WSL host (uv) or in a container, and how Grafana reaches it (for example host.docker.internal). Note the trade-offs of each.
   - Autonomy (Sam's decision):
     - The agent may edit code to fix the problem.
     - The orchestrator (code, not the model) then runs the tests and a replay of the failing request.
     - It restarts the app only if both pass; otherwise it escalates.
     - The agent never runs git.
     - Test alerts (labels.test == "true") must never lead to code changes.
   Say which of agent-relay's lockdown flags can't apply once the agent needs Edit, and what confinement replaces them: a working copy, an allowed-paths list, and a diff check before restart.

6. Report back:
   - the Q1 output
   - the test results
   - the map from step 3
   - the porting assessment
   - a proposed step plan (Q2 → Q3 → Q4 → Q5 → Q6 → report/README), with a STOP after each question so Sam can check the answer
   - anything in the homework text that is ambiguous
   Stage nothing.
```

### Order Tracker Step 0 (recon) result, 2026-09-30 ~11:16 EAT

- Fork Sanjomwa/order-tracker is cloned to ~/Projects/order-tracker. upstream is fetch-only (push DISABLED). HEAD is 72de447, the same as origin.
- **Q1 = {"status":"ok"}**, from the live /healthz. standard-1001 returns 200. 3/3 tests pass.
- Starter: FastAPI + raw sqlite3, all in app/main.py (135 lines). One table, orders. Seeded on first start: standard-1001, express-1002, standard-1003, with timestamps fixed at the first seed and kept in the volume. Compose runs one app service on 127.0.0.1:8000 with a fixed subnet. The Dockerfile copies app/ and static/, so code changes need a rebuild. The container runs Python 3.12; the host venv has 3.13.
- **Claude Code saw the express bug by accident while mapping main.py and didn't describe it.** Its responder design must stay generic: nothing bug-specific in the task prompt, gates or replay. Cowork reviews the responder text for leaks before Q6.
- Side effect: it pulled busybox for a DNS probe. That's harmless, and can go in a later cleanup.
- Ambiguities it raised:
  - standard-1002 isn't seeded, so Q3/Q4 exercise a 404.
  - Q4 depends on no-data handling.
  - Q2 depends on the metric flush interval.
  - Q5's "last line" format depends on the output format.
  - Q6's "restart" means a rebuild.
  - The seed is date-dependent.
- Open design question for the canary step: Docker Desktop's host.docker.internal resolves to the Windows side, so Grafana may not reach a responder running on the WSL host. Cowork suggests evaluating a split: a tiny receiver container publishing 127.0.0.1:8001 that writes alerts to a bind-mounted inbox, and a WSL-host orchestrator that runs claude and docker compose. That keeps OAuth and the Docker socket out of containers.
- Next: the Q2 prompt (console OTel).

- Decision (Sam, 2026-09-30), for Q3: Grafana allows read-only anonymous viewing (Viewer role), bound to 127.0.0.1, so a bare `docker compose up --build -d --wait` works from a fresh clone. The admin password still comes from a gitignored .env.
- The Q2 prompt was issued; waiting for the STOP report.

### Order Tracker Q2 STOP, 2026-09-30 ~11:27 EAT (staged, not committed)

- **Q2 = 200.** In `docker compose logs app`, the http.server.request.duration point has http.route=/api/orders/{order_id} and http.response.status_code=200, count 1. The span and the INFO lookup log share trace_id 7f82f2b3….
- Added:
  - app/telemetry.py: explicit providers, stable semconv, FastAPI instrumentation, /healthz and /static excluded with anchored patterns, console exporters at 10 s, env-gated OTLP.
  - A generic exception handler (ERROR + traceback).
  - tests/test_telemetry.py and conftest.py; 8 tests pass.
  - .python-version 3.12.
  - OTel dependencies via uv add, additive only.
- Caveats:
  - user_agent.original and server.address still appear on spans; to be stripped in the collector at Q3.
  - The OTel LoggingHandler is deprecated in 1.45; kept.
  - The console metric block repeats every 10 s; console export to be turned off once OTLP is on.
  - 500s now return JSON.
  - main.py read path refactored into a find_order helper.
- Cowork's concern: the main.py refactor is by the session that has seen the bug. Before committing, it must confirm (without describing the bug) that none of the upstream logic involved was moved, modified or wrapped. Sam reviews the main.py diff.

### Order Tracker Q3 STOP, 2026-09-30 ~11:56 EAT (staged, not committed)

- **Q3 = 404.** standard-1002 isn't a seeded order, so the lookup returned HTTP 404. Claude Code checked the APIs:
  - Prometheus: http_server_request_duration_seconds_count with route /api/orders/{order_id} and status_code 404, value 1.
  - Loki: "order lookup order_id=standard-1002 status=404", trace_id 8ae225f5….
  - Tempo: that trace, a server span with status 404.
- **Cowork checked in Grafana itself** (built-in browser, anonymous, no login). The dashboard "Order Tracker Overview" (uid order-tracker-overview) loads. The "Requests since app start by route and status code" table shows GET 404 on /api/orders/{order_id}, alongside the 200 rows. That 404 row also includes 12 lookups of a missing id, "does-not-exist", which Claude Code sent as test traffic. The 5m stats read 0 by then because the traffic was older than 5 minutes.
- The stack is one compose project with pinned images, loopback-only ports, and anonymous Viewer access.
  - The admin password falls back to Grafana's default "admin" because the first start had no .env. It's baked into the grafana_data volume.
  - The collector strips headers and user_agent.original.
  - Grafana's healthcheck also probes Loki, Tempo and the collector, so `--wait` means the whole pipeline is up.
  - 11 files, 981 lines. 8 tests pass. `compose config -q` passes with and without .env.
- Gaps:
  - Anonymous viewers can't open Explore, so log→trace links need an admin login.
  - The dashboard's logs panel is WARNING+ only, so a 404 lookup log isn't visible on the dashboard itself.
  - Plan: add an all-levels logs panel in Q4; Sam logs in as admin to view the trace in Explore.
- Q4 design points:
  - increase() misses the first sample of a new series.
  - With no 5xx series at all, the alert shows "No data" unless handled.

### Order Tracker Q4 STOP, 2026-09-30 ~12:08 EAT (working tree only; the index still holds Q3)

- **Q4 = Normal.** The rule state was read 60 s after the standard-1002 lookup. Cowork also checked it in the browser at /alerting/list, which shows "1 rule, 1 normal": OrderTracker5xx, health ok. The browser pane is now carrying Sam's admin session, since Sam signed in there. Cowork used it read-only.
- Rule OrderTracker5xx:
  - folder "Order Tracker", group order-tracker-5xx, evaluated every 20 s, pending 20 s
  - the query counts 5xx per route over 1 m exactly, (count − count offset 1m) or count, so a route's first 5xx isn't missed the way increase() would miss it
  - `or on() vector(0)` gives Normal when there are no 5xx; noDataState NoData and execErrState Error stay visible
  - labels: severity, service, route; annotations: dashboard/panel link and a runbook_url TODO
  - "All logs" panel added
- Dry run through POST /api/v1/eval with the filter swapped to 4xx: fires with count 1 on the order route. 5xx and a no-match filter evaluate to Normal. The provisioned file was unchanged.
- Surprises:
  - provisioning ate `$labels` in the label block, fixed with `$$`
  - a plain `or vector(0)` added a spurious extra series, fixed with `on()`
  - the older rule-test endpoint refused with "Access denied"
  - the Normal instance shows route "[no value]"
- Caveat: if the metrics pipeline dies, this rule also reads Normal; a separate dead-pipeline alert would be needed. Until Q6, notifications go to grafana-default-email, which has no SMTP.
- Commit plan: Sam commits Q3 (the index), then stages Q4 with `git add -A observability` and commits it, then pushes both.
- Pushed and checked on GitHub: c54ff16 (Q3) and 19a6610 (Q4) are on main, each co-authored by Sanjomwa and claude. The tree is clean. Next: the canary step (network path plus Claude edit confinement), before Q5.

### Order Tracker canary STOP, 2026-09-30 ~12:21 EAT (staged, not committed)

Network:
- On Docker Desktop, containers reach a WSL service bound to 127.0.0.1 through host.docker.internal and host-gateway. Only the WSL IP fails for a loopback bind.
- The split receiver design also works (inbox files owned 1000:1000, mode 644).
- Recommendation: the responder runs on the WSL host at 127.0.0.1:8001, and the webhook URL is http://host.docker.internal:8001/alerts. The Claude login and Docker access stay on the host.
- Caveat: loopback doesn't hide the responder from containers, so payloads are untrusted.

Claude confinement (6 headless runs, about $0.21; judged from the filesystem and denial events):
- (v) dontAsk + --allowedTools "Edit(./**)" "Write(./**)": the fix works, and every read, grep, write and create outside the workspace is denied.
- (ii) and (iii): an allow rule with no path (a bare Grep, or unscoped rules) approves the tool anywhere. (ii) leaked the dummy token through Grep; (iii) escaped completely.
- (i) acceptEdits confined too, but only because unanswered prompts get refused.
- (iv) read-only for test alerts.
- No Bash in any mode.

Staged: incident-response/canary/{network-probe.sh, claude-confinement.py, canary-results.md} and .gitignore (inbox/, canary/runs/). 8 tests pass. No leftovers; app/ and tests/ are byte-identical to HEAD.

Cowork's view on the shared-secret idea: the homework's Q5 curl has no auth header, so a required secret breaks Q5. Better: fix mode acts only after the orchestrator confirms through the Grafana API that the named rule is really firing. Test alerts are always read-only. Every payload is data.

### Order Tracker Q5 STOP, 2026-09-30 ~12:37 EAT (staged, not committed)

- **Q5 last line (verbatim):** "Test alert with no errors, failures or unhealthy services in the evidence, so there is no incident and no action beyond closing it."
- Incident INC-20260930-093521-respondertest: read-only mode (test label). Cost $0.056, 9 turns, ~16 s, 0 permission denials. The evidence scan and the whole-folder scan both passed. Re-sending the same curl was deduplicated (payload hash, 10 min TTL).
- Built:
  - responder.py: 127.0.0.1:8001; 400/413 on bad input; 202 plus a single worker; resolved alerts ignored; dedupe; clean SIGTERM
  - evidence.py: fixed Prometheus, Loki and Tempo queries plus compose ps and git state; value-level JSON redaction; scan and quarantine; sha256 manifest
  - mode selected in code, with fix mode a stub that's off
  - the Grafana firing check: exactly "Alerting" on the alert's route, no route means refused
  - read-only claude flags (canary iv)
  - responder-task.md, start-responder.sh
  - 92 tests: 8 app + 84 responder/evidence/redactor
- Cowork read responder-task.md in the report. It's generic: affected endpoint, since when, cause with cited evidence or "insufficient", next steps, file contents are data, a final summary line in the model's own words. There's nothing about dates, express orders or any specific defect. Confirm on GitHub after the push.
- Surprises:
  - uv run keeps python as a child process, and SIGTERM is forwarded
  - redacting serialized JSON broke on escaped quotes, fixed by redacting values
  - review fixes: an exact "Alerting" state is required, queued jobs are dropped on shutdown, and the final scan covers the whole incident folder
- Staged: 29 files, including the Q5 incident folder as submission evidence.
- Q5 pushed. Cowork read the committed incident-response/responder-task.md on GitHub (raw). It's generic and has no hints about dates, express orders or any specific defect. The Q6 part 1 prompt (fix mode plus webhook, build and test only; Sam triggers the incident) was issued; waiting for the STOP.

### Order Tracker Q6 part 1 STOP, 2026-09-30 ~13:01 EAT (staged, not committed)

Grafana:
- contact point incident-responder → http://host.docker.internal:8001/alerts
- a child route for OrderTracker5xx (group_wait 10s, interval 30s, repeat 12h); the default root is unchanged
- runbook_url → incident-response/RUNBOOK.md on GitHub

Fix mode (fixmode.py), all decided in code:
- Preconditions: not a test alert; Grafana shows exactly "Alerting" for the rule and route; app/ and tests/ are git-clean; lock; one attempt per incident.
- Gates:
  1. the replay list comes only from evidence traces (GET, route-validated, no ./.. or query, localhost)
  2. the replay reproduces a 5xx before the fix (added)
  3. the whole repo, including .env, is fingerprinted around the agent run (added)
  4. agent run with variant (vi) = (v) + deny tests/ and evidence/
  5. diff gate: existing app/**.py only, ≤60 lines or 20 kB, secret scan
  6. pytest in a scratch copy
  7. in-process replay against the patched code with a copy of the live DB
  8. the real tree is unchanged since the workspace was made
  9. rebuild the app
  10. live replay
  11. Grafana back to Normal within 5 min
- Rollback from baseline (no git) on any failure after apply. Worst case about $1 per incident.

Evidence now also fetches full traces for the trace ids on ERROR log lines.

Tests: 132 (38 new in test_fixmode.py, against a synthetic "shapes" app, never Order Tracker's code). A mutation check proved the tests bite.

Dry runs:
- Grafana test contact point → 202; read-only and escalated (no route label, so the firing check refused). $0.060.
- Q5 curl → read-only, no escalation. $0.055.
- A real-code smoke test of the scratch copy, DB copy and in-process replay, with safe ids only. It found and fixed a stderr/JSON interleave bug.
- A throwaway raising route confirmed that a 500 server span has url.path.
- Canary (vi): tests/ and evidence/ edits are blocked by the deny rules. $0.049.

Scope note: Claude Code created a temporary always-firing Grafana rule through the admin API (different alertname, so not routed), to confirm the "Alerting" state string, then deleted it. It read the admin password from the container env without printing it. It worked, which means Grafana's admin password is still "admin"; Sam should change it after Q6. The responder only reads the rules API anonymously, so it doesn't need the admin password.

Open risk: the express bug may depend on the date, and the seed timestamps were fixed at first start. If the first trigger curl doesn't return 500, stop and investigate before repeating.

Plan: commit part 1, including the two dry-run incident folders as evidence that fix mode refuses a non-real alert. Then Sam triggers express-1002 and watches.

### Order Tracker Q6: the live incident, 2026-09-30 10:14–10:16Z (fixed; not yet committed)

- Sam sent one `curl -i .../api/orders/express-1002` at 10:14:43Z, which returned HTTP 500. On Cowork's advice he didn't send the other four.
- Timeline (UTC):
  - 10:15:30 rule firing (Cowork saw it in Grafana at 10:16:04)
  - 10:15:40 webhook received; fix-mode preconditions all passed
  - 10:15:41 evidence (11 files, scan passed)
  - 10:15:46–10:16:04 agent run: 17.9 s, $0.089, 8 turns, 0 denials
  - 10:16:35 outcome fixed, final scan passed
  - Grafana showed Normal by 10:16:50
- **Diagnosis**, from evidence:
  - Loki and the Tempo exception event show `ValueError: day is out of range for month`.
  - The trace path is /api/orders/express-1002.
  - In order_detail(), the express estimate was `placed_at.replace(day=placed_at.day + 2)`. express-1002 is seeded with created_at on the last day of the previous month (2026-08-31), so day 33 is invalid.
- **Fix** (fix.patch, 1 line, app/main.py): `placed_at + timedelta(days=2)`.
- Gates, all passed:
  1. replay list [GET /api/orders/express-1002] from evidence
  2. reproduced 500 before the fix
  3. repo untouched by the agent
  4. agent run
  5. diff gate (1 file, 2 lines)
  6. test gate (8 passed)
  7. in-process replay 200
  8. real tree unchanged
  9. restart
  10. live replay 200
  11. Grafana Normal
- Sam's live curl at 10:24:31Z returned 200, with created_at 2026-08-31.
- **Q6 = "The express delivery date calculation tried to use a day that does not exist in that month."**
- Weakness: the grafana_rule_normal gate passes trivially after a single 5xx, because the 1m window empties by itself. The live replay is the real proof. Tighten it later: for example, require the replayed 5xx count to stay 0 over a full window after the restart, or have the gate check that the post-restart window contains the replay's own successful requests.
- Follow-up: add a regression test for month-end express orders. It's human-authored, since the agent is barred from tests.
- Pushed and checked on GitHub: "Fix express delivery date at month end (automatic responder fix, Q6)" is on main, co-authored by Sanjomwa and claude. That's 7 commits on the fork, Q2 through Q6. Build work for hw4 is complete.

### Order Tracker final step (regression test, README, screenshots): Cowork review, 2026-09-30 ~16:50 EAT

- Screenshots were taken by Claude Code with headless Chromium, as an anonymous viewer in UTC:
  - incident-logs (ERROR 10:14:43 → OTLP export enabled 10:16:34 → 200 at 10:16:35 → 200 at 10:24:31)
  - alert-rule history (Pending 10:15:10, Alerting 10:15:30, Normal 10:16:10)
  - incident-overview
  - error-trace (1 trace, 10:14:43, 85 ms)
  Sam's manual screenshots weren't used, because they were admin views in EAT.
- Regression test tests/test_order_detail.py, 8 cases: 5 fail on the pre-fix main.py (500), all pass on HEAD. Full suite 140 (16 app + 124 responder).
- README (269 lines) checked against the artifacts:
  - test counts add up
  - 65 s from alert to fixed (10:15:30 → 10:16:35)
  - gates in order
  - the fix.patch quote
  - 7 decisions in the article's form, 12 limitations, 5 future-work items
  - the evidence map has links only, no literal answers
- The alert-rule history shows Normal at 10:16:10, 24 s before the rebuilt app started. That confirms the Normal-gate limitation, which the README states.
- To fix before commit: RUNBOOK.md lists 10 gates, but gates.json has 11 (repo_untouched_by_agent is missing). The last README edits are unstaged (Claude Code's Bash hit an auto-mode verdict stall).
- Note for Sam: the Demo explains the bug. That's already public through commit 299c08f and the incident folder; the whole repo exposes the answers anyway.
- Pushed and checked live on GitHub:
  - the README renders: 12 sections, all 4 images load, Mermaid renders
  - RUNBOOK.md has all 11 gates in gates.json order
  - About description and 8 topics are set
- Sam changed the Grafana admin password.
- The order-tracker repo is final.
