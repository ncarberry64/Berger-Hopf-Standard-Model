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
| CP phase / Z6 holonomy | `ARTIFACT_BACKED` | Local CP holonomy phase artifact and CKM/PMNS attachment evidence | Standalone production interaction theorem | `artifacts/CP_no_fit_holonomy_output_v1.json` |
| Boundary constants | `ARTIFACT_BACKED` | No-fit boundary package and adapter | No automatic promotion of downstream theorems | `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json` |
| Mass ratios | `ARTIFACT_BACKED` | Frozen charged-sector ratio artifact and adapter | Precision external comparisons are scheme-sensitive | `theory/bhsm_v1_frozen_prediction_set.json` |
| W calibration policy | `REFERENCE_ONLY` | W may set the geometric-to-physical unit scale | It is not independent in the same calibrated run | `python -m bhsm.interface status W_boson` |
| Electron-neutrino comparison policy | `REFERENCE_ONLY` | Default comparison is upper-limit based | A vetted central mass reference is not supplied by default | `python -m bhsm.interface status electron_neutrino` |
| CP O_int | `CANDIDATE / OPEN` | CP phase and CKM/PMNS attachment are artifact-backed; a callable symbolic candidate exists | Action-backed production theorem, production eligibility, runtime export validation | `python -m bhsm.interface cp-o-int-field-action --format json` |
| X_ch | `OPEN` | Boundary-response source artifacts and closure machinery exist | Field content, Lorentz/gauge attachment, coupling normalization, action theorem | `python -m bhsm.interface close-theorem X_ch` |
| Neutrino physical basis/scale | `OPEN` | Neutral boundary/operator seed and closure machinery exist | Physical basis, dimensional scale, Dirac/Majorana theorem | `python -m bhsm.interface close-theorem neutrino_basis_scale` |
| FeynRules minimal model | `RUNTIME_GATED` | Disabled handoff assets and validation contracts exist | Complete eligible interaction set and live FeynRules validation | `python -m bhsm.interface status feynrules_minimal_model` |
| UFO export | `RUNTIME_GATED` | Export contract and runner scaffolds exist | Real export and loadability validation | `python -m bhsm.interface status ufo_export` |
| MadGraph smoke test | `RUNTIME_GATED` | Smoke-test plan and runner scaffolds exist | Validated UFO plus live MadGraph execution | `python -m bhsm.interface status madgraph_smoke_test` |

The detailed claim boundary is centralized in [CLAIMS.md](CLAIMS.md).

