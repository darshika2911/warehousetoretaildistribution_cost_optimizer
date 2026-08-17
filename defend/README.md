# Defend (Blue Team)

Classifier trained on legit + synthetic fraud data from `/generate`.

- Baseline: XGBoost/LightGBM
- Metrics: precision, recall, F1, AUC-PR (not plain AUC-ROC — data is imbalanced)
- Generalization check: does the model trained on synthetic fraud catch real, unseen Kaggle/IEEE-CIS fraud rows?
- Per-attack-type breakdown, not just aggregate — this is what surfaces the closed-loop feedback for `/identify`
