# BHSM v6.0.7 B8/S7-to-Berger-S3 Reduction Theorem

## Mathematical theorem and constructive architecture

Primary result:

`BHSM_B8_S7_TO_BERGER_S3_REDUCTION_OBSTRUCTED`

Subsidiary results:

- `BHSM_SP1_TO_U1_REDUCTION_TOPOLOGICALLY_OBSTRUCTED`;
- `BHSM_BERGER_MODE_ASSOCIATED_BUNDLE_MAP_DERIVED`;
- `BHSM_BERGER_CONSISTENT_TRUNCATION_FAILED` for the existing standalone
  scalar-mode interpretation.

Program architecture results:

- `BHSM_TWISTOR_MEDIATED_BERGER_ROUTE_SELECTED`;
- `BHSM_BERGER_ASSOCIATED_BUNDLE_FORMULATION_REQUIRED`;
- `BHSM_DIRECT_FIXED_AXIS_REDUCTION_EXCLUDED`.

The exact obstruction concerns a direct global fixed-axis scalar reduction
over `S4`. It does not obstruct Berger geometry, the nested Hopf structure,
the use of each `S3` fiber, or the twistor-mediated route.

The complete family of `U(1)` directions is encoded globally by
`S2 -> CP3 -> S4`, while `S1 -> S7 -> CP3` supplies the global circle bundle.
Together they retain the full `S1`-over-`S2` structure of every quaternionic
`S3` fiber without choosing a section of `CP3 -> S4`. This selects the nested
twistor architecture and associated-bundle fields as the constructive route.

## Topological conventions

Use the exact nested diagram

\[
 Sp(1)\longrightarrow S^7\stackrel{p_H}{\longrightarrow}S^4,
 \qquad
 U(1)\longrightarrow S^7\stackrel{p_C}{\longrightarrow}CP^3,
 \qquad
 S^2\longrightarrow CP^3\stackrel{\tau}{\longrightarrow}S^4,
\]

with `p_H=tau o p_C`. The quaternionic bundle has instanton number and
second Chern class `c2=+1` in the declared orientation. Reversing orientation
changes the sign but not the obstruction.

The principal connection is a global `sp(1)`-valued one-form `omega` with

\[
 R_g^*\omega=\operatorname{Ad}(g^{-1})\omega,
 \qquad
 \Omega=d\omega+\tfrac12[\omega,\omega].
\]

Individual components `eta_i` are meaningful only in a declared Lie-algebra
frame or local gauge. Local connection pullbacks obey the inhomogeneous
transition law and cannot be identified between charts without it.

## Global 4+2+1 metric

The proposed tensor is

\[
 g_7=L_4^2g_H+L_2^2(\eta_1^2+\eta_2^2)+L_1^2\eta_3^2.
\]

The ranks are exactly `4+2+1=7`: the vertical rank-three distribution is the
direct sum of a selected two-plane and line. No direction is double counted.

A fixed subgroup `U(1) subset Sp(1)` defines global orbit and complementary
distributions on total `S7`, so the tensor can be written globally on the
total space after that extra choice. For `L1 != L2`, however, its vertical
quadratic form is not `Ad(Sp(1))` invariant. It is invariant only under the
Hopf-preserving subgroup and does not define a gauge-independent metric on the
adjoint bundle over `S4`. The round case `L1=L2` restores the full vertical
invariance.

Thus “globally defined on total space after a fixed subgroup choice” and
“globally selected reduction of the principal bundle over the base” are
different statements.

## Sp(1)-to-U(1) obstruction theorem

A principal `U(1)` reduction is equivalent to each of:

- a `U(1)` subbundle of the principal `Sp(1)` bundle;
- a section of `P/U(1)=P x_Ad S2`;
- a unit adjoint direction;
- a splitting `ad(P)=R n direct-sum n-perp`;
- a globally preferred imaginary-quaternion axis.

Let `E=P x_Sp(1) C2` be the associated rank-two complex bundle. A reduction
would split it as

\[
 E=L\oplus L^{-1},
 \qquad c_2(E)=-c_1(L)^2.
\]

But `H^2(S4;Z)=0`, so every complex line bundle on `S4` has `c1(L)=0`.
The reduction would therefore imply `c2(E)=0`, contradicting the Hopf bundle
value `c2(E)=1`.

Consequently there is no global preferred `U(1)` direction. The twistor space
`CP3=P/U(1)` is the associated `S2` bundle itself, not a section of that
bundle. A nowhere-zero adjoint order parameter would be precisely the
forbidden section; it must contain zeros/defects or change the topology.

## Intrinsic Berger fiber

On a locally framed fiber `F_x=p_H^{-1}(x)` the restriction is exactly

\[
 g_F=L_2^2(\sigma_1^2+\sigma_2^2)+L_1^2\sigma_3^2.
\]

This matches the stored repository coefficient form under
`r_base=L2`, `r_fiber=L1`. For the stored Maurer--Cartan convention

\[
 d\sigma_1=-\sigma_2\wedge\sigma_3
\]

cyclically, and full `SU(2)` Euler ranges, the oriented volume is

\[
 \operatorname{Vol}(F)=16\pi^2L_2^2L_1.
\]

The orthonormal Ricci eigenvalues are

\[
 \left(
 \frac1{L_2^2}-\frac{L_1^2}{2L_2^4},
 \frac1{L_2^2}-\frac{L_1^2}{2L_2^4},
 \frac{L_1^2}{2L_2^4}
 \right),
\]

and

\[
 R_F=\frac2{L_2^2}-\frac{L_1^2}{2L_2^4}.
\]

At `L1=L2=R/2`, these give `Ric=2/R^2` and `R_F=6/R^2`, the round
three-sphere result. Zero scale limits are degenerate and lie outside the
positive Berger domain.

This is an intrinsic/local fiber theorem. It does not select a global axis,
physical normalization, or consistent lower-dimensional theory.

## Local versus global classification

Horizontal `Sp(1)` holonomy rotates the anisotropy axis. Therefore the
nonround fibers form a gauge-dependent associated family rather than one
bundle-natural fixed Berger geometry over `S4`. Only the round fiber metric is
canonical without extra structure.

The existing engine is consequently classified as an independent homogeneous
effective model, local gauge-fixed diagnostic, or future associated-bundle
sector. It is not parent-derived.

## Measure and Hodge reduction

For orientation

\[
 \operatorname{vol}_7=\operatorname{vol}_{H4}\wedge
 \eta_1\wedge\eta_2\wedge\eta_3,
\]

the local volume form has Jacobian

\[
 L_4^4L_2^2L_1.
\]

Physical fiber integration contains `Vol(F)`. Normalized averaging divides by
that volume and is a different operation. Restriction to one fiber is also
different from the orientation-defined pushforward `(p_H)_*`.

For horizontal degree `p` and vertical degree `q`, the pointwise product
Hodge formula is

\[
 *_7(\alpha_p\wedge\beta_q)=
 (-1)^{q(4-p)}(*_H\alpha_p)\wedge(*_V\beta_q).
\]

In the unscaled coframe the horizontal factor is `L4^(4-2p)`. For
`beta=eta_I`, the vertical factor is

\[
 \frac{L_2^2L_1}{\prod_{i\in I}L_i^2},
 \qquad (L_1^{\rm coframe},L_2^{\rm coframe},L_3^{\rm coframe})
 =(L_2,L_2,L_1).
\]

This recovers the stored vertical Berger coefficient pattern. The parent and
legacy physical measure normalizations remain unmatched.

## Operators and mode globalization

The exterior derivative is a connection-adapted bicomplex containing
vertical, horizontal covariant, and curvature-insertion pieces. Therefore

\[
 \Delta_7\ne\Delta_{S4}+\Delta_{S3}
\]

as a universal identity. The scalar, Hodge, connection, curl, and Dirac
operators contain connection, O'Neill, spin-connection, representation, and
possibly mean-curvature corrections.

If a local vertical harmonic transforms in representation `R`, then local
coefficients obey the inverse transition law. A trivial representation gives
a scalar zero mode. A nontrivial representation gives a section of

\[
 E_R=P\times_R V_R\longrightarrow S^4,
\]

not a global scalar coefficient. The contracted equivariant total-space field
may still be global. This associated-bundle globalization theorem is exact.

## Consistent truncation

A consistent truncation must make every discarded-mode equation vanish for
every reduced solution. The existing standalone scalar-mode engine fails this
gate. Its retained modes generically source:

- connection and base-covariant fields;
- stress and squashing backreaction;
- nonlinear harmonic products;
- discarded representations;
- metric and modulus modes.

The topological `U(1)` gate, measure normalization, operator intertwiner,
general branching, action reduction, and coefficient sources also fail. A
future associated-bundle effective approximation remains open; “mode
restriction” is not promoted to “consistent truncation.”

## Representation branching

The exact low levels of the round-S7 scalar representation give the checks

| ell | SO(8) | Sp(2) x Sp(1) | Dimensions |
|---:|---|---|---:|
| 0 | `[0,0,0,0]` | `(1,1)` | 1 |
| 1 | `[1,0,0,0]` | `(4,2)` | 8 |
| 2 | `[2,0,0,0]` | `(10,3) + (5,1)` | 30+5=35 |

With the declared `U(1)` normalization, the doublet has weights `-1,+1` and
the triplet `-2,0,+2`. General branching, reality conventions, normalized
intertwiners, and the map to legacy `(k,j)` labels remain open. Eigenvalue or
dimension coincidence alone is not a map.

## Existing ledgers and action sectors

The frozen lepton, up, down, heavy, charged-current, neutral, and
scalar/topographic ledgers are unchanged. Their `(k,j)`, `q=k-2j`, incidence,
and projector labels remain effective notation until both representation and
operator maps close.

Scalar reduction gives associated-bundle covariant kinetic terms, vertical
eigenvalue matrices, fiber-volume factors, and quartic overlaps. It does not
derive `A_ST=-2`, `G_ST=8`, or `|sigma|=1/2`.

The nested connection supplies a future gauge-reduction architecture but no
Standard Model gauge fields, gauge normalization, geometric aperture, or
fine-structure constant. The formal Dirac split is structurally compatible
with a twisted horizontal operator plus Berger vertical operator and
connection corrections; no fermion spectrum, masses, or generations follow.

For P1, P2, and P3, physical fiber integration structurally produces base and
fiber curvature, squashing potentials, connection terms, moduli, and volume
terms, with the corresponding boundary completions only after a physical
boundary is selected. No Lovelock family is selected by v5 matching.

## Boundary firewall

A Hopf fiber is a closed codimension-four internal orbit. Its normal bundle in
`S7` is horizontal rank four, not a single outward normal. This object is not:

- the normal to `S7` as a possible boundary of `B8`;
- a Lorentzian spacetime interface normal;
- a collar coordinate;
- the v5 physical boundary.

Intrinsic fiber geometry and B8 boundary geometry remain separate.

## Coefficients and scale

Every candidate reduced coefficient retains explicit dependence on parent
`kappa_k`, radii, physical fiber volume, connection normalization,
representation traces, mode normalizations, and overlap tensors. No v5 number
appears on the parent side.

The ratios `b=L1/L2`, `L2/L4`, and `L1/L4` are dimensionless but not selected
by a stationarity theorem. Under a common rescaling all ratios remain fixed,
while curvatures and eigenvalues scale as `lambda^-2` and volumes with their
dimensions. The common modulus and absolute unit remain open.

## Route condition

Completion gate:

`V6_0_7_DIRECT_FIXED_AXIS_ROUTE_STOPS_ASSOCIATED_BUNDLE_ROUTE_CONTINUES`

Recommended next branch:

`bhsm-twistor-mediated-berger-associated-bundle-v6-0-8`

No measured input, frozen-output change, particle derivation, gauge-coupling
derivation, absolute-scale generation, or full-BHSM claim is made.
