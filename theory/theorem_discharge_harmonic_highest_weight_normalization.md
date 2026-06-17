# Theorem Discharge: Harmonic Highest-Weight Normalization

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry by testing whether the raw-mode relation `q=k-2j` fixes the Wigner/Hopf `n` weight convention.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers derived the symbolic `(q,j)->psi_qj(y)` scaffold, the raw map `k=q+2j`, and an m-weight audit. PO-BH-26 left the selected harmonic convention open because the naive `ell=k/2, n=j` convention fails Wigner admissibility on frozen modes.

## 3. Why PO-BH-26 Left The Harmonic Convention Open

The prior branch did not promote a harmonic convention from admissibility alone. It also did not derive the remaining Wigner/base/orientation label `m`.

## 4. BHSM Identity `q=k-2j`

```text
q=k-2j
```

## 5. Highest-Weight Rewriting `q/2=k/2-j`

```text
q/2 = k/2 - j
```

## 6. Definition Of `ell=k/2`

```text
ell = k/2
```

## 7. Definition Of `n=q/2`

```text
n = q/2
```

## 8. Interpretation Of `j` As Lowering/Descent Index

With `ell=k/2` and `n=q/2`, the BHSM identity gives:

```text
j = ell - n
```

Thus `j` is interpreted as the lowering/descent count from the highest-weight state, while `n` is the candidate Wigner/Hopf weight.

## 9. Admissibility Audit Across Frozen Ledgers

| sector | index | k | j | ell=k/2 | n=q/2 | ell-n | admissible |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| reference_charged | 0 | 0 | 0 | 0 | 0 | 0 | True |
| reference_charged | 1 | 5 | 2 | 5/2 | 1/2 | 2 | True |
| reference_charged | 2 | 9 | 3 | 9/2 | 3/2 | 3 | True |
| reference_neutral | 0 | 0 | 0 | 0 | 0 | 0 | True |
| reference_neutral | 1 | 3 | 0 | 3/2 | 3/2 | 0 | True |
| reference_neutral | 2 | 3 | 1 | 3/2 | 1/2 | 1 | True |
| cyclic_upper | 0 | 0 | 0 | 0 | 0 | 0 | True |
| cyclic_upper | 1 | 6 | 0 | 3 | 3 | 0 | True |
| cyclic_upper | 2 | 10 | 1 | 5 | 4 | 1 | True |
| cyclic_lower | 0 | 0 | 0 | 0 | 0 | 0 | True |
| cyclic_lower | 1 | 6 | 3 | 3 | 0 | 3 | True |
| cyclic_lower | 2 | 8 | 2 | 4 | 2 | 2 | True |

Every listed frozen raw mode satisfies `|n|<=ell` and `ell-n=j` with integer `j`.

## 10. Selected Harmonic n-Convention

Selected n-convention: `ell=k/2, n=q/2, j=ell-n`.

Status: `DERIVED_CONDITIONAL`.

## 11. Remaining m-Weight Problem

The remaining `m` orientation/base-weight assignment is not derived in this branch.

Status: `M_WEIGHT_ASSIGNMENT_REMAINS_OPEN`.

## 12. Bridge To Candidate Eigenfunctions

The candidate notation remains:

```text
psi_{k,j,m} ~ D^ell_{m,n}, ell=k/2, n=q/2
```

This fixes only the `n` side of the Wigner label pair.

## 13. Impact On Local Feature Vectors At `y0`

The local feature-vector scaffold may now use `D^ell_{m,q/2}` once `m` and the explicit harmonic representative are derived.

## 14. Numerical Eigenfunction Status

Explicit eigenfunction values, gradients, Hessians, and moment contractions are not computed here.

## 15. Rank-Three/Yukawa Status

The finite-width rank-three Yukawa theorem and numerical Yukawa values remain open.

## 16. Non-Tautology Audit

The branch uses only the existing BHSM identity `q=k-2j` and frozen mode ledgers. It does not use measured masses, CKM values, PMNS values, or admissibility-only convention selection.

## 17. What This Achieves

This branch conditionally derives the BHSM highest-weight harmonic normalization. The identity `q=k-2j` is rewritten as `q/2=k/2-j`, so with `ell=k/2` the Wigner/Hopf weight is `n=q/2` and `j` is interpreted as the lowering index from the highest-weight state.

## 18. What Remains Before Full BHSM Replacement Claim

The remaining `m` orientation/base-weight assignment, explicit eigenfunction values, finite-width rank-three theorem, and numerical Yukawa values remain open.

## Conclusion

This branch conditionally derives the BHSM highest-weight harmonic normalization. The identity q=k-2j is rewritten as q/2=k/2-j, so with ell=k/2 the Wigner/Hopf weight is n=q/2 and j is interpreted as the lowering index from the highest-weight state. This resolves the n-weight convention without fitting masses or selecting a convention only by admissibility. The remaining m orientation/base-weight assignment, explicit eigenfunction values, finite-width rank-three theorem, and numerical Yukawa values remain open.
