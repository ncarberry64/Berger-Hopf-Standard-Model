# Blackhole Tracker: formal reviewer source

This BHSM repository is the authoritative reviewer-facing home of this
research product. The `Manuscript-Generation` repository is its development
workspace. Norman P. Carberry is the hypothesis and research author.

The 107 upstream product files here are byte-exact Git-blob copies from
workspace commit `bb68862018c1859df35fe9df22bf28c416469227`, including the
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
python -m pip wheel --no-deps --no-build-isolation . --wheel-dir dist
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
amendment and ledger. Formal paper sources and reviewed PDF will be added under
`papers/bhsm_blackhole_tracker_20261021/`, with the original supporting sibling
paper directory names preserved. This code publication precedes that paper
addition so its availability statement can cite an actual BHSM code commit.
