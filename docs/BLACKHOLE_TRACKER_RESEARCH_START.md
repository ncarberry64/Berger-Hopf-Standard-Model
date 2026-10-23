# Blackhole Tracker: researcher start

**Blackhole Tracker: BHSM Boundary Interpretation of Compact-Lens Mass, Motion,
and Conditional Response** accompanies the `0.2.0rc2` research product. This
repository is the formal reviewer record. The
[Manuscript-Generation workspace](https://github.com/ncarberry64/Manuscript-Generation/pull/24)
records development history; it is not a separate source of reviewer authority.

| Review task | Start here |
| --- | --- |
| Read the manuscript | [Reviewed 30-page PDF](../papers/bhsm_blackhole_tracker_20261021/manuscript/main.pdf), [paper guide](../papers/bhsm_blackhole_tracker_20261021/README.md), [result statement](../papers/bhsm_blackhole_tracker_20261021/RESULT_STATEMENT.md) |
| Understand the contribution and limits | [Lay report](../papers/bhsm_blackhole_tracker_20261021/LAY_REPORT.md), [model chain and freedoms](../papers/bhsm_blackhole_tracker_20261021/CHAIN_AND_FREEDOMS.md), [validation](../papers/bhsm_blackhole_tracker_20261021/VALIDATION.md) |
| Install the app or reproduce an analysis | [Formal product guide](../products/blackhole_tracker/REVIEWER.md), followed by the complete [user and measurement guide](../products/blackhole_tracker/README.md) |
| Inspect independent internal review | [Installed usability review](../papers/bhsm_blackhole_tracker_20261021/review/RC2_INSTALLED_USABILITY_REVIEW.md), [scientific/editorial review](../papers/bhsm_blackhole_tracker_20261021/review/RC2_SCIENTIFIC_EDITORIAL_REVIEW_20261022.md), [derivation review](../papers/bhsm_blackhole_tracker_20261021/review/CORE_SURFACE_DERIVATION_REVIEW_20261022.md) |
| Inspect public explanation and animation | [Blackhole Tracker Museum exhibit](https://ncarberry64.github.io/Berger-Hopf-Standard-Model/#blackhole-tracker), [Museum source](../museum/) |

The paper is prepared for *Galaxies*. Preparation, internal review and successful
software checks do not assert journal submission, external peer review or
acceptance. Bundled measurements and the exhibit animation are synthetic.

## A first complete run

Use Python 3.11 or newer; the dedicated product CI uses Python 3.12 on Linux
and Windows. For direct app access, the
[Museum exhibit](https://ncarberry64.github.io/Berger-Hopf-Standard-Model/#blackhole-tracker)
provides the exact reviewed product ZIP and wheel with research-license notices.
Extract the product ZIP completely; its app directory is `product/`, where
Windows users can double-click `Start_Blackhole_Tracker.cmd`. The environment
installation commands below also apply from that directory on other platforms.
For the complete paper/reviewer source, obtain the portable source archive
from a completed run of the
[Formal Blackhole Tracker workflow](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/blackhole-tracker.yml).
Select a run and revision explicitly, rather than treating any latest run as
the manuscript's reviewed release. The `blackhole-tracker-paper-and-source`
artifact includes the product, three paper directories, verification helpers
and license notices. A complete BHSM clone is optional.

From the root of that archive or this checkout:

```text
cd products/blackhole_tracker
python -m venv .venv
```

Install and launch using the environment's interpreter. PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m bhtracker serve --open
```

Linux/macOS:

```bash
.venv/bin/python -m pip install .
.venv/bin/python -m bhtracker serve --open
```

Windows users can instead double-click
[`Start_Blackhole_Tracker.cmd`](../products/blackhole_tracker/Start_Blackhole_Tracker.cmd)
in the product directory. The default app address is
`http://127.0.0.1:8765/`; add `--port 8766` if the port is occupied. The Museum
explains the workflow and provides access instructions; inference runs in the
locally installed application. Dependency installation uses the configured
package index. Fitting needs no remote account or API key.

1. Load **Nearby compact-mass track** (CLI example `nearby_motion`), select **Validate dataset**, then **Run fit** with
   **Ordinary lens response**.
2. Read the status, mass, reference center, observer proper motion, uncertainties
   and residuals. Open the BHSM interpretation to see which quantities are
   fitted, derived at a declared radius or proposed.
3. Select **Download replay bundle** and retain that ZIP with the wheel/revision
   used. It includes input, full covariance, fit controls, result and provenance.
4. Replay the downloaded ZIP in a fresh output directory, using the same
   installed interpreter. Replace the example filename with the actual download:

```text
python -m bhtracker replay /path/to/bhsm-analysis-replay.zip --output /path/to/fresh/replayed
```

Here and below, `python` means the installed environment interpreter shown
above. Inspect `replayed/replay_check.json` for prediction differences and
software/interpretation comparisons. Older exports can retain matching
predictions while recording an explicit interpretation-version change.

For a browser-free round trip, run from the product directory with that same
interpreter:

```text
python -m bhtracker example nearby_motion --output user_runs/nearby.json
python -m bhtracker validate user_runs/nearby.json
python -m bhtracker fit user_runs/nearby.json --family gr --nuisance shear --starts 3 --output user_runs/fit
python -m bhtracker replay user_runs/fit --output user_runs/replayed
```

Use fresh output directories. The CLI name `gr` selects the ordinary optical
family with its explicit BHSM interpretation. For the Python API, complete
CSV/full-covariance contract, negative statuses and conditional `r1` mode, use
the [product guide](../products/blackhole_tracker/README.md). The executed
notebooks are [mass and motion](../products/blackhole_tracker/notebooks/01_compact_mass_and_motion.ipynb)
and [conditional boundary response](../products/blackhole_tracker/notebooks/02_conditional_boundary_response.ipynb).
Their replay dependencies and interpreter selection are described in the
[paper reproduction guide](../papers/bhsm_blackhole_tracker_20261021/README.md#reproduce-the-separate-calculations).
Full historical calibration is a separate reproduction task, not a first-run
installation requirement.

## What the BHSM result does and does not establish

The adopted Einstein/GHY sector describes one compact exterior. Ordinary
mass, center and motion fit that same configuration; its spherical boundary
representation counts the same gravitational potential once. A supplied
enclosing radius is not an observed hard surface. The optional R1 calculation
has separate source/metric matching and admission assumptions. A supported
track is evidence for the admitted optical model, not a unique microscopic
BHSM state, a horizon detection or an already discovered new black hole.
Rejected, partly constrained and unresolved results remain scientific outputs.

The [boundary dictionary](../papers/bhsm_blackhole_tracker_20261021/provenance/bhsm_boundary_mass_interpretation.md)
and [hashed source ledger](../papers/bhsm_blackhole_tracker_20261021/provenance/bhsm_boundary_mass_interpretation_sources.json)
connect those interpretations to recovered BHSM sources. The
[22 October core/surface amendment](BHSM_NORMAN_CORE_SURFACE_AMENDMENT_20261022.md)
separates abstract, nonspacetime core data from spacetime-side surface dynamics;
its [claim ledger](../artifacts/current_semantics/BHSM_NORMAN_CORE_SURFACE_AMENDMENT_20261022.json)
records remaining matching and terminal-transfer requirements. No measured
core parameter or terminal rate is supplied by the tracker.

For the broader program, read [claim boundaries](../CLAIMS.md),
[current BHSM status](current_bhsm_status.md), the
[system integration map](../artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json)
and [gate ledger](../theory/gate_ledger.md). `FULL_BHSM_COMPLETE = FALSE` remains
the program's status; product reproducibility does not close unrelated physical
completion gates.

## Revisions, citations and repository layout

The reviewed product code is pinned at
[`33f26a5113392c0d2c323d7e4a36c7e81bd3ee29`](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/33f26a5113392c0d2c323d7e4a36c7e81bd3ee29/products/blackhole_tracker).
The completed manuscript/integration review is pinned at
[`1fd11510cd217218d6b230cb50516776eb746e1a`](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/1fd11510cd217218d6b230cb50516776eb746e1a/papers/bhsm_blackhole_tracker_20261021).
The dated amendment source pin is
`3c820fee74a5c715ef58bf30998edb1d7b26fe78`. Later navigation or Museum changes
do not rewrite these historical source citations. Cite Norman P. Carberry,
the formal BHSM repository, the relevant paper/product path and exact revision;
see [CITATION.cff](../CITATION.cff) and the exported `project_citation` records.

| Location | Research role |
| --- | --- |
| `papers/bhsm_blackhole_tracker_20261021/` | Central manuscript, reviewed PDF, results, internal review and provenance |
| `products/blackhole_tracker/` | Installable product, full-covariance examples, tests and executed notebooks |
| `papers/bhsm_angular_lensing_20261021/`, `papers/bhsm_state_rotation_20261021/` | Preserved supporting calculations and provider/source history, with their own domains |
| `docs/`, `theory/`, `artifacts/current_semantics/` | Current interpretation, derivations, explicit open objects and machine-readable source/claim records |
| Versioned campaign documents and archived records | Historical conclusions for their stated actions/domains; use the [documentation index](README.md) to follow later successors |
| `museum/` | Public animation and explanation; presentation data do not feed inference |

Source locations and frozen artifacts are preserved for replay. The top-level
BHSM core package is a separate installation from the tracker product. The
[institutional guide](INSTITUTIONAL_START.md) provides its bounded core checks.
Tracker checks and portable archive verification are in the
[formal product guide](../products/blackhole_tracker/REVIEWER.md).

[Academic evaluation permission](../ACADEMIC_USE.md) and the
[repository license](../LICENSE.md) accompany the research source. Commercial
rights are reserved; retained providers preserve their own attribution and
scope.
