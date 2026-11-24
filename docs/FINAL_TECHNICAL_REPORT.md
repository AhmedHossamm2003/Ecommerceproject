# Final Technical Report

## Outcome

The project implements a reproducible local data platform for the nine-file Olist dataset. It preserves immutable raw values, creates a typed and traceable clean layer, builds a reconciled order-item star schema, enforces configurable quality policy, schedules the workflow in Kestra, and exposes controlled PostgreSQL views for Power BI.

## Implemented pipeline

```text
Olist CSVs
   -> Python streaming ingestion
   -> raw_data JSONB + ingestion lineage
   -> typed clean_data + rejects + metrics
   -> warehouse dimensions + fact_order_items
   -> configurable quality gate
   -> analytics reporting views
   -> Power BI build kit

Kestra schedules and monitors every executable stage.
```

## Phase summary

| Phase | Delivered outcome |
|---|---|
| 1 | Proposal, analytical definitions, architecture, source profile, Docker platform |
| 2 | Strict idempotent ingestion and immutable raw storage for 1,550,922 records |
| 3 | 1,289,091 typed clean rows, 112,650 fact rows, star schema, analytical views |
| 4 | Configurable blocking/warning rules with durable run and result evidence |
| 5 | Persistent Kestra service, retries, logs, weekly schedule, four-stage flow |
| 6 | Executive/pipeline-health views and a credential-free Power BI build kit |

## Data correctness

- The fact grain is one (`order_id`, `order_item_id`).
- Item revenue is sourced from `order_items.price`; freight remains separate.
- Payments and reviews are never joined directly to items, avoiding many-to-many inflation.
- Phase 3 reconciled all 112,650 item rows and 13,591,643.70 of all-status item revenue exactly.
- All 1,000,163 geolocation source rows remain represented after normalization and deduplication.
- Transformation and quality metadata identify the precise source and rule evidence for each run.

## Operational behavior

- Ordinary `docker compose up -d` starts only PostgreSQL and pgAdmin.
- One-shot profiles prevent accidental ingestion, rebuild, validation, or BI preparation.
- Raw ingestion skips identical filename/hash pairs unless deliberately forced.
- Derived tables rebuild atomically under an advisory lock.
- Quality policy returns a failing process exit code for any blocking failure.
- Kestra invokes the same tested container image and stops downstream work on a failed stage.

## Reporting contract

Power BI consumes only controlled `analytics` views. The report specification contains:

1. Executive revenue, order, item, category, monthly, and state visuals.
2. Full category/geography detail with accessible ranked bars.
3. Pipeline freshness and quality status.

The build kit does not contain credentials. A `.pbix` binary and visual screenshots require Power BI Desktop and are deliberately not fabricated in an environment where Desktop is absent.

## Reproduction

```powershell
docker compose up -d postgres pgadmin
docker compose --profile ingestion run --rm ingestion --strict-files
docker compose --profile transformation run --rm transformation
docker compose --profile quality run --rm quality
docker compose --profile bi run --rm bi-prepare
docker compose --profile orchestration up -d kestra-postgres kestra
```

See the root README, phase reports, verification SQL, `flows/README.md`, and `powerbi/README.md` for detailed operation.

## Submission boundary

The repository engineering work is complete. GitHub publication requires an authenticated remote; video narration requires a human presenter; Power BI binary creation requires Power BI Desktop. Those external/manual actions must be evidenced when performed and are not falsely claimed here.
