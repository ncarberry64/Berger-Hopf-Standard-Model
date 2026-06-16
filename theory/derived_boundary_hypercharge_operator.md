# Derived Boundary Hypercharge Operator

Define active orientation projection:

```text
P_w^2=P_w
eigenvalue(P_w)=w in {0,1}
```

The active orientation generator is

```text
T3_boundary = 1/2 P_w S_sigma
```

Define hypercharge as residual boundary charge after removing the active orientation generator:

```text
Y_boundary = 2(Q_boundary - T3_boundary)
```

Thus

```text
Y(C,sigma,w) = (4/3)C - 1 + (1-w)sigma
```

This equals the prior audited primitive bridge

```text
Y = C/3 - ell + (1-w)sigma
```

using `ell = 1-C`.

| C | sigma | w | Q | T3 | Y |
| --- | --- | --- | --- | --- | --- |
| 0 | +1 | 1 | 0 | 1/2 | -1 |
| 0 | -1 | 1 | -1 | -1/2 | -1 |
| 1 | +1 | 1 | 2/3 | 1/2 | 1/3 |
| 1 | -1 | 1 | -1/3 | -1/2 | 1/3 |
| 0 | +1 | 0 | 0 | 0 | 0 |
| 0 | -1 | 0 | -1 | 0 | -2 |
| 1 | +1 | 0 | 2/3 | 0 | 4/3 |
| 1 | -1 | 0 | -1/3 | 0 | -2/3 |

Guardrail: this derives the charge/hypercharge skeleton, not gauge dynamics.

Status: `PO_BH_10_CHARGE_HYPERCHARGE_OPERATORS_DERIVED_CONDITIONAL`.
