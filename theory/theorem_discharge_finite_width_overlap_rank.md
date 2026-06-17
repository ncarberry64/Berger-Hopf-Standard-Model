# Theorem Discharge: Finite-Width Overlap Rank

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch investigates whether finite-width moments of the universal scalar/topographic profile can lift the BHSM Yukawa overlap kernel beyond the strict point-sampling rank-one limit without fitted fermion masses or mixing data.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the closure spectrum, finite boundary algebra, charge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, scalar doublet, Yukawa operator closure, symbolic Yukawa matrix scaffolds, overlap-kernel selection rules, distance diagnostics, and the legacy geometric-overlap kernel bridge.

## 3. PO-BH-22 Geometric Kernel Bridge

PO-BH-22 identified the BHSM overlap kernel with the legacy scalar-topographic internal overlap integral:

```text
I_f(i,j)=integral_{B^3} Psi_A_f_i^*(y) Phi_H_f(y) Psi_S_f_j(y) dV_gamma
```

with universal profile:

```text
Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]
```

## 4. Why Strict Point Sampling Is Rank-Limited

```text
rank(I)<=1 for strict point-sampling I_ij=a_i^* b_j
```

Strict point sampling gives an outer product. It cannot by itself generate a rank-three Yukawa matrix.

## 5. Finite-Width Profile And Local Coordinate Expansion

Using local coordinates `xi` around `y0`:

```text
Psi_A_i(y)=Psi_A_i(y0)+xi^a partial_a Psi_A_i(y0)+1/2 xi^a xi^b partial_a partial_b Psi_A_i(y0)+...
```

```text
Psi_S_i(y)=Psi_S_i(y0)+xi^a partial_a Psi_S_i(y0)+1/2 xi^a xi^b partial_a partial_b Psi_S_i(y0)+...
```

## 6. Moment Tensors Of The Universal Profile

```text
M0=integral Phi(y) dV_gamma
M_ab=integral xi_a xi_b Phi(y) dV_gamma
M_abcd=integral xi_a xi_b xi_c xi_d Phi(y) dV_gamma
```

## 7. Finite-Width Overlap Expansion

```text
I_ij=M0 a_i^* b_j + M_ab (partial_a a_i^*)(partial_b b_j) + higher finite-width moments
```

The `M0` term is the strict point-sampling outer-product contribution. Higher finite-width moment terms can add independent matrix structures.

## 8. Rank-Three Condition

```text
rank(I_f)=3 if finite-width moment contributions span three independent row/column structures
```

## 9. Internal Eigenfunction Independence Condition

```text
the sets {a_i, partial_a a_i, partial_a partial_b a_i, ...} and {b_j, partial_a b_j, partial_a partial_b b_j, ...}, contracted with universal profile moments, must provide at least three independent matrix structures
```

This condition is not yet proven from BHSM eigenfunctions.

## 10. Universal Profile Width Guardrail

```text
sigma must be fixed by internal geometry and cannot be tuned by flavor or generation
```

## 11. Status Of Rank-Three Derivation

Finite-width moments can in principle raise the rank, but this branch does not derive the required independence of the internal mode amplitudes and derivatives. Rank-three remains open.

## 12. Status Of Numerical Yukawa Values

Numerical Yukawa values are not derived in this branch.

## 13. Impact On Mass Hierarchy Theorem

The mass hierarchy theorem remains narrowed to deriving internal eigenfunctions, their derivatives near `y0`, and finite-width moment contractions without fitting measured fermion masses.

## 14. Impact On CKM/PMNS Theorem

CKM and PMNS values remain open because no numerical off-diagonal kernel values or diagonalization matrices are derived.

## 15. Non-Tautology Audit

See [Finite-Width Overlap Rank Non-Tautology Audit](finite_width_overlap_rank_non_tautology_audit.md).

## 16. What This Achieves

| component | statement | status | guardrail |
| --- | --- | --- | --- |
| sharp_peak_outer_product | `rank(I)<=1 for strict point-sampling I_ij=a_i^* b_j` | `SHARP_PEAK_RANK_ONE_LIMIT_DERIVED_CONDITIONAL` | strict point sampling cannot produce rank three |
| finite_width_moment_expansion | `I_ij=M0 a_i^* b_j + M_ab (partial_a a_i^*)(partial_b b_j) + higher finite-width moments` | `FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL` | symbolic expansion only; no numerical moments computed |
| rank_three_condition | `rank(I_f)=3 if finite-width moment contributions span three independent row/column structures` | `RANK_THREE_OVERLAP_CONDITION_DERIVED_CONDITIONAL` | condition is not asserted satisfied |
| internal_eigenfunction_independence | `the sets {a_i, partial_a a_i, partial_a partial_b a_i, ...} and {b_j, partial_a b_j, partial_a partial_b b_j, ...}, contracted with universal profile moments, must provide at least three independent matrix structures` | `INTERNAL_EIGENFUNCTION_INDEPENDENCE_REMAINS_OPEN` | requires BHSM eigenfunction theorem or computation |
| universal_width_guardrail | `sigma must be fixed by internal geometry and cannot be tuned by flavor or generation` | `UNIVERSAL_PROFILE_WIDTH_GUARDRAIL_DERIVED_CONDITIONAL` | no flavor or generation tuning of sigma |

## 17. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until numerical overlap values, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, scalar potential numerics, and the full low-energy Lagrangian theorem are complete.

Follow-up theorem layer: [Theorem discharge: QJ eigenfunction map](theorem_discharge_qj_eigenfunction_map.md) isolates the next blocker: deriving the explicit non-fitted map from generation labels `(q,j)` to internal Berger/BHSM eigenfunctions and their local features.

## Conclusion

This branch derives the finite-width overlap-moment scaffold for the BHSM Yukawa kernel and identifies the condition under which the overlap matrix can exceed the strict point-sampling rank-one limit. The strict sharp-peak term remains rank-limited, while finite-width moments can in principle raise the rank if the relevant internal eigenfunction derivative and moment structures are linearly independent. This branch does not promote numerical Yukawa values, fermion mass ratios, CKM values, or PMNS values. Rank-three Yukawa structure remains open unless the required internal eigenfunction independence is derived from BHSM geometry.

## Verdict Labels

- `PO_BH_23_FINITE_WIDTH_OVERLAP_RANK_THEOREM_PARTIAL`
- `FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL`
- `SHARP_PEAK_RANK_ONE_LIMIT_DERIVED_CONDITIONAL`
- `RANK_THREE_OVERLAP_CONDITION_DERIVED_CONDITIONAL`
- `INTERNAL_EIGENFUNCTION_INDEPENDENCE_REMAINS_OPEN`
- `UNIVERSAL_PROFILE_WIDTH_GUARDRAIL_DERIVED_CONDITIONAL`
- `FINITE_WIDTH_RANK_THREE_REMAINS_OPEN`
- `NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN`
- `FERMION_MASS_RATIOS_REMAIN_OPEN`
- `CKM_VALUES_REMAIN_OPEN`
- `PMNS_VALUES_REMAIN_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
