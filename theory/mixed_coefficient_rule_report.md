# BHSM v2.11 Mixed Coefficient Rule Report

Rule status: `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR`
All slots classified: `True`
Exact missing axiom: ``
Theorem complete: `True`

| Slot | Symbol | Source | Rule/value | Free coefficient forbidden | Representation target | Vanishes | Contributes to R_bundle | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hopf_fiber_base_cross` | `C_HB(q,j)` | Berger metric compatibility + Hopf fibration connection compatibility | C_HB is not an independent coefficient; vertical-horizontal cross curvature is zero/absorbed by compatibility | `True` | `A0 + V_Hopf bookkeeping only` | `True` | `False` | `MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY` |
| `base_boundary_cross` | `C_Bbd(j,Omega_f)` | boundary functional compatibility | represented by the existing boundary operator package | `True` | `V_boundary` | `False` | `False` | `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR` |
| `boundary_coframe_cross` | `C_bdC(Omega_f,cof)` | coframe triplet structure + boundary functional | represented by the PSD/profile topographic sector | `True` | `V_PSD/profile` | `False` | `False` | `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR` |
| `hopf_boundary_coframe_mixed` | `C_HbdC(q,Omega_f,cof)` | Hopf/boundary/coframe compatibility | represented by scalar/topographic screened sector | `True` | `scalar/topographic screened sector` | `False` | `False` | `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR` |
| `chirality_dependence` | `C_chi(chi)` | chirality projection + mirror exclusion | represented by chiral projector and P_perp lift package | `True` | `V_chi + P_perp_lift` | `False` | `False` | `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR` |
| `sector_dependence` | `C_sector(f)` | sector lepton/up/down compatibility | represented by sector boundary functional and K_sector bookkeeping | `True` | `V_boundary + K_sector` | `False` | `False` | `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR` |

## Limitations

- Every coefficient slot is classified by the BHSM bundle-separation/topographic-representation axiom.
- The rule closes the independent mixed coefficient gap, but it does not prove the full H_T theorem.
- No empirical output, mass, CKM, PMNS, residual, or prediction-ledger data are used.
