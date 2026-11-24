# Phase 3 Lab Guide

## Short explanations

1. **What changed from Phase 2?** Phase 2 preserves strings in raw JSONB. Phase 3 applies documented types and creates analysis-ready tables.
2. **Why keep a clean layer and a warehouse layer?** Clean tables stay close to source subjects; the warehouse reorganizes them for reliable reporting.
3. **What is the fact grain?** One product line inside one order, identified by (`order_id`, `order_item_id`).
4. **Why are payments and reviews outside the fact?** Both can have multiple rows per order and could multiply item revenue.
5. **Why is geolocation deduplicated?** The source has repeated coordinates. The clean table stores one normalized row and an occurrence count.
6. **What happens to invalid rows?** They are copied to `clean_data.rejected_records` with their raw payload and reason; they are never silently discarded.
7. **What is an Unknown dimension member?** Key `0` keeps facts countable when a descriptive value is missing or unmatched.
8. **How is idempotency achieved?** Each run rebuilds only derived tables from the same latest successful raw runs inside one transaction.
9. **How is revenue protected?** Fact row count and `SUM(item_price)` must exactly reconcile with clean order items before commit.
10. **What followed in later phases?** Phase 4 added configurable quality gates, Phase 5 added Kestra scheduling, and Phase 6 added Power BI-facing views and the dashboard build kit.

## Live demo

```powershell
docker compose --profile transformation run --rm transformation
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT status, clean_records, fact_records, rejected_records FROM clean_data.transformation_runs ORDER BY started_at DESC LIMIT 1;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT * FROM analytics.vw_category_sales ORDER BY sales_revenue DESC LIMIT 10;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT * FROM analytics.vw_monthly_sales ORDER BY month_start;"
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT * FROM analytics.vw_state_sales ORDER BY sales_revenue DESC;"
```

Then show `sql/verify_phase3.sql` and explain the row/revenue reconciliation result.
