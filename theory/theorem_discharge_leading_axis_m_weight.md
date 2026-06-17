# Theorem Discharge: Leading-Axis M-Weight Assignment

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to test whether the leading focused component at the distinguished internal point `y0` fixes the remaining Wigner/base/orientation label `m`.

## 2. Previous Theorem Layers Achieved

PO-BH-27 conditionally derived `ell=k/2`, `n=q/2`, and `j=ell-n`.

## 3. PO-BH-27 Highest-Weight Normalization

The current candidate harmonic form is:

```text
D^ell_{m,n} = D^(k/2)_{m,q/2}
```

## 4. Why `m` Remains The Next Blocker

The `n` side of the Wigner label pair is fixed conditionally, but the `m` side is still required before explicit internal harmonics and local feature values can be computed.

## 5. The Role Of `y0`

Prior overlap layers use `y0` as a distinguished sharp-peak/topographic sampling point. They do not yet prove that `y0` is the group identity, Hopf pole, or equivalent Wigner axis.

## 6. Audit Of `y0` As Identity/Hopf Axis/Focal Point

| route | repo support | status | note |
| --- | --- | --- | --- |
| group identity | `False` | `OPEN` | The repo has symbolic y0 sampling but no theorem identifying y0 with the group identity. |
| north/south Hopf pole | `False` | `OPEN` | No theorem identifies y0 with a Hopf pole or proves pole sampling for Wigner labels. |
| squashed-axis focal point | `False` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | The legacy overlap bridge gives a distinguished sharp-peak point y0, not an axis identity theorem. |
| generic internal point | `True` | `PARTIAL` | Current repo support treats y0 as a symbolic topographic sampling point. |

## 7. Wigner Identity-Axis Selection Rule

For a group identity axis one expects:

```text
D^ell_{m,n}(e)=delta_{m,n}
```

The repo does not yet contain the BHSM theorem identifying `y0` with this axis or translating the rule into the Berger/Hopf sampling setup.

## 8. Candidate Assignment `m=n`

Candidate leading-axis assignment:

```text
m=n
```

Status: `M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

## 9. Resulting Assignment `m=q/2`

Using PO-BH-27, the candidate leading component is:

```text
m=n=q/2
```

## 10. Admissibility Audit Across Frozen Ledgers

| sector | index | k | ell | n | m | j | ell-n | ell-m | admissible |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| reference_charged | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True |
| reference_charged | 1 | 5 | 5/2 | 1/2 | 1/2 | 2 | 2 | 2 | True |
| reference_charged | 2 | 9 | 9/2 | 3/2 | 3/2 | 3 | 3 | 3 | True |
| reference_neutral | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True |
| reference_neutral | 1 | 3 | 3/2 | 3/2 | 3/2 | 0 | 0 | 0 | True |
| reference_neutral | 2 | 3 | 3/2 | 1/2 | 1/2 | 1 | 1 | 1 | True |
| cyclic_upper | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True |
| cyclic_upper | 1 | 6 | 3 | 3 | 3 | 0 | 0 | 0 | True |
| cyclic_upper | 2 | 10 | 5 | 4 | 4 | 1 | 1 | 1 | True |
| cyclic_lower | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True |
| cyclic_lower | 1 | 6 | 3 | 0 | 0 | 3 | 3 | 3 | True |
| cyclic_lower | 2 | 8 | 4 | 2 | 2 | 2 | 2 | 2 | True |

## 11. Leading-Axis Harmonic Representatives

| sector | index | representative | scope |
| --- | ---: | --- | --- |
| reference_charged | 0 | `D^(0)_(0,0)` | leading-axis candidate only |
| reference_charged | 1 | `D^(5/2)_(1/2,1/2)` | leading-axis candidate only |
| reference_charged | 2 | `D^(9/2)_(3/2,3/2)` | leading-axis candidate only |
| reference_neutral | 0 | `D^(0)_(0,0)` | leading-axis candidate only |
| reference_neutral | 1 | `D^(3/2)_(3/2,3/2)` | leading-axis candidate only |
| reference_neutral | 2 | `D^(3/2)_(1/2,1/2)` | leading-axis candidate only |
| cyclic_upper | 0 | `D^(0)_(0,0)` | leading-axis candidate only |
| cyclic_upper | 1 | `D^(3)_(3,3)` | leading-axis candidate only |
| cyclic_upper | 2 | `D^(5)_(4,4)` | leading-axis candidate only |
| cyclic_lower | 0 | `D^(0)_(0,0)` | leading-axis candidate only |
| cyclic_lower | 1 | `D^(3)_(0,0)` | leading-axis candidate only |
| cyclic_lower | 2 | `D^(4)_(2,2)` | leading-axis candidate only |

## 12. Scope: Leading Focused Component Only

This is only a leading-axis/focused-component scaffold. It does not supply finite-width corrections, transport, mixing, or rank-three support.

## 13. What Remains For Finite-Width Rank-Three

Finite-width moment contractions, independent local features, and off-diagonal transport/dressing terms remain open.

## 14. Numerical Yukawa Status

No numerical eigenfunction values, Yukawa values, mass ratios, CKM values, or PMNS values are derived here.

## 15. Non-Tautology Audit

The branch does not use measured masses, CKM values, PMNS values, or fitted residuals. It also does not promote `m=n` from admissibility alone.

## 16. What This Achieves

This branch records that `m=n=q/2` is an admissible leading-axis candidate on the frozen ledgers.

## 17. What Remains Before Full BHSM Replacement Claim

The next blocker is to derive `y0` as a Berger/Hopf identity axis or equivalent focal point and derive the corresponding Wigner/Hopf axis sampling rule in BHSM notation.

## Conclusion

This branch audits the candidate leading-axis m-weight assignment m=n=q/2. The assignment is admissible on the frozen ledgers, but it is not promoted because the repo does not yet support y0 as the Berger/Hopf identity axis or equivalent focal point and does not yet support the relevant Wigner/Hopf axis sampling rule. Explicit eigenfunctions, finite-width rank-three support, numerical Yukawa values, and replacement-level claims remain open.
