# E-commerce Sales Data Pipeline

## Phase 1 Presentation Brief

**Course:** Data Engineering  
**Dataset:** Olist Brazilian E-Commerce Public Dataset  
**Submission date:** 19 November 2026

### Team

| Student | University ID | Phase 1 role |
|---|---:|---|
| Ahmed Hossam Ahmed | 692400737 | Project coordination and data engineering |
| Karim Khaled | 692300126 | Database design and SQL |
| Moaz Ahmed | 692300067 | Docker environment and documentation |

## 1. Project scope

Olist stores orders, items, customers, products, sellers, payments, reviews, and locations in separate CSV files. This makes consistent analysis difficult and creates a risk of duplicated revenue when one-to-many files are joined incorrectly.

Phase 1 establishes the verified dataset, analytical definitions, proposed architecture, conceptual database design, Git repository, and a reproducible Docker environment. It intentionally does not implement the later ingestion pipeline, star schema, Kestra flows, or Power BI dashboard.

### Verified dataset

| Source | Rows | Main content |
|---|---:|---|
| Orders | 99,441 | Status and timestamps |
| Order items | 112,650 | Product, seller, price, freight |
| Customers | 99,441 | Customer identifiers and state |
| Products | 32,951 | Category and physical attributes |
| Payments | 103,886 | Payment methods and values |
| Reviews | 99,224 | Scores and optional comments |
| Sellers | 3,095 | Seller location |
| Geolocation | 1,000,163 | Postal-prefix coordinates |
| Category translation | 71 | Portuguese to English categories |

### Primary analytical questions

1. Which product categories generate the highest sales revenue?
2. How do monthly sales revenue and distinct order volumes change over time?
3. Which Brazilian customer states contribute the most to total sales revenue?

### Agreed analytical rules

- Sales revenue is `SUM(order_items.price)` and excludes freight.
- Primary completed-sales analysis uses delivered orders.
- Order volume uses distinct `order_id`.
- Monthly grouping uses `order_purchase_timestamp`.
- Geographic analysis uses customer state.
- Payments are not joined directly to order items, avoiding revenue duplication.

## 2. Proposed architecture and database design

The future workflow is:

Olist CSV files -> Python ingestion -> PostgreSQL raw storage -> Python cleaning and transformation -> PostgreSQL analytical tables -> SQL quality validation -> SQL views -> Power BI.

Kestra will orchestrate the later ingestion, cleaning, loading, and validation steps.

### Phase boundary

**Implemented in Phase 1:** repository structure, Docker Compose, PostgreSQL, pgAdmin, persistent volumes, dataset profiling, architecture, and documentation.

**Planned for later phases:** ingestion code, populated raw tables, transformations, star schema, automated quality checks, Kestra flows, analytical views, and Power BI.

### Conceptual star schema

- `dim_customers`
- `dim_products`
- `dim_sellers`
- `dim_date`
- `fact_order_items`

The fact-table grain is one order item. The natural uniqueness rule is (`order_id`, `order_item_id`). Missing dimension references will map to explicit unknown members instead of dropping facts.

## 3. Environment proof and readiness

| Check | Verified result |
|---|---|
| Docker Compose | Configuration resolved successfully |
| PostgreSQL | Version 17.12; healthy |
| pgAdmin | Version 9.19; healthy |
| Database | `ecommerce_db` exists |
| Database user | `ecommerce_user` authenticated |
| pgAdmin HTTP | `200 PING` |
| Browser connection | pgAdmin displayed **Server connected** |
| Persistence | PostgreSQL and pgAdmin named volumes use the local driver |

### Submission status

- Short presentation PDF: ready.
- Full academic proposal: ready.
- Local Git repository: ready and clean.
- Docker demonstration: ready and running.
- Video script: ready; recording remains a team action.
- GitHub publication: requires creation of the remote repository and push.

## References

1. Olist, *Brazilian E-Commerce Public Dataset*, Kaggle: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. PostgreSQL documentation: https://www.postgresql.org/docs/
3. Docker Compose documentation: https://docs.docker.com/compose/
4. pgAdmin container documentation: https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html
