# OKRio Platform Architecture Blueprint

This blueprint summarises the technical scope for the OKRio enterprise OKR platform and maps the product requirements into a modular implementation plan.

## High-level system view

- **Frontend**: React 18 + TypeScript SPA following Feature-Sliced Design. Uses Redux Toolkit and RTK Query for state and data fetching, Chakra UI for theming (light/dark/brand). Supports PWA, offline cache, push notifications, keyboard navigation (WCAG 2.1 AA), drag-and-drop, inline editing, and localisation (RU/EN via `react-i18next`).
- **Backend**: Python 3.11 FastAPI monolith organised by domain modules (Auth, Accounts, Org, OKR, Workflow, Analytics, Notifications, Integrations, Data Connectors). Designed for future extraction of Workflow, Analytics, and Data Connectors into services. Exposes REST, WebSocket, and optional GraphQL APIs. Celery handles async workloads (reports, notifications, AD sync, connector refreshes) backed by Redis/RabbitMQ.
- **Data tier**: PostgreSQL 15 with row-level security (tenant, workspace, manager subtree, object roles) and audit trails. Redis for caching, sessions, rate-limiting. OpenSearch for full-text search (comments, OKR objects). S3-compatible storage for attachments.
- **Integrations**: Azure AD (SSO + SCIM), Microsoft Graph (Excel connectors, calendars), Jira/Azure DevOps/GitLab, Teams/Slack/Email, BI connectors (Power BI, Looker Studio), REST webhooks, API clients with granular scopes.
- **Infrastructure**: Docker images orchestrated by Kubernetes. CI/CD via GitHub Actions feeding into ArgoCD. Terraform for cloud resources. Observability with Prometheus/Grafana, OpenTelemetry tracing, centralised logging (ELK). Feature flags with LaunchDarkly/Unleash.

## Domain breakdown

### Auth & Accounts
- Azure AD OAuth 2.0 Authorization Code + PKCE; optional local login.
- Token service stores encrypted refresh tokens, enforces MFA via Azure policies.
- SCIM 2.0 endpoints to sync users/groups, map AD groups to workspaces, labels, and roles.
- Attribute-based access (workspace membership, manager subtree, dotted-line assignments, labels, AD groups, levels). Stakeholder access expressed as object-level role `viewer`.

### Org Management
- Org chart with manager/subordinate relations, dotted-line connections, workspace hierarchy (company → business unit → team → individual).
- Period management (quarter/half-year/year/custom), label manager, level manager, custom fields with validation, status lifecycle (On Track, At Risk, etc.).
- Managers derived from org tree; no explicit "manager" role.

### OKR Lifecycle
- Objective templates, best-practice validation, alignment map, weight/prioritisation, tags, initiative linkage.
- Key Results support percentage/absolute/binary/scale/KPI types, data bindings to connectors, weights, periodicity, comments, audit logs, attachments, mass operations.
- Initiatives/Projects capture tasks, metrics, RACI roles.
- Workflow: employee draft → OKR expert review → derived manager approval → activation. Closure includes self-assessment, manager review, expert validation, with audit trail and ability to return to previous stage.

### Check-ins & Communications
- Scheduled check-ins (weekly/bi-weekly) with reminders via Teams/Email, 1:1 agendas, pulse surveys, team NPS, engagement scoring.

### Analytics & Reporting
- Dashboards: Alignment, Performance, Engagement, Health. Heatmaps, waterfall, burndown, health score, confidence, workload fairness.
- Report builder with presets, export to PDF/Excel, real-time KPI widgets, drill-down, change history, hygiene score.

### Notifications
- Multi-channel delivery (Email, Teams, Slack, push, in-app). Notification manager controls frequency, quiet hours, SLA. Covers events: assignments, comments, returns, overdue actions, check-ins, digests.

### Data Connectors
- **Excel (Microsoft Graph)**: bind KR to ranges/tables; schedule/manual/webhook refresh; OAuth delegated/app permissions; data preview and freshness indicators; failure handling marks KR "At Risk (data)".
- **PostgreSQL (RO)**: bind KR to SELECT queries returning single aggregate; DSN stored in vault; allow-list of schemas/tables; on-demand/cron refresh with Redis cache; error notifications.
- Common features: one KR ↔ one binding; formula support for multi-source; data lineage and sampling logs; fail-safe freeze on errors.

## Security & Compliance

- RBAC + ABAC enforcement in service layer; PostgreSQL RLS policies aligned with tenant/workspace/manager/object-role attributes.
- OAuth scopes for API clients, idempotency keys for non-idempotent REST operations, rate limiting (sliding window), TLS 1.2+, encryption at rest, audit/security/compliance logs (ISO 27001, SOC2, GDPR).
- Secrets managed through Kubernetes Secrets + External Secrets (Vault/Key Vault) with rotation. DR strategy: Multi-AZ, RPO ≤5m, RTO ≤30m.

## DevOps & Quality

- CI/CD pipeline: linting (black, isort, mypy, eslint, stylelint) → unit/integration tests → Docker build → staging deploy → automated tests → manual approval → production. Preview environments per PR.
- Testing targets: ≥80% unit, ≥60% integration. Storybook for UI components, OpenAPI/Swagger for backend.
- Observability: synthetic monitoring, SLO/error budget tracking, Prometheus metrics, OpenTelemetry traces, correlation IDs.

## Roadmap considerations

1. **MVP foundation**: authentication, org structure, OKR CRUD with workflow, check-ins, analytics dashboards, notifications, Excel/PostgreSQL connectors (manual refresh), RBAC/ABAC/RLS.
2. **Enterprise hardening**: SCIM provisioning, automated connector schedules, BI connectors, audit exports, performance tuning, localisation polish.
3. **Intelligence layer**: Insights & Recommendations, OKR Coach with ML suggestions, hygiene/confidence scoring, what-if alignment scenarios.
4. **Ecosystem**: Marketplace, bots for Teams/Slack, learning hub, advanced reporting integrations.

This document complements the code scaffolding under `backend/` and guides future implementation of the OKRio platform.
