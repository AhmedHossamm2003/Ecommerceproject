# Proposed End-to-End Architecture

## Status legend

- **Green, solid:** implemented during Phase 1.
- **Blue, dashed:** planned for future phases; not operational yet.
- **Orange, dashed:** planned orchestration; Kestra is not installed in Phase 1.

![Proposed Olist data architecture](architecture.png)

The editable diagram source is in `architecture.mmd`. The architecture deliberately separates the reproducible Phase 1 platform from future pipeline functionality.

## Phase 1 - implemented

| Component | Purpose | Evidence |
|---|---|---|
| Git repository structure | Versioned documentation and reserved project directories | Repository files and initial commit |
| Docker Compose | Defines the local PostgreSQL and pgAdmin services | `docker-compose.yml` |
| PostgreSQL | Future raw and analytical storage platform | Container definition, health check, named volume |
| pgAdmin | Browser-based PostgreSQL administration | Container definition, persistent settings volume, predefined server |

The environment definition is complete, but runtime validation remains pending on this workstation because Docker is unavailable. That limitation does not imply that the containers have been tested successfully.

## Future phases - planned

1. The unmodified Olist CSV files will be read by a Python ingestion component.
2. Source-aligned data will be loaded into PostgreSQL raw tables.
3. Python steps will standardize types, category names, missing values, and business rules.
4. Conformed dimensions and an order-item-grain fact table will be built in PostgreSQL.
5. SQL tests will validate uniqueness, referential integrity, accepted values, and reconciliation totals.
6. SQL views will expose safe analytical datasets without one-to-many join inflation.
7. Power BI will consume the views for category, monthly trend, and customer-state reporting.
8. Kestra will schedule and monitor ingestion, transformation, loading, and validation.

## Design decisions

- **PostgreSQL is the system of record.** Separate raw and analytical layers will provide traceability without modifying source files.
- **The analytical grain is one order item.** This supports product and seller analysis while keeping revenue at the source `price` grain.
- **Delivered orders are the primary completed-sales population.** Other statuses may be shown separately but are excluded from the main revenue measures.
- **Revenue is not derived by joining payments to order items.** Both tables can contain multiple rows per order; joining them directly can multiply values.
- **Containers are local and reproducible.** Named volumes retain PostgreSQL and pgAdmin state across normal stops and container recreation.
- **Phase boundaries are explicit.** No ingestion container, Kestra service, star schema, validation framework, or dashboard is presented as implemented in Phase 1.

## Runtime and connectivity

Both services share `ecommerce_network`. From the host, PostgreSQL is available on the configured host port (default `5432`) and pgAdmin on `http://localhost:5050`. From pgAdmin, the database host is the Compose service name `postgres`, never `localhost`.

The predefined pgAdmin entry uses the `.env.example` defaults (`ecommerce_db` and `ecommerce_user`) and prompts for the database password. If those two values are changed, update or recreate the pgAdmin server registration.
