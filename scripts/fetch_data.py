#!/usr/bin/env python3
"""Download the UniMiB SHAR dataset into data/.

Fetches the official distribution zip from the research group's page
(http://www.sal.disco.unimib.it/technologies/unimib-shar/) and extracts only
the files this project needs: the ADL accelerometer windows + labels, the
fall windows + labels (for reference), the activity name tables, and the
dataset readme. Everything lands in data/, which is gitignored.

Usage (from the project root):
    python scripts/fetch_data.py
"""

import sys
import urllib.request
import zipfile
from pathlib import Path

# Direct-download link published on the official UniMiB SHAR page (?dl=1 forces
# a raw file download instead of the Dropbox preview page).
DATASET_URL = "https://www.dropbox.com/s/x2fpfqj0bpf8ep6/UniMiB-SHAR.zip?dl=1"

# Only these members are extracted; the zip also carries MATLAB eval code and
# precomputed cross-validation splits we don't need.
WANTED = [
    "UniMiB-SHAR/readme.txt",
    "UniMiB-SHAR/data/adl_data.mat",
    "UniMiB-SHAR/data/adl_labels.mat",
    "UniMiB-SHAR/data/adl_names.mat",
    "UniMiB-SHAR/data/fall_data.mat",
    "UniMiB-SHAR/data/fall_labels.mat",
    "UniMiB-SHAR/data/fall_names.mat",
    "UniMiB-SHAR/data/acc_names.mat",
]

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    zip_path = DATA_DIR / "UniMiB-SHAR.zip"

    print(f"Downloading UniMiB SHAR (~250 MB)...\n  from: {DATASET_URL}")
    try:
        urllib.request.urlretrieve(DATASET_URL, zip_path)
    except Exception as exc:  # network errors, Dropbox hiccups, etc.
        print(f"Download failed: {exc}", file=sys.stderr)
        print("Grab the zip manually from "
              "http://www.sal.disco.unimib.it/technologies/unimib-shar/ "
              "and place it at data/UniMiB-SHAR.zip, then re-run.", file=sys.stderr)
        sys.exit(1)
    print(f"  saved to {zip_path} ({zip_path.stat().st_size / 1e6:.0f} MB)")

    print("Extracting needed files into data/ ...")
    with zipfile.ZipFile(zip_path) as zf:
        for member in WANTED:
            zf.extract(member, DATA_DIR)
            # Flatten: UniMiB-SHAR/data/adl_data.mat -> data/adl_data.mat
            src = DATA_DIR / member
            dst = DATA_DIR / Path(member).name
            if src != dst:
                src.replace(dst)
    # Remove the now-empty extracted tree and the zip (re-downloadable anytime).
    for leftover in [DATA_DIR / "UniMiB-SHAR"]:
        if leftover.exists():
            import shutil
            shutil.rmtree(leftover)
    zip_path.unlink()
    print("Done. data/ now holds:")
    for p in sorted(DATA_DIR.iterdir()):
        print(f"  {p.name} ({p.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
