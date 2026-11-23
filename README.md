# E-commerce Sales Data Pipeline

University data engineering project using the [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Phases 1-3 now provide the local environment, immutable raw ingestion, typed cleaning, an auditable star schema, and analysis-ready PostgreSQL views.

## Project overview

E-commerce data is distributed across orders, items, customers, products, sellers, payments, reviews, and locations. Phase 1 established the proposal, conceptual architecture, database model, repository, and local PostgreSQL/pgAdmin environment. Phase 2 ingests unchanged parsed source values into an auditable PostgreSQL raw layer. Phase 3 converts the latest successful raw runs into typed clean tables, a reconciled order-item star schema, and category, monthly, and state sales views. Configurable quality gates, orchestration, and Power BI remain future work.

The official source files have now been inspected locally. The verified profile contains 99,441 orders, 112,650 order items, 99,441 customer records, 32,951 products, 103,886 payment records, 99,224 reviews, 3,095 sellers, 1,000,163 geolocation rows, and 71 category translations. Raw files remain excluded from Git; reproducible hashes and measured quality results are recorded in `docs/dataset_profile.md`.

## Analytical questions

1. Which product categories generate the highest sales revenue?
2. How do monthly sales revenue and distinct order volumes change over time?
3. Which Brazilian customer states contribute the most to total sales revenue?

Primary product-sales revenue is `SUM(order_items.price)`, excluding freight. Primary analysis includes delivered orders, counts orders with `COUNT(DISTINCT order_id)`, groups months by `order_purchase_timestamp`, and attributes geography to customer state. Payments are not directly joined to order items because both can contain multiple records per order.

## Architecture

![Proposed architecture](docs/architecture.png)

Implemented through Phase 3: Docker Compose, PostgreSQL, pgAdmin, persistent named volumes, one-shot Python ingestion/transformation containers, immutable JSONB raw storage, typed clean tables, transformation lineage, reject/metric evidence, a star schema, and analytical views. Kestra, configurable quality gates, and Power BI are future work. The original Phase 1 proposal diagram remains in `docs/architecture.md` and `docs/architecture.mmd`; implemented details are in the Phase 2 and Phase 3 technical reports.

## Technology stack

| Technology | Phase 1 use | Status |
|---|---|---|
| Git/GitHub | Version control and collaboration | Local Git initialized; remote must be added |
| Docker Compose | Reproducible local services | Configuration and WSL 2 runtime validated |
| PostgreSQL 17.12 | Raw, clean, warehouse, and analytical data store | Running and verified through Phase 3 |
| pgAdmin 4 9.19 | Database administration | Container healthy; HTTP, login, server registration, and connection tested |
| Python 3.12 | Streaming ingestion, profiling, and transformation control | Implemented in one-shot containers |
| psycopg 3 | PostgreSQL connection and COPY loading | Implemented |
| Mermaid | Architecture source | Diagram source supplied |
| Kestra | Future orchestration | Planned only |
| Power BI | Future dashboard | Planned only |

## Repository structure

```text
ecommerce-sales-pipeline/
|-- config/pgadmin/servers.json  # Default Docker server registration
|-- data/
|   |-- raw/                    # Local unmodified CSVs; ignored by Git
|   `-- README.md
|-- docs/
|   |-- proposal.md / proposal.pdf
|   |-- phase1_presentation_brief.md
|   |-- architecture.md / architecture.mmd / architecture.png
|   |-- database_design.md
|   |-- dataset_profile.md
|   |-- data_dictionary.md
|   |-- environment_validation.md
|   |-- phase1_video_script.md
|   |-- PHASE2_TECHNICAL_REPORT.md
|   |-- PHASE2_LAB_GUIDE.md
|   |-- PHASE3_TECHNICAL_REPORT.md
|   |-- PHASE3_LAB_GUIDE.md
|   |-- phase2_data_profile.md / phase2_data_profile.csv
|   `-- evidence/
|-- flows/README.md             # Reserved for later Kestra work
|-- scripts/
|   |-- ingest.py / transform.py / ingestion/
|   |-- Dockerfile / requirements.txt
|   |-- profile_dataset.py
|   |-- generate_artifacts.py
|   |-- generate_presentation_brief.py
|   `-- README.md
|-- output/pdf/
|   `-- ecommerce_phase1_presentation_brief.pdf
|-- sql/
|   |-- 02_raw_storage.sql
|   |-- 03_phase3_schema.sql / 04_phase3_transform.sql
|   `-- verify_phase2.sql / verify_phase3.sql
|-- tests/                      # Synthetic ingestion and SQL safety tests
|-- docker-compose.yml
|-- .env.example
|-- .gitignore
`-- README.md
```

## Prerequisites

- Git
- Docker Desktop with Docker Compose v2
- A browser for pgAdmin
- Python 3.10+ only when regenerating the dataset profile or documentation artifacts
- Kaggle account and accepted dataset terms to download the source data

Confirm Docker is running:

```bash
docker --version
docker compose version
docker info
```

## First-time environment setup

1. Clone the repository and enter its root.
2. Create a local environment file:

   **PowerShell**

   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS/Linux**

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and replace both example passwords. Do not commit `.env`.
4. Validate and start the services:

   ```bash
   docker compose config
   docker compose up -d
   docker compose ps
   ```

5. Wait until both services show `healthy`. Inspect logs if needed:

   ```bash
   docker compose logs postgres
   docker compose logs pgadmin
   ```

## PostgreSQL connection

From a host database client:

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `POSTGRES_PORT` from `.env` (default `5432`) |
| Database | `POSTGRES_DB` (default `ecommerce_db`) |
| Username | `POSTGRES_USER` (default `ecommerce_user`) |
| Password | `POSTGRES_PASSWORD` from `.env` |

Verify from inside the container without exposing the password:

```bash
docker compose exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT current_database(), current_user;"
```

If the shell has not loaded `.env` variables, substitute the configured values explicitly. With the `.env.example` non-secret names:

```bash
docker compose exec postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT current_database(), current_user;"
```

## pgAdmin access

Open `http://localhost:5050` (or the configured `PGADMIN_PORT`) and sign in with `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`.

A server named **E-commerce PostgreSQL (Docker)** is pre-registered with:

| Setting | Value |
|---|---|
| Host | `postgres` |
| Port | `5432` |
| Maintenance database | `ecommerce_db` |
| Username | `ecommerce_user` |
| Password | Enter `POSTGRES_PASSWORD` when prompted |

Inside Docker, pgAdmin must use host `postgres`, not `localhost`. The predefined registration reflects `.env.example`; if the database or username is changed, edit the server properties in pgAdmin. No database password is stored in version control.

## Verify the environment

```bash
docker compose config
docker compose ps
docker compose exec postgres pg_isready -U ecommerce_user -d ecommerce_db
docker compose exec postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT datname FROM pg_database WHERE datname = 'ecommerce_db';"
docker volume inspect ecommerce_postgres_data
docker volume inspect ecommerce_pgadmin_data
```

In pgAdmin, expand the predefined server, enter the database password, open **Query Tool**, and run:

```sql
SELECT current_database(), current_user, version();
```

Do not report the pgAdmin browser check as successful until this query has actually run.

## Stop, preserve, or reset data

Stop containers while preserving both named volumes:

```bash
docker compose stop
```

Remove containers and network while preserving data:

```bash
docker compose down
```

Start again with the retained data:

```bash
docker compose up -d
```

To permanently reset both PostgreSQL and pgAdmin state, first back up anything important, then run the following **only with team approval**:

```bash
docker compose down --volumes
```

This destructive command is documented but was not executed during Phase 1.

## Dataset acquisition and profiling

Download the nine CSV files from the official Kaggle page and copy them unchanged to `data/raw/`. The files are ignored by Git. If Kaggle CLI is configured, a typical command is:

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

Never commit `kaggle.json`, tokens, or raw CSVs. Generate the verified local profile with:

```bash
python scripts/profile_dataset.py
```

On this workstation the command completed successfully against the official files. Other team members can compare the recorded SHA-256 hashes to confirm that they downloaded the same inputs.

## Phase 2: raw ingestion

### What it does

The one-shot ingestion service discovers the nine expected CSVs, validates strict CSV structure, calculates SHA-256, initializes the non-destructive `raw_data` schema, and streams every record into `raw_data.records` with PostgreSQL `COPY`. It records each attempt in `raw_data.ingestion_runs` and then regenerates a full initial profile.

Source values are not cleaned, trimmed, converted, filtered, or deduplicated. Empty fields stay empty strings in JSONB. JSONB is a parsed representation, not a byte-for-byte copy; the read-only files in `data/raw/` remain the exact originals.

### Build and run

The Compose service uses the existing network and waits for PostgreSQL health. It is behind an optional profile, so ordinary startup does not trigger ingestion.

```powershell
docker compose up -d postgres pgadmin
docker compose --profile ingestion build ingestion
docker compose --profile ingestion run --rm ingestion --strict-files
```

The command exits `0` only when ingestion and profiling complete successfully. Logs are written to stdout and include UTC timestamps, run UUID, filename, byte size/hash, read/insert/skip counts, duration, status, and errors. HTTP status codes are not applicable to local CSV ingestion.

### Idempotency and reruns

A successful filename/SHA-256 pair is skipped by default on later executions, so accidental reruns do not duplicate raw records:

```powershell
docker compose --profile ingestion run --rm ingestion --skip-profile
```

Use `--force` only when an additional immutable ingestion run is deliberate. It preserves all earlier runs:

```powershell
docker compose --profile ingestion run --rm ingestion --force --skip-profile
```

Generate the profile without a database connection:

```powershell
docker compose --profile ingestion run --rm --no-deps ingestion --profile-only --strict-files
```

### Inspect raw storage

```powershell
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, COUNT(*) FROM raw_data.records GROUP BY source_file ORDER BY source_file;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, status, records_read, records_inserted, started_at FROM raw_data.ingestion_runs ORDER BY started_at DESC;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, source_row_number, raw_payload FROM raw_data.records ORDER BY raw_record_id LIMIT 1;"
```

If `.env` uses different database/user names, substitute them. In pgAdmin, open Query Tool on `ecommerce_db` and execute `sql/verify_phase2.sql`.

### Run tests

Tests use only clearly labeled synthetic fixtures and never represent test data as Olist results:

```powershell
docker compose --profile ingestion run --rm --no-deps --entrypoint python ingestion -m unittest discover -s /app/tests -v
```

The suite covers strict parsing, a missing file, string preservation, repeated execution, forced execution, metadata behavior, profile calculations, report generation, and failure status.

### Verify persistence

First record the grouped counts, then recreate containers without deleting volumes:

```powershell
docker compose down
docker compose up -d postgres pgadmin
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, COUNT(*) FROM raw_data.records GROUP BY source_file ORDER BY source_file;"
```

The before/after results must match. Never use `docker compose down -v` for this test because `-v` deletes the persistent database volume.

### Phase 2 documentation

- Technical design and handoff: `docs/PHASE2_TECHNICAL_REPORT.md`
- Full verified profile: `docs/phase2_data_profile.md` and `.csv`
- Read-only verification SQL: `sql/verify_phase2.sql`
- Lab discussion/demo: `docs/PHASE2_LAB_GUIDE.md`
- Actual execution evidence and screenshot checklist: `docs/evidence/`

## Phase 3: clean data and analytical warehouse

### What it does

The manual one-shot transformation selects the latest successful Phase 2 run for each of the nine source files. It safely converts raw strings into typed source-aligned tables, records structurally invalid rows without changing raw storage, and rebuilds a reporting star schema in one transaction.

The fact grain is one order item, identified by (`order_id`, `order_item_id`). Payments and reviews stay in the typed clean layer so their one-to-many relationship with orders cannot multiply item revenue. Exact normalized geolocation duplicates are collapsed while `source_occurrence_count` preserves the source-row total.

### Build and run

```powershell
docker compose up -d postgres pgadmin
docker compose --profile transformation build transformation
docker compose --profile transformation run --rm transformation
```

The service uses an advisory transaction lock, replaces only derived clean/warehouse data, and preserves raw records plus historical transformation metadata. Rerunning with unchanged raw inputs produces the same derived counts.

### Inspect and verify

```powershell
Get-Content -Raw sql\verify_phase3.sql | docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db
```

The verification covers lineage, clean counts, rejects, quality metrics, dimension/fact counts, item row and revenue reconciliation, geolocation occurrence reconciliation, and the three analytical views:

- `analytics.vw_category_sales`
- `analytics.vw_monthly_sales`
- `analytics.vw_state_sales`

The verified official dataset produced 1,289,091 clean rows, 112,650 fact rows, zero rejected rows, and exactly reconciled item revenue of 13,591,643.70. The geolocation clean table contains 738,332 normalized rows representing all 1,000,163 source rows.

### Phase 3 documentation

- Technical design and results: `docs/PHASE3_TECHNICAL_REPORT.md`
- Read-only verification SQL: `sql/verify_phase3.sql`
- Lab discussion/demo: `docs/PHASE3_LAB_GUIDE.md`
- Actual execution evidence: `docs/evidence/PHASE3_VERIFICATION.md`

## Current project status

- Proposal Markdown and rendered PDF: complete.
- Concise four-page presentation and email PDF: complete.
- Architecture and conceptual database design: complete.
- Compose, PostgreSQL, pgAdmin, health checks, volumes, and network: configured and validated live.
- Local Git repository and initial commit: complete.
- Dataset profile: complete and verified against all nine official CSV files.
- Docker runtime validation: complete using Docker Desktop 4.99.0 with the WSL 2 backend; both services are healthy.
- Phase 2 immutable ingestion: complete for all nine official files (1,550,922 raw rows).
- Phase 3 typed clean layer, star schema, reconciliation, and analytical views: complete and verified.
- Video: script and checklist complete; recording is a manual team action.
- GitHub publication: pending creation/connection of a remote and authenticated push.

## Publish to GitHub

Create an empty GitHub repository named `ecommerce-sales-pipeline` without adding a README, license, or `.gitignore`, then connect and push this existing local repository:

```bash
git remote add origin https://github.com/hossamadel7/ecommerce-sales-pipeline.git
git remote -v
git push -u origin main
```

If `origin` already exists but points to the wrong repository, inspect it first and then deliberately update it:

```bash
git remote -v
git remote set-url origin https://github.com/hossamadel7/ecommerce-sales-pipeline.git
git push -u origin main
```

Do not report the repository as published until the push succeeds and the files are visible on GitHub.

## Future phases

Phase 4 will add configurable automated quality gates, Phase 5 will add Kestra orchestration, and Phase 6 will add Power BI. None is falsely marked operational in this repository.

## Troubleshooting

### `docker` is not recognized

Install Docker Desktop, enable its Compose v2 plugin, restart the terminal, and verify `docker info` succeeds.

### Port 5432 or 5050 is already in use

Change `POSTGRES_PORT` or `PGADMIN_PORT` in `.env`. Internal container ports remain 5432 and 80.

### PostgreSQL is unhealthy

Run `docker compose logs postgres`. Check that the password is non-empty and that an old volume was not initialized with different credentials. Changing `.env` does not rewrite users in an existing database volume.

### pgAdmin cannot connect

Use host `postgres`, port `5432`, and the PostgreSQL credentials - not the pgAdmin login. Confirm `docker compose ps` shows PostgreSQL healthy.

### pgAdmin login or server appears unchanged

The persistent `pgadmin_data` volume retains settings. The Compose configuration replaces predefined server definitions at startup, but it does not reset the pgAdmin account database. Reset only with explicit team approval.

### Dataset profiler reports missing files

Confirm all filenames exactly match the expected list and are directly inside `data/raw/`, not in a nested extracted directory.

### Ingestion reports PostgreSQL unavailable

Run `docker compose ps` and `docker compose logs postgres`. Confirm PostgreSQL is healthy and that the ingestion container uses host `postgres`, not `localhost`.

### An unchanged file is skipped

This is expected idempotent behavior. Check `raw_data.ingestion_runs` for the earlier successful filename/hash. Use `--force` only for a deliberate additional raw run.

### Transformation reports missing successful source runs

Run Phase 2 ingestion first and verify that every expected filename has a successful row in `raw_data.ingestion_runs`. Skipped and failed attempts are intentionally excluded from Phase 3 source selection.

### A transformation fails

Inspect the transformation service output and `clean_data.transformation_runs.error_message`. The derived rebuild is atomic: a failed guard rolls back the clean/warehouse changes while leaving raw storage untouched.

### Profiling takes time or memory

The profile scans every row and retains compact row digests to calculate full exact-duplicate counts. This is intentional, especially for the one-million-row geolocation file. It does not use sampling.

## References

- [Olist dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [PostgreSQL official Docker image](https://hub.docker.com/_/postgres)
- [pgAdmin container deployment](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html)
- [Docker Compose startup order and health dependencies](https://docs.docker.com/compose/how-tos/startup-order/)
- [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html)
