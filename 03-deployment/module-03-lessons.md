# Module 3 — lessons from the lesson content (article + workshop transcript)

**Not the homework spec.** This file captures technique-level lessons pulled from the Module 3 lesson materials (video: "Test, Containerize, and Deploy an AI-Assisted App," article: [Deploy a Full-Stack App with AI Coding Assistants](https://aishippingblog.com/p/deploy-a-full-stack-app-with-ai-coding)). Those materials walk through continuing the presenter's own app and deploying it to AWS — a different track from the actual graded `hw03` (Agent Relay → local Kubernetes via `kind`, resolved 2026-09-16: **`homework.md` is authoritative**, not the lesson narrative — see `status-log.md`). Logged here because the *techniques* are reusable even though the *target* isn't the one we're building toward.

## Containerization

- **Multi-stage Docker build, one container not two.** Stage 1 uses a Node image to `npm run build` the frontend into static files. Stage 2 is the backend's own image, which `COPY --from=<stage1>` pulls the compiled static files into, and the backend serves them directly (checks for `index.html`, serves the SPA). Avoids running/coordinating two separate containers for a single logical app.
- **README the run/build commands as you go**, in the same session that builds the Dockerfile — don't rely on re-asking the agent every time; you need a command you can run yourself without the agent in the loop.
- **Volume-map the database file** so container restarts don't lose data — an easy thing to forget until you notice data vanishing on restart.

## Database portability

- **ORM abstraction (SQLAlchemy) is what makes SQLite→Postgres a non-event.** Stated explicitly and on purpose from the start of the app: "don't use SQLite-specific syntax... be database agnostic," specifically so swapping to Postgres later doesn't require rewriting queries.
- Agent Relay's own starter (`alexeygrigorev/agent-relay`) is built the same way on purpose: its README states the storage seam is designed so "students can port this storage seam to PostgreSQL later without changing the HTTP protocol or lifecycle in SPEC.md" — same lesson, directly applicable to our actual hw03 work (Q4).

## Docker Compose

- Health checks matter: add a `pg_isready`-style healthcheck to the Postgres service, and make the app service `depends_on: postgres: condition: service_healthy` — without it, the app can start before Postgres is actually accepting connections.
- Compose networking: services reach each other by **service name as hostname**, not `localhost` — the app's DB connection string needs to point at the Postgres service name, not `127.0.0.1`.

## Testing strategy

- Distinct test tiers: **unit** (component-only), **integration** (real component-to-component — e.g., backend-to-real-DB), **end-to-end** (full browser automation via Playwright, driven against a running Compose stack).
- E2E/integration tests get their own top-level directory (not nested under frontend or backend) when they don't cleanly belong to just one side.
- **Don't reflexively judge or delete agent-authored tests that look pointless to you.** The presenter's stated experience: tests an agent writes often catch mistakes *the agent itself* is prone to making, even if a human wouldn't have written that specific test. Deleting one as "not useful" risks silently reintroducing a regression the agent was specifically guarding against.

## Cloud/infra-specific caution (less directly applicable to `kind`, still worth knowing)

- **Infra/deployment tasks are not a "kick it off and walk away" category**, unlike most agent coding tasks — explicitly called out as needing active supervision of every step, not a vibe-check after the fact.
- **Constrain agent-driven cloud changes to one auditable artifact.** Give the agent temporary elevated (e.g., AWS admin) access, but require it to express everything as a single Infrastructure-as-Code file (CloudFormation in this case) rather than letting it free-range across the console/CLI. Makes the blast radius reviewable and the whole thing cleanly destroyable later.
- **Revoke elevated access once the stack is validated.** Ongoing deploys after that go through CI/CD only, authenticated via OIDC (GitHub Actions assumes a narrowly-scoped IAM role via STS) — no long-lived static credentials sitting in CI secrets.
- **Cost discipline:** get a cost estimate before deploying, but also check the *actual* billed cost a day or two later — a scheduled job pulling a multi-GB Docker image every few minutes produced real, unexpected charges; the estimate and the actual can diverge by an order of magnitude.
- The CI/CD debug loop (push → watch Actions run → fix → push again) is inherently slow — budget real time for it, it's not a quick iterate-locally loop.

## Explicit scope boundary (from the lesson materials themselves)

The lesson video explicitly defers Kubernetes, managed databases (RDS), and dev/prod environment separation to a *later* module (DevOps/observability). That's a second, independent confirmation — beyond the homework.md text itself — that this specific lesson was never going to cover the Kubernetes work our actual `hw03` requires. Module 4 is presumably where that content lives instead.
