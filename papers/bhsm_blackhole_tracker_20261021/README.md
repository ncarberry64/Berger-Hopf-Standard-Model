# Blackhole Tracker: BHSM inference and candidate atlas

Blackhole Tracker is a runnable lens-inference research product with a local app, CLI, Python API, notebooks and replayable exports. The RC5 update adds a candidate sky atlas: 155 distinct historical source/event directions, three differently qualified investigation targets, and a separate published black-hole benchmark. Candidate selection is useful before a precise mass is available. No new black hole or reliable engine recovery of the known benchmark is established. The resolved-pair, native-photometry and separately versioned joint routes retain their earlier evidence and limitations.

The **formal reviewer repository is [BHSM](https://github.com/ncarberry64/Berger-Hopf-Standard-Model)**, branch [codex/blackhole-tracker-real-data-20261022](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/codex/blackhole-tracker-real-data-20261022). Formal product: `products/blackhole_tracker/`; paper: `papers/bhsm_blackhole_tracker_20261021/`. Manuscript-Generation is a development workspace. Historical RC4 code remains pinned to [1a556d37a40e](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/1a556d37a40ef89deb54f9c07d231b5496163838/products/blackhole_tracker); that pin does not certify the atlas additions. The RC5 product is pinned to [8ca349fa8eb5](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/8ca349fa8eb5c54c661a022790ae915d05060b59/products/blackhole_tracker) with 193 exact upstream files. Installed 257-test/29-subtest checks, five notebooks and actual browser export/replay pass. The 45-page PDF and 198-word manual-submission abstract are bound by [PDF QA](provenance/RC5_PDF_VISUAL_QA.json) and [RC5 submission metadata](submission/rc5/submission_metadata.json). Final hosted CI is recorded separately against the exact remote heads.

## Start with the evidence

- [Plain-language account](LAY_REPORT.md) and [precise result statement](RESULT_STATEMENT.md).
- [Portable candidate-inventory metadata and offline rebuild](candidate_atlas_20261023/README_INVENTORY_v3.txt), [155-event inventory plus separate benchmark](candidate_atlas_20261023/inventory_v3.json), and [independent portable-rebuild check](candidate_atlas_20261023/INDEPENDENT_PORTABLE_INVENTORY_REVIEW.json).
- [Complete real-data pilot and replay instructions](real_data_pilot_20261022/README.md).
- [All 100 results with literature annotations](real_data_pilot_20261022/literature_annotations_v1/all_100_results.csv), [JSON](real_data_pilot_20261022/literature_annotations_v1/all_100_results.json).
- [Two historical archival-follow-up targets](real_data_pilot_20261022/literature_annotations_v1/followup_ranking.csv); their masses remain unavailable.
- [All 100 residual plots](real_data_pilot_20261022/derived_v1/residuals/) and [diagnostics/profiles](real_data_pilot_20261022/derived_v1/diagnostics/).
- [2023 joint known-system audit](joint_known_system_20261022/README.md), including failed baselines, profiles, controls and reproduction instructions.
- [2022 known-system benchmark](real_data_pilot_20261022/derived_v1/historical_benchmark/summary.json).
- [Validation scope and receipts](VALIDATION.md), [native-data paper section](manuscript/real_observations.tex) and [BHSM interpretation](manuscript/bhsm_interpretation.tex).
- [Formal product guide](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/codex/blackhole-tracker-real-data-20261022/products/blackhole_tracker/README.md) and [prior-literature audit](review/REAL_DATA_PRIOR_LITERATURE_20261022.json).

The atlas reconciles the 100-event pilot with all 59 Wyrzykowski et al. (2016) parallax events, counting four exact shared identities once: **100 + 59 - 4 = 155**. All 142 published parallax model modes remain metadata. Twenty-six older 2015 tables were located and hash-verified (19,068 rows); 33 exact-ID matches remain unavailable. Their 2016 reduction, masks and calibration are not assumed identical. The atlas performs no new parallax fit and creates no new follow-up ranking.

Its three investigation targets have distinct bases. 0585 and 3092 passed the original frozen photometric follow-up screen; PAR-13 retains a disputed, prior-dependent literature possibility, with unreliable Gaia source astrometry and a lower-mass alternative recorded. The historical 13 dark-remnant-consistent events are not 13 black holes. Later literature also revises PAR-02 toward a roughly 0.9-solar-mass star under its adopted priors. None of the 155 entries receives a new black-hole candidate or strongly identified tier. The separate OB110462 benchmark has strong published support labeled **literature**, while independent engine recovery remains unresolved and uncalibrated.

Map markers locate catalog source/event directions. J2000 is an equinox, not an observing epoch or a current lens position. Lens position, uncertainty, mass, distance, absolute proper motion and radial velocity remain null. The atlas supplies no three-dimensional or propagated lens location; unmarked sky is not evidence of black-hole absence.

The frozen pilot uses all 100 supplied historical OGLE-III events and 76,344 native numeric rows. All 109 raw hashes and exact selection verify. Eighty-nine fail the stated PSPL photometric adequacy screen; eleven are not rejected by that screen. Only 0585 and 3092 pass every stricter archival-follow-up rule. Neither is a new event or a measured black hole. All pilot mass, distance and absolute-motion fields remain unavailable.

The 2022 OB110462 benchmark retains its own observation version and unresolved HST export mapping. The separate rc4 benchmark uses the published 2023 HST reduction, actual matched exposure metadata and corrected OGLE photometry: 12,521 photometric rows and 21 angular rows at 11 visits. It is not a substitution into the older benchmark. All three frozen noise models converge, yet fail residual-structure checks; the calibrated-error competitor also reaches its correlation-timescale cap. Conditional masses and profile crossings are diagnostic, not accepted mass measurements. Forty parametric controls and whole-observing-night heldout predictions remain auditable. No new black hole or reliable known-system identification is claimed.

## Run and replay an analysis

Install the supplied wheel using the Python environment selected for the project, then open the local app:

```powershell
python -m pip install C:/path/to/bhsm_blackhole_tracker-0.2.0rc5-py3-none-any.whl
python -m bhtracker serve --open
```

Use the matching wheel only after its release checks are complete. To open the atlas directly, use `python -m bhtracker serve --open --page atlas` or the atlas launcher. Metadata-only CLI export and replay use fresh output paths:

```powershell
python -m bhtracker atlas list --tier BLACK_HOLE_SEARCH_TARGET --output C:/path/to/targets.json
python -m bhtracker atlas export --tier BLACK_HOLE_SEARCH_TARGET --output C:/path/to/targets_replay.json
python -m bhtracker atlas replay C:/path/to/targets_replay.json --output C:/path/to/fresh_restored_atlas
```

JSON replay retains every event and the separate benchmark, including unselected and failed records, together with the filters and exact selected records. It preserves the original UTF-8 inventory text and line endings. Hash checks establish consistency; they are not authenticity signatures, new fits or scientific acceptance. CSV is a filtered view; use JSON replay for the complete inventory. The Python interface is `bhtracker.candidate_atlas`.

From `candidate_atlas_20261023/`, the factual metadata rebuild works offline without redistributing native observations:

```powershell
python build_inventory_v3.py --freeze INPUT_FREEZE_v3.json --out C:/path/to/fresh_inventory.json
python test_inventory_v3.py
```

The rebuilt inventory SHA-256 is `4a76300f0e0e3883a0c9c343e1e0c5fbead595c9b4f333aaa01ec05c9ec9debc`. Original source hashes and the prior raw-file availability audit remain separate from verification of the bundled metadata snapshots.

For an actual optimized OGLE-III photometry file, use the native route documented in the product guide. The optional metadata JSON preserves event aliases/catalog provenance; it does not add mass information.

```powershell
python -m bhtracker import-ogle3 C:/path/to/photometry.dat --metadata C:/path/to/event_metadata.json --output C:/path/to/native.json
python -m bhtracker fit-photometry C:/path/to/native.json --output C:/path/to/native_analysis
python -m bhtracker replay C:/path/to/analysis.zip --output C:/path/to/replayed
```

For the optional joint route install the wheel with `[astrometry]` (or run `Start_Blackhole_Tracker_Joint.cmd`) and open `/joint`. Import the hash-verified 2023 source ZIP or a calibrated versioned JSON. See the [joint guide](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/1a556d37a40ef89deb54f9c07d231b5496163838/products/blackhole_tracker/JOINT_RESEARCH.md). Four notebooks run against a clean installed wheel.

The app supports native import, diagnostics, BHSM interpretation, export and replay. A photometric fit reports its model status and unavailable quantities. The resolved-image import contract remains separate and requires its actual positions/flux ratios/delays and supplied covariance.

The complete frozen100-event analysis has a separate replay wrapper, because later interface/provenance edits must not overwrite historical kernel identity. From `real_data_pilot_20261022/`:

```powershell
python reproduce_frozen_pilot.py --verify-only --data-root C:/path/to/data
python reproduce_frozen_pilot.py --data-root C:/path/to/data --output C:/path/to/new_external_output
```

The data root contains `download_manifest.json`, `pilot_selection.json` and `raw/`. The wrapper checks hashes, reconstructs the exact frozen own-code layout in a temporary workspace, and refuses an existing started output directory. Verification-only reproduces selection without fitting. Full replay retains every event and unsuccessful case.

## BHSM and what the observations identify

One optical exterior is interpreted in the declared BHSM Einstein/GHY sector and counted once. Mass identified by suitable observations can be represented as a declared static sphere's curvature deficit or BrownÃ¢â‚¬â€œYork energy. Native brightness-only timescales do not identify that mass, so these derived quantities remain unavailable. Agreement with an ordinary lens model does not test the abstract core or detect a new deformation.

The dated core/surface proposal assigns no primitive spacetime metric, clock, trajectory or frequency to the abstract core. Reviewed theory/source revision [705d4c7e](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/705d4c7e2f9a832b457f63ff975e7d4dc8008645) states the radial membrane assumptions and applied-pressure variation, preserves both handoff versions, and compares the recovered original PDFs at their restricted mathematical scope. It supplies no terminal core transfer or new optical coefficient.

The optional R1 transfer calculation retains a uniform sufficient state cap in its declared local exterior and exact optical blind directions. Its admitted nearby envelope remains below the supplied noise. It is conditional theory, not observed BHSM-core or black-hole deformation evidence.

## Source preservation and rights

The frozen 100-event pilot and 2022 benchmark native files remain external and unmodified. The separate 2023 portable source pack redistributes its explicitly licensed author observations with attribution and bounded HST header prefixes. [Data provenance](real_data_pilot_20261022/data_provenance/) supplies acquisition URLs, citations, hashes and selection details. The 2022 Zenodo deposit declares CC BY 4.0; no blanket OGLE redistribution license is inferred from public access. The repository distributes compact derived results, diagnostics, plots and replay/fetch instructions rather than the raw OGLE observation cohort.

Source-line identities and complete native inputs/predictions remain in the external replay output identified by the pilot summary. Literature annotations are a separate version with a receipt proving frozen numerical results/ranking unchanged. Primary searches identify four prior-parallax overlaps and 3092's OGLE/MOA aliases; incomplete novelty clearance is explicit.

## Historical evidence and scope

The prior 64- and128-draw resolved-pair calibrations remain versioned historical evidence, not reruns of the revised kernel or coverage calibration for native photometry. The original theoretical replay remains `python scripts/reproduce.py` from this paper directory. Product checks and notebook commands are in the product guide; reviewed correction and installed-workflow receipts are summarized in [VALIDATION.md](VALIDATION.md).

This completed baseline supports auditable photometric screening and historical reanalysis priorities. The software executes the supplied observations, but reliable black-hole mass identification remains unestablished. A separately frozen estimator with justified correlation/calibration assumptions, or further angular/parallax and calibration evidence, would need validation and physical association tests. No journal submission or new black-hole discovery is claimed by this baseline.
