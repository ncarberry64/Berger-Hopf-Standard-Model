# Theorem Discharge: QJ To Internal Eigenfunction Map

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch sharpens the finite-width overlap-rank blocker by isolating the missing non-fitted map from generation labels `(q,j)` to internal Berger/BHSM eigenfunctions.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the closure spectrum, finite boundary algebra, charge operators, gauge skeletons, scalar doublet, Yukawa operator closure, symbolic Yukawa matrix scaffolds, overlap-kernel selection rules, distance diagnostics, the legacy geometric-overlap kernel bridge, and the finite-width rank condition.

## 3. PO-BH-23 Rank Condition

PO-BH-23 derived the symbolic condition that finite-width moment terms can lift the rank if independent internal feature structures exist. It did not prove the required internal eigenfunction independence.

## 4. Why `(q,j) -> psi_qj(y)` Is The Next Blocker

The finite-width rank condition cannot be tested until the generation labels `(q,j)` are mapped to actual internal Berger/BHSM eigenfunctions or harmonics.

## 5. BHSM Generation Mode Ledgers

| sector | index | q | j | symbolic eigenfunction |
| --- | ---: | ---: | ---: | --- |
| reference_charged | 0 | 0 | 0 | `psi_q0_j0(y)` |
| reference_charged | 1 | 1 | 2 | `psi_q1_j2(y)` |
| reference_charged | 2 | 3 | 3 | `psi_q3_j3(y)` |
| reference_neutral | 0 | 0 | 0 | `psi_q0_j0(y)` |
| reference_neutral | 1 | 3 | 0 | `psi_q3_j0(y)` |
| reference_neutral | 2 | 1 | 1 | `psi_q1_j1(y)` |
| cyclic_upper | 0 | 0 | 0 | `psi_q0_j0(y)` |
| cyclic_upper | 1 | 6 | 0 | `psi_q6_j0(y)` |
| cyclic_upper | 2 | 8 | 1 | `psi_q8_j1(y)` |
| cyclic_lower | 0 | 0 | 0 | `psi_q0_j0(y)` |
| cyclic_lower | 1 | 0 | 3 | `psi_q0_j3(y)` |
| cyclic_lower | 2 | 4 | 2 | `psi_q4_j2(y)` |

## 6. Candidate/Internal Eigenfunction Map

```text
E:(q,j)->psi_qj(y)
```

Status: `SCAFFOLD_DERIVED_CONDITIONAL`. This is a symbolic scaffold, not an explicit Wigner/Hopf/Berger eigenfunction theorem.

## 7. Local Value/Gradient/Hessian Data At `y0`

For each mode, the required data are value, gradient, and Hessian components at `y0`.

## 8. Finite-Width Feature Vectors

```text
F_n = [psi_n(y0), d1 psi_n(y0), d2 psi_n(y0), d3 psi_n(y0), d11 psi_n(y0), d12 psi_n(y0), d13 psi_n(y0), d22 psi_n(y0), d23 psi_n(y0), d33 psi_n(y0)]
```

## 9. Diagonal Hierarchy Route

```text
diagonal hierarchy may arise from generation-dependent singlet/internal amplitudes or diagonal finite-width overlaps
```

## 10. Full Rank-Three Matrix Route

```text
full rank-three matrix requires derived active-mode structure, delta_ij channel selection, finite-width moment independence, or boundary transport/dressing
```

## 11. Internal Feature Independence Condition

```text
rank-three support requires three generation feature vectors to remain independent under universal finite-width moment contractions
```

## 12. Numerical Eigenfunction Status

Explicit eigenfunctions, local amplitudes, gradients, Hessians, and moment contractions are not computed in this branch.

## 13. Impact On Yukawa Values

Numerical Yukawa values remain open.

## 14. Impact On CKM/PMNS

CKM and PMNS values remain open because no numerical off-diagonal kernel values or diagonalization matrices are derived.

## 15. Non-Tautology Audit

See [QJ Eigenfunction Map Non-Tautology Audit](qj_eigenfunction_map_non_tautology_audit.md).

## 16. What This Achieves

| component | statement | status | guardrail |
| --- | --- | --- | --- |
| qj_symbolic_map | `E:(q,j)->psi_qj(y)` | `QJ_EIGENFUNCTION_MAP_SCAFFOLD_DERIVED_CONDITIONAL` | symbolic scaffold only; explicit Berger eigenfunctions remain open |
| local_feature_vectors | `F_n=(value, gradient, Hessian components at y0)` | `INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL` | features are symbolic, not evaluated |
| diagonal_hierarchy_route | `diagonal hierarchy may arise from generation-dependent singlet/internal amplitudes or diagonal finite-width overlaps` | `DIAGONAL_HIERARCHY_ROUTE_IDENTIFIED_CONDITIONAL` | hierarchy route is not a full rank-three matrix theorem |
| full_rank_three_route | `full rank-three matrix requires derived active-mode structure, delta_ij channel selection, finite-width moment independence, or boundary transport/dressing` | `FULL_RANK_THREE_ROUTE_CONDITION_DERIVED_CONDITIONAL` | condition is not asserted satisfied |
| rank_three_support_condition | `rank-three support requires three generation feature vectors to remain independent under universal finite-width moment contractions` | `INTERNAL_FEATURE_INDEPENDENCE_REMAINS_OPEN` | requires explicit eigenfunction independence proof |

## 17. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until explicit internal eigenfunctions, finite-width moment contractions, numerical Yukawa values, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, scalar potential numerics, and the full low-energy Lagrangian theorem are complete.

## Conclusion

This branch derives the symbolic scaffold for the missing BHSM map from generation labels (q,j) to internal Berger/BHSM eigenfunctions psi_qj(y). The branch identifies local values, gradients, Hessians, and finite-width moment contractions as the required data for proving diagonal hierarchy support and full rank-three Yukawa support. Because an explicit theorem-derived eigenfunction map and evaluated local feature independence are not derived in this branch, numerical Yukawa values, fermion mass ratios, CKM values, PMNS values, and replacement-level claims remain open.

## Verdict Labels

- `PO_BH_24_QJ_TO_INTERNAL_EIGENFUNCTION_MAP_PARTIAL`
- `QJ_EIGENFUNCTION_MAP_SCAFFOLD_DERIVED_CONDITIONAL`
- `INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL`
- `DIAGONAL_HIERARCHY_ROUTE_IDENTIFIED_CONDITIONAL`
- `FULL_RANK_THREE_ROUTE_CONDITION_DERIVED_CONDITIONAL`
- `QJ_TO_BERGER_EIGENFUNCTION_MAP_REMAINS_OPEN`
- `INTERNAL_FEATURE_INDEPENDENCE_REMAINS_OPEN`
- `RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN`
- `NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN`
- `FERMION_MASS_RATIOS_REMAIN_OPEN`
- `CKM_VALUES_REMAIN_OPEN`
- `PMNS_VALUES_REMAIN_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
