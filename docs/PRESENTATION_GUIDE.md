# Presentation Guide

## What to open before presenting

1. Docker Desktop: keep the Containers view visible and expand the e-commerce stack.
2. Kestra: open `http://localhost:8080`, sign in with `KESTRA_ADMIN_USERNAME` and `KESTRA_ADMIN_PASSWORD` from the ignored local `.env`, then open execution `53nPULTPqt8UbkQAGzc9dA`.
3. pgAdmin: open `http://localhost:5050`, connect to **E-commerce PostgreSQL (Docker)**, and prepare the read-only queries in `sql/verify_phase4.sql` plus `SELECT * FROM analytics.vw_executive_kpis;`.
4. Repository: open the project folder in VS Code with the README, `flows/olist_ecommerce_pipeline.yaml`, and this guide available.
5. If Power BI Desktop is available, open the report assembled from `powerbi/README.md`. Otherwise, show the source kit and explain that the live analytical views are its reporting contract.

Never display `.env`, passwords, tokens, or connection dialogs containing credentials.

## How the project works

```text
9 Olist CSV files
        |
        v
Immutable raw JSONB + ingestion lineage
        |
        v
Typed clean tables + reject evidence
        |
        v
Star schema (dimensions + order-item fact)
        |
        v
12-rule blocking/warning quality gate
        |
        v
Controlled analytics views -> Power BI

Kestra schedules and monitors every executable stage.
```

- Ingestion hashes every file and records every run. Identical files are skipped, making reruns safe and idempotent.
- Raw values remain immutable in PostgreSQL JSONB so every transformation can be traced back to source.
- The transformation converts text to valid types, normalizes geolocation occurrences, records rejects, and rebuilds a star schema at order-item grain.
- The quality framework evaluates configurable SQL rules. Any blocking failure stops downstream reporting; warning thresholds remain visible without hiding the result.
- BI views expose a stable, narrow contract so report logic does not depend on internal warehouse tables.
- Kestra runs the same tested image for ingestion, transformation, validation, and BI preparation, with retries, logs, persistence, and a Monday 03:00 Cairo schedule.

## Suggested 6–8 minute walkthrough

### 0:00–0:40 — Problem and outcome

Say: “This project converts the public nine-file Olist e-commerce dataset into a reproducible analytical platform. It preserves raw evidence, creates typed clean data, builds a star schema, enforces quality policy, schedules the workflow, and exposes controlled views for reporting.”

Show the repository README and architecture section.

### 0:40–1:40 — Runtime architecture

Show Docker Desktop. Point out:

- `ecommerce-postgres` stores raw, clean, warehouse, quality, and analytics schemas.
- `ecommerce-kestra-postgres` stores orchestration metadata.
- `ecommerce-kestra` schedules and monitors the workflow.
- pgAdmin provides a database demonstration interface.

### 1:40–2:40 — Raw ingestion and lineage

Show `scripts/ingest.py`, then explain file hashing and duplicate skipping. State the measured total: 1,550,922 raw records across nine expected files.

Say: “The successful presentation run found the same hashes and skipped duplicate inserts, proving the process is idempotent rather than duplicating data.”

### 2:40–3:40 — Cleaning and warehouse

Show the star schema documentation or analytical views. State:

- 1,289,091 clean records
- 112,650 order-item fact rows
- 0 rejected rows

Explain that the fact grain is one order item, linked to date, customer, product, seller, and geography dimensions.

### 3:40–4:40 — Data quality

Run or show `sql/verify_phase4.sql`. Explain that all 12 rules passed with zero blocking and warning failures. Mention revenue reconciliation, uniqueness, foreign keys, nonnegative measures, source completeness, view population, and the documented translation-gap threshold.

### 4:40–5:40 — Orchestration

Show Kestra execution `53nPULTPqt8UbkQAGzc9dA`. Click through the four green tasks:

1. `ingest_raw_files`
2. `build_clean_warehouse`
3. `enforce_quality_gate`
4. `prepare_bi_views`

Point out retries, logs, the Monday schedule, and final `SUCCESS` state.

### 5:40–6:40 — Business output

Show `analytics.vw_executive_kpis` in pgAdmin or the Power BI executive page. State the verified acceptance values:

- Delivered revenue: 13,221,498.11
- Delivered orders: 96,478
- Delivered items: 110,197
- Purchasing customers: 93,358
- Delivered freight: 2,198,275.64
- Average delivered order-item revenue: 137.04
- Purchase-date range: 15 September 2016 to 29 August 2018

### 6:40–7:20 — Reproducibility and close

Say: “The code, SQL, tests, Docker definitions, Kestra flow, reporting contract, evidence, and presentation assets are version controlled. Secrets and raw source files are excluded. A new machine can rebuild the system with Docker and the documented source files.”

## Likely questions

**Why store raw JSONB?** It preserves the exact source values and accommodates different CSV shapes while keeping lineage uniform.

**Why is the fact table larger than delivered orders?** The fact grain is order item, so one order can contribute multiple rows.

**How are reruns safe?** File hashes prevent duplicate raw loads, and downstream tables are rebuilt transactionally from the latest successful source runs.

**What happens when quality fails?** A blocking rule makes the quality task fail, so Kestra stops before BI preparation. Warning rules are recorded but do not block unless policy changes.

**Why use analytics views for Power BI?** They create a stable reporting contract, centralize business definitions, and reduce report-side transformation.

**Is everything automatic?** The data pipeline is fully automatic and live-verified. Creating the `.pbix`, recording narration, and publishing to a GitHub remote require the relevant desktop app, a human presenter, and authenticated account access.
