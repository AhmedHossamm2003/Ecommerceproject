# Dataset Profiling Report

**Profile status:** VERIFIED AGAINST LOCAL CSV FILES

**Generated:** 2026-11-19 07:18:46 UTC

**Method:** `scripts/profile_dataset.py` streamed the unmodified files in `data/raw/`. Counts below are measured locally. SHA-256 values identify the exact inputs.

Dataset source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## File inventory

| Filename | Rows | Columns | Exact duplicate rows | Size (bytes) | SHA-256 |
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

## Per-file columns, inferred types, and missing values

### `olist_orders_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `order_id` | TEXT | 0 | e481f51cbdc54678b7cc49136f2d6af7, 53cdb2fc8bc7dce0b6741e2150273451, 47770eb9100c2d0c44946d9cf07ec65d, 949d5b44dbf5de918fe9c16f97b45f8a, ad21c59c0840e6cb83a9ceb5573f8159 |
| `customer_id` | TEXT | 0 | 9ef432eb6251297304e76186b10a928d, b0830fb4747a6c6d20dea0b8c802d7ef, 41ce2a54c0b03bf3443c3d931a367089, f88197465ea7920adcdbec7375364d82, 8ab97904e6daea8866dbdbc4fb7aad2c |
| `order_status` | TEXT | 0 | delivered, invoiced, shipped, processing, unavailable |
| `order_purchase_timestamp` | TIMESTAMP | 0 | 2017-10-02 10:56:33, 2018-07-24 20:41:37, 2018-08-08 08:38:49, 2017-11-18 19:28:06, 2018-02-13 21:18:39 |
| `order_approved_at` | TIMESTAMP | 160 | 2017-10-02 11:07:15, 2018-07-26 03:24:27, 2018-08-08 08:55:23, 2017-11-18 19:45:59, 2018-02-13 22:20:29 |
| `order_delivered_carrier_date` | TIMESTAMP | 1,783 | 2017-10-04 19:55:00, 2018-07-26 14:31:00, 2018-08-08 13:50:00, 2017-11-22 13:39:59, 2018-02-14 19:46:34 |
| `order_delivered_customer_date` | TIMESTAMP | 2,965 | 2017-10-10 21:25:13, 2018-08-07 15:27:45, 2018-08-17 18:06:29, 2017-12-02 00:28:42, 2018-02-16 18:17:02 |
| `order_estimated_delivery_date` | TIMESTAMP | 0 | 2017-10-18 00:00:00, 2018-08-13 00:00:00, 2018-09-04 00:00:00, 2017-12-15 00:00:00, 2018-02-26 00:00:00 |

Candidate-key tests:

- PASS: (`order_id`) - null-key rows: 0; duplicate-key rows: 0

### `olist_order_items_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `order_id` | TEXT | 0 | 00010242fe8c5a6d1ba2dd792cb16214, 00018f77f2f0320c557190d7a144bdd3, 000229ec398224ef6ca0657da4fc703e, 00024acbcdf0a6daa1e931b038114c75, 00042b26cf59d7ce69dfabb4e55b4fd9 |
| `order_item_id` | INTEGER | 0 | 1, 2, 3, 4, 5 |
| `product_id` | TEXT | 0 | 4244733e06e7ecb4970a6e2683c13e61, e5f2d52b802189ee658865ca93d83a8f, c777355d18b72b67abbeef9df44fd0fd, 7634da152a4610f1595efa32f14722fc, ac6c3623068f30de03045865e4e10089 |
| `seller_id` | TEXT | 0 | 48436dade18ac8b2bce089ec2a041202, dd7ddc04e1b6c2c614352b383efe2d36, 5b51032eddd242adc84c38acab88f23d, 9d7a1d34a5052409006425275ba1c2b4, df560393f3a51e74553ab94004ba5c87 |
| `shipping_limit_date` | TIMESTAMP | 0 | 2017-09-19 09:45:35, 2017-05-03 11:05:13, 2018-01-18 14:48:30, 2018-08-15 10:10:18, 2017-02-13 13:57:51 |
| `price` | NUMERIC | 0 | 58.90, 239.90, 199.00, 12.99, 199.90 |
| `freight_value` | NUMERIC | 0 | 13.29, 19.93, 17.87, 12.79, 18.14 |

Candidate-key tests:

- PASS: (`order_id`, `order_item_id`) - null-key rows: 0; duplicate-key rows: 0

### `olist_customers_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `customer_id` | TEXT | 0 | 06b8999e2fba1a1fbc88172c00ba8bc7, 18955e83d337fd6b2def6b18a428ac77, 4e7b3e00288586ebd08712fdd0374a03, b2b6027bc5c5109e529d4dc6358b12c3, 4f2d8ab171c80ec8364f7c12e35b23ad |
| `customer_unique_id` | TEXT | 0 | 861eff4711a542e4b93843c6dd7febb0, 290c77bc529b7ac935b93aa66c333dc3, 060e732b5b29e8181a18229c7b0b2b5e, 259dac757896d24d7702b9acbbff3f3c, 345ecd01c38d18a9036ed96c73b8d066 |
| `customer_zip_code_prefix` | INTEGER | 0 | 14409, 09790, 01151, 08775, 13056 |
| `customer_city` | TEXT | 0 | franca, sao bernardo do campo, sao paulo, mogi das cruzes, campinas |
| `customer_state` | TEXT | 0 | SP, SC, MG, PR, RJ |

Candidate-key tests:

- PASS: (`customer_id`) - null-key rows: 0; duplicate-key rows: 0

### `olist_products_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `product_id` | TEXT | 0 | 1e9e8ef04dbcff4541ed26657ea517e5, 3aa071139cb16b67ca9e5dea641aaa2f, 96bd76ec8810374ed1b65e291975717f, cef67bcfe19066a932b7673e239eb23d, 9dc1a7de274444849c219cff195d0b71 |
| `product_category_name` | TEXT | 610 | perfumaria, artes, esporte_lazer, bebes, utilidades_domesticas |
| `product_name_lenght` | INTEGER | 610 | 40, 44, 46, 27, 37 |
| `product_description_lenght` | INTEGER | 610 | 287, 276, 250, 261, 402 |
| `product_photos_qty` | INTEGER | 610 | 1, 4, 2, 3, 5 |
| `product_weight_g` | INTEGER | 2 | 225, 1000, 154, 371, 625 |
| `product_length_cm` | INTEGER | 2 | 16, 30, 18, 26, 20 |
| `product_height_cm` | INTEGER | 2 | 10, 18, 9, 4, 17 |
| `product_width_cm` | INTEGER | 2 | 14, 20, 15, 26, 13 |

Candidate-key tests:

- PASS: (`product_id`) - null-key rows: 0; duplicate-key rows: 0

### `olist_order_payments_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `order_id` | TEXT | 0 | b81ef226f3fe1789b1e8b2acac839d17, a9810da82917af2d9aefd1278f1dcfa0, 25e8ea4e93396b6fa0d3dd708e76c1bd, ba78997921bbcdc1373bb41e913ab953, 42fdf880ba16b47b59251dd489d4441a |
| `payment_sequential` | INTEGER | 0 | 1, 2, 4, 5, 3 |
| `payment_type` | TEXT | 0 | credit_card, boleto, voucher, debit_card, not_defined |
| `payment_installments` | INTEGER | 0 | 8, 1, 2, 3, 6 |
| `payment_value` | NUMERIC | 0 | 99.33, 24.39, 65.71, 107.78, 128.45 |

Candidate-key tests:

- PASS: (`order_id`, `payment_sequential`) - null-key rows: 0; duplicate-key rows: 0

### `olist_order_reviews_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `review_id` | TEXT | 0 | 7bc2406110b926393aa56f80a40eba40, 80e641a11e56f04c1ad469d5645fdfde, 228ce5500dc1d8e020d8d1322874b6f0, e64fb393e7b32834bb789ff8bb30750e, f7c4243c7fe1938f181bec41a392bdeb |
| `order_id` | TEXT | 0 | 73fc7af87114b39712e6da79b0a377eb, a548910a1c6147796b98fdf73dbeba33, f9e4b658b201a9f2ecdecbb34bed034b, 658677c97b385a9be170737859d3511b, 8e6bfb81e283fa7e4f11123a3fb894f1 |
| `review_score` | INTEGER | 0 | 4, 5, 1, 3, 2 |
| `review_comment_title` | TEXT | 87,658 | recomendo, Super recomendo, Não chegou meu produto , Ótimo, Muito bom. |
| `review_comment_message` | TEXT | 58,275 | Recebi bem antes do prazo estipulado., Parabéns lojas lannister adorei comprar pela Internet seguro e prático Parabéns a todos feliz Páscoa, aparelho eficiente. no site a marca do aparelho esta impresso como 3desinfector e ao chegar esta com outro nome...atualizar com a marca correta uma vez que é o mesmo aparelho, Mas um pouco ,travando...pelo valor ta Boa. , Vendedor confiável, produto ok e entrega antes do prazo. |
| `review_creation_date` | TIMESTAMP | 0 | 2018-01-18 00:00:00, 2018-03-10 00:00:00, 2018-02-17 00:00:00, 2017-04-21 00:00:00, 2018-03-01 00:00:00 |
| `review_answer_timestamp` | TIMESTAMP | 0 | 2018-01-18 21:46:59, 2018-03-11 03:05:13, 2018-02-18 14:36:24, 2017-04-21 22:02:06, 2018-03-02 10:26:53 |

Candidate-key tests:

- FAIL: (`review_id`) - null-key rows: 0; duplicate-key rows: 814
- PASS: (`review_id`, `order_id`) - null-key rows: 0; duplicate-key rows: 0

### `olist_sellers_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `seller_id` | TEXT | 0 | 3442f8959a84dea7ee197c632cb2df15, d1b65fc7debc3361ea86b5f14c68d2e2, ce3ad9de960102d0677a81f5d0bb7b2d, c0f3eea2e14555b6faeea3dd58c1b1c3, 51a04a8a6bdcb23deccc82b0b80742cf |
| `seller_zip_code_prefix` | INTEGER | 0 | 13023, 13844, 20031, 04195, 12914 |
| `seller_city` | TEXT | 0 | campinas, mogi guacu, rio de janeiro, sao paulo, braganca paulista |
| `seller_state` | TEXT | 0 | SP, RJ, PE, PR, GO |

Candidate-key tests:

- PASS: (`seller_id`) - null-key rows: 0; duplicate-key rows: 0

### `olist_geolocation_dataset.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `geolocation_zip_code_prefix` | INTEGER | 0 | 01037, 01046, 01041, 01035, 01012 |
| `geolocation_lat` | NUMERIC | 0 | -23.54562128115268, -23.546081127035535, -23.54612896641469, -23.5443921648681, -23.541577961711493 |
| `geolocation_lng` | NUMERIC | 0 | -46.63929204800168, -46.64482029837157, -46.64295148361138, -46.63949930627844, -46.64160722329613 |
| `geolocation_city` | TEXT | 0 | sao paulo, são paulo, sao bernardo do campo, jundiaí, taboão da serra |
| `geolocation_state` | TEXT | 0 | SP, RN, AC, RJ, ES |

Candidate-key tests:

- No primary key assumed; uniqueness requires a separate design decision.

### `product_category_name_translation.csv`

| Column | Inferred type | Missing values | Non-null sample values (up to 5) |
|---|---|---:|---|
| `product_category_name` | TEXT | 0 | beleza_saude, informatica_acessorios, automotivo, cama_mesa_banho, moveis_decoracao |
| `product_category_name_english` | TEXT | 0 | health_beauty, computers_accessories, auto, bed_bath_table, furniture_decor |

Candidate-key tests:

- PASS: (`product_category_name`) - null-key rows: 0; duplicate-key rows: 0

## Candidate foreign-key tests

- **PASS** `olist_orders_dataset.csv` (customer_id) -> `olist_customers_dataset.csv` (customer_id): 0 distinct unmatched non-null key(s)
- **PASS** `olist_order_items_dataset.csv` (order_id) -> `olist_orders_dataset.csv` (order_id): 0 distinct unmatched non-null key(s)
- **PASS** `olist_order_items_dataset.csv` (product_id) -> `olist_products_dataset.csv` (product_id): 0 distinct unmatched non-null key(s)
- **PASS** `olist_order_items_dataset.csv` (seller_id) -> `olist_sellers_dataset.csv` (seller_id): 0 distinct unmatched non-null key(s)
- **PASS** `olist_order_payments_dataset.csv` (order_id) -> `olist_orders_dataset.csv` (order_id): 0 distinct unmatched non-null key(s)
- **PASS** `olist_order_reviews_dataset.csv` (order_id) -> `olist_orders_dataset.csv` (order_id): 0 distinct unmatched non-null key(s)
- **WARN** `olist_products_dataset.csv` (product_category_name) -> `product_category_name_translation.csv` (product_category_name): 2 distinct unmatched non-null key(s)

## Potential data-quality problems identified by the profile

- `olist_orders_dataset.csv` has missing values: `order_approved_at`=160, `order_delivered_carrier_date`=1,783, `order_delivered_customer_date`=2,965.
- `olist_products_dataset.csv` has missing values: `product_category_name`=610, `product_name_lenght`=610, `product_description_lenght`=610, `product_photos_qty`=610, `product_weight_g`=2, `product_length_cm`=2, `product_height_cm`=2, `product_width_cm`=2.
- `olist_order_reviews_dataset.csv` has missing values: `review_comment_title`=87,658, `review_comment_message`=58,275.
- `olist_order_reviews_dataset.csv` candidate key issue: FAIL: (`review_id`) - null-key rows: 0; duplicate-key rows: 814
- `olist_geolocation_dataset.csv` contains 261,831 repeated exact row(s).
- Interpret foreign-key warnings carefully for optional category translations; quantify and map unknown members rather than dropping facts.
- This structural profile does not replace semantic validation of status/date order, monetary ranges, geographic consistency, or join reconciliation.

## Reproducibility

Run `python scripts/profile_dataset.py` again after any source-file change. Compare SHA-256 values before treating two profiles as equivalent.
