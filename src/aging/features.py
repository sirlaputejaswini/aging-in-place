"""Feature extraction from raw accelerometer windows.

Each window is 3 axes x 151 samples @ 50 Hz (~3 s). We deliberately use
simple, interpretable time-domain statistics rather than a learned
representation: for a sensing-pipeline prototype, an engineer should be able
to read the features and say what each one means physically.

The last four features (jerk, peak_transient, mag_variability, sma) double
as the instability signals feeding the fall-risk proxy in risk.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def extract_features(X: np.ndarray) -> pd.DataFrame:
    """Compute one feature row per window.

    Args:
        X: (N, 3, 151) float array of x/y/z acceleration traces.

    Returns:
        DataFrame with one row per window and named feature columns.
    """
    X = np.asarray(X, dtype=np.float64)
    n = X.shape[0]
    feats: dict[str, np.ndarray] = {}

    # --- per-axis time-domain statistics ---------------------------------
    for i, axis in enumerate("xyz"):
        a = X[:, i, :]
        feats[f"{axis}_mean"] = a.mean(axis=1)
        feats[f"{axis}_std"] = a.std(axis=1)
        feats[f"{axis}_min"] = a.min(axis=1)
        feats[f"{axis}_max"] = a.max(axis=1)
        feats[f"{axis}_range"] = feats[f"{axis}_max"] - feats[f"{axis}_min"]
        feats[f"{axis}_energy"] = (a**2).mean(axis=1)
        feats[f"{axis}_mad"] = np.abs(a - a.mean(axis=1, keepdims=True)).mean(axis=1)
        q75, q25 = np.percentile(a, 75, axis=1), np.percentile(a, 25, axis=1)
        feats[f"{axis}_iqr"] = q75 - q25

    # --- acceleration magnitude ------------------------------------------
    mag = np.sqrt((X**2).sum(axis=1))  # (N, 151)
    feats["mag_mean"] = mag.mean(axis=1)
    feats["mag_std"] = mag.std(axis=1)
    feats["mag_min"] = mag.min(axis=1)
    feats["mag_max"] = mag.max(axis=1)
    feats["mag_range"] = feats["mag_max"] - feats["mag_min"]
    feats["mag_energy"] = (mag**2).mean(axis=1)

    # --- cross-axis correlation (posture / coordination signal) -----------
    # corrcoef on a constant trace is NaN; those become 0 = "no linear coupling".
    for (i, j, name) in [(0, 1, "corr_xy"), (0, 2, "corr_xz"), (1, 2, "corr_yz")]:
        xi = X[:, i, :] - X[:, i, :].mean(axis=1, keepdims=True)
        xj = X[:, j, :] - X[:, j, :].mean(axis=1, keepdims=True)
        denom = np.sqrt((xi**2).sum(axis=1) * (xj**2).sum(axis=1))
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = (xi * xj).sum(axis=1) / denom
        feats[name] = np.nan_to_num(corr)

    # --- instability signals (also used by the fall-risk proxy) -----------
    dmag = np.diff(mag, axis=1)
    feats["jerk"] = np.abs(dmag).mean(axis=1)          # shakiness of the motion
    feats["peak_transient"] = np.abs(                  # strongest abrupt change
        mag - np.median(mag, axis=1, keepdims=True)
    ).max(axis=1)
    feats["mag_variability"] = feats["mag_std"]        # overall motion variability
    feats["sma"] = (np.abs(X).sum(axis=1)).mean(axis=1)  # signal magnitude area

    df = pd.DataFrame(feats)
    return df


# Computed once from a dummy window so the name list can never drift
# out of sync with the extractor above.
FEATURE_NAMES: list[str] = list(extract_features(np.zeros((1, 3, 151))).columns)
