# Derived Boundary Charge Operator

Definitions:

```text
P_C^2=P_C
S_sigma^2=I
eigenvalue(P_C)=C in {0,1}
eigenvalue(S_sigma)=sigma in {+1,-1}
```

Algebraic requirements:

1. orientation grading contributes a unit lowering from `sigma=+1` to `sigma=-1`;
2. the `sigma=+1`, `C=0` reference state is the neutral boundary reference;
3. cyclic three-channel closure contributes the normalized cyclic shift `(3-1)/3 = 2/3`.

Therefore

```text
Q_boundary = 1/2(S_sigma-I) + 2/3 P_C
```

and

```text
Q(C,sigma) = (sigma-1)/2 + (2/3)C
```

| C | sigma | Q |
| --- | --- | --- |
| 0 | +1 | 0 |
| 0 | -1 | -1 |
| 1 | +1 | 2/3 |
| 1 | -1 | -1/3 |

Guardrail: these rows are boundary eigenvalue rows, not particle-label assumptions.

Status: `BOUNDARY_CHARGE_OPERATOR_DERIVED_CONDITIONAL`.
