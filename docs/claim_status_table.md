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
| Finite algebra | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, theorem-discharge files | Finite closure spectrum or algebra blocks fail guardrail tests |
| SM-like charges | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, charge/anomaly bridge tests | Charge table or anomaly bridge fails |
| Gauge normalization scaffold | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, trace-normalization files | Trace weights or normalization factors fail |
| Charged hierarchy mechanism | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Required symbolic hierarchy inputs cannot be localized |
| CKM source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Up/down sector-relative source cannot be represented |
| CKM CP source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Phase loop cannot be represented sector-relatively |
| Neutral topographic suppression route | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral suppression operator cannot be represented |
| PMNS source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral/charged-lepton diagonalization source fails |
| PMNS CP source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral phase loop cannot be represented |
| Full fermion-sector architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Numerical fermion masses or mixing values are not claimed |
| Gauge-Higgs-fermion architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Full numerical SM prediction is not claimed |
| Full numerical SM prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Must not be claimed until all open numerical inputs are locked before comparison |
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
- `STRUCTURALLY_INTEGRATED`
- `STRUCTURALLY_DERIVED_CONDITIONAL`
- `INTEGRATED_CONDITIONAL`
- `NOT_ACHIEVED`
- `FORBIDDEN`
