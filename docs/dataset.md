# Dataset provenance

- **Dataset:** UniMiB SHAR — *UniMiB SHAR: a new dataset for human activity
  recognition using acceleration data from smartphones* (Micucci, Mobilio,
  Napoletano, 2017).
- **URL:** <http://www.sal.disco.unimib.it/technologies/unimib-shar/>
- **Contents used:** ADL split — **7,579 windows** × 151 samples @ 50 Hz,
  **9 activities of daily living**, **30 subjects**. (The dataset also
  ships 4,192 simulated-fall windows, fetched for reference but
  deliberately excluded from the pipeline — see limitations.)
- **License:** the distribution ships **no explicit license file**; it is
  released for research use with a citation request. If you use the data,
  cite: Micucci et al., *arXiv:1611.07688* (2017).
- **Verification:** downloaded from the research group's official link
  before building; fetch script reproduces the exact download.
- **Storage:** raw data downloads to `data/` (gitignored, never
  committed). Only derived artifacts (`results/`) are committed.
