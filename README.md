# Aging in Place — privacy-preserving fall-risk sensing from ambient motion

**Full documentation:** [docs/problem.md](docs/problem.md) ·
[docs/approach.md](docs/approach.md) · [docs/running.md](docs/running.md) ·
[docs/dataset.md](docs/dataset.md) · [docs/limitations.md](docs/limitations.md) ·
[docs/vision.md](docs/vision.md) — non-obvious insights, what this unlocks,
and use cases at scale
· [results/FINDINGS.md](results/FINDINGS.md)

A research prototype that turns raw accelerometer signals into an activity
classification plus a **fall-risk proxy score** — with no cameras and no
wearables required. The goal: show that the sensing pipeline for
camera-free, dignity-preserving elder monitoring is buildable from
commodity motion data.

This one is personal. The people I love are getting older, and I keep thinking about how thin the line gets between *independent* and *alone* — and how late we usually notice it being crossed. Cameras feel like surveillance and wearables end up forgotten on chargers; I wanted to see whether ordinary motion data could notice decline early, with nobody's dignity as the price.

> **Not a medical device.** This is a research prototype demonstrating a
> sensing pipeline. It has no clinical validation and must not be used for
> health decisions. See [Limitations](#limitations-blunt-version) — read
> that section before citing any number here.

## The problem

Falls are the leading cause of injury-related death in adults over 65, and
most older adults say they want to keep living independently — "aging in
place." Today's options are bad: cameras feel like surveillance, wearables
get forgotten on chargers, and emergency pendants only help *after* the
fall. What's missing is **ambient sensing that notices decline early**:
a home that can tell, from ordinary motion, that someone's gait is getting
less steady this month than last — and prompts a check-in *before* anyone
hits the floor.

## Why this matters for the future

The demographic math is unavoidable: the 65+ population is growing far
faster than the caregiver workforce. The future of elder care can't be
"more humans watching" — it has to be environments that watch *well*:
camera-free homes where the building itself notices functional decline
early, the way a good nurse notices a shuffle that wasn't there last week.
This project is one small proof that the perception half of that future —
classify what someone is doing, score how stable the movement looks —
already works on commodity accelerometer data. The remaining work is
longitudinal personalization (your baseline vs. your today, not you vs. a
population), real-home validation, and clinical grounding — all named in
the limitations below.

## What the pipeline does

```
accelerometer window (3 axes × 151 samples @ 50 Hz)
        │
        ▼
  37 interpretable time-domain features        (src/aging/features.py)
  (per-axis stats, magnitude stats, cross-axis
   correlation, jerk / transient / variability)
        │
        ▼
  activity classifier (random forest)          (src/aging/classify.py)
  → walking, running, stairs, sit↔stand, …
        │
        ▼
  fall-risk proxy score in [0, 1]              (src/aging/risk.py)
  → z-scored movement-instability heuristic
```

The classifier answers "what is the person doing"; the risk proxy answers
"how unsteady does this motion look relative to the population." Both are
deliberately simple and explainable — when the downstream consumer is
anything safety-adjacent, legible failure modes beat black-box accuracy.

## Dataset

**UniMiB SHAR** — *UniMiB SHAR: a new dataset for human activity
recognition using acceleration data from smartphones* (Micucci, Mobilio,
Napoletano, 2017).

- URL: <http://www.sal.disco.unimib.it/technologies/unimib-shar/>
- Contents used: ADL split — **7,579 windows** × 151 samples @ 50 Hz,
  **9 activities of daily living**, **30 subjects**. (The dataset also
  ships 4,192 simulated-fall windows, fetched for reference but not used
  in the pipeline — see limitations.)
- License: the distribution ships **no explicit license file**; it is
  released for research use with a citation request. If you use the data,
  cite: Micucci et al., *arXiv:1611.07688* (2017).

### Fetch steps

```bash
python scripts/fetch_data.py
```

downloads the official `UniMiB-SHAR.zip` (~250 MB) from the research
group's Dropbox link and extracts only the needed `.mat` files into
`data/` (gitignored, never committed).

## How to run

```bash
cd aging-in-place
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # numpy, pandas, scikit-learn, matplotlib, scipy, requests
python scripts/fetch_data.py        # one-time dataset download into data/
python scripts/run_pipeline.py      # full pipeline, ~15 seconds
```

### Expected output

Console:

```
Loading UniMiB SHAR (ADL split)...
  7579 windows x 151 samples @ 50 Hz, 9 activity classes, 30 subjects.
Extracting features...
  7579 windows x 37 features
Training activity classifier...
  held-out accuracy: 0.9703 (6063 train / 1516 test)
Computing fall-risk proxy scores...
  risk score range: [0.137, 0.939], mean 0.497
  wrote confusion_matrix.png, risk_by_activity.png
  wrote metrics.txt
```

Artifacts in `results/`:

- `metrics.txt` — classifier accuracy, per-class accuracy, error analysis,
  and the full risk-score distribution (numbers from the actual run)
- `confusion_matrix.png` — where the classifier confuses activities
- `risk_by_activity.png` — mean fall-risk proxy per activity

## What the data actually showed

All numbers below are from the real run (`results/metrics.txt`), 80/20
stratified split, random forest with 200 trees.

**1. The pipeline is weakest exactly where fall risk matters most.**
Locomotion is nearly perfect — walking 1.000, jumping 1.000, running
0.992 — but the postural *transitions* are the worst classes:
getting_up 0.791, standing_up 0.903, lying_down 0.915. That stings,
because the sit-to-stand transfer is precisely the movement geriatricians
use to assess fall risk (it's the basis of the chair-stand test). The
sensor's blind spot overlaps the clinical signal — the single most
important thing this prototype taught us, and the reason a production
system would need transition-specific features (duration, sway, recovery
time), not just window statistics.

**2. The model's mistakes are humble, not confident — the right failure
mode for safety-adjacent systems.** Mean prediction confidence is 0.513
on the 45 errors vs. 0.860 on correct predictions: when it's wrong, it
*knows* it's unsure. Uncertainty this visible can gate alerts (don't page
a caregiver on a 0.51-confidence guess). The confusions also make physical
sense rather than looking random: stairs collapse into walking
(going_up→walking 7, going_down→walking 6 windows) because from a
phone in a pocket, stair climbing *is* walking with a different cadence;
getting_up is mistaken for lying_down (8 windows) because both are slow
whole-body postural shifts with similar acceleration envelopes.

**3. The risk proxy rediscovers that stairs are dangerous — but also
exposes what it can't see.** Without being told anything about stairs,
the proxy orders going_down (0.476) > going_up (0.447) > walking (0.366),
matching the clinical reality that stair *descent* is the riskier activity
for older adults. But the top of the scale is running (0.703) and jumping
(0.645) — vigorous *healthy* movement. The proxy measures motion
intensity/instability, not danger, and it happily conflates the two.
Meanwhile the quiet transitions clinicians care about —
getting_up 0.252, sitting_down 0.238, standing_up 0.222 — score no higher
than lying still (0.257). An intensity proxy is blind to the wobble in a
sit-to-stand. Any real fall-risk signal has to look at *how* a transition
is performed, not just how energetic it is.

**4. Class imbalance mirrors real life, and the model handles it — mostly.**
Walking (1,738 windows) and running (1,985) dominate; sitting_down has
only 200. Despite that, sitting_down still hits 0.925 accuracy. The
exception is getting_up (216 windows, 0.791): rare *and* confusable is a
bad combination, and it's another argument that transitions need dedicated
modeling rather than being one class among nine.

## Where this could go — concrete uses at scale

1. **Caregiver early warning, before the first fall.** Run the proxy
   longitudinally against each person's own baseline (not a population
   mean, as this prototype does). A slow drift — walking getting
   jerkier month over month — triggers a check-in or a physical-therapy
   referral while the person is still independent. One prevented hip
   fracture pays for a lot of sensing.
2. **Post-discharge monitoring without wearables.** Hospitals send older
   patients home with a phone-based monitor instead of a wearable they'll
   forget to charge. No behavior change required, no camera in the
   bedroom — adherence comes free because the sensor is already in their
   pocket.
3. **Population-level prevention targeting.** Health systems and insurers
   could screen for high-risk cohorts and direct them to strength-and-
   balance programs (which are proven to cut fall rates), instead of
   spending prevention dollars uniformly. The sensing is cheap; the
   targeting is what's missing today.

## Limitations (blunt version)

- **Not a medical device.** No clinical validation whatsoever. Do not use
  these scores for any health decision, for anyone, ever.
- **Wrong population, wrong setting.** The data comes from 30 healthy
  volunteers aged 18–60 performing scripted activities in a lab with a
  phone in their pocket. There are no older adults, no real homes, no
  clutter, no walkers, no second person in the room. Generalization to
  actual elder living is entirely unproven.
- **The "risk" score was never validated against falls.** It is a
  heuristic built from motion intensity/instability features, standardized
  against the dataset population — not against any individual's baseline,
  and never correlated with real fall outcomes. The dataset's falls are
  *simulated* by young volunteers and were deliberately excluded from the
  pipeline; nothing here predicts falls.
- **Optimistic accuracy.** The train/test split is stratified but *not*
  subject-disjoint — the same people's windows appear in both sets — so
  0.9703 overstates how it would do on a stranger.
- **Single sensor, single placement.** Everything assumes a
  pocket-positioned phone accelerometer at 50 Hz. Real ambient sensing
  (wall sensors, different placements, sampling rates) is a different
  problem this prototype doesn't touch.

## Project layout

```
aging-in-place/
├── README.md
├── requirements.txt
├── .gitignore
├── data/                    # fetched dataset (gitignored)
├── results/                 # metrics.txt + figures from the real run
├── scripts/
│   ├── fetch_data.py        # downloads UniMiB SHAR into data/
│   └── run_pipeline.py      # entry point: python scripts/run_pipeline.py
└── src/aging/
    ├── __init__.py
    ├── __main__.py          # `python -m aging` (with src/ on path)
    ├── pipeline.py          # orchestration + metrics + figures
    ├── data.py              # .mat loading → numpy windows
    ├── features.py          # 37 interpretable time-domain features
    ├── classify.py          # random-forest activity classifier
    └── risk.py              # fall-risk proxy score
```
