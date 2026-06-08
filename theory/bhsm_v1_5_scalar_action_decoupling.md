# BHSM v1.5 Scalar/Topographic Action-Decoupling Proof Scaffold

Theorem complete: `False`
Status: `SCALAR_ACTION_SCAFFOLD_PASSES`
Corrected H_T dependency: `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`

## Scalar Action Terms

| ID | Channel | Expression | Status |
| --- | --- | --- | --- |
| `SA1` | `HIGGS_PROJECTED_LIGHT_MODE` | `|D_mu H_0|^2 - V(H_0)` | `ACTION_SCAFFOLD` |
| `SA2` | `HOPF_GAP_LIFTED` | `m_perp^2 |Phi_perp|^2, m_perp >= 4*pi^2*v` | `HOPF_GAP_SCAFFOLD` |
| `SA3` | `HT_COMPLEMENT_LIFTED` | `Phi_perp H_T Phi_perp` | `HT_FORMAL_KERNEL_LINKED` |
| `SA4` | `DERIVATIVE_SCREENED` | `(partial_mu T_loc)^2 / Lambda_T^2` | `SCREENING_SCAFFOLD` |
| `SA5` | `CURVATURE_SCREENED` | `K[rho_Phi] T_loc^2` | `SCREENING_SCAFFOLD` |
| `SA6` | `VIRTUAL_ONLY` | `virtual/off-shell scalar-topographic exchange` | `STATE_ONTOLOGY_LINKED` |
| `SA7` | `FORBIDDEN_UNSCREENED_LIGHT_SCALAR` | `g_phi psi_bar psi phi_light` | `FALSIFIER_RULE` |

## Topographic Action Terms

| ID | Channel | Expression | Status |
| --- | --- | --- | --- |
| `TA1` | `DERIVATIVE_SCREENED` | `(nabla_mu T_loc)^2 / Lambda_T^2` | `DERIVATIVE_SCREENING_SCAFFOLD` |
| `TA2` | `CURVATURE_SCREENED` | `K[rho_Phi] T_loc^2` | `CURVATURE_SCREENING_SCAFFOLD` |
| `TA3` | `VIRTUAL_ONLY` | `off-shell T_loc exchange` | `VIRTUAL_ONLY_ONTOLOGY_LINKED` |

## Scalar Mode Classification

| Mode | Channel | Mass | Coupling | On-shell light | Status |
| --- | --- | --- | --- | --- | --- |
| `higgs_projection` | `HIGGS_PROJECTED_LIGHT_MODE` | `None` | `SM Higgs coupling` | `True` | `ALLOWED_SM_HIGGS` |
| `heavy_scalar_complement` | `HOPF_GAP_LIFTED` | `40000.0` | `lifted/decoupled` | `False` | `HEAVY_LIFTED_STATE` |
| `ht_scalar_complement` | `HT_COMPLEMENT_LIFTED` | `40000.0` | `lifted/decoupled` | `False` | `HT_COMPLEMENT_LIFTED` |
| `derivative_topographic` | `DERIVATIVE_SCREENED` | `100.0` | `derivative-filtered` | `False` | `DERIVATIVE_SCREENED_CONDITIONAL` |
| `curvature_topographic` | `CURVATURE_SCREENED` | `100.0` | `curvature-filtered` | `False` | `CURVATURE_SCREENED_CONDITIONAL` |
| `virtual_topographic` | `VIRTUAL_ONLY` | `None` | `virtual-only` | `False` | `VIRTUAL_ONLY_NOT_PARTICLE` |

## Fifth-Force Bound Rows

| Mode | Mass | Compton range (m) | Coupling to matter | Status | Violates ontology |
| --- | --- | --- | --- | --- | --- |
| `phi_0` | `125.1` | `1.5773539600319745e-18` | `True` | `SM_HIGGS_ALLOWED` | `False` |
| `phi_1` | `10692.3983816086` | `1.8454884802965363e-20` | `False` | `HEAVY_RANGE_SUPPRESSED` | `False` |
| `phi_2` | `2430.0905412746815` | `8.120149313304761e-20` | `False` | `DERIVATIVE_SCREENED_CONDITIONAL` | `False` |
| `phi_3` | `1944.0724330197452` | `1.0150186641630952e-19` | `False` | `CURVATURE_SCREENED_CONDITIONAL` | `False` |
| `phi_4` | `1620.0603608497877` | `1.2180223969957142e-19` | `False` | `SCREENED_TOPOGRAPHIC_CONDITIONAL` | `False` |
| `phi_5` | `14580.54324764809` | `1.3533582188841268e-20` | `False` | `HEAVY_RANGE_SUPPRESSED` | `False` |

## Risk Assessment

Open scalar risks: `0`
Dangerous proxy modes: `0`

The forbidden unscreened light scalar channel is retained as a falsifier rule. It is not present in the current scalar inventory.

## Limitations

- This is an action-level scaffold, not FULL_ACTION_PROVEN.
- Conditional derivative/curvature screening remains to be proven from the complete action.
- H_T-dependent scalar complement lifting uses DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL scaffold status.
- No frozen BHSM predictions are changed.

## v1.6 Screening Follow-Up

Branch `bhsm-v1.6-scalar-screening-proof` adds derivative-screening,
curvature-screening, matter-coupling, and fifth-force exclusion scaffolds for
the v1.5 scalar/topographic channels. It reports zero current
`OPEN_SCALAR_RISK` rows and keeps the direct unscreened light scalar channel
as a forbidden falsifier. It does not claim a full scalar-screening theorem
from the complete action.
