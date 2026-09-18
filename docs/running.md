# How to run

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt   # numpy, pandas, scikit-learn, matplotlib, scipy, requests

# 3. Fetch the dataset (one-time download into data/, ~250 MB)
python scripts/fetch_data.py

# 4. Run the full pipeline (~15 seconds)
python scripts/run_pipeline.py
```

## Outputs

| Path | Contents |
|---|---|
| `results/metrics.txt` | Classifier accuracy, per-class accuracy, error analysis, full risk-score distribution |
| `results/confusion_matrix.png` | Where the classifier confuses activities |
| `results/risk_by_activity.png` | Mean fall-risk proxy per activity |

Reference run (2026-09-18, real data, 7,579 windows, 80/20 stratified split):

```
held-out accuracy: 0.9703 (6063 train / 1516 test)
risk score range: [0.137, 0.939], mean 0.497
```
