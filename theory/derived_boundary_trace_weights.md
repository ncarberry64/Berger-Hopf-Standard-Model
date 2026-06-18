# Derived Boundary Trace Weights

## Active Sector

```text
Y_active(0)=-1
Y_active(1)=1/3
```

Active contribution to `K_1`:

```text
2*1*(-1/2)^2 + 2*3*(1/6)^2
= 1/2 + 1/6
= 2/3
```

## Conjugate Inactive Sector

```text
Y^c = 0, 2, -4/3, 2/3
```

Inactive contribution to `K_1`:

```text
0^2 + 1^2 + 3*(-2/3)^2 + 3*(1/3)^2
= 1 + 4/3 + 1/3
= 8/3
```

## Total Abelian Trace Weight

```text
K1 = 2/3 + 8/3 = 10/3
```

## Non-Abelian Trace Weights

```text
K2 = (1+3)*(1/2) = 2
K3 = 4*(1/2) = 2
```

Status: `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL`.
