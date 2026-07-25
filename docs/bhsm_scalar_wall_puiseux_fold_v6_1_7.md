# BHSM v6.1.7 scalar-wall Puiseux curvature fold

Primary result:

`BHSM_SCALAR_WALL_PUISEUX_BRANCH_DERIVED_CONDITIONALLY`.

This sprint keeps the provisional P1+GHY+B1 action and all B1 coefficients
fixed while controlling `mu=-A5/Z5`. It constructs both local nonanalytic
curvature sheets in the declared dimensionless representative
`q5=Z5/kappa1=G5/Z5=1`. This is a conditional solution of that frozen
representative, not a parent derivation of its coefficients or an absolute
scale.

## Double-root normal form

At `C_partial/kappa1=1/(2 sqrt(q5))`, the exact normal constraint and B1
junction give

```text
(X-2q5)^2/(4q5) = (Z5/(12kappa1)) sigma_J'^2.
```

The derivative with respect to `X` vanishes at `(X,sigma_J')=(2q5,0)`, so the
ordinary implicit-function theorem does not apply. The natural scalar
coordinate is `r=|epsilon|`. The two sheets are

```text
X-2q5 = +/- sqrt(q5 Z5/(3kappa1)) |sigma_J'|.
```

Recomputing the regular-pole/Dirichlet eigenpair gives

```text
mu_c/q5              = 29.430918352947...
u1(0)                = 8.923902707116...
u1'(rho_J)           = -9.124976903426...
integral a0^4 u1^2  = 1
integral a0^4 u1^4  = 21.690130229412...
|chi1|               = 5.268307871542...
```

Normal reversal changes signed extrinsic curvature and the signed normal
scalar derivative, but not intrinsic `X`; it therefore does not exchange the
two sheets. The sheets locally reconnect to the low- and high-curvature
v6.1.4 roots.

## The order-r geometric Jacobi field

Scalar stress begins at `O(r^2)`, but the double-root geometry has a
homogeneous `O(r)` Jacobi field. In proper normal distance,

```text
a(X,y)=sqrt(X/q5) sin(sqrt(q5)y),
ell(X)=q5^(-1/2) asin(sqrt(q5/X)).
```

For the normalized critical cap and fixed coordinate `t in [0,1]`,
`y=ell(X)t`, so

```text
a1 = chi1 [a0/4-sqrt(2)t cos(pi t/4)/4],
N1 = ell1 = -chi1/4,
K1 = -chi1/2
```

in the declared orientation. It is regular at the pole and preserves
`a_J=1`. It is not gauge because it changes intrinsic scalar curvature by
`delta X=chi1 r`. Differentiating the exact cap family independently gives
the same response.

## Quadratic scalar solvability

The `O(r^2)` scalar equation is

```text
(L_c-mu_c)u2=S2,       <u1,u2>=0.
```

In proper-normal moving-endpoint gauge, the operator's explicit warp
normalization cancels and the shape derivative is

```text
dmu/dell = -a_J^4 u1'(ell)^2,
dell/dX = -1/4
```

at the normalized critical cap. Thus

```text
nu1 = chi1 u1'(rho_J)^2/4.
```

Numerically,

```text
nu1_upper = +109.666681740423...
nu1_lower = -109.666681740423...
```

One proper-normal bookkeeping convention assigns zero explicit gravity and
junction pieces and the displayed value to the endpoint/domain piece. Under
fixed-domain coordinate changes those named pieces redistribute. Only their
sum is gauge invariant; the repository does not mislabel the decomposition
itself as invariant.

The direct `G5 u1^3/Z5` term is not used at this order.

## Coupled continuation

The normalized equations solved are

```text
sigma''+4(a'/a)sigma' = -mu sigma+(G5/Z5)sigma^3,
a'' = -a[6+U5+3 sigma'^2/2]/6,
a(0)=0, sigma'(0)=0,
a_J=1, sigma_J=0, a'_J=X/2.
```

The last condition is the fixed B1 metric junction. Regular pole expansions
start the integration; `(X,mu)` are solved simultaneously. Continuation uses
`r`, never signed epsilon. Both scalar signs give identical geometry and
opposite scalar profiles.

Both sheets converge over the audited local interval `0.001<=r<=0.02`.
Hamiltonian, scalar, B1-junction, normal-form, virial, and cap-regularity
residuals converge under mesh refinement. The lower sheet has decreasing
`X` and `mu`; the upper sheet has increasing `X` and `mu`. Neither sheet
encounters a cap pole or loses positive curvature in that local interval.
This establishes a local branch for the normalized representative only; it
does not prove global continuation for every allowed primitive ratio.

The `O(r^2)` Einstein response is thereby validated numerically with scalar
kinetic and potential stress, quadratic Jacobi-field terms, junction
corrections, and the lapse/length response retained. No delta stress,
boundary tension, or vacuum-energy subtraction is inserted. The singlet
source remains isotropic, so `p1-p2=0`.

## Cubic coefficient, action, and stability

The direct cubic projection regresses to

```text
C_direct=(G5/Z5) 21.690130229412...
```

The complete analytic `u2/a2` projection ledger has not yet separated
`C_gravity`, `C_junction`, and `C_domain` gauge-invariantly. No total cubic
coefficient is claimed merely from the numerical branch.

A complete action comparison also remains open. Although a radial reduced
density can be evaluated, changing `X` changes the Lorentzian M4 geometry.
A common regulated M4 volume and boundary normalization have not been fixed,
so that radial number is not promoted to the complete P1+GHY+B1 on-shell
action difference. Consequently no fold-direction action stability sign is
claimed. The full constrained scalar-metric-junction-Berger spectrum remains
open.

## Ensemble theorem ledger

1. **Fixed action coefficients.** Both Puiseux sheets are solutions of the
   normalized frozen provisional B1 boundary-value problem as `mu` is
   controlled.
2. **Varying `C_partial`.** This compares neighboring provisional B1
   theories; it is not motion in one frozen action.
3. **Dynamical `C_partial`.** No parent-source theorem exists, so this
   ensemble is unavailable.

The v6.1.6 status
`BHSM_SCALAR_WALL_BIFURCATION_ENSEMBLE_DEPENDENT` remains historically
correct: at that stage the fixed-coefficient Puiseux boundary problem had not
been constructed. No B1 primitive is now called derived.

Completion gate:
`V6_1_7_FOLD_ACTION_AND_FULL_MIXED_STABILITY_OPEN`.

`FULL_BHSM_NOT_COMPLETE`.
