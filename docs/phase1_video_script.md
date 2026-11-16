# Phase 1 Video Walkthrough Script (3-5 minutes)

## Before recording

Replace team placeholders in `proposal.md`, regenerate the PDF, install/start Docker, download the dataset if the instructor expects a local file demonstration, and complete the runtime checks in the root README. Do not state that an item is working unless it is visible in the recording.

## 0:00-0:30 - Team and project introduction

**On screen:** Proposal cover page or repository README.

**Speaker notes:**

"Hello. We are [team names], and our project is the E-commerce Sales Data Pipeline. We selected the public Olist Brazilian E-Commerce dataset. Our long-term goal is to build a reproducible pipeline that loads, validates, transforms, and stores e-commerce data in PostgreSQL for business intelligence. This presentation covers Phase 1 only: the proposal, design, repository, and development environment."

## 0:30-1:30 - Dataset and analytical questions

**On screen:** `docs/data_dictionary.md` and `docs/dataset_profile.md`.

**Speaker notes:**

"Olist publishes anonymized order data from Brazilian marketplaces across multiple CSV files: orders, order items, customers, products, payments, reviews, sellers, geolocation, and category translation. The publisher describes about 100,000 orders from 2016 to 2018, which exceeds the course minimum. [If profiling is complete: briefly show verified row counts and quality findings. If not: say the files still require local download and the profile is intentionally marked pending.]

Our first question asks which product categories generate the highest sales revenue. Revenue uses item price and excludes freight. The second asks how monthly revenue and distinct order volumes change using the purchase timestamp. The third asks which customer states contribute the most revenue. The main analysis includes delivered orders. We avoid joining payments directly to order items because that could multiply values."

## 1:30-2:15 - Proposed architecture

**On screen:** `docs/architecture.png`.

**Speaker notes:**

"The green lane shows Phase 1: Docker Compose defines PostgreSQL and pgAdmin, both with persistent named volumes, and Git stores the repository and documentation. The blue lane is planned work: CSV ingestion, raw PostgreSQL storage, Python cleaning and transformation, analytical tables, SQL quality checks, analytical views, and Power BI. Kestra will later schedule and monitor the processing steps. The dashed style makes clear that these later components are not operational yet."

## 2:15-3:15 - Docker Compose demonstration

**On screen:** Terminal in the repository root.

**Commands:**

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose exec postgres pg_isready -U ecommerce_user -d ecommerce_db
docker compose exec postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT current_database(), current_user;"
```

**Speaker notes:**

"The resolved Compose configuration validates successfully. We start the services in detached mode. PostgreSQL becomes healthy before pgAdmin starts because pgAdmin uses a service-health dependency. The readiness and SQL commands show that PostgreSQL accepts connections and that `ecommerce_db` exists. The named volumes preserve database and pgAdmin state when containers are stopped or recreated."

If a command fails, show the failure honestly and explain the remediation; do not narrate it as a success.

## 3:15-4:15 - pgAdmin connectivity

**On screen:** Browser at `http://localhost:5050`.

**Actions:**

1. Sign in using the pgAdmin credentials from the local `.env` file without revealing the password on screen.
2. Select **E-commerce PostgreSQL (Docker)**.
3. Enter the PostgreSQL password when prompted.
4. Open Query Tool and run:

```sql
SELECT current_database(), current_user, version();
```

**Speaker notes:**

"pgAdmin reaches PostgreSQL through the Docker network using service host `postgres` and internal port 5432. The query confirms the database, user, and server version. The host browser reaches pgAdmin through port 5050."

## 4:15-4:45 - Results and next steps

**On screen:** README Phase 1 status and future phases.

**Speaker notes:**

"Phase 1 delivers the proposal, dataset documentation, analytical questions, architecture, conceptual star schema, reproducible Compose environment, and team walkthrough instructions. The next phase will inspect and ingest the original files. Later work will implement transformations, quality checks, Kestra orchestration, analytical views, and Power BI. Thank you."

## Recording checklist

- [ ] Replace all student name, ID, and role placeholders.
- [ ] Keep the recording between 3 and 5 minutes.
- [ ] Hide `.env`, passwords, tokens, email notifications, and personal paths.
- [ ] Increase terminal and browser font sizes for readability.
- [ ] Confirm Docker is running before recording.
- [ ] Show `docker compose config`, `up -d`, and `ps` with real output.
- [ ] Show both services healthy; do not use an old screenshot as evidence.
- [ ] Run an actual PostgreSQL query in the terminal.
- [ ] Run an actual PostgreSQL query through pgAdmin.
- [ ] Distinguish implemented Phase 1 components from planned future work.
- [ ] State dataset profiling status accurately.
- [ ] Confirm microphone clarity and that no credentials appear in the final video.
- [ ] Upload using the university's required method and test playback permissions.

This file prepares the walkthrough; it does not claim that the video has been recorded or uploaded.
