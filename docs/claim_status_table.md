# Claim Status Table

| Claim | Status | Where to inspect | What would break it |
| --- | --- | --- | --- |
| Standard Model gauge ledger is reproduced conditionally | `DERIVED_CONDITIONAL` | `theory/claims_ledger.json`, `tests/test_hypercharges.py`, `tests/test_anomalies.py` | Failure of admitted ledger consistency or anomaly tests |
| Hypercharge derivation within admitted chiral pattern | `VERIFIED_TEST` | `src/hypercharge.py`, `tests/test_hypercharges.py` | Hypercharges no longer satisfy invariance/anomaly checks |
| Anomaly cancellation | `VERIFIED_TEST` | `src/anomalies.py`, `tests/test_anomalies.py` | Nonzero anomaly residuals |
| Gauge/electroweak screens | `STRONG_SCREEN` | `src/gauge_couplings.py`, `src/higgs_scale.py`, `tests/test_couplings.py` | Screen values leave fixed tolerance bands |
| Charged-sector mode selection | `STRONG_SCREEN` | `src/mode_selection.py`, `theory/boundary_operator_scaffold.md` | Boundary operators fail to recover the frozen ledger |
| H_T gap / no-extra-light-state audit | `PROXY_AUDIT` | `src/ht_operator.py`, `src/spectral_gap.py`, prediction ledger | Full twisted Dirac spectrum produces extra light states |
| Scalar/topographic decoupling | `PROXY_AUDIT` | `src/scalar_decoupling.py`, scalar tests | Unscreened light scalar/topographic mode survives |
| Precision QCD/RG matching | `OPEN` | QCD/RG scaffold files | Scheme-consistent precision comparison fails fixed bands |
| Full structural architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, theorem-discharge chain | Does not imply numerical closure or Standard Model replacement |
| Numerical closure | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Must remain open until all symbolic numerical inputs are derived and locked before comparison |
| Finite algebra | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, theorem-discharge files | Finite closure spectrum or algebra blocks fail guardrail tests |
| SM-like charges | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, charge/anomaly bridge tests | Charge table or anomaly bridge fails |
| Gauge normalization scaffold | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, trace-normalization files | Trace weights or normalization factors fail |
| Charged hierarchy mechanism | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Required symbolic hierarchy inputs cannot be localized |
| CKM source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Up/down sector-relative source cannot be represented |
| CKM CP source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Phase loop cannot be represented sector-relatively |
| CKM numerical prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Requires pre-comparison lock of CKM finite-width, displacement, phase, and exponent inputs |
| CKM `1/16` exponent | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | `docs/open_blockers_backlog.md` | Must not be fit to CKM residuals |
| Neutral topographic suppression route | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral suppression operator cannot be represented |
| Neutral topographic suppression action `S_nu_topo` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_neutral_topographic_suppression_action.md` | Must not be claimed until `Delta y_nu`, `H_topo^(nu)`, `E_nu`, and `S_barrier` are derived before comparison |
| Neutral saddle displacement `Delta_y_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_neutral_saddle_displacement.md` | Must not be claimed until the stationary-point or centroid ingredients are derived before comparison |
| Neutral effective action `S_eff_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_neutral_effective_action.md` | Must not be claimed until the internal metric, projection/lapse map, neutral boundary tensors, neutral boundary condition, and neutral profile are derived before comparison |
| Subsurface neutral projection geometry `g_sub`, `ellapse_nu`, `Pi_sub_to_ext` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_subsurface_projection_geometry.md` | Must not be claimed until the scalar/topographic profile, coordinate-invariant projection convention, internal metric, positivity/causality proof, and neutral boundary tensors are derived before comparison |
| Scalar/topographic boundary variation | `DERIVED_CONDITIONAL` | `theory/theorem_discharge_scalar_topographic_boundary_variation.md` | Conditional symbolic boundary operator fails or is fit to neutrino data |
| Normal-coupling/collar convention `R_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_normal_coupling_collar_convention.md` | Must not be claimed until fixed-normal, collar, or Robin convention is derived without fitted neutrino data |
| Neutral boundary tensors `chi_nu_AB`, `lambda_nu`, `neutral_boundary_condition` | `OPEN_LOCALIZABLE` for tensor values; symbolic boundary condition `DERIVED_CONDITIONAL` | `theory/theorem_discharge_neutral_boundary_tensors.md`, `theory/theorem_discharge_scalar_topographic_boundary_variation.md` | Must not be claimed until tensor values, normal-coupling convention, internal/subsurface metric, neutral profile, and positivity/stability proof are derived before comparison |
| Neutral topographic suppression action value | `OPEN` | `theory/theorem_discharge_neutral_topographic_suppression_action.md` | No numerical value is derived or fitted |
| Neutrino mass prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Requires derived `S_nu_topo` and locked neutral matrix inputs before comparison |
| PMNS source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral/charged-lepton diagonalization source fails |
| PMNS CP source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral phase loop cannot be represented |
| PMNS numerical prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Requires pre-comparison lock of neutral operator parameters and phase loop |
| Full fermion-sector architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Numerical fermion masses or mixing values are not claimed |
| Gauge-Higgs-fermion architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Full numerical SM prediction is not claimed |
| Full numerical SM prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Must not be claimed until all open numerical inputs are locked before comparison |
| Stability/coupling bounds | `OPEN` | `docs/open_blockers_backlog.md` | Must not be asserted from finite diagnostics alone |
| Higher-loop thresholds | `OPEN` | `docs/open_blockers_backlog.md` | Must not use mixed-scale masses as precision truth |
| Replacement readiness | `NOT_ACHIEVED` | `docs/bhsm_numerical_input_closure_map.md` | Must not be claimed until numerical and theorem blockers close |
| Full first-principles SM derivation | `FORBIDDEN` | `theory/forbidden_claims.md` | This claim is not made in this release |
| QCD confinement proof | `FORBIDDEN` | `theory/forbidden_claims.md` | This claim is not made in this release |
| Experimental confirmation/community acceptance | `FORBIDDEN` | this release package | This claim is not made in this release |

Status categories used in this release:

- `DERIVED_CONDITIONAL`
- `VERIFIED_TEST`
- `STRONG_SCREEN`
- `PROXY_AUDIT`
- `OPEN`
- `OPEN_LOCALIZABLE`
- `STRUCTURALLY_INTEGRATED`
- `STRUCTURALLY_DERIVED_CONDITIONAL`
- `INTEGRATED_CONDITIONAL`
- `NOT_ACHIEVED`
- `FORBIDDEN`
