"""Activity classification: which daily-living activity is this window?

A random forest on the hand-built features. Nothing exotic on purpose: the
point of this prototype is the end-to-end pipeline (sense -> classify ->
risk), and a transparent model keeps the failure modes legible — which
matters more than squeezing the last point of accuracy when the downstream
consumer is a fall-risk heuristic.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split


def train_classifier(
    features: pd.DataFrame,
    labels: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """Train a random forest and evaluate on a held-out split.

    The split is stratified so every activity is represented in both sets,
    but note it is NOT subject-disjoint (see README limitations).

    Returns a dict with the fitted model, accuracy, confusion matrix,
    per-class accuracy, test labels/predictions, and prediction confidence
    (max predicted probability) for error analysis.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=test_size,
        random_state=random_state, stratify=labels,
    )
    model = RandomForestClassifier(
        n_estimators=200, random_state=random_state, n_jobs=-1
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)
    pred = model.classes_[proba.argmax(axis=1)]
    confidence = proba.max(axis=1)

    cm = confusion_matrix(y_test, pred, labels=np.unique(labels))
    per_class_acc = cm.diagonal() / cm.sum(axis=1)

    return {
        "model": model,
        "accuracy": accuracy_score(y_test, pred),
        "confusion_matrix": cm,
        "class_labels": np.unique(labels),
        "per_class_accuracy": per_class_acc,
        "y_test": y_test,
        "y_pred": pred,
        "confidence": confidence,
        "n_train": len(y_train),
        "n_test": len(y_test),
    }
