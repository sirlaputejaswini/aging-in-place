# Findings — reference run, 2026-09-18 (real UniMiB SHAR data)

Dataset: UniMiB SHAR, ADL split — 7,579 accelerometer windows (3 axes ×
151 samples @ 50 Hz), 9 activities of daily living, 30 subjects. Research
use with citation (no explicit license file). Pipeline: 37 interpretable
time-domain features → random-forest activity classifier (200 trees) →
fall-risk proxy score in [0, 1]. Stratified 80/20 split (6,063 train /
1,516 test). Runtime ~11 s end to end.

## What the numbers say

- **Held-out accuracy: 0.9703.** Per-class: walking 1.000, jumping 1.000,
  running 0.992, going_down 0.959, going_up 0.940, sitting_down 0.925,
  lying_down 0.915, standing_up 0.903, getting_up 0.791.
- **Errors are humble:** mean confidence 0.513 on the 45 errors vs. 0.860
  on correct predictions. Top confusions: getting_up→lying_down (8),
  going_up→walking (7), going_down→walking (6).
- **Risk proxy** (population-relative, mean 0.497, std 0.197, range
  0.137–0.939): running 0.703, jumping 0.645, going_down 0.476, going_up
  0.447, walking 0.366, lying_down 0.257, getting_up 0.252, sitting_down
  0.238, standing_up 0.222.

## Non-obvious insights

1. Weakest exactly where it matters: transitions (getting_up 0.791) are
   the movements geriatricians use to assess fall risk — the sensor's
   blind spot overlaps the clinical signal.
2. Mistakes are humble, not confident (0.513 vs 0.860) — the right failure
   mode for safety-adjacent systems; confusions have physical
   explanations.
3. The proxy rediscovers stair-descent > ascent > walking risk ordering
   unprompted — but conflates vigorous healthy movement (running 0.703)
   with instability, and is blind to quiet sit-to-stand wobble (~0.24,
   same as lying still).
4. Rare *and* confusable is a bad combination (getting_up: 216 windows,
   0.791) — transitions need dedicated modeling.

See [docs/vision.md](../docs/vision.md) for the full write-up: what becomes
possible in the future because of this work, and concrete use cases at scale.

## Artifacts

- `metrics.txt` — classifier accuracy, per-class accuracy, error analysis,
  full risk-score distribution.
- `confusion_matrix.png` — where the classifier confuses activities.
- `risk_by_activity.png` — mean fall-risk proxy per activity.

Re-run any time (`python scripts/fetch_data.py && python scripts/run_pipeline.py`)
to refresh these findings.
