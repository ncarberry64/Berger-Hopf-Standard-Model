# BHSM v6.0.10 P1 Lorentzian Background Constraint Closure

Primary result: `BHSM_P1_FIXED_SHAPE_DYNAMIC_BACKGROUND_DERIVED`.

## Scope

The parent domain is `M8=I_t x S7`, with signature `(-+++++++)` and

```text
ds8^2=-N(t)^2dt^2+a4(t)^2g_H4+a2(t)^2g_V2+a1(t)^2eta^2.
```

The lapse remains arbitrary until after variation. The `S4` factor is the
Riemannian Hopf base, not observed spacetime, and the solutions below are
eight-dimensional parent backgrounds rather than observed cosmologies.

## ADM action and constraints

For `q_i=ln a_i`, `H_i=dot(a_i)/(Na_i)`, and multiplicities `(4,2,1)`,

```text
V7=(128 pi^4/3)a4^4a2^2a1,
K=4H4+2H2+H1,
KijKij=4H4^2+2H2^2+H1^2.
```

After the GHY cancellation,

```text
L_g=V7/2[(kappa1/N) qdot^T G qdot
          +N(kappa1 R7-kappa0)],

G=[[-12,-8,-4],[-8,-2,-2],[-4,-2,0]].
```

Lapse variation gives

```text
C_H=[kappa1(R7-H^T G H)-kappa0]/2-rho=0.
```

This equals the parent `tt` equation. With covariant matter conservation,
`D_t C_H=-Theta C_H`, where `Theta=4H4+2H2+H1`. The pre-homogeneous momentum
constraint is checked explicitly; it vanishes for the diagonal invariant
zero-shift ansatz with no momentum current.

The independent scale equations are

```text
G D_t H = 1/2[d(T+R7-lambda)+grad_q R7]
          +d p/kappa1-Theta G H,
T=H^T G H, lambda=kappa0/kappa1.
```

The variables

```text
rho=(4q4+2q2+q1)/7, beta=q1-q2, gamma=q2-q4
```

separate the constrained common-volume direction from two positive-kinetic
shape directions. The lapse and time-reparameterization gauge are removed
before physical shape stability is classified.

## Static product theorem

For any static scale factors, the required diagonal support is

```text
rho_req=(kappa1 R7-kappa0)/2,
p_i_req=kappa1(r_i-R7/2)+kappa0/2,
r_i=-(1/(2d_i)) partial R7/partial q_i.
```

The round fixed-lapse extremum requires
`rho_req=kappa0/5=3kappa1/(2a4^2)` and `p4=p2=p1=0`. The Jensen extremum
requires `rho_req=kappa0/5=27kappa1/(10a4^2)` and the same zero pressures.
Thus both are spatial extrema requiring positive dust-like diagnostic stress,
not vacuum static products: `BHSM_P1_STATIC_PRODUCT_BACKGROUND_EXCLUDED`.
No fluid is introduced by this calculation.

A constant stationary canonical sigma has `p=-rho`, so it cannot provide this
positive static dust-like source. The canonical Hopf connection is already
included in the connection-metric curvature and cannot be counted again as
support.

## Exact fixed-shape Lorentzian branches

For `lambda>0`, the round Einstein shape obeys

```text
H^2+1/(4a^2)=lambda/42,
ddot(a)/a=lambda/42,
a=sqrt(21/(2lambda)) cosh[sqrt(lambda/42)(t-t0)].
```

It joins contracting and expanding branches through a smooth positive
minimum. After constraint reduction its two homogeneous shape masses are
both `4/a^2`. There is no homogeneous shape tachyon; the expanding half is
friction-damped, while the contracting half has antifriction and the restoring
force becomes asymptotically marginal as `a` grows.

The Jensen ratios `a2/a4=a1/a4=1/sqrt(5)` are also an exact Einstein
invariant submanifold:

```text
H^2+9/(20a4^2)=lambda/42,
a4=sqrt(189/(10lambda)) cosh[sqrt(lambda/42)(t-t0)].
```

However, its physical shape masses are `52/(5a4^2)` and `-4/a4^2`. The
Jensen trajectory therefore exists exactly but has one homogeneous shape
instability. This replaces the earlier fixed-lapse saddle statement with a
full constraint-reduced Lorentzian result.

## Existing fields and normalized operators

The selected sigma singlet has

```text
rho_sigma=Z sigma_dot^2/2+U,
p_sigma=Z sigma_dot^2/2-U,
Z(D_t^2 sigma+Theta D_t sigma)+U'(sigma)=0.
```

Its isotropic stress is compatible with fixed Einstein shapes dynamically,
but no potential coefficient or vacuum value is chosen to manufacture a
solution.

Along a background,

```text
K=(kappa1 Vol(F)/2)diag(a2^2,a2^2,a1^2)
```

remains positive. Its time dependence changes canonical field normalization
and friction; it is not renormalization-group running or a physical gauge
coupling.

An associated scalar multiplet obeys

```text
D_t^2 phi+Theta D_t phi
 +[lambda_(J,m)(a2,a1)+E_(J,m)+M_parent^2]phi
 +interaction sources=0.
```

No particle or mass identification follows.

## Dynamic tower control

The instantaneous gap remains

```text
Delta(t)=min[1/(2a2^2)+1/(4a1^2),2/a2^2].
```

Controlled reduction requires small `E^2/Delta`, `H_i^2/Delta`,
`|D_t Delta|/Delta^(3/2)`, `|D_tH_i|/Delta`, and normalized source ratios.
For fixed shape, `Delta` scales as `a^-2`. On the positive-`lambda` cosh
solutions it tends to zero at large `|t|` while `H` tends to a constant, so
the tower EFT is eventually uncontrolled even though no finite-time gap
closing occurs.

## Scale and continuation

P1 derives the parent expansion relation `H_lambda^2=lambda/42` and the
round/Jensen minimum radii in terms of `lambda=kappa0/kappa1`. Because those
primitive coefficients are not independently fixed in physical units, this
is not an absolute unit.

The stable round fixed-shape trajectory closes the P1 Lorentzian parent
background gate without P2/P3 or new matter. Jensen instability and late-time
tower loss remain constructive limitations.

`FULL_BHSM_NOT_COMPLETE`.

Recommended continuation: `bhsm-round-background-gauge-scalar-sector-v6-1`.
