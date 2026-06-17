# Theorem Discharge: M-Multiplet Harmonic Features

## 1. Mission

This branch derives a conditional m-multiplet harmonic feature scaffold for BHSM internal modes. It does not force a single m-weight assignment.

## 2. Mode Labels

For each mode, the scaffold uses:

```text
k = q + 2j
ell = k/2
n = q/2
m in {-ell, -ell+1, ..., ell}
```

## 3. Multiplet Definition

```text
Psi_{k,q}^multiplet(y) = { D^{k/2}_{m,q/2}(y) }_{m=-ell}^ell
```

## 4. Local Feature Multiplet

```text
F_{k,q}(y0) = {
  D^{k/2}_{m,q/2}(y0),
  partial_a D^{k/2}_{m,q/2}(y0),
  partial_a partial_b D^{k/2}_{m,q/2}(y0)
}_{m=-ell}^ell
```

## 5. Admissible Multiplets

| sector | index | k | ell | n | m count | m values | n admissible |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| reference_charged | 0 | 0 | 0 | 0 | 1 | 0 | `True` |
| reference_charged | 1 | 5 | 5/2 | 1/2 | 6 | -5/2, -3/2, -1/2, 1/2, 3/2, 5/2 | `True` |
| reference_charged | 2 | 9 | 9/2 | 3/2 | 10 | -9/2, -7/2, -5/2, -3/2, -1/2, 1/2, 3/2, 5/2, 7/2, 9/2 | `True` |
| reference_neutral | 0 | 0 | 0 | 0 | 1 | 0 | `True` |
| reference_neutral | 1 | 3 | 3/2 | 3/2 | 4 | -3/2, -1/2, 1/2, 3/2 | `True` |
| reference_neutral | 2 | 3 | 3/2 | 1/2 | 4 | -3/2, -1/2, 1/2, 3/2 | `True` |
| cyclic_upper | 0 | 0 | 0 | 0 | 1 | 0 | `True` |
| cyclic_upper | 1 | 6 | 3 | 3 | 7 | -3, -2, -1, 0, 1, 2, 3 | `True` |
| cyclic_upper | 2 | 10 | 5 | 4 | 11 | -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5 | `True` |
| cyclic_lower | 0 | 0 | 0 | 0 | 1 | 0 | `True` |
| cyclic_lower | 1 | 6 | 3 | 0 | 7 | -3, -2, -1, 0, 1, 2, 3 | `True` |
| cyclic_lower | 2 | 8 | 4 | 2 | 9 | -4, -3, -2, -1, 0, 1, 2, 3, 4 | `True` |

## 6. Axis-Collapse Case

If y0 is derived as an identity/Hopf-axis point, D^ell_{m,n}(y0)=delta_mn and the leading component is m=n=q/2.

This case remains conditional on a future derivation of `y0` as the relevant identity/Hopf-axis point.

## 7. Generic Y0 Case

If y0 is generic, retain the full D^ell_{m,n}(alpha0,beta0,gamma0) multiplet for Wigner evaluation at the universal sampling point.

## 8. Rank Support Condition

Finite-width rank-three support remains open. The current branch only supplies the local harmonic feature scaffold required by a future finite-width moment theorem.

## 9. Yukawa Bridge

The multiplet scaffold can feed a future Yukawa overlap theorem, but this branch does not derive numerical Yukawa values, mass ratios, CKM, PMNS, or replacement readiness.

## 10. Non-Tautology Guardrail

The branch avoids promoting `m=n=q/2` as a single forced label. The full admissible m-multiplet is retained unless the stronger y0 axis-sampling theorem is later derived.

## Conclusion

This branch derives the m-multiplet harmonic feature scaffold for BHSM internal modes. Rather than forcing a single m-weight assignment, each mode with ell=k/2 and n=q/2 is assigned its full admissible Wigner/Hopf m-multiplet. If y0 is later derived as an identity/Hopf-axis point, the multiplet can collapse to the leading m=n=q/2 component. If y0 is generic, the full multiplet remains available for Wigner evaluation at the universal sampling point. This branch does not derive finite-width rank-three Yukawa matrices, numerical Yukawa values, CKM, PMNS, or replacement readiness.

Follow-up: `theory/theorem_discharge_generic_y0_wigner_feature_rank.md` evaluates the retained multiplets symbolically at `y0=(alpha0,beta0,gamma0)` and connects the result to the feature-rank support problem.
