# Phase 2 Initial Data Profile

**Status:** VERIFIED AGAINST THE LOCAL UNMODIFIED CSV FILES

**Generated:** 2026-11-23 14:28:38 UTC

This is a full streaming profile, not a sample. Empty strings and the case-insensitive markers `null`, `none`, `na`, `n/a`, and `nan` are counted as missing for profiling only. Raw ingestion preserves the original parsed strings, including empty strings.

## File summary

| Source file | Rows | Columns | Exact duplicate rows | Size (bytes) | SHA-256 |
|---|---:|---:|---:|---:|---|
| `olist_orders_dataset.csv` | 99,441 | 8 | 0 | 17,654,914 | `8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf` |
| `olist_order_items_dataset.csv` | 112,650 | 7 | 0 | 15,438,671 | `0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279` |
| `olist_customers_dataset.csv` | 99,441 | 5 | 0 | 9,033,957 | `983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2` |
| `olist_products_dataset.csv` | 32,951 | 9 | 0 | 2,379,446 | `3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc` |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | 0 | 5,777,138 | `4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0` |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | 0 | 14,451,670 | `012b61c7593e34f51fa614efdf802b9c7056ce6aae5307ddb93236e7cfc797d7` |
| `olist_sellers_dataset.csv` | 3,095 | 4 | 0 | 174,703 | `1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e` |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | 261,831 | 61,273,883 | `b514f6fc991b9566aeba02aa5d67e2c3630f034b60a0e05aa0d082a3b66d88d6` |
| `product_category_name_translation.csv` | 71 | 2 | 0 | 2,613 | `a81f0d1f27b27e7293f761bc79e3ce8f348ee39c4b3ed3e49bde38f478586278` |

## `olist_orders_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `order_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | e481f51cbdc54678b7cc49136f2d6af7, 53cdb2fc8bc7dce0b6741e2150273451, 47770eb9100c2d0c44946d9cf07ec65d |
| `customer_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 9ef432eb6251297304e76186b10a928d, b0830fb4747a6c6d20dea0b8c802d7ef, 41ce2a54c0b03bf3443c3d931a367089 |
| `order_status` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | delivered, invoiced, shipped |
| `order_purchase_timestamp` | TIMESTAMP | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 2017-10-02 10:56:33, 2018-07-24 20:41:37, 2018-08-08 08:38:49 |
| `order_approved_at` | TIMESTAMP | 160 | 0.16% | 0 | 0 | 0 | 0 | 0 | 2017-10-02 11:07:15, 2018-07-26 03:24:27, 2018-08-08 08:55:23 |
| `order_delivered_carrier_date` | TIMESTAMP | 1,783 | 1.79% | 0 | 0 | 0 | 0 | 0 | 2017-10-04 19:55:00, 2018-07-26 14:31:00, 2018-08-08 13:50:00 |
| `order_delivered_customer_date` | TIMESTAMP | 2,965 | 2.98% | 0 | 0 | 0 | 0 | 0 | 2017-10-10 21:25:13, 2018-08-07 15:27:45, 2018-08-17 18:06:29 |
| `order_estimated_delivery_date` | TIMESTAMP | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 2017-10-18 00:00:00, 2018-08-13 00:00:00, 2018-09-04 00:00:00 |

Candidate business-key checks:

- PASS: (order_id); missing-key rows=0; duplicate-key rows=0

## `olist_order_items_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `order_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 00010242fe8c5a6d1ba2dd792cb16214, 00018f77f2f0320c557190d7a144bdd3, 000229ec398224ef6ca0657da4fc703e |
| `order_item_id` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 1, 2, 3 |
| `product_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 4244733e06e7ecb4970a6e2683c13e61, e5f2d52b802189ee658865ca93d83a8f, c777355d18b72b67abbeef9df44fd0fd |
| `seller_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 48436dade18ac8b2bce089ec2a041202, dd7ddc04e1b6c2c614352b383efe2d36, 5b51032eddd242adc84c38acab88f23d |
| `shipping_limit_date` | TIMESTAMP | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 2017-09-19 09:45:35, 2017-05-03 11:05:13, 2018-01-18 14:48:30 |
| `price` | NUMERIC | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 58.90, 239.90, 199.00 |
| `freight_value` | NUMERIC | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 13.29, 19.93, 17.87 |

Candidate business-key checks:

- PASS: (order_id, order_item_id); missing-key rows=0; duplicate-key rows=0

## `olist_customers_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `customer_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 06b8999e2fba1a1fbc88172c00ba8bc7, 18955e83d337fd6b2def6b18a428ac77, 4e7b3e00288586ebd08712fdd0374a03 |
| `customer_unique_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 861eff4711a542e4b93843c6dd7febb0, 290c77bc529b7ac935b93aa66c333dc3, 060e732b5b29e8181a18229c7b0b2b5e |
| `customer_zip_code_prefix` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 14409, 09790, 01151 |
| `customer_city` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | franca, sao bernardo do campo, sao paulo |
| `customer_state` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | SP, SC, MG |

Candidate business-key checks:

- PASS: (customer_id); missing-key rows=0; duplicate-key rows=0

## `olist_products_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `product_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 1e9e8ef04dbcff4541ed26657ea517e5, 3aa071139cb16b67ca9e5dea641aaa2f, 96bd76ec8810374ed1b65e291975717f |
| `product_category_name` | TEXT | 610 | 1.85% | 0 | 0 | 610 | 0 | 0 | perfumaria, artes, esporte_lazer |
| `product_name_lenght` | INTEGER | 610 | 1.85% | 0 | 0 | 0 | 0 | 0 | 40, 44, 46 |
| `product_description_lenght` | INTEGER | 610 | 1.85% | 0 | 0 | 0 | 0 | 0 | 287, 276, 250 |
| `product_photos_qty` | INTEGER | 610 | 1.85% | 0 | 0 | 0 | 0 | 0 | 1, 4, 2 |
| `product_weight_g` | INTEGER | 2 | 0.01% | 0 | 0 | 0 | 0 | 0 | 225, 1000, 154 |
| `product_length_cm` | INTEGER | 2 | 0.01% | 0 | 0 | 0 | 0 | 0 | 16, 30, 18 |
| `product_height_cm` | INTEGER | 2 | 0.01% | 0 | 0 | 0 | 0 | 0 | 10, 18, 9 |
| `product_width_cm` | INTEGER | 2 | 0.01% | 0 | 0 | 0 | 0 | 0 | 14, 20, 15 |

Candidate business-key checks:

- PASS: (product_id); missing-key rows=0; duplicate-key rows=0

## `olist_order_payments_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `order_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | b81ef226f3fe1789b1e8b2acac839d17, a9810da82917af2d9aefd1278f1dcfa0, 25e8ea4e93396b6fa0d3dd708e76c1bd |
| `payment_sequential` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 1, 2, 4 |
| `payment_type` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | credit_card, boleto, voucher |
| `payment_installments` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 8, 1, 2 |
| `payment_value` | NUMERIC | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 99.33, 24.39, 65.71 |

Candidate business-key checks:

- PASS: (order_id, payment_sequential); missing-key rows=0; duplicate-key rows=0

## `olist_order_reviews_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `review_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 7bc2406110b926393aa56f80a40eba40, 80e641a11e56f04c1ad469d5645fdfde, 228ce5500dc1d8e020d8d1322874b6f0 |
| `order_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 73fc7af87114b39712e6da79b0a377eb, a548910a1c6147796b98fdf73dbeba33, f9e4b658b201a9f2ecdecbb34bed034b |
| `review_score` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 4, 5, 1 |
| `review_comment_title` | TEXT | 87,658 | 88.34% | 0 | 0 | 0 | 1,996 | 0 | recomendo, Super recomendo, Não chegou meu produto  |
| `review_comment_message` | TEXT | 58,275 | 58.73% | 0 | 0 | 0 | 9,424 | 0 | Recebi bem antes do prazo estipulado., Parabéns lojas lannister adorei comprar pela Internet seguro e prático Parabéns a todos feliz Páscoa, aparelho eficiente. no site a marca do aparelho esta impresso como 3desinfector e ao chegar esta com outro nome...atualizar com a marca correta uma vez que é o mesmo aparelho |
| `review_creation_date` | TIMESTAMP | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 2018-01-18 00:00:00, 2018-03-10 00:00:00, 2018-02-17 00:00:00 |
| `review_answer_timestamp` | TIMESTAMP | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 2018-01-18 21:46:59, 2018-03-11 03:05:13, 2018-02-18 14:36:24 |

Candidate business-key checks:

- WARN: (review_id); missing-key rows=0; duplicate-key rows=814
- PASS: (review_id, order_id); missing-key rows=0; duplicate-key rows=0

## `olist_sellers_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `seller_id` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 3442f8959a84dea7ee197c632cb2df15, d1b65fc7debc3361ea86b5f14c68d2e2, ce3ad9de960102d0677a81f5d0bb7b2d |
| `seller_zip_code_prefix` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 13023, 13844, 20031 |
| `seller_city` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | campinas, mogi guacu, rio de janeiro |
| `seller_state` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | SP, RJ, PE |

Candidate business-key checks:

- PASS: (seller_id); missing-key rows=0; duplicate-key rows=0

## `olist_geolocation_dataset.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `geolocation_zip_code_prefix` | INTEGER | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 01037, 01046, 01041 |
| `geolocation_lat` | NUMERIC | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | -23.54562128115268, -23.546081127035535, -23.54612896641469 |
| `geolocation_lng` | NUMERIC | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | -46.63929204800168, -46.64482029837157, -46.64295148361138 |
| `geolocation_city` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 1 | 0 | sao paulo, são paulo, sao bernardo do campo |
| `geolocation_state` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | SP, RN, AC |

Candidate business-key checks:

- NOT TESTED: no candidate business key is assumed

## `product_category_name_translation.csv`

| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | Empty identifier | Whitespace | Invalid category/range | Samples |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `product_category_name` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | beleza_saude, informatica_acessorios, automotivo |
| `product_category_name_english` | TEXT | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | health_beauty, computers_accessories, auto |

Candidate business-key checks:

- PASS: (product_category_name); missing-key rows=0; duplicate-key rows=0

## Interpretation and limitations

- Exact duplicates and candidate-key duplicates are reported, never removed.
- Numeric/date checks validate parseability only; semantic cleaning belongs to Phase 3.
- Category/range checks cover state-code formatting, known order statuses, review scores, and coordinate bounds. They do not assert that every semantically valid domain is complete.
- A 128-bit row digest is retained during each file scan to calculate full duplicate counts without retaining every full row in memory. Hash collision risk is negligible but non-zero.
- JSONB storage preserves parsed column names and string values, not exact CSV bytes, quoting, line endings, or column order. The unchanged CSV files remain the byte-level source of record.
