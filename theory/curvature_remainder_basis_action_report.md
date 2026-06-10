# BHSM v2.8 Curvature Remainder Basis Action Report

Formula status: `REMAINDER_FORMULA_OPEN`
Status: `REMAINDER_BASIS_ACTION_OPEN`
Theorem complete: `False`

| Feature | Status | Conclusion | Limitation |
| --- | --- | --- | --- |
| `diagonal_or_off_diagonal` | `OPEN` | not computable without complete curvature coefficients | Could be diagonal, off-diagonal, or mixed. |
| `sector_mixing` | `OPEN` | not computable without sector curvature contraction | Sector representation inputs alone do not determine the curvature action. |
| `chirality_mixing` | `OPEN` | not computable without Clifford/chirality contraction | Mirror leakage cannot be ruled out from formula scaffold alone. |
| `base_fiber_dependence` | `OPEN` | not computable without Hopf/base mixed curvature formula | Existing Hopf/base terms are represented, but the mixed remainder is not. |
| `boundedness_behavior` | `OPEN` | no growth law or norm estimate is available | Relative-bound constants cannot be derived. |
| `formal_kernel_action` | `OPEN` | not proven to vanish on formal kernel | Kernel safety requires explicit action. |
| `h_perp_preservation` | `OPEN` | not proven to preserve H_perp | Commutator with the complement projector cannot be closed. |
| `mirror_leakage` | `OPEN` | not proven absent | Mirror-channel safety remains conditional. |

## Limitations

- The basis action cannot be derived more strongly than the formula.
- No finite-basis or analytic action matrix is introduced for an unidentified curvature term.
