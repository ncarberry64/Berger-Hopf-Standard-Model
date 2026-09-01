# N12 C2 1,222-segment transposed duration-action coverage

For segment `e` of the certified fixed-descriptor C2 cover, let

```text
h_e(Y_e) = integral_(s_e)^(s_(e+1)) q_tau(Y(s),s) ds,
q_tau = N_boundary*s/Delta.
```

The exact first variation is the inverse-free transposed action

```text
D_Ye h_e = integral D_Y q_tau(Y(s),s) J_e(s) ds,
```

where `J_e` is the exact fixed-descriptor state Jacobi action.  The existing
moving-duration certificate bounds this covector on every one of the 1,222
segment tubes by

```text
||D_Ye h_e||
 <= h_e^+ G_e (||D log N_boundary|| + ||D Delta||_e^+/Delta_e^-).
```

Consequently each exact segment covector lies in a closed action-dual ball
centered at zero with the stored radius.  These are genuine interval actions,
not merely duration-value intervals: they enclose the transposed exact
segment map without constructing or inverting a transition matrix.

The segment-1214 joint-domain result supplies a much sharper nonzero-centered
ball and is contained strictly inside its corresponding coarse interval
action.  It therefore validates the signed refinement route, but the other
1,221 expensive signed `DDelta` row sweeps are not a prerequisite for
well-defined interval reverse propagation.

This theorem does not manufacture the actual signed Gate-7 force.  A signed
reverse sweep must be contracted with the coefficient cotangent of the
retained graded heat-minus-zeta functional.  The currently stored `z=-1`
Weyl cotangent is a resolvent probe and cannot occupy that source slot.
Accordingly the next upstream dependency is controlled spectral synthesis of
the actual graded coefficient cotangent (and the complete upstream arm), not
repetition of finite norm-only duration certificates.
