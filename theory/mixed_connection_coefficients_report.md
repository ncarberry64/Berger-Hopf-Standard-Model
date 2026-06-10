# BHSM v2.10 Mixed Connection Coefficients Report

Status: `MIXED_COEFFICIENT_OPEN`
Theorem complete: `False`
Exact missing rule: `MIXED_HOPF_BASE_BOUNDARY_COFRAME_COEFFICIENT_RULE`

| Coefficient | Sources | Symbolic form | Status | Acts on | Limitation |
| --- | --- | --- | --- | --- | --- |
| `hopf_fiber_base_cross` | `('Hopf fiber', 'base/S2')` | `C_HB(q,j) [nabla_H,nabla_B]` | `MIXED_COEFFICIENT_OPEN` | `('Hopf/base/fiber modes', 'H_perp')` | The coefficient rule C_HB(q,j) is not derived from the full connection. |
| `base_boundary_cross` | `('base/S2', 'boundary functional')` | `C_Bbd(j,Omega_f) [nabla_B,nabla_boundary]` | `MIXED_COEFFICIENT_OPEN` | `('lepton', 'up', 'down', 'boundary functional')` | The coefficient rule tying base nodes to boundary functional phases is not derived. |
| `boundary_coframe_cross` | `('boundary functional', 'coframe')` | `C_bdC(Omega_f,cof) [nabla_boundary,nabla_cof]` | `MIXED_COEFFICIENT_OPEN` | `('up', 'down', 'coframe channels')` | The coframe participation coefficient in the mixed connection is not fixed. |
| `hopf_boundary_coframe_mixed` | `('Hopf fiber', 'boundary functional', 'coframe')` | `C_HbdC(q,Omega_f,cof) mixed triple contraction` | `MIXED_COEFFICIENT_OPEN` | `('charged sectors', 'mirror channels', 'formal kernel')` | The triple mixed coefficient is the exact missing geometric rule. |
| `chirality_dependence` | `('chirality projector', 'mixed connection')` | `C_chi(chi) mixed chirality sign` | `MIXED_COEFFICIENT_OPEN` | `('chirality', 'mirror channels')` | The chirality-resolved mixed coefficient is not derived. |
| `sector_dependence` | `('lepton/up/down sector labels', 'mixed connection')` | `C_sector(f) mixed sector weight` | `MIXED_COEFFICIENT_OPEN` | `('lepton', 'up', 'down')` | The sector weights of the mixed connection are not derived. |

## Open Coefficients

- `hopf_fiber_base_cross`
- `base_boundary_cross`
- `boundary_coframe_cross`
- `hopf_boundary_coframe_mixed`
- `chirality_dependence`
- `sector_dependence`

## Limitations

- The mixed coefficient slots are identified, but their BHSM geometric rule is not derived.
- No numerical or residual fit is used to choose coefficients.
