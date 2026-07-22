# BHSM v6.1 round-background gauge and scalar sector

## Scope and result

Primary result: `BHSM_ROUND_BACKGROUND_GAUGE_SCALAR_ACTION_DERIVED_CONDITIONALLY`.

This sprint reduces and canonically normalizes the bosonic connection and
declared scalar-singlet sectors on the exact round P1 Lorentzian trajectory
selected in v6.0.10.  The immediate reduced base is

\[
M_5=I_t\mathbin{\times}S^4,
\]

not a selected physical `3+1` spacetime.  The result is therefore a parent
M8-to-effective-M5 construction.  It supplies a precise input to a later
physical-boundary or further-reduction theorem; it does not supply a physical
dimensionless gauge coupling, a Standard Model identification, or a particle
map.

Subsidiary results are
`BHSM_ROUND_SP1_CONNECTION_NORMALIZATION_DERIVED`,
`BHSM_COMPLEX_HOPF_U1_NORMALIZATION_DERIVED_CONDITIONALLY`,
`BHSM_EFFECTIVE_BASE_DIMENSION_5D_CONFIRMED`, and
`BHSM_SIGMA_PARENT_FIELD_SELECTED_POTENTIAL_OPEN`.

## Exact round background and control test

Put \(\lambda=\kappa _0/\kappa _1>0\) and
\(x=\sqrt{\lambda/42}(t-t_0)\).  The preserved solution is

\[
a(t)=\sqrt{\frac{21}{2\lambda}}\cosh x,
\qquad
a_{\min}^2=\frac{21}{2\lambda},
\qquad H(t_0)=0.
\]

The lowest nonzero round-fiber scalar eigenvalue is

\[
\Delta(t)=\frac{3}{4a(t)^2}
          =\frac{\lambda}{14}\operatorname{sech}^2x.
\]

The geometric pieces of the requested control parameter are exact:

\[
\frac{H^2}{\Delta}=\frac{\sinh^2x}{3},\qquad
\frac{|\dot\Delta|}{\Delta^{3/2}}
 =\frac{2|\sinh x|}{\sqrt3},\qquad
\frac{|\dot H|}{\Delta}=\frac13.
\]

Consequently, the full requested parameter has the irreducible floor
\(\epsilon_{\rm control}\ge 1/3\).  There is no interval satisfying a
parametric requirement \(\epsilon_\star\ll1\).  The slice \(t=t_0\) is an
exact instantaneous normalization surface, not a static universe.  A wider
interval defined with \(\epsilon_\star\ge1/3\) is only a diagnostic finite-gap
window, and source, energy, and interaction-amplitude bounds remain separate
assumptions.  No global controlled-tower claim follows.

## Round geometric connection

With the frozen coframe, trace, and physical-pushforward conventions,

\[
K_{ab}=K_R\delta_{ab},\qquad
K_R=8\pi^2\kappa_1a^5,
\qquad
A_{\rm can}^a=\sqrt{K_R}A^a.
\]

For \([\kappa_1]=L^{-6}\), the M5 dimensions are
\([K_R]=L^{-1}\), \([A_{\rm can}]=L^{-3/2}\), and

\[
g_{5,{\rm geom}}=K_R^{-1/2},\qquad [g_{5,{\rm geom}}]=L^{1/2}.
\]

Writing \(F=dA+A\wedge A\), canonical normalization gives the same
\(g_{5,{\rm geom}}\) in the cubic vertex and
\(g_{5,{\rm geom}}^2\) in the quartic vertex.  Thus the algebraic gauge
identity and Bianchi identity survive the field redefinition.  Because
\(K_R\propto a^5\), the canonical field also carries the pump term
\(-5H A_{\rm can}/2\).  This time dependence is background evolution, not
renormalization-group running.  Gauge zero modes and constrained longitudinal
modes are not physical polarizations.

The normalized algebra is geometrically `Sp(1)` (and hence algebraically
isomorphic to `SU(2)`).  No physical Standard Model group identification is
made.

## Nested complex-Hopf U(1) and charges

The circle in `S1 -> S7 -> CP3` is the nested `V1` direction.  Before the
twistor-two-sphere pushforward its coefficient is
\(2\pi\kappa_1a^3\).  The complete S3 pushforward gives the inherited M5
coefficient \(K_R\).  It is a constrained component of the same geometric
connection, not an additional independent M5 field.

In the inherited four-periodic subgroup convention,
\(K_{U(1)}/K_{Sp(1)}=1\).  For a standard two-periodic unit-charge field
\(B=A/2\), \(K_{U(1)}=4K_R\) and
\(g_{U(1)}/g_{Sp(1)}=1/2\).  The ratio is scale independent but depends on
the embedding and generator convention.  It is not frozen as a physical
mixing candidate and is not a hypercharge result.

For the geometric representation \(J\), the associated bundle has rank
\(2J+1\), Casimir \(J(J+1)\), and weights \(m=-J,\ldots,J\).  With integral
weight \(q=2m\), the standard-circle canonical coefficient is
\(qg_{5,{\rm geom}}/2\).  These are canonical geometric charge operators,
not observed electric or weak charges.  Conjugation sends \(q\) to \(-q\)
and preserves the full reality-paired spectrum.

## Scalar normalization and potential audit

The frozen provisional parent action contains a dimensionless, neutral,
Z2-even bulk singlet variable \(\sigma\).  Its M5 kinetic coefficient and
canonical field are

\[
Z_5=16\pi^2Z_\sigma a^3,
\qquad s_5=\sqrt{Z_5}\,\sigma,
\qquad [s_5]=L^{-3/2}.
\]

The raw sigma equation has friction \(7H\); the canonical M5 equation has
friction \(4H\).  At \(t_0\), the time-dependent field redefinition adds the
operator mass \(-\lambda/28\).  If

\[
A_{\rm eff}=A_0+Z_\chi g(\nabla\chi)^2,
\]

then the canonical t0 quadratic coefficient is
\(A_{\rm eff}/Z_\sigma-\lambda/28\), while the canonical M5 quartic is
\(G_0/(16\pi^2 Z_\sigma^2a^3)\).  The selected vacuum chi branch makes the
displayed chi-gradient contribution zero.  The stationary points are
\(\sigma=0\), plus
\(\sigma=\pm\sqrt{-A_{\rm eff}/G_0}\) only when
\(A_{\rm eff}<0\) and \(G_0>0\).  The parent action does not select those
signs.

The associated singlet is the best available parent representative of the
v5 sigma field because its domain, neutrality, parity, and kinetic structure
match.  Its v5 boundary/topographic map, coefficient origin, vacuum, physical
M4 normalization, and stability are not derived.  The result is therefore
`BHSM_SIGMA_PARENT_FIELD_SELECTED_POTENTIAL_OPEN`, not a Higgs identification.
The choice is not based on rescaling sigma to `1/2`, and the v5 values
`A_ST=-2` and `G_ST=8` are not used as parent inputs.

After lapse, time-gauge, and Hamiltonian-constrained volume directions are
removed, the t0 homogeneous scalar/shape Hessian at \(\sigma=0\) is diagonal:

\[
\left\{
A_0/Z_\sigma-\lambda/28,
\;8\lambda/21,
\;8\lambda/21
\right\}.
\]

Z2 symmetry makes the sigma-shape cross terms vanish at that point.  The
shape block is positive; sigma stability remains conditional on an unsourced
coefficient inequality.  No phase transition follows without the full stable
potential.

## Tower and gauge-scalar terms

A local polynomial of the pure fiber singlet stays in \(J=0\), so it has no
tree-level source for a nontrivial heavy representation.  For a more general
retained multiplet, elimination of a controlled heavy mode has the formal
term

\[
-\frac12\langle J_H,{\cal O}_H^{-1}J_H\rangle,
\]

with spectral denominators, overlap tensors, derivative expansion, and a
nonlocal remainder.  Its sign is not universal, and the strict requested
control interval does not exist because of the one-third floor.

The exact modulus dependence produces

\[
K_R(ae^{\delta\rho})=K_R(a)
\left(1+5\delta\rho+\frac{25}{2}\delta\rho^2+\cdots\right),
\]

and hence geometric modulus-`F^2` vertices.  Nontrivial associated scalars
couple through their covariant derivatives.  The frozen P1 action contains no
sigma-`F^2` term.  A neutral sigma background neither reduces `Sp(1)` to
`U(1)` nor gives the connection a mass, so no electroweak-breaking statement
is available.

## Aperture, M4, spectrum, and spinorial boundary-operator forward link

The connection and matter normalizations needed for an aperture calculation
are explicit, but the physical domain `C`, measure, projector, mode profile,
and M5-to-M4 map are not.  Therefore neither the overlap nor
\(g_{\rm geom}^2|I_R|^2/N_A\) is a physical dimensionless coupling, and no
alpha value is produced.

The M5 coefficient has dimension \(L^{1/2}\).  A formula such as
\(g_4^2=g_5^2/L_{\rm eff}\) is valid only after a normalized boundary,
collar, localization, or interval profile derives \(L_{\rm eff}\).  No such
length is invented here.  This is
`BHSM_PHYSICAL_3P1_REDUCTION_REMAINS_REQUIRED`.

At t0 the round S3 scalar spectrum is

\[
\lambda_J=\frac{J(J+1)}{a_{\min}^2}
          =\frac{2\lambda J(J+1)}{21},
\]

with weights \(q=-2J,-2J+2,\ldots,2J\), associated rank \(2J+1\), and total
round degeneracy \((2J+1)^2\).  The first gap is \(\lambda/14\).  No mode is
assigned to a particle.  A later BHSM-native fermionic action sprint still
requires a physical M4 domain, boundary conditions, chirality mechanism,
parent spinor representation, fermion normalization, Yukawa or
geometric-mass source, and particle map.

## Permanent fermionic/Clifford and no-monopole firewall

BHSM does not assume a physical fermion equation as a foundational parent
law.  Clifford algebras, spin structures, spin connections, and first-order
geometric operators are mathematical constructions.  They may be used only
with a specified domain and an identified BHSM action source, and they are not
promoted automatically to the physical Dirac equation.

BHSM contains no physical magnetic-monopole sector.  Dirac strings, monopole
harmonic mode bases, magnetic-charge sectors, magnetic-charge quantization,
monopole-induced chirality, and monopole-generated generations are excluded.
Hopf winding, principal U1 bundles, first Chern classes, transition functions,
and connection curvature remain geometric bundle data.  They carry no
physical magnetic interpretation without a separately derived magnetic field,
asymptotic charge definition, and physical source theorem.

This permanent doctrine is
`BHSM_FERMIONIC_CLIFFORD_AND_NO_MONOPOLE_FIREWALL_FROZEN`.

## Scale, primitives, and stop condition

The scale remains fixed only in terms of the primitive ratio
\(a_{\min}^2=21\kappa_1/(2\kappa_0)\).  The seven raw coefficients of the
frozen provisional parent theory reduce by field-normalization conventions to
five invariant combinations, but no primitive value or absolute unit is
generated.

Completion gate:
`V6_1_M5_BOSONIC_NORMALIZATION_DERIVED_M4_REDUCTION_REQUIRED`.

Recommended next branch:
`bhsm-parent-m5-to-physical-boundary-m4-reduction-v6-1-1`.

The frozen predictions and official prediction logic are unchanged.
`FULL_BHSM_NOT_COMPLETE`.
