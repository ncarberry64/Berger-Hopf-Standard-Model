# PR #98 CMS Open Data Animation

## Data shown

The animation continuously morphs 128 real muon four-vectors from 64
deterministically selected rows of the published CMS dimuon education dataset,
CERN Open Data Record 303, DOI `10.7483/OPENDATA.CMS.4M97.3SQ9` (CC0 Public
Domain). Both muons from each selected event are retained. This is a display
sample, not the full dataset and not a new benchmark run.

## PR #98 validation

PR #98 validated the BHSM Engine coordinate path over 100,000 events and
200,000 unique muon four-vectors. Replication by ten produced a 2,000,000-vector
timed workload. The committed result reports 3.225x speedup versus the
vectorized control, maximum absolute delta `5.821e-11`, and scale-aware
backward error below 2.4 machine-epsilon against a 128-epsilon CI gate.

The authoritative metrics and source checksums are in
[`artifacts/cern_open_data_benchmark/results.json`](../artifacts/cern_open_data_benchmark/results.json).

## Generation

The checked-in generator verifies the source SHA-256 when the raw CSV is
available, selects 64 evenly spaced source-event row indices, writes the compact
JSON sample, and renders the GIF and static SVG deterministically. If the raw
CSV is absent, it regenerates the visual assets from the checked-in compact
sample so ordinary repository work stays offline. The raw 15 MB CSV remains
ignored.

```bash
python docs/assets/pr98_cms_open_data_animation/generate_pr98_cms_animation.py
```

Source extraction requires the pinned source in `data/external/cern_open_data/`
or an explicit `--input` path. Regenerating the display GIF from the committed
compact sample, viewing the README, and running ordinary tests require no source
file and no network access.

## Claim boundary

This is BHSM Engine validation of precision-gated four-vector coordinate
transformations. It is not detector reconstruction, empirical validation of
BHSM Physics, CMS/CERN endorsement, or a BHSM theorem input. It changes no
frozen prediction or official prediction logic.
