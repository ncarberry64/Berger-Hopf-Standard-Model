# BHSM v2.10 Hopf/Base/Boundary/Coframe Report

Coefficient status: `MIXED_COEFFICIENT_OPEN`
Status: `HOPF_BASE_BOUNDARY_COFRAME_OPEN`
Theorem complete: `False`

| Feature | Status | Conclusion | Limitation |
| --- | --- | --- | --- |
| `hopf_fiber_base_cross_terms` | `OPEN` | symbolic slot identified | coefficient rule is not derived |
| `base_boundary_cross_terms` | `OPEN` | symbolic slot identified | base/boundary phase coefficient is not derived |
| `boundary_coframe_cross_terms` | `OPEN` | symbolic slot identified | coframe coefficient is not derived |
| `hopf_boundary_coframe_mixed_terms` | `OPEN` | symbolic slot identified | triple mixed coefficient is not derived |
| `chirality_dependence` | `OPEN` | chirality dependence is identified but not computed | mirror-channel action remains open |
| `sector_dependence` | `OPEN` | sector dependence is identified but not computed | lepton/up/down weights remain open |
| `formal_kernel_action` | `OPEN` | not proven to vanish on formal kernel | requires explicit mixed coefficients |
| `h_perp_preservation` | `OPEN` | not proven to preserve H_perp | requires explicit mixed coefficients |

## Limitations

- The mixed sector is formalized but not derived.
- No formal-kernel or H_perp safety follows without coefficients.
