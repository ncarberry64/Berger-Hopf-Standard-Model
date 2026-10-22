# Blackhole Tracker rc4: formal reviewer source

This BHSM repository is the formal reviewer home. `Manuscript-Generation`
is the development workspace. Norman P. Carberry is the hypothesis and
research author. The 176 upstream files are copied byte-for-byte from
immutable development commit `3dedfc526cb534011ba28921df850bc2d1224fc3`.
[FORMAL_PROVENANCE.json](FORMAL_PROVENANCE.json) records their paths, sizes
and SHA-256. The [manuscript/release receipt](../../papers/bhsm_blackhole_tracker_20261021/provenance/FORMAL_REPOSITORY.json)
records the formal product-code citation separately, avoiding a
self-referential future commit. This guide is a formal addition; upstream
source files remain byte-exact.

Use the complete `BHSM_Blackhole_Tracker_Source.zip` or a matching
`blackhole-tracker-paper-and-source` CI artifact. Its root contains `products/`,
`papers/`, `tools/` and both license notices. A full clone of the much larger
BHSM repository is optional. The source includes four notebooks, the app,
CLI/Python APIs, tests, pinned providers and historical validation records.
The current product suite has **244 tests**. Software verification and replay
do not establish scientific acceptance or journal acceptance.

## Install and run

Python 3.11 or newer is required; the dedicated Linux/Windows CI uses 3.12.
From the source-archive or BHSM root:

```text
cd products/blackhole_tracker
python -m pip install -e ".[dev,astrometry]"
python -m bhtracker serve --open
```

This explicitly opts into Astropy for the joint research tests and notebooks.
For base resolved-image/native-photometry use, `python -m pip install .`
suffices. Windows users can double-click `Start_Blackhole_Tracker.cmd`; joint
research uses the separate **`Start_Blackhole_Tracker_Joint.cmd`** or the explicit
`--astrometry` flag. Dependencies install from the configured package index;
opening a web page never installs them. See the [complete user guide](README.md)
for virtual-environment, local-wheel, port and export/replay instructions.

## Three observation routes and their limits

The resolved route fits one compact exterior's mass, center and observer
motion under supplied distances, primary-pair association and full covariance.
The BHSM Einstein/GHY interpretation counts the same optical potential once.
A supplied enclosing radius is not an observed hard surface or horizon.
The optional R1 extension has separate source, metric and admission assumptions.
Numerical references do not impose physical priors; unidentified reporting
covariance stays unavailable and profiles seek admitted nuisance states.

The native-magnitude route at `/photometry` preserves measurement errors,
source-row identities, clocks, calibration annotations and raw hashes. The
[frozen pilot](../../papers/bhsm_blackhole_tracker_20261021/real_data_pilot_20261022/README.md)
keeps all 100 events/76,344 observations: 89 simple-model inadequate and 11
photometric-screen fits, with two archival follow-ups. Every pilot mass remains
unresolved. The corresponding 2022 benchmark retains its original ambiguous
HST time/frame metadata; no precision epoch is guessed.

The separately versioned `/joint` route uses calibrated native photometry and
angular centroids. Explicitly install the optional `astrometry` extra and
follow [JOINT_RESEARCH.md](JOINT_RESEARCH.md). The reviewed
`BHSM_OB110462_2023_SourcePack_v1.zip` has exact author observations, 82 exposure
header prefixes, hashes, rights, timing evidence and a refetch helper. The app
checks its hash and imports data without executing archived helpers. It keeps
all 15,533 original OGLE rows and documented selection/calibration; the fit uses
12,500 selected OGLE rows, 21 HST magnitudes and 21 two-coordinate angular
rows at 11 dated visits. This 2023 version never replaces the original 2022 benchmark.

**All three declared known-system model/noise candidates fail adequacy. No
reliable mass interval or black-hole identification is accepted by this run.**
A converged state, global quadratic or successful forward replay does not
override failed structure, an artificial cap or unstable parameters. The
published object's classification is prior literature evidence. Read the
[negative campaign record](../../papers/bhsm_blackhole_tracker_20261021/joint_known_system_20261022/README.md)
and its [unsent manual calibration request](../../papers/bhsm_blackhole_tracker_20261021/joint_known_system_20261022/MANUAL_CALIBRATION_DATA_REQUEST_TEMPLATE.txt).
New calibration/observations require a new frozen protocol. No mass is
inferred from duration alone; no core mode, membrane deformation, horizon,
absolute lens motion, lens distance or new black-hole discovery is established.

## Verification and reproducibility

From the BHSM/source-archive root:

```text
python tools/verify_blackhole_tracker_snapshot.py
cd products/blackhole_tracker
python -m pytest -q tests
python -m pip wheel --no-deps . --wheel-dir dist
cd ../..
python tools/smoke_blackhole_tracker_wheel.py --wheel products/blackhole_tracker/dist/bhsm_blackhole_tracker-0.2.0rc4-py3-none-any.whl
```

The dedicated workflow installs `[dev,astrometry]` for the full product suite
on Linux and Windows with Node 24 browser-contract checks. It retains a
separate fresh **base-only** wheel installation for resolved/native fits,
then a second noneditable wheel installation with `[astrometry]` for the
synthetic joint recovery/null/replay control. It runs the optional probe with
isolated Python from outside the checkout. To repeat that probe after
installing the matching wheel with its extra in a fresh environment, run from
an unrelated working directory, replacing the absolute paths:

```text
python -I /absolute/path/products/blackhole_tracker/scripts/probe_joint_install.py --output /absolute/path/joint-install-receipt.json
```

`--sourcepack ZIP` and `--result RESULT.json` optionally add actual native
import and saved-state export/replay checks. The safe CI default is synthetic;
no measured-event acceptance is inferred from that control. The four notebooks
are `01_compact_mass_and_motion`, `02_conditional_boundary_response`,
`03_native_unresolved_photometry` and `04_joint_astrometry_and_parallax`.
The [validation directory](validation/) retains matching receipts; historical
rc2/rc3 evidence is not relabeled as final rc4 evidence.

The top-level BHSM core Python 3.10+ matrix is separate from the product's
Python 3.11+ requirement. Its dispatch-only full historical corpus is not
silently claimed to have run. Historical Monte Carlo calibration in
`scripts/validate_product.py`, the frozen 100-event analysis and the separate
joint campaign each have their own protocol and scope.

The dated BHSM theory/source record is pinned at
`705d4c7e2f9a832b457f63ff975e7d4dc8008645`. The package carries its exact
source ledger and interpretation files. The ordinary exterior and boundary
representation remain one potential. Conditional responses supply no terminal
core-transfer law or an inferred microscopic core state.

Build and verify the complete source archive from the BHSM root:

```text
python papers/bhsm_blackhole_tracker_20261021/scripts/package_release.py tmp/tracker-release
python tools/verify_blackhole_tracker_release.py --archive tmp/tracker-release/BHSM_Blackhole_Tracker_Source.zip
```

The complete archive contains both canonical notices, all three paper
folders, the installable product and verification/reproduction helpers.
Its manifest excludes its own hash. Paper CI compiles to a temporary output
directory and verifies/regenerates theory inputs in an isolated extracted
copy; it leaves the committed reviewed PDF untouched. The
[central paper](../../papers/bhsm_blackhole_tracker_20261021/README.md),
[reviewed PDF](../../papers/bhsm_blackhole_tracker_20261021/manuscript/main.pdf)
and [formal release provenance](../../papers/bhsm_blackhole_tracker_20261021/provenance/FORMAL_REPOSITORY.json)
record the manuscript separately. Prior source/review history remains preserved.

[Repository licensing](../../LICENSE.md) and [academic evaluation permission](../../ACADEMIC_USE.md)
accompany the BHSM source. Native source-pack data and retained providers keep
their original authors' attribution, licenses and domain statements. The manual
journal-submission handoff performs no upload, external review or acceptance.
