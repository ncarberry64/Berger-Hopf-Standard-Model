# AE4 affine-72 proper-time gauge Calderon first jet

## Reused assets

The moving-endpoint first/two-jet chain rules, the 72-direction exact-affine
history jet, the cancelled-arc proper-time pullback, and the inverse-free
Weyl coefficient cotangent were already derived.  This unit composes them;
it does not rebuild any of those objects or any particle state.

The action arc is first pulled back to physical proper time using

```text
d tau/d r = N_boundary s / ||G_theta||_action.
```

At fixed normalized proper time `u=tau/T`, the scalar Weyl derivative is

```text
D M = <D_x M,D x> + <D_h M,D h>,
D h_i = (u_(i+1)-u_i) D T.
```

The corrected coexact potential is `4/R4^2`.  The lowest nonconstant scalar
BRST potential is `3/R4^2`; the two real constraint coordinates and one
complex ghost use identical coefficient and endpoint jets, so their first
variations cancel exactly.  The surviving gauge/BRST first jet is the
coexact one.

On the materialized affine carrier the decomposition is numerically sharp:

```text
||D_logR M_coexact||_2 = 8.30e-5,
||D_T    M_coexact||_2 = 3.58e5.
```

Thus the candidate response is dominated by the moving first-stop duration
by more than nine orders of magnitude.  This does not promote the affine
carrier, but it proves that a fixed-endpoint reconstruction would discard the
decisive term rather than approximate it.

## Scientific boundary

This is the first explicit 72-component gauge Calderon first-jet candidate
on the stop-matched proper-time path.  It is not promoted as the nonlinear
physical operator jet.  The repository's existing transfer audit proves that
the current affine-to-nonlinear Volterra bound is not contractive.  Component
radii are retained as a warning, and no fit or field normalization is used to
hide that failure.

The missing object is therefore narrower than the older ledgers stated: the
same-center 74-dimensional interval contraction, or an equivalent continuous
outward nonlinear variational carrier.  Once that closes, this identical
proper-time Weyl-cotangent contraction can be repeated with authority.

```text
AE4_CURRENT_C2_AFFINE72_PROPER_TIME_GAUGE_CALDERON_FIRST_JET_EVALUATED = TRUE
AE4_CURRENT_C2_NONLINEAR72_GAUGE_CALDERON_FIRST_JET_DERIVED            = FALSE
CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED                          = FALSE
FULL_BHSM_COMPLETE                                                      = FALSE
```
