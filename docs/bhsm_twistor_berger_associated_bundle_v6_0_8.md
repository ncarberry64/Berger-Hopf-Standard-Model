# BHSM v6.0.8 Twistor-Mediated Berger Associated-Bundle Construction

## Constructive result

Primary result:

`BHSM_BERGER_COVARIANT_MULTIPLET_ARCHITECTURE_DERIVED`

Supporting results:

- `BHSM_TWISTOR_MEDIATED_BERGER_METRIC_DERIVED`;
- `BHSM_BERGER_COVARIANT_LINEAR_MULTIPLET_REDUCTION_DERIVED`;
- `BHSM_SO8_HOPF_SCALAR_BRANCHING_FORMULA_DERIVED`;
- `BHSM_GENERIC_NONLINEAR_FINITE_MULTIPLET_REQUIRES_TOWER`;
- `BHSM_TWISTOR_MEDIATED_REDUCTION_REQUIRES_ACTION_NORMALIZATION`.

The v6.0.7 characteristic-class theorem is retained exactly. It excludes a
section of `CP3 -> S4` and therefore excludes one fixed `U(1)` axis over
`S4`. It does not exclude the nested total-space construction. The positive
replacement uses both global fibrations

\[
 U(1)\longrightarrow S^7\stackrel{p_C}{\longrightarrow}CP^3,
 \qquad
 S^2\longrightarrow CP^3\stackrel{\tau}{\longrightarrow}S^4,
\]

with `p_H=tau o p_C`. No section of the twistor bundle is introduced.

## Global nested distributions

Fix the canonical complex-Hopf connection on `p_C` and the compatible
quaternionic-Hopf connection. Define

\[
 V_1=\ker(dp_C),
\]

the global circle-vertical line. Define

\[
 V_2=(\ker dp_C)^H\cap\ker(dp_H),
\]

equivalently the `p_C`-horizontal lift of `ker(d tau)`. Finally let `H4` be
the metric-horizontal complement of `V2 direct-sum V1`. Then

\[
 TS^7=H_4\oplus V_2\oplus V_1,
 \qquad 7=4+2+1.
\]

This is a direct sum: the circle direction is not counted again inside the
twistor two-plane. The pieces and their sums have different integrability
properties:

- `V1` integrates to the complex-Hopf circles;
- `V2` is not integrable alone, because its bracket has a `V1` component;
- `V2 direct-sum V1` integrates to the quaternionic-Hopf `S3` fibers;
- `H4` is generally nonintegrable, with vertical bracket measured by the
  `Sp(1)` connection curvature.

The orientation is fixed by

\[
 \operatorname{vol}_7=\operatorname{vol}_{H4}\wedge
 \operatorname{vol}_{V2}\wedge\eta.
\]

## Exact twistor reconstruction of each S3

For `x in S4`, let

\[
 S^2_x=\tau^{-1}(x),\qquad F_x=p_C^{-1}(S^2_x).
\]

The composition identity gives

\[
 F_x=p_C^{-1}(\tau^{-1}(x))
     =(\tau\circ p_C)^{-1}(x)
     =p_H^{-1}(x).
\]

Thus `F_x` is the quaternionic Hopf fiber, so

\[
 F_x\simeq Sp(1)\simeq S^3,
 \qquad
 S^1\longrightarrow F_x\longrightarrow S^2_x
\]

is the ordinary Hopf fibration. The construction retains all circle orbits in
every fiber rather than choosing one orbit as a preferred axis over `S4`.

## Global nested metric and symmetry

For positive constants `L4`, `L2`, and `L1`, define

\[
 g_7=L_4^2g_{H4}+L_2^2g_{V2}+L_1^2\eta^2.
\]

This is a global metric on total `S7`. Generically its invariance group is
`Sp(2) x U(1)_R`. The `U(1)_R` is the global circle action of
`S7 -> CP3`; it is not a principal `U(1)` reduction over `S4`. When
`L1=L2`, quaternionic vertical isotropy is restored and the canonical
variation has `Sp(2) x Sp(1)` symmetry. At the correctly normalized round
point the symmetry enhances to `SO(8)`.

On `F_x`, the restriction is

\[
 g_{F_x}=L_2^2g_{S^2_x}+L_1^2\eta^2
 =L_2^2(\sigma_1^2+\sigma_2^2)+L_1^2\sigma_3^2.
\]

Therefore the repository coefficient convention is recovered exactly with

\[
 r_{\rm base}=L_2,\qquad r_{\rm fiber}=L_1.
\]

This conclusion uses the complete nested fibration and does not require a
preferred adjoint axis field on `S4`.

## Berger harmonics and eigenspace bundles

Use the stored Maurer--Cartan convention

\[
 d\sigma_1=-\sigma_2\wedge\sigma_3
\]

cyclically. A scalar Berger harmonic is labeled by left spin `J` and the
commuting right-`U(1)` magnetic number `m`. With integral weight `q=2m`,

\[
 \lambda_{J,m}(L_1,L_2)=
 \frac{J(J+1)}{L_2^2}
 +m^2\left(\frac1{L_1^2}-\frac1{L_2^2}\right).
\]

At `L1=L2=L` this reduces to

\[
 \lambda_{J,m}=\frac{J(J+1)}{L^2}
 =\frac{n(n+2)}{4L^2},\qquad n=2J.
\]

For fixed `(J,m)`, the left index has dimension `2J+1`. The corresponding
fiberwise eigenspaces assemble into

\[
 \mathcal H_{J,m}=S^7\times_{\rho_J}V_J\longrightarrow S^4.
\]

Hence a parent scalar expands locally as

\[
 \Phi=\sum_{J,m,n}\phi^{J,m}_n(x)Y^J_{n,m}(y),
\]

but `phi^(J,m)` is a section of `mathcal H_(J,m)`, not an ordinary scalar
unless `J=0`. The right weight can also be described through complex-Hopf
line bundles over the intermediate `CP3`; regrouping the left multiplet gives
the natural `Sp(1)`-associated bundle over `S4`.

For a real parent field, the `m` and `-m` sectors are paired by Wigner charge
conjugation. This is a reality relation, not a particle/antiparticle claim.

## Transition law and covariant operator

On an overlap, write `s_b=s_a h_ab`. Then the fiber coordinates satisfy
`g_b=h_ab^-1 g_a`, the local bases rotate in `rho_J`, and the coefficient
column obeys the corresponding associated-bundle transition. The connection
transforms as

\[
 A_b=h_{ab}^{-1}A_a h_{ab}+h_{ab}^{-1}dh_{ab},
\]

and

\[
 D_A\phi=d\phi+\rho_{J*}(A)\phi,
 \qquad
 [D_\mu,D_\nu]\phi=\rho_{J*}(\Omega_{\mu\nu})\phi.
\]

Left `Sp(1)` transport commutes with the right `U(1)` symmetry, so `m` is
preserved by connection transport.

For the declared constant-scale connection metric with totally geodesic Hopf
fibers, the minimally coupled scalar operator on one multiplet is

\[
 \mathcal O_{J,m}=-D_A^*D_A+\lambda_{J,m}(L_1,L_2).
\]

An explicit parent mass or potential Hessian adds its own endomorphism. Forms,
spinors, nonminimal curvature couplings, and varying scale fields add
representation-specific Weitzenbock, curvature, and modulus terms. Those
terms are not set to zero by the scalar theorem.

## General round-S7 branching

The scalar harmonics of degree `ell` branch exactly as

\[
 \mathcal H^\ell(\mathbb R^8)\big|_{Sp(2)\times Sp(1)}
 =\bigoplus_{r=0}^{\lfloor\ell/2\rfloor}
 V^{Sp(2)}_{(\ell-2r,r)}\otimes
 V^{Sp(1)}_{\ell-2r}.
\]

For `Sp(2)` Dynkin labels `(a,b)`,

\[
 \dim V_{(a,b)}=
 \frac{(a+1)(b+1)(a+b+2)(a+2b+3)}6.
\]

The `Sp(1)` highest-weight-`n` representation branches to `U(1)` weights
`-n,-n+2,...,n`. Dimension identities have been checked through `ell=8` in
the artifact and are implemented for arbitrary nonnegative `ell`.

This extends the v6.0.7 checks rather than inferring particles. No existing
v5 `(k,j)` mode is mapped to an `SO(8)` representation without a normalized
intertwiner and operator match.

## Covariant closure and the nonlinear tower

Each fixed `(J,m)` multiplet closes exactly under the linear parent scalar
operator and connection transport. Nonlinear products obey Clebsch--Gordan
and weight-addition rules:

\[
 V_{J_1}\otimes V_{J_2}
 =\bigoplus_{J=|J_1-J_2|}^{J_1+J_2}V_J,
 \qquad m=m_1+m_2.
\]

Consequently a generic finite nontrivial set cannot be exactly closed under
arbitrary polynomial interactions: its highest retained spin produces a
higher channel. This exact sub-result selects constructive options rather
than stopping the reduction:

- retain the exact linear covariant multiplet theory;
- derive action-selected vanishing overlap tensors;
- integrate out a spectrally separated tower;
- use a controlled adiabatic/effective truncation;
- identify a symmetry-protected finite sector.

The standalone-scalar failure is therefore not generalized to a failure of
covariant multiplets.

## Parent action and v5 reinterpretation

For a provisional P1 parent with a minimally coupled scalar, a
physical-fiber-orthonormal basis gives the quadratic structure

\[
 S_2=\frac12\sum_{J,m}\int_{S^4}
 \left(\langle D\phi,D\phi\rangle
 +(M_{\rm parent}^2+\lambda_{J,m})\langle\phi,\phi\rangle\right)d\mu_4.
\]

Polynomial interactions are controlled by the exact overlap tensors

\[
 C_{a_1\ldots a_p}=\int_{F_x}
 Y_{a_1}\cdots Y_{a_p}\,d\mu_{F_x}.
\]

The P1 geometric sector structurally supplies base curvature, intrinsic
Berger curvature and squashing terms, connection-curvature terms, and modulus
terms. Their physical coefficients require the parent `kappa_1`, connection
trace, physical measure, reference-metric normalization, and stationary
metric. P2/P3 use the same multiplet architecture with additional curvature
contractions. No family is selected by v5 numerical matching.

The existing v5 Berger engine is now classified as exact for its declared
intrinsic fiber metric/operator calculations and as a local component model
for associated-bundle transport. Its legacy particle-sector, `(k,j)`,
dressing, and coefficient maps remain effective until the parent intertwiner
and action normalization are derived. No frozen ledger is changed.

## Gauge and scalar forward links

The `Sp(1)` Hopf connection transports the multiplets on `S4`; the complex
Hopf `U(1)` connection lives on `S7 -> CP3`. Their curvature and representation
actions form a geometric gauge precursor. A kinetic coefficient can arise
symbolically from the parent curvature reduction, but no Standard Model gauge
group, charge normalization, aperture, physical coupling, or fine-structure
constant is derived here.

The `(J,m)=(0,0)` sector is a genuine scalar singlet. It remains distinct from
the squashing modulus `L1/L2`, the fiber-volume modulus `L2^2 L1`, and any
physical boundary response. The existing topographic `sigma` has not yet been
identified uniquely with one of these objects. Recovering
`V_red=-sigma^2+2sigma^4` requires a parent field identification, canonical
normalization, Hessian, overlap tensor, modulus mixing, and physical measure;
the target coefficients are not inserted as inputs.

## Scale and next construction

The construction derives the dimensionless ratios

\[
 b=L_1/L_2,\qquad c=L_2/L_4,
\]

and representation/eigenvalue ratios. Under a common rescaling, eigenvalues
scale as length to the minus two and volumes with their dimensions. Thus the
common scale modulus is not lifted by the associated-bundle construction.

Completion gate:

`V6_0_8_CONTINUE_TO_TWISTOR_BERGER_ACTION_NORMALIZATION`

Recommended next branch:

`bhsm-twistor-berger-action-normalization-v6-0-9`

That sprint should normalize the P1 connection, moduli, physical fiber
measure, and overlap tensors, then test whether a spectral gap supports a
controlled tower integration. Frozen predictions and official prediction
logic remain unchanged.

## Mathematical cross-checks

The nested 3-Sasakian geometry was cross-checked against Boyer and Galicki,
[*3-Sasakian Manifolds*](https://arxiv.org/abs/hep-th/9810250). The homogeneous
Berger spectral normalization was checked against Lauret,
[*The smallest Laplace eigenvalue of homogeneous 3-spheres*](https://arxiv.org/abs/1801.04259),
which gives the full scalar spectrum for Berger spheres. The interpretation of
fiber Fourier/representation modes as associated-bundle sections and of the
horizontal operator as a connection operator was cross-checked against
[*Semiclassical analysis on principal bundles*](https://arxiv.org/abs/2405.14846).
These sources support the mathematical architecture; they are not evidence for
BHSM particle or physical-coupling claims.
