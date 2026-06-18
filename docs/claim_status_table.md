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
| Full first-principles SM derivation | `FORBIDDEN` | `theory/forbidden_claims.md` | This claim is not made in this release |
| QCD confinement proof | `FORBIDDEN` | `theory/forbidden_claims.md` | This claim is not made in this release |
| Experimental confirmation/community acceptance | `FORBIDDEN` | this release package | This claim is not made in this release |

Status categories used in this release:

- `DERIVED_CONDITIONAL`
- `VERIFIED_TEST`
- `STRONG_SCREEN`
- `PROXY_AUDIT`
- `OPEN`
- `FORBIDDEN`
