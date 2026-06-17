# Theorem Discharge: Raw-Mode Berger Harmonic Map

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch refines the symbolic `(q,j)->psi_qj(y)` scaffold by using the existing BHSM relation `q=k-2j` to derive the raw-mode map `(q,j)->(k=q+2j,j)`.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the geometric overlap kernel, finite-width rank scaffold, and symbolic `(q,j)->psi_qj(y)` eigenfunction map scaffold.

## 3. Why PO-BH-24 Left The Explicit Eigenfunction Map Open

PO-BH-24 defined symbolic `psi_qj(y)` labels but did not connect them to raw Berger/Hopf harmonic labels or fix the remaining orientation/base weight.

## 4. The BHSM Relation `q=k-2j`

The existing BHSM Hopf charge relation is:

```text
q=k-2j
```

## 5. Raw-Mode Map `k=q+2j`

```text
raw_mode(q,j)=(k,j)=(q+2j,j)
```

## 6. Generation Ledgers In `q,j` And Raw `k,j` Form

| sector | index | q | j | k=q+2j | raw `(k,j)` |
| --- | ---: | ---: | ---: | ---: | --- |
| reference_charged | 0 | 0 | 0 | 0 | `(0,0)` |
| reference_charged | 1 | 1 | 2 | 5 | `(5,2)` |
| reference_charged | 2 | 3 | 3 | 9 | `(9,3)` |
| reference_neutral | 0 | 0 | 0 | 0 | `(0,0)` |
| reference_neutral | 1 | 3 | 0 | 3 | `(3,0)` |
| reference_neutral | 2 | 1 | 1 | 3 | `(3,1)` |
| cyclic_upper | 0 | 0 | 0 | 0 | `(0,0)` |
| cyclic_upper | 1 | 6 | 0 | 6 | `(6,0)` |
| cyclic_upper | 2 | 8 | 1 | 10 | `(10,1)` |
| cyclic_lower | 0 | 0 | 0 | 0 | `(0,0)` |
| cyclic_lower | 1 | 0 | 3 | 6 | `(6,3)` |
| cyclic_lower | 2 | 4 | 2 | 8 | `(8,2)` |

## 7. Candidate Berger/Hopf Harmonic Interpretation

```text
psi_{k,j,m}(alpha,beta,gamma) ~ D^{k/2}_{m,j}(alpha,beta,gamma)
psi_{k,j,m}(alpha,beta,gamma) ~ exp(i m alpha) d^{k/2}_{m,j}(beta) exp(i j gamma)
```

## 8. Audit Of `j` As Hopf/Fiber Weight

`j` is structurally compatible with the fiber-side index in the candidate harmonic notation, but this is not promoted to a completed harmonic theorem.

## 9. The Remaining `m` Orientation/Base-Weight Problem

`m` remains open and is not guessed.

Follow-up audit: `theory/theorem_discharge_m_weight_assignment.md` tests candidate boundary/orientation sources and Wigner/Hopf admissibility conventions for this label. It does not derive or select `m`.

## 10. Candidate Sources For `m`

- active/singlet side
- weak orientation
- T3
- charge closure
- sector label
- boundary orientation algebra
- scalar insertion H or H_tilde
- cyclic/reference channel
- left/right chirality

## 11. Bridge To Local Feature Vectors At `y0`

```text
F_{k,j,m}(y0)=(psi, d_a psi, d_a d_b psi)|_{y0}
```

## 12. Numerical Eigenfunction Status

Explicit eigenfunction values are not derived.

## 13. Rank-Three/Yukawa Status

Finite-width rank three and numerical Yukawa values remain open.

## 14. Non-Tautology Audit

See [Raw-Mode Berger Harmonic Non-Tautology Audit](raw_mode_berger_harmonic_non_tautology_audit.md).

## 15. What This Achieves

| component | statement | status | guardrail |
| --- | --- | --- | --- |
| raw_mode_map | `raw_mode(q,j)=(k,j)=(q+2j,j)` | `RAW_MODE_MAP_DERIVED_CONDITIONAL` | direct algebraic inversion of q=k-2j |
| j_fiber_weight | `j is structurally consistent with a Hopf/fiber harmonic weight` | `J_AS_HOPF_FIBER_WEIGHT_STRUCTURALLY_MOTIVATED_NOT_DERIVED` | repo lacks a full harmonic theorem fixing conventions |
| candidate_harmonic_form | `psi_{k,j,m}(alpha,beta,gamma) ~ D^{k/2}_{m,j}(alpha,beta,gamma)` | `BERGER_HARMONIC_FORM_STRUCTURALLY_MOTIVATED_NOT_DERIVED` | notation only; explicit eigenfunctions not derived |
| m_weight_assignment | `m must be fixed by orientation/base-weight structure` | `M_WEIGHT_ASSIGNMENT_REMAINS_OPEN` | m is not guessed or fitted |
| feature_bridge | `F_{k,j,m}(y0)=(psi, d_a psi, d_a d_b psi)|_{y0}` | `RAW_MODE_TO_FEATURE_VECTOR_BRIDGE_DERIVED_CONDITIONAL` | symbolic local features only |

## 16. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until `m`, explicit eigenfunctions, feature values, moment contractions, numerical Yukawa values, mixing values, and the full low-energy Lagrangian theorem are derived.

## Conclusion

This branch derives the raw-mode map `k=q+2j` from the existing BHSM definition `q=k-2j` and converts the generation ledgers into raw `(k,j)` mode labels. It identifies a candidate Berger/Hopf harmonic notation `psi_{k,j,m}` and records the structural interpretation of `j` as a candidate Hopf/fiber weight. The remaining orientation/base weight `m`, explicit eigenfunction values, finite-width rank-three support, numerical Yukawa values, and replacement-level claims remain open.

## Verdict Labels

- `PO_BH_25_RAW_MODE_BERGER_HARMONIC_MAP_PARTIAL`
- `RAW_MODE_MAP_DERIVED_CONDITIONAL`
- `J_AS_HOPF_FIBER_WEIGHT_STRUCTURALLY_MOTIVATED_NOT_DERIVED`
- `BERGER_HARMONIC_FORM_STRUCTURALLY_MOTIVATED_NOT_DERIVED`
- `M_WEIGHT_ASSIGNMENT_REMAINS_OPEN`
- `EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN`
- `RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN`
- `NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
