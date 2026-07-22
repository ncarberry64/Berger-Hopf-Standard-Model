# BHSM v6.1.4 intrinsic M4 junction-supported background closure

## Result and claim boundary

Primary result:
`BHSM_INTRINSIC_M4_JUNCTION_BACKGROUND_DERIVED_CONDITIONALLY`.

The frozen v6.1.3 intrinsic action admits an exact background on the
positive-curvature P1 branch without adding boundary tension or vacuum
energy. The construction cuts constant-curvature de Sitter-5 by an offset
timelike de Sitter-4 hyperplane, retains a regular cap, and glues an identical
copy across the hyperplane. The Z2-fixed domain has nonzero one-sided
extrinsic curvature even though the two derivatives are opposite.

The construction is conditional. Boundary Axiom B1 is still provisional,
the coefficients remain unsourced, and the full constraint-reduced mixed
bulk-boundary perturbation spectrum has not been solved. The result is not an
identification of M4 with observed spacetime or of its fields with Standard
Model fields.

## Frozen theory

The calculation uses exactly

```text
S_total = S_P1,bulk + S_GHY + S_partial + S_match,

S_P1,bulk = (1/2) integral_M5 sqrt(-g) [kappa_1 R5-kappa_0],

S_partial = integral_M4 sqrt(-h)
  [C_partial R4
   -tau_A Tr(F_mu nu F^mu nu)/4
   -Z_partial h^mu nu partial_mu sigma_partial partial_nu sigma_partial/2
   -U_partial]
  +S_match.
```

The vacuum test sets `A_mu=0`, `sigma_partial=0`, and `U_partial=0`. The
frozen action contains no sourced constant in `U_partial`. No boundary
tension, cosmological term, new matter, higher derivative, `sigma F^2`,
`sigma R`, connection mass, P2/P3 correction, physical fermion action, or
monopole sector is added.

Boundary Axiom B1 remains a provisional physical-domain axiom. It defines
independent intrinsic `h_mu_nu`, `A_mu`, and `sigma_partial` on one member of
the SO(5)-equivalent great-`S3` orbit. It is not derived from P1 and does not
select a preferred parent axis.

## Exact variation and matching

Variation of the bulk action gives

```text
kappa_1 G_AB + (kappa_0/2) g_AB = 0.
```

For each oriented cap the GHY term is

```text
kappa_1 integral_M4 sqrt(-h) K.
```

It cancels normal derivatives of `delta g`. With

```text
K_mu nu = (1/2) L_n h_mu nu,
Q_mu nu = K_mu nu-K h_mu nu,
```

the canonical coefficient in the unmultiplied boundary variation is
`(kappa_1/2)Q_mu nu`. Reversing the normal reverses `K` and `Q`.

The exact matching action is

```text
S_match = integral_M4 sqrt(-h)
  Lambda^mu nu (h_mu nu-iota^*g_mu nu).
```

The variables `g`, `h`, and `Lambda` are varied independently. Variation of
`Lambda` imposes `h=iota^*g`. The bulk boundary equation and intrinsic metric
equation contain the multiplier with opposite constraint forces. Eliminating
it gives

```text
kappa_1 [Q_mu nu] + 2 C_partial G_mu nu^(4)
  = T_A,mu nu + T_sigma,mu nu.
```

The bracket uses a common normal and means the plus value minus the minus
value. On a Z2 double, `Q^-=-Q^+`, so `[Q]=2Q^+`. For an actual one-cap
boundary the corresponding equation is

```text
kappa_1 Q_mu nu + 2 C_partial G_mu nu^(4)=T_partial,mu nu.
```

The multiplier is nondynamical, has no kinetic term, and introduces no
tunable matching coefficient or hidden physical stress.

## Smooth-equator residual

For

```text
ds5^2=-dt^2+a(t)^2[dchi^2+sin^2(chi)dOmega3^2]
```

at `chi=pi/2`, the old smooth equator has `K_mu nu=0`. Define

```text
H = dot(a)/(N a),
X = H^2+a^-2,
A = N^-1 dot(H)+H^2,
Y = 2A+X.
```

The mixed intrinsic Einstein tensor is

```text
G^t_t = -3X,
G^i_j = -Y delta^i_j.
```

In intrinsic vacuum the failed junction equation has residual

```text
R^t_t = -6 C_partial X,
R^i_j = -2 C_partial Y delta^i_j.
```

At finite radius `X>0`, so the temporal residual cannot vanish for
`C_partial>0`. This reproduces
`BHSM_SMOOTH_K0_EQUATOR_INTRINSIC_GRAVITY_RESIDUAL_DERIVED` but is not the
headline result.

## Gaussian-normal bulk system

Use

```text
ds5^2 = dy^2-n(y,t)^2dt^2+r(y,t)^2dOmega3^2.
```

Normal lapse is one and normal shift is zero. At `y=0`,
`n=N_partial` and `r=a_partial`. The one-sided mixed principal curvatures are

```text
k_t = n_y/n,
k_s = r_y/r.
```

For the Z2 construction `n` and `r` are even in `|y|`; their derivatives,
and hence `K`, are odd. Reflection symmetry therefore does not imply
`K^+=0`.

Let `g_ab dx^a dx^b=-n^2dt^2+dy^2` and use its two-dimensional covariant
derivative. The P1 equations are compactly

```text
G_ab = -3 r^-1 nabla_a nabla_b r
       +3 g_ab box_2 r/r
       +3 g_ab (nabla r)^2/r^2
       -3 g_ab/r^2,

G^i_j = [-R2/2+2 box_2 r/r+(nabla r)^2/r^2-r^-2] delta^i_j,

G_AB + lambda_5 g_AB = 0,
lambda_5 = kappa_0/(2kappa_1).
```

Here

```text
R2 = -2 n_yy/n,
box_2 r = -r_tt/n^2+n_t r_t/n^3+(n_y/n)r_y+r_yy,
(nabla r)^2 = -r_t^2/n^2+r_y^2.
```

The independent equations may be taken as the `tt` Hamiltonian equation,
the `yy` normal constraint, the `ty` momentum constraint, and one angular
evolution equation. The bulk Bianchi identity propagates the constraints and
makes the remaining equation dependent where the metric is regular.

## Homogeneous junction equations

Let `m=1` for one actual cap boundary and `m=2` for a Z2 double, and define

```text
eta_m = 2 C_partial/(m kappa_1).
```

In the retained intrinsic vacuum, the temporal and spatial equations give

```text
k_s = -eta_m X,
k_t = eta_m (X-2A).
```

For the Z2 branch, `eta=C_partial/kappa_1`, while the jumps are
`[k_t]=2k_t` and `[k_s]=2k_s`. These factors follow from the variation; they
are not imported from an Israel formula.

## Constant-curvature branch

The bulk equation permits constant sectional curvature

```text
q_5 = kappa_0/(12kappa_1),
R_AB = 4q_5 g_AB,
R5 = 20q_5.
```

This sprint uses the already selected positive-ratio branch
`kappa_0/kappa_1>0`. Its radius is

```text
L5 = q_5^(-1/2) = sqrt(12kappa_1/kappa_0).
```

For a homogeneous isotropic hypersurface, Gauss and Codazzi give

```text
X = q_5+k_s^2,
A = q_5+k_t k_s,
N^-1 dot(k_s) = H(k_t-k_s).
```

On the Z2 vacuum junction, the nonstatic solution has
`k_t=k_s=-eta X` and therefore

```text
eta^2 X^2-X+q_5=0,

X_plus/minus =
  [1 plus/minus sqrt(1-4 eta^2 q_5)]/(2 eta^2).
```

Real branches exist precisely when

```text
0 < C_partial/kappa_1 <= 1/(2 sqrt(q_5)).
```

Both roots satisfy `X>q_5` away from the zero-coefficient limit. At the
critical double root `X=2q_5`, the acceleration equation is degenerate and a
separate static branch described below also exists. The old
smooth equator `X=q_5`, `k=0` is recovered only as a limiting geometry and is
not a solution for positive `C_partial`.

## Regular Z2 double caps

Embed de Sitter-5 of radius `L5` in flat `R^(1,5)` and intersect it with
the timelike hyperplane

```text
X5=c,  |c|<L5.
```

The intersection is de Sitter-4 with

```text
L4^2 = L5^2-c^2,
X = L4^-2,
k^2 = X-q_5,
|c| = L5 sqrt(1-q_5/X).
```

Each side is a region of the smooth constant-curvature parent geometry. To
obtain the required Z2 jump, retain one cap containing its regular pole and
glue an identical copy across the hyperplane. Each cap has finite constant
curvature invariants, no conical defect, and no second junction. Doubled
spatial sections have piecewise-smooth `S4` topology; the sole distributional
hypersurface is the intended M4 junction.

At the critical coefficient there is also an exact static embedding. In the
same flat embedding space set

```text
X0=b sinh(t/b),
X1=b cosh(t/b),
(X2,...,X5)=a Omega3,
a=b=L5/sqrt(2).
```

Its induced geometry is `R x S3` with constant radius `a`. Its principal
curvatures are `k_t=sqrt(q_5)` and `k_s=-sqrt(q_5)`, so the temporal and
spatial Gauss equations and both junction equations hold at
`C_partial=kappa_1/(2sqrt(q_5))`. Doubling either regular spatial cap gives a
global Z2 construction. This branch is distinct from the critical
de Sitter-4 bounce even though both have `X=2q_5`.

The two unequal complementary regions in one uncut de Sitter-5 geometry do
not by themselves provide the required Z2 canonical-momentum jump. The exact
background is therefore the doubled-cap construction, not a relabeling of a
smooth equator.

## Boundary FRW trajectory

The lapse is varied before setting `N_partial=1`. The exact Hamiltonian
constraint is

```text
H^2+a^-2 = q_5+eta^2(H^2+a^-2)^2.
```

Equivalently,

```text
epsilon sqrt(X-q_5) = -eta X.
```

For positive coefficients and the declared normal, `epsilon=-1`. The two
algebraic curvature roots must both be retained. The acceleration equation is
`A=X`, and the proper-time trajectory on either root is

```text
a_partial(tau)=L4 cosh[(tau-tau0)/L4].
```

The dynamic branch contracts for `tau<tau0`, has a regular symmetric bounce at
`a=L4`, and expands for `tau>tau0`. The time-reversed descriptions are the
same complete solution. No globally monotonic dynamic branch is retained. At
the critical coefficient, the separate finite-radius static embedding above
is retained alongside the critical dynamic bounce.

This is a geometric closed de Sitter trajectory. It is not identified with
observed cosmology.

## Gravitational coefficient relation and primitives

The junction relation can be written

```text
C_partial = kappa_1 sqrt(X-q_5)/X.
```

It also imposes

```text
C_partial <= kappa_1/(2sqrt(q_5)).
```

This is a background relation and existence bound. It is not a universal
coefficient derivation because the equations do not select one root `X` or
derive the source of `C_partial`. Instead, supplied parent and boundary
coefficients determine one of two allowed embedding curvatures.

The continuous coefficient content remains:

- parent `kappa_0` and `kappa_1`;
- independent positive `C_partial` within the existence domain;
- independent `tau_A`;
- free-scalar `Z_partial`, removable by field normalization until a scalar
  source is derived.

The root and normal signs are discrete. `tau0` is a time-origin integration
constant. A vanishing connection and scalar background cannot constrain
`tau_A` or `Z_partial`.

## Connection and sigma vacua

`A_mu=0` solves `tau_A D_nu F^(nu mu)=0`, has zero stress, and satisfies the
Gauss constraint. No nonzero electric, magnetic, or monopole configuration is
inserted to repair the junction.

With frozen `U_partial=0`, `sigma_partial=0` solves
`Z_partial box_h sigma_partial=0` and has zero energy density, pressure, and
junction contribution. No `sigma=1/2`, `A_ST=-2`, or `G_ST=8` input is used.

The exact background therefore needs no boundary vacuum term. A term
`-Lambda_partial integral sqrt(-h)` would have coefficient dimension `L^-4`
and stress `-Lambda_partial h_mu nu`, but it is neither required nor added.

## Conservation

After matching-multiplier elimination, Codazzi and the bulk Bianchi identity
give

```text
D^mu(T_partial,mu nu-2C_partial G_mu nu)
  = -[T_bulk,n nu].
```

The connection and scalar equations supply their Ward identities. On the
retained vacuum branch the boundary stress and normal bulk flux both vanish,
so conservation holds identically. Separate boundary conservation would not
be assumed on a branch with nonzero bulk flux.

## Stability and tensor sector

After removing bulk diffeomorphisms, boundary time reparameterization, lapse
and shift constraints, the matching multiplier, and connection gauge zero
modes, the principal diagonal kinetic signs are healthy for

```text
kappa_1>0, C_partial>0, tau_A I_R>0, Z_partial>0.
```

The intrinsic tensor, connection, and scalar characteristic speeds are one
with respect to the induced metric. The bulk P1 principal system is normally
hyperbolic in a valid bulk gauge.

The tensor junction condition is

```text
kappa_1[delta Q_TT]+2C_partial delta G_TT=0.
```

Consequently the tensor candidate is mixed bulk-boundary, with its leakage
and normal spectrum controlled by the cap Green operator. The full
normalizable tensor spectrum, scalar-type bulk metric sector, junction
bending displacement, and root-branch radion sign have not been reduced to a
complete physical quadratic form. No negative mode or ghost is claimed.

This unresolved mixed stability problem is the reason the background result
is conditional rather than a complete stable bosonic closure.

## Fermionic and physical firewalls

The exact classical domain supplies an induced frame, spin structure,
Clifford bundle, intrinsic spin connection, and a mathematical extrinsic
Gauss contribution. These are only BHSM-native first-order-action readiness.
No physical fermionic action, physical Dirac equation, self-adjoint physical
domain, or particle spectrum is constructed.

Hopf curvature, Chern data, winding, and U1 transitions remain bundle
geometry. They are not magnetic charge. Monopoles, monopole harmonics, Dirac
strings, magnetic-charge operators or quantization, and monopole-generated
chirality or generations remain excluded.

## Scale and completion gate

The background derives

```text
L5=sqrt(12kappa_1/kappa_0),
L4=X_plus/minus^(-1/2),
|c|=L5 sqrt(1-q_5/X),
|k|=sqrt(X-q_5).
```

These are radii in terms of unsourced primitive coefficients and a discrete
branch. No Planck length, measured Hubble rate, CMB temperature, particle
mass, gauge coupling, alpha, CKM/PMNS datum, or cosmological parameter is
used. No absolute physical unit is generated.

Completion gate:
`V6_1_4_Z2_TWO_CAP_BACKGROUND_DERIVED_MIXED_STABILITY_AND_COEFFICIENT_SOURCE_OPEN`.

Recommended next branch:
`bhsm-junction-mixed-stability-closure-v6-1-5`.

`FULL_BHSM_NOT_COMPLETE`.
