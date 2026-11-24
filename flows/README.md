# Kestra orchestration

`olist_ecommerce_pipeline.yaml` is loaded automatically when the Kestra service starts. It runs the idempotent ingestion, Phase 3 transformation, and Phase 4 quality gate as separate Docker tasks on `ecommerce_network`.

The flow is scheduled for 03:00 every Monday and can also be triggered manually at `http://localhost:8080`. Each task retries once after 30 seconds and a quality-gate failure stops the execution.

Before starting Kestra, set `PIPELINE_RAW_DATA_HOST_PATH` in `.env` to the absolute host path of `data/raw`. Docker task containers receive the database password through Kestra's process environment; the password is not stored in the flow source.

Start and inspect orchestration:

```powershell
docker compose --profile orchestration up -d postgres kestra-postgres kestra
docker compose --profile orchestration ps
docker compose --profile orchestration logs kestra
```

The flow definition is preloaded from `/app/flows` by the Kestra server's `--flow-path` option.
