# Blackhole Tracker: formal reviewer source

This BHSM repository is the authoritative reviewer-facing home of this
research product. The `Manuscript-Generation` repository is its development
workspace. Norman P. Carberry is the hypothesis and research author.

For a focused review, use the verified `BHSM_Blackhole_Tracker_Source.zip`
supplied with the research handoff or the `blackhole-tracker-paper-and-source`
artifact from the dedicated GitHub workflow. Extract it to a new directory
and open a terminal in its root, which contains `products/`, `papers/`,
`tools/` and both license notices. The commands below work from that extracted
root. A complete clone of the much larger BHSM repository is optional.

The 108 upstream product files here are byte-exact Git-blob copies from
workspace commit `ab0fd069195f63a864d74b0926d23311f1c3523e`, including the
runtime, examples, two executed notebooks, tests, source pins and historical
validation receipts. [FORMAL_PROVENANCE.json](FORMAL_PROVENANCE.json) records
every source path, byte count and SHA-256. It excludes its own hash and the
future BHSM commit, avoiding a self-referential receipt. This reviewer guide
is an additional formal-repository document. The upstream README is retained
verbatim as part of the provenance snapshot; use the BHSM paths below.

From the BHSM checkout, with Python 3.11 or newer (CI uses 3.12):

```powershell
cd products/blackhole_tracker
python -m pip install -e ".[dev]"
python -m bhtracker serve --open
```

Windows users can double-click `Start_Blackhole_Tracker.cmd` in this directory.
The app is local. The [upstream user guide](README.md) documents the versioned
measurement schema, full covariance ordering, CLI, Python API, export/replay,
notebooks and inference-status meanings. Declared observed data remain distinct
from the supplied synthetic examples. No survey acquisition or submission is
performed. The root [license](../../LICENSE.md) applies; retained providers keep
their source attribution and domain statements.

Reviewer checks from the BHSM root:

```powershell
python tools/verify_blackhole_tracker_snapshot.py
cd products/blackhole_tracker
python -m pytest -q tests
python -m pip wheel --no-deps . --wheel-dir dist
cd ../..
python tools/smoke_blackhole_tracker_wheel.py --wheel products/blackhole_tracker/dist/bhsm_blackhole_tracker-0.2.0rc2-py3-none-any.whl
```

The dedicated workflow runs the product tests on Linux and Windows with Node24
for the browser-contract fixture, then installs its wheel in a fresh environment
outside the checkout. The core BHSM Python3.10+ matrix is retained separately;
the tracker has its own Python3.11+ requirement. This does not hide or replace
existing tests. `scripts/validate_product.py` also contains the historical
Monte Carlo calibration replay; it is not needed for this unchanged-source
publication and is not rerun by this integration's CI.

Wheel building uses the declared isolated build-system requirements rather
than depending on a preinstalled host backend. Reviewer fit/export/replay uses
the vendored provider and source pins in this snapshot. The optional developer
source-sync script requires the complete three-paper source tree; it is a
provenance tool, not a prerequisite for using the installed product. The formal
paper workflow checks source regeneration in an isolated copy when that tree
is available, leaving this reviewed snapshot untouched.

The ordinary workflow estimates one compact exterior's mass, center and motion
under its supplied distances, calibrations, primary-pair association and full
covariance. Its BHSM boundary interpretation counts the same configuration
once. The enclosing radius is supplied, not a measured hard boundary/horizon.
R1 response is a conditional extension with distinct metric/source and
admission assumptions. The source package preserves projection nulls,
degeneracies, rejected/unresolved output suppression and the ordinary optical
regression tolerance. It derives no core mode, terminal daughter state, burn
rate or neutron-star threshold from a lens track.

The dated core/surface source remains pinned at BHSM commit
`3c820fee74a5c715ef58bf30998edb1d7b26fe78`; the package contains its exact
amendment and ledger. The formal product code citation is
`33f26a5113392c0d2c323d7e4a36c7e81bd3ee29`.

The [central paper](../../papers/bhsm_blackhole_tracker_20261021/README.md),
[reviewed PDF](../../papers/bhsm_blackhole_tracker_20261021/manuscript/main.pdf)
and its supporting angular/Hopf paper directories are preserved under `papers/`.
[FORMAL_REPOSITORY.json](../../papers/bhsm_blackhole_tracker_20261021/provenance/FORMAL_REPOSITORY.json)
records their immutable development source and the formal release-manifest
regeneration. The original supporting papers remain attributed research records.

From the BHSM root, build and verify the portable source archive:

```powershell
python papers/bhsm_blackhole_tracker_20261021/scripts/package_release.py tmp/tracker-release
python tools/verify_blackhole_tracker_release.py --archive tmp/tracker-release/BHSM_Blackhole_Tracker_Source.zip
```

The source archive contains both canonical license notices, all three paper
directories, the installable product and verification helpers. Its release
manifest excludes its own hash. The dedicated paper CI compiles the TeX source
to a temporary output directory, checks the complete source ZIP and regenerates
the packaged theory inputs in an isolated extracted copy. The committed,
visually reviewed PDF remains unchanged. See
[FORMAL_INTEGRATION_REVIEW.md](FORMAL_INTEGRATION_REVIEW.md) for findings,
corrections and the scope of these checks.
