# AE3.1 current-C2 quark--Higgs incidence-support transport

The historical BHSM boundary theorem already selected the two colored
renormalizable closure classes. It used two-component fields:

```text
A_cyc + H       + S_cyc_upper,
A_cyc + H_tilde + S_cyc_lower.
```

The current AE3.1 action uses barred four-component fields. The anti-linear
fermion convention change, together with the `SU(2)` epsilon intertwiner on
the scalar doublet, transports these classes as

```text
(A_cyc,H,S_cyc_upper)         -> (bar(Q_L),H_tilde,u_R),
(A_cyc,H_tilde,S_cyc_lower)   -> (bar(Q_L),H,d_R).
```

This is not an imported Standard Model operator table. The doubled
hypercharges transform respectively as

```text
(1/3, 1,-4/3) -> (-1/3,-1, 4/3),
(1/3,-1, 2/3) -> (-1/3, 1,-2/3),
```

and both sides close to zero.

The existing finite-sector projector formulas

```text
P_u=C(1+sigma)/2,
P_d=C(1-sigma)/2
```

then select disjoint up/down support. On the ordered LR basis
`(Q_L_up,Q_L_down,u_R,d_R)`, the two binary incidence matrices connect only
`Q_L_up <-> u_R` and `Q_L_down <-> d_R`. They are orthogonal and linearly
independent. Hence the current support pencil is

```text
rho_qH_support(h)=h_tilde I_up+h I_down.
```

This finite internal attachment does not alter the reset-generated radial
operator or birth trace. The exact tensor identity

```text
[D_C2 tensor I, I tensor I_f]=0
```

shows that bounded finite incidence and the already-defined finite family
operators preserve the current radial domain.

Promoted conditionally:

- the historical-to-current field-convention bridge;
- the two quark--Higgs incidence supports on current `C2`;
- preservation of the current radial operator domain and birth trace.

Not promoted:

- action-owned values of the up/down residues;
- the first vertices `V_u,V_d` or contact jet `Q_fg`;
- quark poles, masses, or CKM mixing.

The remaining functional is

```text
Gamma_qH_current_C2[bar(Q_L),u_R,d_R,H]
```

with a common action, trace, field normalization, and boundary domain. Its
first and second variations must fix the two residues and full contact jet
while reusing the existing `T_u,T_d` family shapes. Independent Yukawa
coefficients or mass fits remain forbidden.

`FULL_BHSM_COMPLETE = FALSE`.
