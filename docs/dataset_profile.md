# Dataset Profiling Report

**Profile status:** PENDING - source CSV files were not available locally on 2026-11-16.

**Integrity statement:** No row counts, missing-value counts, duplicate counts, inferred data types, or key-test results in this document have been fabricated. The Kaggle publisher describes the dataset as approximately 100,000 orders from 2016 to 2018, which satisfies the course's minimum-size selection criterion, but that publisher statement is not a locally verified CSV measurement.

Dataset source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## Local acquisition result

- No expected CSV files were found in `data/raw/`.
- The Kaggle command-line client was not installed.
- No Kaggle configuration file or Kaggle credential environment variables were detected.
- The original files were therefore not downloaded or modified.

## Expected file inventory

| Filename | Rows | Columns | Column names / inferred types | Missing values | Exact duplicates | Status |
|---|---:|---:|---|---|---:|---|
| `olist_orders_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_order_items_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_customers_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_products_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_order_payments_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_order_reviews_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_sellers_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `olist_geolocation_dataset.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |
| `product_category_name_translation.csv` | Not measured | Not measured | Pending inspection | Not measured | Not measured | Missing locally |

Expected column names and proposed logical types are documented separately in `data_dictionary.md`; they remain unverified until the CSV headers are inspected.

## Candidate key and relationship tests

| File | Candidate primary key test | Candidate foreign key tests | Current result |
|---|---|---|---|
| Orders | `order_id` | `customer_id` -> customers | Not run |
| Order items | (`order_id`, `order_item_id`) | Order, product, seller references | Not run |
| Customers | `customer_id` | None | Not run |
| Products | `product_id` | Category -> translation | Not run |
| Payments | (`order_id`, `payment_sequential`) | `order_id` -> orders | Not run |
| Reviews | Profile `review_id` and (`review_id`, `order_id`) | `order_id` -> orders | Not run |
| Sellers | `seller_id` | None | Not run |
| Geolocation | None assumed; profile postal-prefix multiplicity | None | Not run |
| Translation | `product_category_name` | None | Not run |

## Potential data-quality risks to measure

These are hypotheses for inspection, not verified findings:

- Optional lifecycle timestamps may be null for orders that did not reach later stages.
- Product categories or physical attributes may be missing.
- Review titles and messages are optional and may contain many nulls.
- Multiple items, payments, or reviews per order can multiply values in careless joins.
- Geolocation postal prefixes may have multiple rows and inconsistent city labels.
- Portuguese category labels may lack an English translation match.
- Customer and seller location text may require conservative standardization.
- Timestamp parsing and status/date consistency should be validated.

## How to create the verified profile

1. Download the dataset from Kaggle and place the nine unmodified CSV files in `data/raw/`.
2. From the repository root, run `python scripts/profile_dataset.py` (Python 3.10+; standard library only).
3. Review the regenerated report, especially key violations and unmatched foreign keys.
4. Commit the report if course policy permits derived metadata, but keep raw CSVs untracked.

The profiler records file size, SHA-256, row and column counts, headers, inferred logical types, null counts, exact duplicate counts, candidate-key results, foreign-key results, sampled distinct values, and potential quality warnings. It streams rows and does not alter source files.
