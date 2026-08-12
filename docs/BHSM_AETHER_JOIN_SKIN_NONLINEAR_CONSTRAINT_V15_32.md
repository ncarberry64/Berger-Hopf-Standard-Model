# BHSM v15.32 — Hopf-join skin nonlinear constraint result

The v15.31 `S6`-radial trace is not smooth at both collapse poles of
`S7=S3*S3`.  The reciprocal common-preimage geometry instead selects

```text
w_join proportional to sin(f)^2 cos(f)^2.
```

It vanishes at both poles, is reflection-compatible, and puts the material
surface at the Hopf seam.  Its identity response jet is

```text
a^2 U_join'(sigma) = -20 sigma + (5 pi^2/3) sigma^3 + O(sigma^5).
```

The weighted physical Hessian on the smooth two-pole domain has lowest
eigenvalue approximately `-14.202`.  This is a physical enclosure mode, not a
gauge direction.

The pole-fixing nonlinear family

```text
tan(chi_tilde)=exp(-ell) tan(chi)
```

moves the wall while preserving its endpoint vacua and smoothness.  The seam
is an energy maximum along this family; energy decreases toward either pole
and approaches zero.  Thus the candidate creates a critical material skin,
but not a stable encapsulated child.

Eliminating a positive metric/eta constraint complement gives

```text
H_eff = H_sigma - B H_response^-1 B^dagger <= H_sigma,
```

so it cannot remove the negative mode.  If the complement is not positive,
the coupled system already has another physical instability.  A constant
formation pressure also cannot stabilize the wall because at every stationary
join radius

```text
E'' = T A (log A)'' < 0,
A=sin(chi)^3 cos(chi)^3.
```

The next required stabilizer must carry a different radius scaling, such as
an action-owned conserved Hopf-fiber charge, flux, or internal rotation.  None
was inserted in this calculation.

Exact next object:

```text
ACTION_OWNED_CONSERVED_HOPF_FIBER_CHARGE_FLUX_OR_ROTATION_STABILIZATION_IN_THE_COUPLED_JOIN_CONSTRAINT_SYSTEM
```
