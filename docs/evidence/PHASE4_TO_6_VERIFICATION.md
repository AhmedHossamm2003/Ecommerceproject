# Phases 4–6 Verification Evidence

## Validation performed on 24 November 2026

- Docker Desktop 4.99.0 and Docker Engine 29.9.3 were running.
- PostgreSQL, pgAdmin, Kestra PostgreSQL, and Kestra were live; the database and orchestration services were healthy.
- The production image built successfully and all 24 tests passed inside that image.
- The combined Compose configuration parsed successfully.
- `powerbi/OlistSales.Theme.json` passed JSON parsing.
- Kestra 2.0 loaded revision 1 of `university.ecommerce.olist_ecommerce_pipeline` with its weekly Cairo schedule enabled.
- Manual Kestra execution `53nPULTPqt8UbkQAGzc9dA` completed with state `SUCCESS`.

## Phase 2–3 results from the successful Kestra execution

- All nine source files were found. Their unchanged hashes matched prior successful runs, so ingestion correctly skipped duplicate loading and exited with code 0.
- Raw records remained at 1,550,922.
- Transformation run `d28e2e3c-3736-42ac-add4-00a513f46e8b` succeeded.
- Clean records: 1,289,091.
- Fact records: 112,650.
- Rejected records: 0.

## Phase 4 quality gate

- Quality run `49b8608d-c25a-44f6-a372-f0a026048f56` passed.
- 12 enabled rules were evaluated.
- Blocking failures: 0.
- Warning failures: 0.
- Delivered revenue was positive at 13,221,498.11.
- Product translation gaps were 13, equal to the accepted threshold of 13.
- Fact row, revenue, foreign-key, grain, nonnegative-measure, geolocation, source-count, and transformation-status checks all passed.

Use `sql/verify_phase4.sql` for the read-only database proof query.

## Phase 5 orchestration

- Kestra and its PostgreSQL metadata store persist in named volumes.
- The four tasks ran in order: ingestion, clean-warehouse build, quality gate, and BI preparation.
- Each task completed with state `SUCCESS` in execution `53nPULTPqt8UbkQAGzc9dA`.
- Tasks run on `ecommerce_network`, inherit credentials through environment variables, and retry once after 30 seconds.
- The flow is scheduled for 03:00 every Monday in `Africa/Cairo`.
- Kestra basic authentication is sourced from ignored local environment variables.
- Docker task mounts are enabled explicitly for Kestra 2.0. On Docker Desktop for Windows, the raw bind source uses the daemon-visible `/run/desktop/mnt/host/c/...` path.

## Phase 6 reporting

- BI preparation completed successfully in the same Kestra execution.
- Delivered sales revenue: 13,221,498.11.
- Delivered orders: 96,478.
- `analytics.vw_executive_kpis`, `analytics.vw_pipeline_health`, monthly sales, category sales, and state sales are live.
- The reporting contract returns 26 monthly rows, 72 category rows, 27 state rows, and one pipeline-health row.
- The Power BI kit contains controlled Power Query sources, DAX measures, an accessible theme, a three-page specification, and acceptance values.
- No credential is stored in reporting assets.

Power BI Desktop is not installed on this workstation. The source-controlled BI build kit and database views are verified, but creating and visually reviewing a `.pbix` remains a manual action on a machine with Power BI Desktop.

## Presentation evidence to capture

1. Docker Desktop showing the healthy PostgreSQL and Kestra services.
2. Kestra execution `53nPULTPqt8UbkQAGzc9dA` with all four green tasks.
3. The 12 passing quality-rule logs or the result of `sql/verify_phase4.sql`.
4. Executive KPI and pipeline-health views in pgAdmin.
5. The three Power BI pages after the source kit is assembled in Power BI Desktop.
6. The GitHub repository after an authenticated remote is connected and the final commit is pushed.
