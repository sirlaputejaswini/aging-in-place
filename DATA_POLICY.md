# Data policy

This repo runs on a **public dataset that is fetched, never vendored**.

- `scripts/fetch_data.py` downloads the data into a local `data/`
  directory. `data/` is gitignored.
- Raw data is never committed. Only small derived artifacts are committed:
  `results/metrics.txt` and `results/*.png` figures from an actual run.
- The README and `docs/dataset.md` name the dataset, its source URL, and
  its license.
- No credentials, API keys, or tokens are stored in this repo. Ever.

To reproduce:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_data.py
python scripts/train.py   # see README for the exact entry point
```
