# Data directory

`raw/` is the local landing area for the nine unmodified Olist CSV files. Source data is excluded
from Git because it is downloaded separately from Kaggle, is large, and is governed by the source
dataset terms. The pipeline code, schemas, hashes, measured profile, and synthetic test fixture are
versioned; each collaborator downloads the official source data independently.

## Download the official dataset

1. Open the [Olist Brazilian E-Commerce dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
2. Sign in, accept any dataset terms, and download the archive.
3. Extract these files directly into `data/raw/` (not a nested folder):

   - `olist_customers_dataset.csv`
   - `olist_geolocation_dataset.csv`
   - `olist_order_items_dataset.csv`
   - `olist_order_payments_dataset.csv`
   - `olist_order_reviews_dataset.csv`
   - `olist_orders_dataset.csv`
   - `olist_products_dataset.csv`
   - `olist_sellers_dataset.csv`
   - `product_category_name_translation.csv`

With an authenticated Kaggle CLI, the equivalent command is:

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

Never commit `kaggle.json`, API tokens, the downloaded archive, or the raw CSV files. Confirm the
filenames and reproduce the recorded dataset profile with:

```bash
python scripts/profile_dataset.py
```

The ingestion service reads this folder as read-only and preserves source values in immutable raw
storage. See the root [`README.md`](../README.md) for the complete ingestion-through-BI workflow.
