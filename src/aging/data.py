"""Dataset loading for the Aging-in-Place pipeline.

Wraps the UniMiB SHAR MATLAB files into plain numpy arrays so the rest of
the pipeline never has to know about .mat internals.

UniMiB SHAR layout (see dataset readme.txt):
  adl_data.mat   - one row per ADL window; the 453 columns are the x, y, z
                   acceleration traces (151 samples each, 50 Hz) concatenated
  adl_labels.mat - one row per ADL window: [activity_label, subject_id, trial]
  *_names.mat    - human-readable activity names for each label id
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.io import loadmat

# Fallback names, kept in sync with the dataset's acc_names.mat. Used only if
# the .mat name files cannot be read, so the pipeline degrades gracefully.
_FALLBACK_NAMES = {
    1: "Walking",
    2: "Running",
    3: "GoingUpS",
    4: "Jumping",
    5: "GoingDownS",
    6: "LyingDownFS",
    7: "StandingUpFL",
    8: "SittingDown",
    9: "FallingForw",
    10: "FallingRight",
    11: "FallingBack",
    12: "HittingObstacle",
    13: "FallingWithPS",
    14: "FallingBackSC",
    15: "Syncope",
    16: "FallingLeft",
    17: "StandingUpFS",
}


def _read_names(path: Path) -> dict[int, str]:
    """Read a *_names.mat file into {label_id: activity_name}."""
    mat = loadmat(path, squeeze_me=True)
    # The variable name differs per file; take the first non-dunder entry.
    key = next(k for k in mat if not k.startswith("__"))
    raw = mat[key]
    names: dict[int, str] = {}
    for i, entry in enumerate(np.atleast_1d(raw).ravel(), start=1):
        names[i] = str(entry).strip()
    return names or dict(_FALLBACK_NAMES)


def load_windows(data_dir: str | Path, split: str = "adl") -> dict:
    """Load accelerometer windows and labels.

    Args:
        data_dir: directory holding the extracted UniMiB-SHAR/data/*.mat files.
        split: "adl" (9 daily-living activities), "fall" (8 fall types), or
            "acc" (all 17 classes).

    Returns:
        dict with:
          X            (N, 3, 151) float32 acceleration windows [x, y, z]
          activity     (N,) int activity label ids
          subject      (N,) int subject ids
          trial        (N,) int trial numbers
          names        {label_id: activity_name}
          sample_hz    sampling rate of the traces
    """
    data_dir = Path(data_dir)
    mat_path = data_dir / f"{split}_data.mat"
    lab_path = data_dir / f"{split}_labels.mat"
    if not mat_path.exists() or not lab_path.exists():
        raise FileNotFoundError(
            f"Expected {mat_path} and {lab_path}. "
            "Run `python scripts/fetch_data.py` first."
        )

    data = loadmat(mat_path, squeeze_me=True)
    labels = loadmat(lab_path, squeeze_me=True)
    data_key = next(k for k in data if not k.startswith("__"))
    lab_key = next(k for k in labels if not k.startswith("__"))

    raw = np.asarray(data[data_key], dtype=np.float64)
    lab = np.asarray(labels[lab_key], dtype=np.int64).reshape(-1, 3)

    # One row per window; the 453 columns are the x, y, z traces (151 samples
    # each @ 50 Hz) concatenated end to end.
    n_windows, n_cols = raw.shape
    if n_cols % 3 != 0:
        raise ValueError(f"Unexpected window width {n_cols}: not divisible by 3")
    X = raw.reshape(n_windows, 3, n_cols // 3).astype(np.float32)

    names_path = data_dir / f"{split}_names.mat"
    names = _read_names(names_path) if names_path.exists() else dict(_FALLBACK_NAMES)

    return {
        "X": X,
        "activity": lab[:n_windows, 0],
        "subject": lab[:n_windows, 1],
        "trial": lab[:n_windows, 2],
        "names": names,
        "sample_hz": 50,
    }


def describe(dataset: dict) -> str:
    """One-paragraph human summary of a loaded dataset (for logging)."""
    n = len(dataset["activity"])
    n_subjects = len(np.unique(dataset["subject"]))
    n_classes = len(np.unique(dataset["activity"]))
    win = dataset["X"].shape[2]
    return (
        f"{n} windows x {win} samples @ {dataset['sample_hz']} Hz, "
        f"{n_classes} activity classes, {n_subjects} subjects."
    )
