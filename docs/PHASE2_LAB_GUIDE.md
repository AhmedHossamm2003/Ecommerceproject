# Phase 2 Lab Discussion Guide

## Questions every team member should be able to answer

1. **What is data ingestion?** It is the controlled movement of data from a source into storage where later pipeline steps can use it.
2. **Why use Docker?** Docker gives each teammate the same Python, PostgreSQL, and dependency versions without a machine-specific setup.
3. **Why a separate ingestion container?** It has one job, can exit clearly with success/failure, and does not mix application dependencies into PostgreSQL or pgAdmin.
4. **What is PostgreSQL?** It is the relational database that persistently stores run metadata and raw JSONB records.
5. **What is raw data storage?** It is the first database layer, before business cleaning or analytical modeling.
6. **Why preserve original records?** Later rules can change. Keeping raw values makes transformations auditable and repeatable.
7. **Why JSONB?** The nine CSVs have different columns. One JSONB landing table can retain every file's headers and string values without premature type decisions.
8. **Raw versus clean data?** Raw data mirrors parsed source values. Clean data has validated types, standardized values, deduplication rules, and business decisions; clean data begins in Phase 3.
9. **How do logs work?** Python writes UTC logs to stdout with run UUID, filename, file size/hash, counts, duration, status, and errors. Docker displays the same output.
10. **What if PostgreSQL is unavailable?** Compose waits for health and Python retries. If the database stays unavailable, the process exits nonzero and never claims success.
11. **How are missing values detected?** Profiling counts empty fields and documented null-like markers. Ingestion itself preserves the original strings.
12. **How are duplicates detected?** A compact hash identifies exact repeated rows; candidate key tuples identify likely business-key repetition. Nothing is removed.
13. **What happens on a second execution?** SHA-256 matches the prior successful file, the new attempt is recorded as skipped, and the raw count stays unchanged. `--force` creates a deliberate additional run.
14. **How is persistence proved?** Query counts, run metadata, and sample JSONB; run `docker compose down` without `-v`; start again; run the same queries and compare counts.
15. **How will Phase 3 use this?** It will read successful raw runs, cast and validate columns, make documented cleaning decisions, and build relational/analytical models.

## Short live demo (about five minutes)

From PowerShell in the repository root:

```powershell
docker compose ps
docker compose run --rm ingestion --skip-profile
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, COUNT(*) FROM raw_data.records GROUP BY source_file ORDER BY source_file;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, status, records_inserted, started_at FROM raw_data.ingestion_runs ORDER BY started_at DESC LIMIT 12;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT source_file, source_row_number, raw_payload FROM raw_data.records ORDER BY raw_record_id LIMIT 1;"
Get-Content docs\phase2_data_profile.md -TotalCount 35
```

Explain that the rerun logs show `skipped`, then prove the count did not increase. Open pgAdmin only if the instructor wants a GUI view.

For the persistence demonstration:

```powershell
docker compose down
docker compose up -d postgres pgadmin
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT COUNT(*) AS raw_records_after_restart FROM raw_data.records;"
```

Never add `-v` or `--volumes` to the persistence demo.
