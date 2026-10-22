# Blackhole Tracker 0.2.0rc3

The reviewed corrections make physical fits independent of numerical epoch and mass references, genuinely profile physically admitted nuisance states, and report unidentified motion covariance as unavailable. Reporting-basis and covariance contracts are versioned; legacy internal profiles require a raw-input refit. Explicit physical bounds and full measurement covariance remain enforced. The historical covariance-only regression tolerance is now 1e-9, justified by independent derivative-step resolution checks; optical/prediction and admission checks retain their original thresholds.

A separate native unresolved-photometry route is available in the app at `/photometry`, CLI, Python and a third executed notebook. It preserves every native observation, error, time convention, calibration, source hash and row identity. Exports and replay retain the exact likelihood controls. Photometry leaves mass, distance, absolute angular motion, horizon and core quantities unavailable.

The frozen supplied 100-event / 76,344-row pilot records 89 inadequate simple-model fits and 11 non-rejected photometric fits. Two historical archival follow-ups pass stricter checks; neither has a measured mass. Five photometry-only analyses of the corresponding 2022 benchmark remain inadequate. Specific HST time/frame metadata gaps block its precision joint mass inference. No mass-supported black-hole candidate or new black-hole interpretation is claimed.

The BHSM radial membrane source now states its fixed Minkowski background, constant-tension and pressure-work assumptions. Both handoff versions and both original documents are preserved and reconciled in the formal repository. This changes no optical force or fitted core parameter: one potential is counted once.

Validation: 182 product tests; clean noneditable wheel installation; resolved and actual native app fit/export/replay; unidentified-covariance replay; and three installed-wheel notebooks. Saved predictions replay exactly, with native row identities and BHSM interpretation unchanged. The new likelihood's actual-cadence injection checks are separate from historical synthetic coverage campaigns, which retain their original versions and limitations.

```text
python -m pip install bhsm_blackhole_tracker-0.2.0rc3-py3-none-any.whl
python -m bhtracker serve --open
python -m bhtracker replay analysis.zip --output replayed
```

## Previous release candidate 0.2.0rc2

This release fixes the trajectory date-label rounding defect and integrates Norman P. Carberry's dated core/surface amendment through the shared BHSM interpretation. It preserves the ordinary compact-lens engine, one-potential accounting, supplied radius and the conditional R1 metric/source-mass distinction.

- SVG trajectory endpoint labels preserve the complete supplied integer or fractional epoch. The previous three-significant-digit display rounded 2015/2025 to 2020/2030; fitted/exported dates were already correct.
- Additive interpretation schema 2 supplies a hash-checked `core_surface` contract, attributed proposal/status, concise surface/core summaries, advanced matching/claim ledger and exact source provenance. The result/measurement schema remains 1. Legacy reports stay usable.
- The shared explanation separates fitted exterior parameters, derived boundary representations and proposed core ontology. No core slider, daughter/rate probability, new halo or additional optical contribution is introduced. Unsupported numerical boundary outputs remain suppressed.
- Replay records original/current interpretation schemas and whether interpretation changed, while preserving input/covariance and the saved original bundle. The new analysis bundle and executed notebooks carry the updated metadata.
- Prospective discovery of uncatalogued compact-lens/black-hole candidates is explicit. A supported track requires suitable supplied observations/model assumptions and is not a horizon classification.
- The app, package URLs, health response, interpretation and software/export metadata cite the formal BHSM GitHub repository. Historical source pins retain their original immutable locations.
- Full review corrected imported JSON text preservation (duplicate keys must reach strict validation), rejection of nonnumeric array cells and boolean schema versions, and recovery when a restarted server no longer has a requested job. Network interruptions retain duplicate-submission protection.

Focused numerical regression compares predictions, likelihood, all stored estimates, mass/center/motion uncertainties and motion covariance with the preserved pre-interpretation and installed 0.2.0rc1 baselines at the unchanged 2e-11 tolerance. Current installed-app/export/replay, source-pin, notebook, renderer, PDF and final-head CI outcomes are recorded in the external release receipt. The original calibration and launcher hardening records below are retained; their expensive campaigns are not repeated for this interpretation/display update.

```text
python -m pip install bhsm_blackhole_tracker-0.2.0rc2-py3-none-any.whl
python -m bhtracker serve --open
python -m bhtracker replay BHSM_Blackhole_Tracker_Example_Analysis.zip --output replayed
```

The accompanying BHSM amendment carries the actual regular-side interface response calculation and constrained matching specification, and identifies the remaining terminal/core correspondence. Passing software checks is not physical confirmation of those hypotheses. See the source manifest and final two-repository commit/PR receipt.

## Previous release candidate 0.2.0rc1

This release candidate makes the BHSM-interpreted compact-lens workflow portable and reproducible. It analyzes supplied resolved image pairs, corrected geometric flux ratios, delays and full covariance.

## Changes

- Correct package installation before repository pytest, a dedicated tracker-paper build, and fresh Linux/Windows wheel checks outside the checkout; existing checks remain enabled.
- One beginner app path with labeled synthetic examples, supplied calibrations/radius, validation, ordinary BHSM fit, supported/unresolved/rejected results and replay download. Advanced R1 controls, job state and duplicate suppression are explicit. Cancellation is unavailable.
- Complete measurement CSV, metadata, full covariance and native JSON example. Strict JSON rejects duplicate keys; errors locate invalid cells and covariance conditions.
- Exports retain original input/calibrations, fit controls, software/source hashes, parameters, predictions, diagnostics, plots and interpretation. CLI/API replay verifies manifest hashes before repeating inference.
- Invalid supplied R1 timescales are rejected. Motion/evolution admission uses a conservative state-inclusive speed certificate. Ordinary and spherical zero-state predictions remain unchanged.
- The paper specifies the principal extrinsic-curvature deficit of the enclosing sphere on a static spatial slice with flat reference. Its exterior cap is sufficient; exceedance is outside the guarantee/admitted domain, not proof of impossibility.

## Verified scope

115 product tests pass, including the unchanged 2e-11 optical fixture, independent SI point-lens benchmark, full-covariance controls, admission corrections and replay. A fresh Windows wheel resolves its own dependencies. Actual CMD checks cover spaces, missing Python, missing-dependency repair and an occupied port. An installed browser walkthrough and separate 28-check usability review pass. Both notebooks execute through the installed wheel outside the checkout. GUI download, CLI, API and notebook predictions agree exactly for identical input values/configuration; integer/float JSON serialization differences are disclosed.

The theorem/projection/Brown–York chain has an independent internal adversarial review. All 28 PDF pages were rendered and visually inspected; a table float was corrected and affected pages inspected again. These are internal checks, not external peer review. Actual final-head CI outcomes and hashes appear in the accompanying external release receipt; earlier CI passes do not substitute for them.

The original 64 experiment, thresholds, every draw and approximately 2.75 empirical-SEM y-motion offset are preserved. An experiment protocol written before sampling found independent linear Gaussian response reproduces the offset and tighter optimization changes it negligibly. One separately frozen 128-draw experiment retains 126 supported tracks and two goodness-of-fit rejections. Coverage/mean guards do not reject; the uncommon tail count remains disclosed. No algorithm, covariance, threshold or empirical bias correction was tuned. This is limited synthetic evidence, not universal coverage or false-rejection calibration.

## Reproduce an analysis

```text
python -m pip install bhsm_blackhole_tracker-0.2.0rc1-py3-none-any.whl
python -m bhtracker serve --open
python -m bhtracker replay BHSM_Blackhole_Tracker_Example_Analysis.zip --output replayed
```

Install needs package-index access for dependencies. Inference runs locally without a remote service or API key. The README documents Linux environments, Windows launcher options, CSV conversion and Python API use.

## Physical contract

The ordinary fit reconstructs one effective exterior in the adopted BHSM Einstein/GHY sector. Optical mass, center and motion describe that configuration. Boundary energy/curvature derive from that mass at a declared radius; they are not independent measurements or another potential. R1 has its own metric/source mass and conditional flux. An unresolved envelope leaves an otherwise supported ordinary track usable. No microscopic-to-action or horizon map is selected.

Users supply parity/image association, observer epochs, angular frame, distances/redshifts, calibrated geometric fluxes/delays, full covariance and source/model assumptions. Unknown calibration, arbitrary macro lenses, critical crossings, systematic/non-Gaussian errors and real observational sensitivity need separate work. Synthetic noise is not a telescope capability. Author funding/conflict declarations remain human submission information; this draft has not been merged or submitted.
