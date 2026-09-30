# Module 4: DevOps and Observability for AI-Built Apps

Course-following notes and build logs for Module 4 of DataTalksClub's AI Dev Tools Zoomcamp (2026 cohort). This folder holds no application code:

- `module-04-reports.md` is the step-by-step build and verification log for both Module 4 builds below.
- `screenshots/` holds the Grafana captures referenced in that log.

**The graded homework lives in a separate, standalone repo:** [Sanjomwa/order-tracker](https://github.com/Sanjomwa/order-tracker), a fork of [alexeygrigorev/order-tracker](https://github.com/alexeygrigorev/order-tracker). It holds the OpenTelemetry instrumentation, the collector/Prometheus/Loki/Tempo/Grafana stack, the Grafana alert, and the incident responder that fixed a live 5xx in about a minute behind code-enforced gates.

**An earlier, deeper build** was made against the draft of this homework, before the published version switched starter apps on 2026-09-26: [Sanjomwa/agent-relay](https://github.com/Sanjomwa/agent-relay). There a read-only responder proposes, a code-enforced policy decides and a human approves every rollback, with a security audit alongside ([report](https://github.com/Sanjomwa/agent-relay/blob/main/docs/operations-and-security-report.md)).

Submitted answers for the six graded questions and the reflection are recorded in `homework/module_04/_docs/homework-answers.md`.
