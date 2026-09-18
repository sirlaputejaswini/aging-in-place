#!/usr/bin/env python3
"""Run the full Aging-in-Place pipeline end to end.

Usage (from the project root):
    python scripts/run_pipeline.py

Requires the dataset (see scripts/fetch_data.py) and requirements.txt.
Writes metrics + figures into results/.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from aging.pipeline import main

if __name__ == "__main__":
    main()
