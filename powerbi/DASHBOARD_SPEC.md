# Olist Sales Dashboard Specification

Use a 16:9 canvas, the supplied theme, descriptive titles, visible units, and alt text. Currency is Brazilian real (BRL) merchandise value from order-item `price`; it is not profit or cash collected.

## Page 1: Executive Overview

- Four cards: Sales Revenue, Delivered Orders, Delivered Items, Average Order Revenue.
- Horizontal bar chart: top 10 `CategorySales[product_category]` by `[Category Revenue]`, descending.
- Line and clustered column chart: `MonthlySales[month_start]`, columns `[Monthly Revenue]`, line `[Monthly Orders]` on a secondary axis.
- Ranked bar chart: top 10 `StateSales[customer_state]` by `[State Revenue]`.
- Date range subtitle from `ExecutiveKPIs[first_purchase_date]` through `last_purchase_date`.

## Page 2: Category and Geography

- Full ranked category bar chart with revenue and percentage in the tooltip.
- Full ranked customer-state bar chart; use two-letter state codes.
- Detail tables for categories and states with revenue, freight, item count, order count, and revenue percentage.
- Do not use a map as the only state comparison; the ranked bar remains the accessible primary visual.

## Page 3: Pipeline Health

- Status cards for transformation status and quality-gate status.
- Cards for clean rows, fact rows, rejected rows, rules evaluated, blocking failures, and warning failures.
- Last refresh timestamps for transformation and quality gate.
- Conditional colors: green for `success`/`passed`, red for any other terminal state, amber for warnings.

## Acceptance checks

- Sales Revenue equals 13,221,498.11 for delivered items.
- Delivered Items equals 110,197.
- Delivered Orders equals 96,478.
- The top category is `health_beauty` at 1,233,131.72.
- The top state is `SP` at 5,067,633.16.
- Monthly axis includes September 2016 through October 2018, including zero-activity months.
- Pipeline Health shows the latest quality gate as `passed` with zero blocking failures.
- No source password appears in the file, screenshot, or recording.
