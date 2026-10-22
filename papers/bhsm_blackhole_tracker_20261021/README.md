# Blackhole Tracker: BHSM interpretation and native-observation baseline

Blackhole Tracker is a runnable lens-inference research product with a local app, CLI, Python API, notebooks and replayable exports. Release candidate 0.2.0rc4 preserves resolved-pair inference, native unresolved photometry and a separately versioned joint astrometry/parallax research route. All three frozen joint noise models fail the known-system adequacy checks; no reliable black-hole mass is accepted.

The **formal reviewer repository is [BHSM](https://github.com/ncarberry64/Berger-Hopf-Standard-Model)**, branch [codex/blackhole-tracker-real-data-20261022](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/codex/blackhole-tracker-real-data-20261022). Formal product: `products/blackhole_tracker/`; paper: `papers/bhsm_blackhole_tracker_20261021/`. Manuscript-Generation is a development workspace. The rc4 product code is pinned to formal [9f1768a7fbac](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/9f1768a7fbac1d16e0e25713f87b8191cbe02249/products/blackhole_tracker). Final release receipts pin actual source, wheel, PDF and CI revisions.

## Start with the evidence

- [Plain-language account](LAY_REPORT.md) and [precise result statement](RESULT_STATEMENT.md).
- [Complete real-data pilot and replay instructions](real_data_pilot_20261022/README.md).
- [All 100 results with literature annotations](real_data_pilot_20261022/literature_annotations_v1/all_100_results.csv), [JSON](real_data_pilot_20261022/literature_annotations_v1/all_100_results.json).
- [Two historical archival-follow-up targets](real_data_pilot_20261022/literature_annotations_v1/followup_ranking.csv); their masses remain unavailable.
- [All 100 residual plots](real_data_pilot_20261022/derived_v1/residuals/) and [diagnostics/profiles](real_data_pilot_20261022/derived_v1/diagnostics/).
- [2023 joint known-system audit](joint_known_system_20261022/README.md), including failed baselines, profiles, controls and reproduction instructions.
- [2022 known-system benchmark](real_data_pilot_20261022/derived_v1/historical_benchmark/summary.json).
- [Validation scope and receipts](VALIDATION.md), [native-data paper section](manuscript/real_observations.tex) and [BHSM interpretation](manuscript/bhsm_interpretation.tex).
- [Product guide](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/9f1768a7fbac1d16e0e25713f87b8191cbe02249/products/blackhole_tracker/README.md) and [prior-literature audit](review/REAL_DATA_PRIOR_LITERATURE_20261022.json).

The frozen pilot uses all 100 supplied historical OGLE-III events and 76,344 native numeric rows. All 109 raw hashes and exact selection verify. Eighty-nine fail the stated PSPL photometric adequacy screen; eleven are not rejected by that screen. Only 0585 and 3092 pass every stricter archival-follow-up rule. Neither is a new event or a measured black hole. All pilot mass, distance and absolute-motion fields remain unavailable.

The 2022 OB110462 benchmark retains its own observation version and unresolved HST export mapping. The separate rc4 benchmark uses the published 2023 HST reduction, actual matched exposure metadata and corrected OGLE photometry: 12,521 photometric rows and 21 angular rows at 11 visits. It is not a substitution into the older benchmark. All three frozen noise models converge, yet fail residual-structure checks; the calibrated-error competitor also reaches its correlation-timescale cap. Conditional masses and profile crossings are diagnostic, not accepted mass measurements. Forty parametric controls and whole-observing-night heldout predictions remain auditable. No new black hole or reliable known-system identification is claimed.

## Run and replay an analysis

Install the supplied wheel using the Python environment selected for the project, then open the local app:

```powershell
python -m pip install C:/path/to/bhsm_blackhole_tracker-0.2.0rc4-py3-none-any.whl
python -m bhtracker serve --open
```

For an actual optimized OGLE-III photometry file, use the native route documented in the product guide. The optional metadata JSON preserves event aliases/catalog provenance; it does not add mass information.

```powershell
python -m bhtracker import-ogle3 C:/path/to/photometry.dat --metadata C:/path/to/event_metadata.json --output C:/path/to/native.json
python -m bhtracker fit-photometry C:/path/to/native.json --output C:/path/to/native_analysis
python -m bhtracker replay C:/path/to/analysis.zip --output C:/path/to/replayed
```

For the optional joint route install the wheel with `[astrometry]` (or run `Start_Blackhole_Tracker_Joint.cmd`) and open `/joint`. Import the hash-verified 2023 source ZIP or a calibrated versioned JSON. See the [joint guide](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/9f1768a7fbac1d16e0e25713f87b8191cbe02249/products/blackhole_tracker/JOINT_RESEARCH.md). Four notebooks run against a clean installed wheel.

The app supports native import, diagnostics, BHSM interpretation, export and replay. A photometric fit reports its model status and unavailable quantities. The resolved-image import contract remains separate and requires its actual positions/flux ratios/delays and supplied covariance.

The complete frozen100-event analysis has a separate replay wrapper, because later interface/provenance edits must not overwrite historical kernel identity. From `real_data_pilot_20261022/`:

```powershell
python reproduce_frozen_pilot.py --verify-only --data-root C:/path/to/data
python reproduce_frozen_pilot.py --data-root C:/path/to/data --output C:/path/to/new_external_output
```

The data root contains `download_manifest.json`, `pilot_selection.json` and `raw/`. The wrapper checks hashes, reconstructs the exact frozen own-code layout in a temporary workspace, and refuses an existing started output directory. Verification-only reproduces selection without fitting. Full replay retains every event and unsuccessful case.

## BHSM and what the observations identify

One optical exterior is interpreted in the declared BHSM Einstein/GHY sector and counted once. Mass identified by suitable observations can be represented as a declared static sphere's curvature deficit or Brown–York energy. Native brightness-only timescales do not identify that mass, so these derived quantities remain unavailable. Agreement with an ordinary lens model does not test the abstract core or detect a new deformation.

The dated core/surface proposal assigns no primitive spacetime metric, clock, trajectory or frequency to the abstract core. Reviewed theory/source revision [705d4c7e](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/705d4c7e2f9a832b457f63ff975e7d4dc8008645) states the radial membrane assumptions and applied-pressure variation, preserves both handoff versions, and compares the recovered original PDFs at their restricted mathematical scope. It supplies no terminal core transfer or new optical coefficient.

The optional R1 transfer calculation retains a uniform sufficient state cap in its declared local exterior and exact optical blind directions. Its admitted nearby envelope remains below the supplied noise. It is conditional theory, not observed BHSM-core or black-hole deformation evidence.

## Source preservation and rights

The frozen 100-event pilot and 2022 benchmark native files remain external and unmodified. The separate 2023 portable source pack redistributes its explicitly licensed author observations with attribution and bounded HST header prefixes. [Data provenance](real_data_pilot_20261022/data_provenance/) supplies acquisition URLs, citations, hashes and selection details. The 2022 Zenodo deposit declares CC BY 4.0; no blanket OGLE redistribution license is inferred from public access. The repository distributes compact derived results, diagnostics, plots and replay/fetch instructions rather than the raw OGLE observation cohort.

Source-line identities and complete native inputs/predictions remain in the external replay output identified by the pilot summary. Literature annotations are a separate version with a receipt proving frozen numerical results/ranking unchanged. Primary searches identify four prior-parallax overlaps and 3092's OGLE/MOA aliases; incomplete novelty clearance is explicit.

## Historical evidence and scope

The prior 64- and128-draw resolved-pair calibrations remain versioned historical evidence, not reruns of the revised kernel or coverage calibration for native photometry. The original theoretical replay remains `python scripts/reproduce.py` from this paper directory. Product checks and notebook commands are in the product guide; reviewed correction and installed-workflow receipts are summarized in [VALIDATION.md](VALIDATION.md).

This completed baseline supports auditable photometric screening and historical reanalysis priorities. The software executes the supplied observations, but reliable black-hole mass identification remains unestablished. A separately frozen estimator with justified correlation/calibration assumptions, or further angular/parallax and calibration evidence, would need validation and physical association tests. No journal submission or new black-hole discovery is claimed by this baseline.
