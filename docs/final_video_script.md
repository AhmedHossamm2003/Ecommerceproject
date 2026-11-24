# Final Project Walkthrough Script

Target length: 6–8 minutes. A team member should narrate this script while recording the listed screens. Do not show `.env`, passwords, tokens, or connection dialogs containing secrets.

## 0:00–0:45 — Problem and architecture

Show the README and architecture diagram.

“This project turns the public Olist e-commerce files into a reproducible analytical platform. The pipeline preserves raw evidence, applies typed cleaning, builds an order-item star schema, enforces quality policy, schedules the work with Kestra, and supplies reporting views for Power BI.”

## 0:45–1:45 — Raw ingestion

Show `docker compose ps`, the nine source counts, and recent `raw_data.ingestion_runs`.

“Phase 2 streams all nine files into immutable JSONB storage. Every attempt records its filename, SHA-256, counts, timestamps, and outcome. Repeating unchanged input is safe because identical hashes are skipped.”

## 1:45–3:00 — Clean and warehouse layers

Show the Phase 3 verification result in pgAdmin.

“Phase 3 safely converts source strings into typed tables and records invalid rows rather than hiding them. The star schema contains customer, product, seller, and date dimensions with an order-item fact. All 112,650 clean item rows reach the fact table, and item revenue reconciles exactly.”

## 3:00–4:00 — Quality gate

Show `quality.gate_rules`, the latest `quality.gate_runs` row, and its results.

“Phase 4 turns validation into configurable policy. Rules have severity, thresholds, and enable flags. Every observation is stored. A blocking failure makes the job fail, which prevents a bad refresh from being treated as successful.”

## 4:00–5:00 — Kestra

Show the flow topology, schedule, latest successful execution, and task logs.

“Kestra runs ingestion, transformation, validation, and BI preparation as isolated Docker tasks. It retries transient failures once, logs each stage, persists its metadata, and schedules Monday refreshes at 3 AM Cairo time.”

## 5:00–6:30 — Power BI

Show the three report pages and refresh timestamp.

“The executive page answers which categories lead sales, how revenue and orders move monthly, and which states contribute most. The detail page supports ranking and comparison. The pipeline-health page exposes freshness and quality status. Item price is labeled as merchandise value in Brazilian real, not profit or cash collected.”

## 6:30–7:15 — Evidence and conclusion

Show automated test output, verification documents, and Git history.

“The repository includes executable SQL, tests, reproducible commands, actual run evidence, and phase-by-phase technical reports. Secrets and raw CSVs remain outside version control. This creates an auditable path from original files to business reporting.”

## Recording checklist

- [ ] PostgreSQL, pgAdmin, and Kestra health are visible.
- [ ] Latest quality gate shows `passed` and zero blocking failures.
- [ ] Power BI acceptance totals match `powerbi/DASHBOARD_SPEC.md`.
- [ ] GitHub repository and final commit are visible after publication.
- [ ] No credential, token, email password, or `.env` content appears.
- [ ] Audio is clear and the final video is watched once before submission.
