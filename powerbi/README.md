# Olist Sales Power BI build kit

This directory contains the version-controlled Phase 6 dashboard definition kit. Power BI Desktop is not installed in the validation environment, so the repository does not pretend that an unverified `.pbix` binary was generated. The SQL-facing model, Power Query, DAX measures, theme, page layout, and acceptance checklist are complete and can be assembled reproducibly in Power BI Desktop.

## Connect

1. Run `docker compose --profile bi run --rm bi-prepare`.
2. In Power BI Desktop choose **Get data > PostgreSQL database**.
3. Server: `localhost:5432`; database: `ecommerce_db`; mode: **Import**.
4. Authenticate with the PostgreSQL values from `.env`.
5. Open `OlistSales.PowerQuery.m` and create the five named queries in Power Query's Advanced Editor.
6. Add the measures in `OlistSales.Measures.dax` and import `OlistSales.Theme.json`.
7. Build the three pages exactly as specified in `DASHBOARD_SPEC.md`.

No password is stored in these files. Power BI Desktop has included its PostgreSQL provider since December 2019.

## Sources

- `analytics.vw_executive_kpis`
- `analytics.vw_category_sales`
- `analytics.vw_monthly_sales`
- `analytics.vw_state_sales`
- `analytics.vw_pipeline_health`

The views already encode delivered-order filtering and safe order-item revenue grain. Do not join payments or reviews into these dashboard queries.

## Refresh

Run the Kestra pipeline or the transformation, quality, and BI preparation services before selecting **Refresh** in Power BI Desktop. The Pipeline Health page displays the latest transformation and gate status.
