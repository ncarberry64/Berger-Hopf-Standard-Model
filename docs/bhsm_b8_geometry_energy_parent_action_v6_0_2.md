# BHSM v6.0.2 B8 Geometry–Energy Parent Action Construction

## Results

Primary: `BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED`

Physicality sector: `BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED`

Under the explicit assumptions of locality, diffeomorphism invariance,
metric-only geometric dynamics, and field equations no higher than second
order, the eight-dimensional geometry sector is the finite Lovelock family.
This classifies the smallest testable parent actions. It does not make any one
of them a BHSM-derived physical action.

The smallest propagating Dirichlet family is

```text
S_P1 = (1/2) integral_M dmu_G [kappa_0 + kappa_1 R]
     + S_sigma + S_matter
     + kappa_1 integral_boundary dmu_h epsilon_n K
     + S_constraints.
```

Every coefficient, the domain, signature, parent matter action, and the
energy–geometry confinement invariant remain open.

## Eight-dimensional geometry audit

Define

```text
L_k = (1/2^k) delta^(A1B1...AkBk)_(C1D1...CkDk)
      product_j R^(CjDj)_(AjBj).
```

In eight dimensions:

- `L_0=1` is the volume density.
- `L_1=R` is the lowest-derivative propagating metric term.
- `L_2=Riemann^2-4 Ricci^2+R^2` is Gauss–Bonnet and still gives
  second-order metric equations.
- `L_3` is the cubic dynamical Lovelock density.
- `L_4` is the eight-dimensional Euler density. Its bulk Euler–Lagrange
  tensor vanishes; its integral carries topological information plus a
  boundary transgression.
- `L_k` vanishes identically for `k>4`.

For action dimension `[A]`, the coefficient of `L_k` has dimension
`[kappa_k]=[A]L^(2k-8)`. Under `G -> lambda^2 G`, its integrated bulk and
coefficient-locked boundary terms scale as `lambda^(8-2k)`.

The finite families are:

- P0: volume plus matter/physicality, insufficient for propagating geometry.
- P1: volume and scalar curvature, the smallest propagating test family.
- P2: P1 plus Gauss–Bonnet.
- P3: the full dynamical Lovelock family through `L_3`.
- P4: optional Euler/transgression topology, not bulk dynamics.

Independent generic `R^2`, `Ricci^2`, and `Riemann^2` coefficients are excluded
from the minimal family because their generic equations are fourth order and
carry extra-mode or ghost risks. Gauss–Bonnet is the distinguished quadratic
combination under the stated second-order assumption. Lovelock branches still
require an effective-kinetic-sign and degeneracy audit around any proposed
vacuum.

Topology and variational well-posedness do not fix `kappa_k`. No coefficient
quantization is claimed without a normalized integral lattice and global
`exp(iS/hbar)` phase argument.

## Variational equations and boundary completion

For

```text
S_geom=(1/2) sum_k kappa_k integral_M dmu_G L_k,
T_AB=-2/sqrt|G| delta(S_sigma+S_matter)/delta G^AB,
```

the bulk metric family is

```text
sum_k kappa_k H_AB^(k) = T_AB,
H_AB^(0) = -(1/2)G_AB,
H_AB^(1) = R_AB-(1/2)R G_AB.
```

The higher `H_AB^(k)` are the Lovelock tensors. Each obeys
`nabla^A H_AB^(k)=0`; therefore covariant stress conservation follows on shell
when the complete matter equations and boundary flux balance hold. This is a
Lovelock equation, not automatically an Einstein equation.

For Dirichlet induced-metric data, each retained `L_k` requires its generalized
Lovelock–Myers boundary polynomial. For `L_1`, the common bulk factor gives

```text
S_B1=kappa_1 integral_boundary dmu_h epsilon_n K.
```

Its coefficient is locked to `kappa_1`. It cancels normal derivatives of the
metric variation and is not a surface tension. Similarly, `B_2` and `B_3` are
fixed by `kappa_2` and `kappa_3`; `B_4` is the Euler transgression. Any physical
surface energy requires a separate sourced boundary action and stress tensor.

## Physicality field and confinement source

For a dimensionless parent candidate `sigma`, use separate signature
conventions:

```text
S_sigma,L = integral sqrt(-G)[-1/2 Z_sigma (nabla sigma)^2-U_sigma]
S_sigma,E = integral sqrt(G)[+1/2 Z_sigma |grad sigma|^2+U_sigma]

U_sigma = 1/2 A(C_EG)sigma^2 + 1/4 G(C_EG)sigma^4 + O(sigma^6).
```

In eight dimensions, `[Z_sigma]=[A]L^-6` and, for dimensionless `sigma`,
`[A]=[G]=[A]L^-8`. The formation threshold is `A(C_EG,c)=0`. If `A>0`, the
zero branch is locally stable in the isolated sigma direction. If `A<0` and
`G>0`, the quartic truncation has
`sigma_vac^2=-A/G` and sigma-direction Hessian `-2A`. A physical branch still
requires the complete coupled Hessian, valid domain, conserved stress, and
boundary closure.

The stored `A_ST=-2`, `G_ST=8`, and `|sigma|=1/2` are a normalized v5.7 target
reduction. They are not parent coefficients. Recovering them requires an
explicit parent mode, measure, fiber pushforward, and coefficient map.

Candidate `C_EG` objects were audited: stress trace, stress square, normal
pressure jump, extrinsic confinement, collar strain, quasilocal enclosed
energy, current norm, and top-form flux. None is selected. Each needs some
combination of a parent matter action, interface, normal, time orientation,
dimensional conversion, or flux source.

Thus “energy envelops spacetime” has a minimum precise meaning: a conserved
sourced stress distribution, a selected closed interface, nonzero junction or
normal-stress data, and a stable coupled geometry–sigma solution. The phrase
alone is not a confinement invariant.

## Signature and time

P1–P3 accept both Riemannian and Lorentzian nondegenerate metric sectors; they
do not select between them.

- Riemannian B8 gives a gauge-fixed elliptic boundary-value problem and no
  physical timelike energy current.
- Lorentzian B8 gives hyperbolic evolution plus constraints after gauge fixing,
  with time orientation and boundary causal character still additional data.
- `R_t x B8` is nine-dimensional and requires a separate 8+1 formulation.
- `M3,1 x K` requires its dimension-specific product action and reduction.

A nonzero current can orient time only after a Lorentzian sector exists. It
does not create Lorentzian signature. No signature-changing branch is included:
that would require a degenerate-metric surface, matching rules, regularity, and
a separate action definition.

## Collar and nested Hopf structure

The minimal collar is a Gaussian-normal rewriting of the one bulk action:

```text
u=ell_c rho,
ds^2=epsilon_n du^2+h_ab(u,Y)dY^a dY^b,
K_ab=(1/2)partial_u h_ab,
J=sqrt(|det h_u|/|det h_0|),
partial_u log J=K.
```

This does not require an independent collar action. A new collar density is
allowed only if a separately sourced interface material or transition field is
derived. The physical `ell_c` remains missing, and no v5 collar term is promoted
to B8.

A non-double-counted nested metric uses the `4+2+1` split

```text
g_S7=L4^2 g_H4+L2^2 g_V2,cov+L1^2 eta^2.
```

Treating an entire three-dimensional fiber and its one-dimensional subfiber as
independent directions would double count. The compatible standard volume is
`pi^4 L4^4 L2^2 L1/3`. O’Neill reduction conditionally produces base and fiber
curvature, connection-curvature terms, and scale-modulus gradients. Exact
coefficients require a selected connection normalization and parent metric.
Neither Hopf route is selected by gauge-group analogy.

## Stationarity, scale, and stability

The general reduced architecture is

```text
S_red = sum_(k=0)^3 kappa_k L^(8-2k) F_k(r2,r1)
      + L^8 U_sigma(sigma,C_EG)
      + S_interface,
```

with distinct overall scale `L`, twistor ratio `r2`, U(1) ratio `r1`, sigma,
and collar ratio `ell_c/L`. Dimensionless ratios can be stabilized by the
functions `F_k`. An absolute scale requires competing weights and a dimensionful
coefficient ratio such as `kappa_1/kappa_0`; because those coefficients are
unsourced, this would import rather than derive a primitive.

The coupled stability matrix is the Hessian in
`(ln L,r2,r1,sigma,ell_c/L)`. It is defined symbolically but cannot be evaluated.
No stationary physical branch, zero-mode count, or negative-mode count is
claimed.

## Three thresholds and shared-core boundary

The mechanisms remain separate:

1. Physicality formation: the sigma/geometry Hessian loses stability at an
   effective `A=0`.
2. Primordial release: an already formed surface mode reaches
   `lambda_surface=0`.
3. Black-hole de-enveloping: an unknown throat/core/interface mode loses its
   enclosure.

No action equates these eigenvalues. A connected bulk, multiple throat
embeddings, or a shared global flux variable are topologically possible but
not selected. Regular matching and a conserved common source remain absent.

## Reduction and stop condition

The parent-to-v5 maps are identified but not proved. Berger S3 needs an
explicit fiber or independent-factor selection and a consistent truncation.
The scalar/topographic target requires normalized parent modes. The abstract
collar Jacobian is conditionally recovered, while gauge and fermion reductions
still require trace, spin, and vertical-mode data. Historical artifacts remain
unchanged.

The full closure sequence pauses before scalar localization. The exact next
mathematical question is the BHSM selection principle for `C_EG` and its
coupling to sigma. If pursued, the narrow branch is
`bhsm-energy-geometry-confinement-invariant-v6-0-3`.
