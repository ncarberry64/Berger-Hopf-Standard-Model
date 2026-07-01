# PR #98 CMS Open Data Animation Assets

This directory contains a deterministic 128-vector display sample derived from
64 evenly spaced events in the checksum-pinned PR #98 CMS dimuon source. The GIF
is a continuous morph of those real four-vectors, not a slide show. It is not
the full dataset. The 15 MB source remains ignored under `data/external/`.

Regenerate after obtaining or caching the pinned source:

```bash
python docs/assets/pr98_cms_open_data_animation/generate_pr98_cms_animation.py
```

The script verifies the full PR #98 SHA-256 before extracting a new sample when
the raw source is available. If the raw source is absent, it regenerates the GIF,
SVG, and manifest from the checked-in compact sample. Ordinary README rendering
and tests use only checked-in assets and require no network access.

Scope: Engine coordinate-transformation validation only. This is not detector
reconstruction. It is not empirical validation of BHSM Physics. No CMS/CERN endorsement is claimed.
