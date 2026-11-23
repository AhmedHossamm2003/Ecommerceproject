# Phase 2 Evidence

`PHASE2_VERIFICATION.md` records reproducible text evidence from the live container, ingestion, repeat-run, SQL, and restart checks. Text evidence is preferred for exact counts because it is searchable and can be reviewed in Git.

Screenshots are intentionally not fabricated. For the university submission, capture these manually after running the commands in the verification document:

1. Docker Desktop or `docker compose ps` showing healthy PostgreSQL and pgAdmin.
2. Terminal output showing a successful ingestion run with run UUID and inserted counts.
3. pgAdmin Query Tool showing per-file counts from `sql/verify_phase2.sql`.
4. pgAdmin showing one JSONB payload and its source row number.
5. A second count result after `docker compose down` and `docker compose up -d` (without `-v`).

Before taking screenshots, maximize the terminal/query pane and ensure no password, `.env` content, token, or personal path is visible.
