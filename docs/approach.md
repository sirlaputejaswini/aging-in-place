# Approach

A 3-second accelerometer window flows through three stages
(`src/aging/`, entry point `scripts/run_pipeline.py`):

1. **Features** (`features.py`) — 37 interpretable time-domain features:
   per-axis stats, magnitude stats, cross-axis correlation,
   jerk/transient/variability measures. Interpretable on purpose.
2. **Classify** (`classify.py`) — a random-forest activity classifier
   (200 trees) answering "what is the person doing": walking, running,
   stairs, sit↔stand transitions, and more.
3. **Risk proxy** (`risk.py`) — a fall-risk proxy score in [0, 1] built
   from z-scored movement-instability features, answering "how unsteady
   does this motion look relative to the population."

Both stages are deliberately simple and explainable — when the downstream
consumer is anything safety-adjacent, legible failure modes beat black-box
accuracy. `pipeline.py` orchestrates the run and writes metrics and
figures.
