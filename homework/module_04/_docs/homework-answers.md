# Module 4 Homework: Questions and Answers

*AI Dev Tools Zoomcamp 2026, Homework 4: DevOps and Observability for AI-Built Apps. The answers follow the questions in the official `homework.md` (DataTalksClub/ai-dev-tools-zoomcamp, `cohorts/2026/homework/04-devops/homework.md`, published 2026-09-26), in the same order, for pasting into the submission form. Deadline: 2026-10-05T23:00:00Z (6 Oct 02:00 EAT).*

**Where the work lives.** As in Module 3, the graded project isn't in this repo. It's a fork of the published starter, [alexeygrigorev/order-tracker](https://github.com/alexeygrigorev/order-tracker), at **https://github.com/Sanjomwa/order-tracker**, which is the `homework_url` on the form. An earlier, deeper build against the draft of this homework is [Sanjomwa/agent-relay](https://github.com/Sanjomwa/agent-relay); see `04-devops/README.md`.

Each answer was read from the live stack or the committed incident records, not inferred from the code.

## Question 1: Run the app

**`{"status":"ok"}`**, the raw output of `curl http://localhost:8000/healthz` after `docker compose up --build -d --wait`.

## Question 2: Instrument one endpoint

**200.** With console export on, the `http.server.request.duration` data point in `docker compose logs app` for the `standard-1001` lookup carries `http.route=/api/orders/{order_id}` and `http.response.status_code=200`.

## Question 3: Build the telemetry pipeline

**404.** `standard-1002` isn't one of the seeded orders. Grafana's "Requests since app start by route and status code" table shows `GET 404` on `/api/orders/{order_id}`, and the matching Loki log line and Tempo trace share one trace id.

## Question 4: Configure the alert

**Normal.** A 404 isn't a 5xx, so the Grafana-managed rule `OrderTracker5xx` evaluates its no-5xx fallback to 0 and shows Normal rather than No data. Read from Grafana's rules API and the alert list page 60 s after the lookup.

## Question 5: Build the automatic responder

The responder handled the homework test alert read-only (test label), in incident `INC-20260930-093521-respondertest` ($0.056, 9 turns). The last line of its answer (`answer.md`):

> Test alert with no errors, failures or unhealthy services in the evidence, so there is no incident and no action beyond closing it.

## Question 6: Watch the agent fix the incident

**The express delivery date calculation tried to use a day that does not exist in that month.**

One `GET /api/orders/express-1002` returned 500 at 10:14:43 UTC, and `OrderTracker5xx` fired at 10:15:30. The responder received Grafana's webhook, passed every fix-mode precondition, and ran the agent in a sandboxed copy (17.9 s, $0.089). The logs and trace showed `ValueError: day is out of range for month`. `order_detail()` computed the estimate as `placed_at.replace(day=placed_at.day + 2)`, and `express-1002` was placed on 31 August. The fix is `placed_at + timedelta(days=2)`. All 11 code-enforced gates passed, including a live replay returning 200 after the rebuild, and the outcome was `fixed` at 10:16:35. Evidence: `incident-response/incidents/INC-20260930-101540-ordertracker5xx-api-orders-order-id/` and commit `299c08f` in the fork. A human-written regression test followed: 5 of its 8 cases fail on the pre-fix code.

## Reflection: one practical idea from this module

Let the model propose, and let code decide. My responder's fix reached the running app about a minute after the alert, but none of the go/no-go decisions were the model's. Code picked which request to replay (from the traces, never from the model's text), refused to run the agent until the failure reproduced, rejected any change outside `app/`, ran the tests and replayed the request before and after the restart. The agent's only job was the edit. When an AI agent acts on production, every decision that matters should live in code it can't argue with, and the model should only propose.
