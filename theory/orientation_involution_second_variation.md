# Orientation Involution Second Variation

The orientation functional is

```text
S_orientation(R)=||R^2-I||^2 + lambda_trace |Tr(R)|^2
```

For the diagonal surrogate

```text
R = diag(s_i + epsilon_i), s_i^2=1
```

the quadratic term is

```text
S_orientation_quad ~= 4 sum_i epsilon_i^2 + lambda_trace (sum_i epsilon_i)^2
```

and the diagnostic Hessian is

```text
H_orientation = 8 I + 2 lambda_trace J
```

For `R=diag(+1,-1)`, this is a candidate source of `Z_2` orientation grading, `S_sigma`, `P_orient`, and `d=2` orientation-pair closure.

Guardrail: this is not a full `SU(2)` derivation.
