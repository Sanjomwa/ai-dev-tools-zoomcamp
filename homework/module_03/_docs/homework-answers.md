# Module 3 Homework — Questions & Answers

*AI Dev Tools Zoomcamp 2026. Answers below correspond to the questions in the official `homework.md` (DataTalksClub/ai-dev-tools-zoomcamp, `cohorts/2026/homework/03-deployment/homework.md`), in the same order, for pasting into the submission form.*

**Note:** unlike Module 1 and Module 2, the Module 3 project was not built inside this repo. Per a deliberate decision to keep it as a separate standalone repo, it lives at **https://github.com/Sanjomwa/agent-relay** — a fork of `alexeygrigorev/agent-relay`. That URL is the `homework_url` submitted on the form. This file's only job is to record the submitted answers and point to where the real work lives.

## Question 1: Architecture

**Agents claim tasks from a DB through an HTTP API.** Matches the build's actual shape — agent-initiated long-polling claims against a DB-backed queue via a FastAPI HTTP REST API — not a message broker, pub/sub, or peer-to-peer exchange.

## Question 2: Task status after the recipient submits its result

**completed.** Matches the Q2 integration test's own naming and assertion, `test_full_task_exchange_sender_sees_completed_result`.

## Question 3: Docker port publishing

**`-p`.** Matches `compose.yaml`'s own `8010:8000` port mapping for the app service.

## Question 4: Postgres hostname in Docker Compose

**`postgres`.** Matches `compose.yaml`'s `RELAY_DATABASE_URL`, which uses the service name `postgres` — Compose's internal DNS hostname — not `localhost`.

## Question 5: Kubernetes resource for replicas

**Deployment.** Matches `k8s/app.yaml`'s own Deployment resource for the app.

## Question 6: Behavior on test failure

**Keep the existing version running and stop the deployment.** Matches the deliberate test-failure verification done for Q6 — when pytest failed, the build/load/deploy steps never ran, the old pod kept serving unchanged, confirmed live via curl.

## Question 7: Reflection

_Not yet finalized._
