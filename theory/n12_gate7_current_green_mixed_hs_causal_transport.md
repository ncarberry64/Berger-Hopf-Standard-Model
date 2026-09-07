# Current Green mixed Hermite--Simpson causal transport

The endpoint mixed Green/transverse graph is already certified on every
post-reset endpoint.  The remaining mixed transport is fixed by the exact
Hermite--Simpson chain rule.  This unit evaluates only the missing endpoint
first variations and the midpoint intrinsic/incidence terms, then applies the
unchanged frozen causal Newton recurrence.

For central direction `c`, transverse map `T`, first variations
`f^c=DF c`, `F^T=DF T`, and endpoint mixed map `B=D2F[c,T]`,

```text
c_m = (c_L+c_R)/2 + h(f_L^c-f_R^c)/8,
T_m = (T_L+T_R)/2 + h(F_L^T-F_R^T)/8,
W_m = h(B_L-B_R)/8,
B_m^tot = D2F_m[c_m,T_m] + DF_m W_m,
L_i^mix = -h(B_L + 4 B_m^tot + B_R)/6.
```

The reset-side data on interval zero are exactly zero.  The causal coordinate
operator is

```text
C_0 = 0,
C_(i+1) = -R_i^-1 [E_(i+1)^T L_i^mix
                    + E_(i+1)^T A_i E_i C_i].
```

No interpolated Green axis, historical 48-seam map, fitted scale, or empirical
value enters.  Component boxes are never substituted before the local mixed
chain rule.  If the final recurrence wraps, the result remains a numerical
dependency failure and is not interpreted as physical instability.

This unit can promote the mixed midpoint and causal operands only.  The full
transverse quadratic operator, the componentwise two-radius Volterra screen,
Gate 7, and full BHSM completion remain separate.
