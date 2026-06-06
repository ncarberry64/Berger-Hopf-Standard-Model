# Claims Ledger

This ledger is generated from `src/claims.py`. It is an audit/control layer, not a proof upgrade.

| ID | Title | Status | Tests | Limitations |
| --- | --- | --- | --- | --- |
| `sm_gauge_ledger` | Standard Model Gauge Ledger | `DERIVED_CONDITIONAL` | tests/test_hypercharges.py, tests/test_anomalies.py | The representation pattern is admitted rather than derived from pure geometry. |
| `hypercharge_derivation` | Hypercharge Derivation | `VERIFIED_TEST` | tests/test_hypercharges.py | This is conditional on the admitted representation pattern and U(1) normalization. |
| `anomaly_cancellation` | Anomaly Cancellation | `VERIFIED_TEST` | tests/test_anomalies.py | The test audits the admitted one-generation ledger; it is not a derivation of the ledger itself. |
| `three_generation_index` | Three-Generation Index Condition | `OPEN` | None | The index-three kernel has not been computed in this repository. |
| `no_fourth_generation` | No Fourth Protected Chiral Generation | `OPEN` | None | The protected spectrum is not yet computed, so this remains open. |
| `yukawa_overlap_structure` | Yukawa Overlap Structure | `STRONG_SCREEN` | tests/test_mode_selection.py | Mode-selection rules are operational audits, not yet derived from the full action; numerical matches are screens, not predictions. |
| `charged_sector_mode_ledger` | Charged-Sector Mode Ledger | `VERIFIED_TEST` | tests/test_mode_selection.py, tests/test_boundary_derivation.py | The boundary operators Omega_f are ACTION_LINKED by symbolic phase factors but are not fully ACTION_DERIVED from variation or spectrum of the twisted Dirac/bundle action. |
| `ckm_screen` | CKM Screen | `DERIVED_CONDITIONAL` | None | No independent CKM fit or dynamical derivation is implemented yet. |
| `pmns_effective_extension` | PMNS Effective Extension | `DERIVED_CONDITIONAL` | None | Neutrino masses are not part of the minimal Standard Model ledger in this repository. |
| `gauge_coupling_screen` | Gauge Coupling Matching Screen | `STRONG_SCREEN` | tests/test_couplings.py, tests/test_rg_matching.py | Gate 29B implements one-loop RG matching scaffolding only; full two-/three-loop threshold matching remains OPEN and is not a completed theorem. |
| `electroweak_scale_hopf_screen` | Electroweak Scale Hopf Screen | `STRONG_SCREEN` | tests/test_higgs_scale.py | The calculation is a numerical screen and not an independent prediction. |
| `ht_proxy_spectral_gap` | H_T Proxy Spectral Gap | `PROXY_AUDIT` | tests/test_spectral_gap.py, tests/test_positivity.py, tests/test_twisted_dirac_ht.py, tests/test_twisted_dirac_level2.py, tests/test_spectral_bounds.py, tests/test_theorem_scaffold.py | Gate 32D formalizes sufficient proxy theorem assumptions A1-A7, but those assumptions are not proven in the full internal action; the theorem remains open. |
| `psd_curvature_profile_positivity` | PSD Curvature/Profile Positivity | `PROXY_AUDIT` | tests/test_positivity.py | This is a finite-basis proxy construction, not the full curvature/profile operator in the complete action. |
| `scalar_decoupling` | Scalar Decoupling | `OPEN` | tests/test_scalar_decoupling.py | Gate 30B implements a scalar/topographic decoupling scaffold only; full action-level scalar decoupling remains OPEN and not proven. |
| `trace_u1_topological_condition` | Trace U(1) Topological Condition | `OPEN` | None | No independent topological proof is implemented. |
| `forbidden_pure_geometry_derivation` | Forbidden Pure-Geometry Derivation Claim | `FORBIDDEN` | None | The current repository is a conditional audit and screen suite. |
| `forbidden_confinement_proof` | Forbidden Yang-Mills Confinement Claim | `FORBIDDEN` | None | No confinement proof is implemented or audited. |
| `forbidden_completed_no_extra_light_theorem` | Forbidden Completed No-Extra-Light-State Claim | `FORBIDDEN` | None | Only proxy spectral-gap and positivity audits are implemented. |
| `forbidden_neutrino_minimal_sm` | Forbidden Minimal-SM Neutrino-Mass Claim | `FORBIDDEN` | None | Neutrino masses are treated only as an effective extension. |
| `forbidden_numerical_predictions` | Forbidden Numerical-Prediction Claim | `FORBIDDEN` | None | Implemented numerical results are screens unless upgraded by future derivations. |
