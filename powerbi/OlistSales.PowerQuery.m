// Create one blank query per section and name it as shown.
// Credentials are supplied interactively by Power BI and never embedded here.

// Query: ExecutiveKPIs
let
    Source = PostgreSQL.Database(
        "localhost:5432",
        "ecommerce_db",
        [Query = "SELECT * FROM analytics.vw_executive_kpis", CreateNavigationProperties = false]
    )
in
    Source

// Query: CategorySales
let
    Source = PostgreSQL.Database(
        "localhost:5432",
        "ecommerce_db",
        [Query = "SELECT * FROM analytics.vw_category_sales ORDER BY sales_revenue DESC", CreateNavigationProperties = false]
    )
in
    Source

// Query: MonthlySales
let
    Source = PostgreSQL.Database(
        "localhost:5432",
        "ecommerce_db",
        [Query = "SELECT * FROM analytics.vw_monthly_sales ORDER BY month_start", CreateNavigationProperties = false]
    )
in
    Source

// Query: StateSales
let
    Source = PostgreSQL.Database(
        "localhost:5432",
        "ecommerce_db",
        [Query = "SELECT * FROM analytics.vw_state_sales ORDER BY sales_revenue DESC", CreateNavigationProperties = false]
    )
in
    Source

// Query: PipelineHealth
let
    Source = PostgreSQL.Database(
        "localhost:5432",
        "ecommerce_db",
        [Query = "SELECT * FROM analytics.vw_pipeline_health", CreateNavigationProperties = false]
    )
in
    Source
