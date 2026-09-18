"""Fall-risk proxy: turn motion features into a per-window risk score.

WHAT THIS IS: a heuristic "movement instability" score in [0, 1] computed
from how jerky / abrupt / variable a 3-second motion window is. It is a
research-prototype proxy for fall *risk*, not a fall *detector* and not a
fall *predictor*.

WHAT THIS IS NOT:
  - It was never trained against real falls or real fallers. The dataset's
    falls are simulated by healthy volunteers (ages 18-60), so there is no
    ground truth linking these scores to actual fall probability.
  - The z-score standardization below uses the whole-dataset population
    mean/std. A real deployment would standardize against each person's own
    rolling baseline ("is *this* person's gait shakier than *their* usual?"),
    which is strictly more meaningful and is the design this prototype
    points toward.

The score is deliberately simple and explainable: average the z-scored
instability features, squash through a sigmoid so it reads as 0-1.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Instability signals feeding the proxy. All three come straight from
# features.py, where each has a physical interpretation in its comment.
INSTABILITY_FEATURES = ["jerk", "peak_transient", "mag_variability"]


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def risk_scores(features: pd.DataFrame) -> pd.Series:
    """Compute a fall-risk proxy score in [0, 1] for every window.

    Higher = more unstable motion in that window. Scores are relative to the
    dataset population, not to any individual.
    """
    z = features[INSTABILITY_FEATURES].apply(
        lambda col: (col - col.mean()) / (col.std() or 1.0)
    )
    combined = z.mean(axis=1)
    return pd.Series(_sigmoid(combined), index=features.index, name="risk_score")


def summarize_by_activity(
    scores: pd.Series, activities: np.ndarray, names: dict[int, str]
) -> pd.DataFrame:
    """Per-activity risk distribution: mean, median, and spread of the proxy."""
    df = pd.DataFrame({"activity": activities, "risk": scores.to_numpy()})
    summary = (
        df.groupby("activity")["risk"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )
    summary["name"] = summary["activity"].map(names)
    return summary.sort_values("mean", ascending=False).reset_index(drop=True)
