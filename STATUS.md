# BHSM Status

This file is the current area-level status source. Detailed sprint records are
evidence, not competing public status pages.

Status taxonomy: `ESTABLISHED`, `ARTIFACT_BACKED`, `CANDIDATE`, `CONDITIONAL`,
`OPEN`, `BLOCKED`, `RUNTIME_GATED`, `REFERENCE_ONLY`, `RETIRED`.

| Area | Status | What is established | What remains open | Command/artifact |
| --- | --- | --- | --- | --- |
| Frozen internal predictions | `ESTABLISHED` | Frozen Markdown and JSON prediction records with integrity tests | External comparison is separate | `docs/frozen_predictions.md` |
| Python computational interface | `ESTABLISHED` | Offline geometry, prediction, comparison, and report interfaces | New physics formulas require their own evidence | `python -m bhsm.interface --help` |
| Prediction registry | `ESTABLISHED` | Calibration, prediction, comparison, theorem, and runtime statuses | Registry expansion is evidence-driven | `python -m bhsm.interface registry` |
| CLI reports | `ESTABLISHED` | Deterministic text, Markdown, and JSON reports | None for current offline commands | `python -m bhsm.interface report --format json` |
| Prediction gallery | `ARTIFACT_BACKED` | Registry-backed review table and optional plots | External comparisons remain separate | `python -m bhsm.interface gallery --format markdown` |
| Artifact-backed adapters | `ARTIFACT_BACKED` | Source discovery, provenance, formula registry, and five adapters | Open theorems are not inferred from artifacts | `python -m bhsm.interface artifact-sources` |
| CKM matrix | `ARTIFACT_BACKED` | Frozen matrix artifact and provenance adapter | Empirical evaluation is separate | `artifacts/CKM_no_fit_operator_output_v1.json` |
| PMNS matrix | `ARTIFACT_BACKED` | Frozen matrix artifact and provenance adapter | Physical neutrino basis and scale remain open | `artifacts/PMNS_no_fit_operator_output_v1.json` |
| CP phase / Z6 holonomy | `ARTIFACT_BACKED` | Local CP holonomy phase artifact and CKM/PMNS attachment evidence | Numerical external comparison remains separate | `artifacts/CP_no_fit_holonomy_output_v1.json` |
| Boundary constants | `ARTIFACT_BACKED` | No-fit boundary package and adapter | No automatic promotion of downstream theorems | `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json` |
| Mass ratios | `ARTIFACT_BACKED` | Frozen charged-sector ratio artifact and adapter | Precision external comparisons are scheme-sensitive | `theory/bhsm_v1_frozen_prediction_set.json` |
| W calibration policy | `REFERENCE_ONLY` | W may set the geometric-to-physical unit scale | It is not independent in the same calibrated run | `python -m bhsm.interface status W_boson` |
| Electron-neutrino comparison policy | `REFERENCE_ONLY` | Default comparison is upper-limit based | A vetted central mass reference is not supplied by default | `python -m bhsm.interface status electron_neutrino` |
| Standalone CP O_int | `RETIRED_TARGET` | CP is represented by the artifact-backed Z6 holonomy constraint | No standalone production vertex is required or claimed | `python -m bhsm.interface close-minimal-action cp_o_int` |
| X_ch boundary response | `CONDITIONAL_ACTION_THEOREM` | Author ontology plus local boundary sources define field -> `P_ch` -> `X_ch` -> response | Numerical normalization and any 4D production identification remain open | `python -m bhsm.interface close-minimal-action X_ch` |
| Neutrino propagation mass | `CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE` | `K_nu`, `g_nu`, `kappa_nu`, and dimensionless `tau` produce deterministic threshold-response rows | Artifact-backed dimensionful neutral scale and physical flavor-observable map | `python -m bhsm.interface neutrino-propagation-report --format markdown` |
| Neutral dimensionful scale | `OPEN_MISSING_NEUTRAL_SCALE` | Offline candidate, measure, and threshold-map audits distinguish the dimensionless response from physical units | Physical boundary-measure normalization, neutral background energy density, transport normalization, and threshold-to-energy map | `python -m bhsm.interface neutrino-scale-report --format markdown` |
| Legacy curvature mass bridge | `ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL` | Bundled author papers support `m=(c^2/(2G))r^2 k_loc` as a documented matching functional plus scalar-EFT and S3 action context | A BHSM neutral `r_prop`, physical `k_neutral,eff` map, and derivation of the matching functional from the BHSM action | `python -m bhsm.interface legacy-neutral-scale-report --format markdown` |
| Neutral propagation radius | `CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE` | The physical neutral-field domain defines symbolic `r_prop` with length dimension and no empirical input | Numerical metre value and neutral-mode support theorem | `python -m bhsm.interface neutral-propagation-radius --format json` |
| Neutral physical curvature | `CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE` | Dimensionless `R_nu` and symbolic `k_neutral,eff=kappa_curv R_nu` are separated cleanly | Action-derived `kappa_curv` in `m^-2`, boundary stiffness, and physical transport normalization | `python -m bhsm.interface neutral-physical-curvature --format json` |
| Dimensionful neutrino mass | `DIMENSIONFUL_MASS_NOT_AVAILABLE` | Radius, curvature, and mass-dimension gates are executable and fail closed | Numeric radius, physical curvature normalization, and corrected/action-derived mass functional; current legacy formula evaluates dimensionally to mass/length | `python -m bhsm.interface neutral-radius-curvature-report --format markdown` |
| Neutral mass-gap action | `ARTIFACT_BACKED_MASS_GAP_ACTION` | Bundled scalar action and spectral-gap analogue load offline | Neutral coefficients remain conditional | `python -m bhsm.interface neutrino-mass-gap-action --format json` |
| Neutral stiffness ratio | `OPEN_MISSING_NUMERIC_STIFFNESS_RATIO` | `sqrt(A_nu/Z_nu)` is defined symbolically | Numeric action-derived value in metres | `python -m bhsm.interface neutral-stiffness-ratio --format json` |
| Neutral spectral mass | `CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE` | Dimensionally correct theorem shape is executable and fails closed without units | Numeric stiffness length, physical `K_neutral,eff`, and admissible positivity proof | `python -m bhsm.interface neutral-spectral-report --format markdown` |
| FeynRules minimal model | `RUNTIME_GATED` | Disabled handoff assets and validation contracts exist | Complete eligible interaction set and live FeynRules validation | `python -m bhsm.interface status feynrules_minimal_model` |
| UFO export | `RUNTIME_GATED` | Export contract and runner scaffolds exist | Real export and loadability validation | `python -m bhsm.interface status ufo_export` |
| MadGraph smoke test | `RUNTIME_GATED` | Smoke-test plan and runner scaffolds exist | Validated UFO plus live MadGraph execution | `python -m bhsm.interface status madgraph_smoke_test` |

The detailed claim boundary is centralized in [CLAIMS.md](CLAIMS.md).
