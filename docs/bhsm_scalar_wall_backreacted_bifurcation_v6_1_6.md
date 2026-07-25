# BHSM v6.1.6 scalar-wall backreacted bifurcation

## Scope

This sprint starts from the v6.1.5 critical odd scalar mode and tests the
analytic Lyapunov--Schmidt hierarchy against the exact P1 normal constraint
and provisional B1 metric junction. No field, interaction, tension, boundary
vacuum constant, measured input, P2/P3 term, or fitted coefficient is added.
The scalar vacuum energy remains in the action.

Primary result:

`BHSM_SCALAR_WALL_BIFURCATION_ENSEMBLE_DEPENDENT`.

## Independently reproduced critical mode

On the audited dimensionless cap

```text
a0=sqrt(2) sin(rho),  0<=rho<=pi/4,
q5=1, X0=2, C_partial/kappa1=1/2,
```

the regular-pole, odd-junction problem is

```text
L_c u1=-a0^-4 d_rho(a0^4 u1')=mu_c u1,
u1'(0)=0, u1(pi/4)=0.
```

Shooting and the independent hypergeometric/Gegenbauer representation give

```text
mu_c/q5 = 29.430918352948... .
```

With `integral a0^4 u1^2 d rho=1`,

```text
u1(0)=8.923902707116...,
u1'(pi/4)=-9.124976903426...,
integral a0^4 u1^4 d rho=21.690130229412... .
```

The self-adjoint boundary form vanishes because `a0^4` closes the pole and
both domain functions vanish at the odd junction.

## Exact second-order junction test

At the junction, the P1 normal constraint and frozen B1 metric equation give,
in the audited orientation magnitude,

```text
eta^2 X^2-X+q5
  = (Z5/(12 kappa1)) sigma_J'^2,
eta=C_partial/kappa1.
```

At the v6.1.4 critical coefficient,

```text
eta_c=1/(2sqrt(q5)),  X_c=2q5,
```

so the equation completes exactly to

```text
(X-X_c)^2/(4q5)
  = (Z5/(12kappa1)) sigma_J'^2.
```

The requested analytic, scalar-Z2 expansion has
`X=X_c+epsilon^2 X2+...` and
`sigma_J'=epsilon u1'(rho_J)+...`. Its order-`epsilon^2` boundary equation is

```text
0=(Z5/(12kappa1))u1'(rho_J)^2,
```

which is impossible for the reproduced nontrivial eigenmode and positive
`Z5/kappa1`. In the unit diagnostic normalization the positive obstruction
coefficient is `6.938766957338...`.

This is an exact obstruction to the requested **analytic fixed-`C_partial`
hierarchy**, not a theorem excluding every nearby solution.

## Fold response and ensemble dependence

The same completed-square equation permits

```text
X-X_c
 = plus_or_minus sqrt(q5 Z5/(3kappa1))
   |u1'(rho_J)| |epsilon| + ... .
```

Thus the geometry can remain invariant under `epsilon -> -epsilon` while
being nonanalytic in the signed scalar amplitude. For
`q5=Z5/kappa1=1`, the curvature-fold slope is
`5.268307871542...`.

If `X` is instead fixed and the independent B1 coefficient is varied,
an analytic compensation requires

```text
eta2=(Z5/kappa1)u1'(rho_J)^2/(48 q5^(3/2)).
```

That is an ensemble choice, not a derivation of `C_partial`. No parent theorem
currently selects fixed `C_partial`, fixed `X`, fixed cap length, or a fold
sheet. The local classification is therefore ensemble-dependent.

## Why the cubic coefficient is not reported

The formal direct scalar projection in the residual convention

```text
-delta_mu epsilon+C_bif epsilon^3+...=0
```

would contribute

```text
C_direct=(G5/Z5) integral a0^4 u1^4.
```

But `C_gravity`, `C_junction`, and `C_domain` require a consistent
second-order solution. Because the analytic hierarchy fails one order
earlier, a total `C_bif`, an on-shell quartic coefficient, and
supercritical/subcritical language would be fabricated. They remain open.

## Continuation, energy, and stability

No unconstrained shooting scan is substituted for the failed perturbative
seed. Controlled continuation must be reformulated on the two Puiseux
curvature sheets and must solve the complete bulk equations, cap regularity,
constraint, and B1 junction simultaneously. Consequently:

- no finite-amplitude coupled branch is claimed;
- no on-shell energetic preference is claimed;
- the amplitude-direction eigenvalue is unresolved;
- the full scalar--metric--junction--Berger operator remains open;
- singlet stress still has `p1-p2=0`.

The backreacted relation removes no B1 primitive. It does not derive
`C_partial` or `tau_A`, and a bending coordinate is not the declared
`sigma_partial` without an action/domain map.

Completion gate:

`V6_1_6_CRITICAL_DOUBLE_ROOT_PUISEUX_CONTINUATION_AND_MIXED_STABILITY_OPEN`.

`FULL_BHSM_NOT_COMPLETE`.
