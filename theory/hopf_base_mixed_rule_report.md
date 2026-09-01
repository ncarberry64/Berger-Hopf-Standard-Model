# BHSM v2.11 Hopf/Base Mixed Rule Report

Status: `HOPF_BASE_MIXED_REPRESENTED`
Missing axiom: ``
Preserves formal kernel: `True`
Preserves H_perp: `True`
Theorem complete: `True`

| Rule | Geometric input | Coefficient slot | Conclusion | Status | Limitation |
| --- | --- | --- | --- | --- | --- |
| `vertical_horizontal_split` | Hopf fiber/base splitting in Berger-Hopf geometry | `hopf_fiber_base_cross` | cross curvature is zero/absorbed by vertical-horizontal compatibility | `HOPF_BASE_MIXED_REPRESENTED` | This is a representation rule, not a new fitted coefficient. |
| `boundary_phase_coupling` | Higgs-selected U(1) boundary phase and Omega_f | `base_boundary_cross` | sector-sensitive boundary/base mixing is represented by V_boundary | `HOPF_BASE_MIXED_REPRESENTED` | Boundary phase remains in the existing boundary sector. |
| `formal_kernel_safety` | formal protected kernel coordinates (0,18,36) | `hopf_boundary_coframe_mixed` | mixed contribution is not an independent curvature source on the formal kernel | `HOPF_BASE_MIXED_REPRESENTED` | Full H_T proof still requires downstream operator-domain dependencies. |

## Limitations

- The Hopf/base mixed rule is closed as a representation/compatibility rule, not as a numerical coefficient.
- No coefficient is selected from empirical outputs.
