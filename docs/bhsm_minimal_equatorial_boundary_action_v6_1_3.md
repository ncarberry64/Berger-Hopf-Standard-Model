# BHSM v6.1.3 minimal equatorial boundary action freeze

## Result and scope

Primary result:
`BHSM_MINIMAL_EQUATORIAL_BOUNDARY_ACTION_REQUIRES_MULTIPLE_PRIMITIVES`.

Boundary Axiom B1 consistently defines independent intrinsic metric,
connection, and neutral-scalar fields on the Lorentz-selected equatorial
domain. Their frozen Einstein--Hilbert, Yang--Mills, and free-scalar action has
exact M4 Lorentz principal symbols and healthy principal kinetic signs when
its three raw coefficients are positive.

The sprint does not derive B1 or its coefficients from P1. The proposed
one-normalization coefficient lock is underdetermined. Before a scalar
potential or scalar matching is introduced, canonical field redefinitions
leave two physical invariant combinations: the intrinsic gravitational
strength relative to the parent scale and the non-Abelian connection
self-interaction. The free scalar normalization is then a field convention.
All three raw coefficients still require independent action sources, and the
scalar normalization becomes physical again when a potential or matching
source is added.

The intrinsic Einstein term also changes the junction equation. The previous
smooth `K_mu_nu=0` round equator has nonzero intrinsic Einstein tensor and is
therefore not an exact solution for positive `C_partial` without a shifted
embedding, compensating action-derived stress, or modified parent solution.
The complete mixed stability spectrum remains open until that background is
derived.

## Preserved v6.1.2 theorem

For nonnegative scalar or principal-tensor profile density,

\[
 N_s-N_t=a\int\sin\chi\cos^2\chi\,w(\chi)d\chi\ge0.
\]

For a finite admissible tangential connection profile,

\[
 N_B-N_E=a\int\frac{\cos^2\chi}{\sin\chi}|u_A|^2d\chi\ge0.
\]

Finite nonzero equality excludes the collapsed poles and selects the `SO(5)`
orbit of equatorial great `S3` hypersurfaces. It neither selects a unique
parent axis nor creates a physical brane automatically. The finite-width
diagnostic mismatches remain `1/(p+2)` for scalar/principal tensor and `1/p`
for connection.

## Boundary Axiom B1

`BHSM_BOUNDARY_AXIOM_B1_PROVISIONAL_FROZEN`:

- The domain is `M4=I_t x S3`, represented by one member of the
  Lorentz-selected equatorial orbit.
- `h_mu_nu` is an intrinsic boundary metric.
- `A_mu` is an intrinsic boundary connection carrying inherited geometric
  representation and transition data.
- `sigma_partial` is an intrinsic real neutral scalar with a Z2-even action.
- Bulk and boundary fields are distinct variables unless an explicit
  constraint identifies them.
- The physical M4 kinetic terms are intrinsic; smooth bulk zero-mode kinetic
  contributions are not silently added.

B1 is a provisional boundary axiom. It is not derived from P1, GHY, Z2
parity, the round collar, sigma, P2/P3, or classical heavy-mode elimination.

## Trace-field versus intrinsic-field theorem

If a boundary field is merely the trace of a smooth bulk mode, an intrinsic
Lorentz-symmetric scalar kinetic coefficient adds equally to both weights:

\[
 (N_s+Z_\partial)-(N_t+Z_\partial)=N_s-N_t.
\]

Likewise,

\[
 (N_B+\tau_A)-(N_E+\tau_A)=N_B-N_E
\]

for the connection, with the analogous principal tensor identity. A finite
common coefficient can make the ratio closer to one but cannot cancel a
nonzero difference. Thus

`BHSM_SMOOTH_TRACE_FIELD_FINITE_BOUNDARY_TERM_CANNOT_CLOSE_EXACT_LORENTZ`

and, within this additive action structure,

`BHSM_INTRINSIC_BOUNDARY_FIELD_FORMULATION_REQUIRED_FOR_EXACT_M4_LORENTZ`.

Independent intrinsic fields have no bulk profile contribution in their
physical kinetic normalization. Their Lorentz structure is fixed entirely by
the induced M4 metric.

## Frozen action

The action is frozen before its kill tests as

\[
 S_\partial=\int_{M_4}\sqrt{-h}\left[
 C_\partial R_4-
 \frac{\tau_A}{4}\operatorname{Tr}(F_{\mu\nu}F^{\mu\nu})-
 \frac{Z_\partial}{2}(\partial\sigma_\partial)^2-
 U_\partial(\sigma_\partial)\right]+S_{\rm match}.
\]

The primary kill test sets `U_partial=0`, because the parent bulk polynomial
does not automatically become a potential for an independent boundary
scalar. The sign domain is

\[
 C_\partial>0,\qquad \tau_A>0,\qquad Z_\partial>0.
\]

No higher derivatives, `sigma F^2`, `sigma R`, connection mass, symmetry
breaking term, boundary fluid, monopole sector, or physical fermion action is
added after the freeze.

## Exact matching architecture

Only the metric is exactly matched:

\[
 S_{\rm match}=\int_{M_4}\sqrt{-h}\,
 \Lambda^{\mu\nu}(h_{\mu\nu}-\iota^*g_{\mu\nu}).
\]

`Lambda^{mu nu}` is a nondynamical symmetric boundary tensor of dimension
`L^-4`. Its equation imposes `h=iota^*g`; its normalization is a multiplier
convention, not a tunable penalty or physical primitive. Eliminating it
between the intrinsic metric equation and bulk boundary equation produces the
junction condition.

`A_mu` is not set equal to the bulk connection trace. It inherits only the
parent bundle representation and transition law. `sigma_partial` is not set
equal to the bulk singlet. These choices preserve B1 and avoid restoring the
smooth-trace mismatch.

The formal variational system is not overconstrained: the metric constraint,
intrinsic metric equation, and junction equation determine the multiplier and
compatible boundary data. Existence of a compatible shifted background is a
separate open equation, not an assumed result.

## One-normalization lock test

The tested ansatz is

\[
 C_\partial=\beta_\partial\frac{c_g}{a_{\min}^2},\qquad
 \tau_A=\beta_\partial c_A,\qquad
 Z_\partial=\beta_\partial\frac{c_\sigma}{a_{\min}^2},
\]

with

\[
 a_{\min}^2=\frac{21\kappa_1}{2\kappa_0}.
\]

Dimensional analysis fixes the powers of `a_min`, but it does not determine
`c_g:c_A:c_sigma`. Covariance fixes the allowed operator forms. A
representation trace fixes the connection normalization only after a
generator convention is selected; it supplies no theorem relating gauge,
gravity, and neutral-scalar kinetic operators. A common integration measure
also does not equate their coefficients.

No spectral action, physical Dirac operator, or measured coupling is used.
The result is

`BHSM_BOUNDARY_ONE_NORMALIZATION_HYPOTHESIS_UNDERDETERMINED`.

## Physical invariant count

The raw action contains `C_partial`, `tau_A`, and `Z_partial`.

- Because `h` is constrained to the induced metric, a metric rescaling cannot
  remove `C_partial a_min^2` without changing the parent matching.
- With `Tr(T_aT_b)=I_R delta_ab`, canonical connection normalization leaves
  the invariant self-interaction
  `g_partial=(tau_A I_R)^(-1/2)`.
- With `U_partial=0`, neutral `sigma_partial`, and no scalar matching source,
  `s_partial=sqrt(Z_partial)sigma_partial` removes `Z_partial` completely.

There are therefore two physical invariant combinations before a scalar
potential or scalar matching is introduced. If either is later derived,
canonical scalar masses or couplings depend on `Z_partial`, and a third
independently sourced combination returns. This distinction prevents a field
normalization convention from being advertised as a prediction.

## Intrinsic gravity

The ADM form is

\[
 S_{g,\partial}=C_\partial\int N\sqrt q
 \left({}^{(3)}R+K_{ij}K^{ij}-K^2\right)
\]

up to the usual temporal endpoint completion. Lapse and shift impose the
Hamiltonian and momentum constraints. For transverse-traceless perturbations,
the principal quadratic action is

\[
 S_{TT}^{(2)}=\frac{C_\partial}{4}\int a^3
 \left[\dot\gamma_{ij}^{TT}\dot\gamma^{ij}_{TT}
 -a^{-2}(\nabla\gamma_{ij}^{TT})^2+\cdots\right].
\]

There are two physical tensor polarizations, positive principal kinetic and
gradient terms for `C_partial>0`, and `c_T^2=1`. This coefficient is not
identified with the observed Planck mass.

## Intrinsic connection

Let `Tr(T_aT_b)=I_R delta_ab`. Then

\[
 A_{\rm can}^a=\sqrt{\tau_A I_R}\,A^a,
 \qquad
 g_\partial=(\tau_A I_R)^{-1/2}.
\]

The cubic coefficient is `g_partial f_abc`; the quartic coefficient is
`g_partial^2` times the corresponding paired structure constants. The
relative coefficients satisfy the Yang--Mills gauge identity. Gauss law is a
constraint, and the gauge-fixed transverse principal operator is hyperbolic.

The nested U1 remains constrained component/weight data inside the retained
connection architecture. It is not added as a fourth independent boundary
field and is not identified with hypercharge, electromagnetism, or magnetic
charge.

## Intrinsic scalar and potential audit

The canonical scalar is

\[
 s_\partial=\sqrt{Z_\partial}\,\sigma_\partial,
\]

with four-dimensional canonical dimension `L^-1`. For the free primary test,

\[
 \Box_hs_\partial=0,
 \qquad
 \ddot s_\partial+3H\dot s_\partial=0
\]

for the homogeneous mode. Spatial harmonics on `S3_a` have eigenvalues
`l(l+2)/a^2`. The `l=0` mode is flat rather than tachyonic.

The bulk `A0` and `G0` polynomial acts on the bulk scalar trace. It is not
automatically inherited by independent `sigma_partial`. Exact scalar-value
matching would undo B1, and no nonminimal curvature or local bulk-elimination
source is present. Thus

`BHSM_BOUNDARY_SIGMA_KINETIC_ACTION_DERIVED_POTENTIAL_OPEN`.

`A_ST=-2`, `G_ST=8`, and `|sigma|=1/2` are neither inputs nor outputs.

## Combined variation and backreaction

The total action is

\[
 S_{\rm total}=S_{M5,\rm bulk}+S_{\rm GHY}+S_\partial+S_{\rm match}.
\]

In the declared one-side orientation convention, eliminating the matching
multiplier gives

\[
 2C_5(K_{\mu\nu}-Kh_{\mu\nu})
 +2C_\partial G_{\mu\nu}
 =T^{A}_{\mu\nu}+T^\sigma_{\mu\nu}.
\]

Boundary gauge and scalar equations are

\[
 \tau_A D_\nu F^{\nu\mu}=J_{\rm match}^\mu,
 \qquad
 Z_\partial\Box_h\sigma_\partial-U_\partial'=J_{\sigma,\rm match}.
\]

Both matching sources vanish in the minimal freeze. Diffeomorphism and gauge
identities give conditional conservation when all bulk, boundary, and
matching equations hold.

For vacuum boundary fields, `T_A=T_sigma=0`. On the old equator `K_mu_nu=0`,
while

\[
 G_{00}=3(H^2+a^{-2})>0
\]

at finite `a`. The junction residual is `2C_partial G_mu_nu`; hence the old
round trajectory is not an exact solution for positive `C_partial`. A shifted
embedding, compensating action-derived stress, or modified parent solution is
required. Backreaction is not discarded to preserve the desired background.

## Lorentz, hyperbolicity, and stability

All intrinsic sectors have one common temporal/spatial coefficient and unit
principal propagation speed. After constraint and gauge reduction:

- two tensor modes have healthy principal kinetics for `C_partial>0`;
- transverse connection modes have healthy principal kinetics for
  `tau_A I_R>0`;
- the massless neutral scalar has healthy principal kinetics for
  `Z_partial>0`;
- `Lambda` has no derivatives and no propagating degree of freedom.

The full physical spectrum is not closed because it must be expanded about
the unknown shifted junction background and include bulk-boundary mixing and
junction stability. No constrained negative direction is called a ghost or
physical tachyon.

## Boundary, currents, aperture, and fermionic readiness

B1 plus the frozen action supports a conditional intrinsic dynamical boundary
interpretation:

`BHSM_EQUATORIAL_M4_INTRINSIC_BOUNDARY_DOMAIN_DERIVED_CONDITIONALLY`.

It remains a boundary-axiom result, not a parent-action derivation.

The canonical connection interaction is `g_partial`; the neutral scalar
current is zero. Geometric representation weights are not observed charges.
The aperture remains incomplete because normalized boundary matter,
representation projector, and overlap data are absent. `e_eff` and `alpha`
are not evaluated.

The M4 spin structure, Clifford bundle, orthonormal frame, spin connection,
and associated representation data provide
`BHSM_M4_FIRST_ORDER_FERMIONIC_ACTION_READINESS_DERIVED`. No physical
first-order action, physical Dirac equation, self-adjoint domain, or fermionic
spectrum is derived. No monopole or magnetic-charge mechanism is used.

## Scale, hidden inputs, and next gate

`a_min^2=21 kappa_1/(2 kappa_0)` remains a symbolic parent relation.
`kappa_0`, `kappa_1`, `beta_partial`, and the boundary coefficient sources are
not generated. `a_min` is therefore not an absolute physical unit.

Provisional inputs are B1, the existence of intrinsic fields, positive raw
kinetic coefficients, and exact metric matching. The repository does not use
measured masses, couplings, Planck data, alpha, CKM, PMNS, cosmological
parameters, or v5 scalar values to select them.

Completion gate:
`V6_1_3_INTRINSIC_ACTION_FROZEN_COEFFICIENT_LOCK_UNDERDETERMINED_SHIFTED_BACKGROUND_OPEN`.

Recommended next branch:
`bhsm-boundary-coefficient-source-theorem-v6-1-4`.

`FULL_BHSM_NOT_COMPLETE`.
