# Raw dataset landing directory

Place the original Olist CSV files here without renaming or editing them. CSV files in this directory are intentionally ignored by Git.

Expected files:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_products_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `product_category_name_translation.csv`

Download from the [official Kaggle dataset page](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). After copying all files, run:

```bash
python scripts/profile_dataset.py
```

The script reads the originals but never modifies them. It replaces the pending profile in `docs/dataset_profile.md` with measured results.
