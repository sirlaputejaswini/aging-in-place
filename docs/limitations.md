# Honest limitations

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
