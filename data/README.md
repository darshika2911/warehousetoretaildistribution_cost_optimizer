# Data

Raw datasets are gitignored — see `download_data.py` (to be added) to pull them locally.

Sources:
- Kaggle Credit Card Fraud Detection
- IEEE-CIS Fraud Detection
- PaySim (synthetic mobile-money simulator, reference for our own generators)

`schema.md` — shared transaction schema used across Identify → Generate → Defend:
transaction_id, timestamp, card_id, merchant_id, merchant_category, amount, device_id, ip_country, is_fraud, fraud_type

`/samples` — a few hundred committed rows so teammates can run scripts without downloading full datasets first.
