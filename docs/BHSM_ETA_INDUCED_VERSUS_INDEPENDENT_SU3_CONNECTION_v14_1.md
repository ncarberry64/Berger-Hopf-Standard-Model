# BHSM v14.1 — Eta-induced versus independent SU(3) connection

## Fork theorem

The eta-wall projector connection is a genuine induced color-frame/Berry
connection, but it is not action-equivalent to the independent physical
four-dimensional SU(3) connection.

The unique final branch classification is:

`BHSM_COLOR_DYNAMICS_REQUIRES_A_NEW_DECLARED_CROSS_STRATUM_BUNDLE_CONNECTION_ACTION_OBJECT`

The exact next object is:

`ACTION_OWNED_COMMON_HIGHER_DIMENSIONAL_CONNECTION_WHOSE_M4_SU3_RESTRICTION_AND_ETA_POLARIZATION_CONNECTION_ARE_DERIVED_COMPATIBLE_PROJECTIONS`

No new action term, field, multiplier, mass, locking coefficient, physical
(g_3), or gauge-dressed proxy solution is introduced.

## Scientific lineage

| Layer | Classification | Retained result |
| --- | --- | --- |
| main through v11.3 | live merged | reciprocal metric attachment; no color matcher |
| v11.5 / PR 218 | open stacked diagnostic | no-fit spectral current candidate; provenance open |
| v11.6 / PR 219 | open stacked action-owned | weak family current (I_3); uniqueness no-go |
| v13.1 | continuation conditional | degree-one static eta solution and radial stability |
| v13.3 | continuation conditional | FR odd-degree spin parity and knot ontology |
| v13.4–v13.5 | continuation geometric | wall polarization, projector connection, singlet closure |
| v14.0 / PR 220 | open stacked action audit | zero eta/independent-SU3 mixed variation |
| v12.2 Lambda85 flavor bridge | superseded/invalidated | family-central Hessian cannot source off-diagonal flavor |

## Bundle isomorphism audit

The polarization bundle is

\[
E_P=u_\eta^*\mathcal E_{\rm canonical},
\qquad
\mathcal E_{\rm canonical}=T^{1,0}S^6,
\]

whereas the retained color bundle (E_{\rm color}) is an independent
effective-(M_4) input. Equal rank, Hermitian metric, and structure group do
not provide an isomorphism. The action owns no common base map, transition
cocycle identification, collar extension, connection pullback, or

\[
\Phi:E_P\longrightarrow E_{\rm color}.
\]

There is also a global mismatch: (c_2(E_P)=0), while the independent color
bundle admits general second-Chern sectors.

## Local degrees of freedom

For one tangent direction (a\perp u),

\[
d_aP=\frac{-a\otimes u-u\otimes a-iJ_a}{2}
\]

has rank six as a map from (T_uS^6) to projector variations. Curvatures from
the fifteen tangent two-planes span all eight (mathfrak{su}(3)) directions,
and their commutator closure has dimension eight.

For four spacetime derivatives, however, the nonlinear map

\[
(\partial_\mu u)_{24}
\longmapsto
(F^P_{\mu\nu})_{48}
\]

has generic numerical Jacobian rank 23 at four random selector frames. At the
constant-selector vacuum its linear rank is zero. Thus full holonomy does not
imply a generic Yang–Mills configuration space.

## Principal symbol

Around (u=u_0), (du_0=0),

\[
\delta P=O(\delta u),
\qquad
F^P=P[dP,dP]P=O((d\delta u)^2).
\]

Consequently

\[
\int\operatorname{tr}(F_P^2)=O((d\delta u)^4).
\]

The quadratic Hessian and principal symbol are identically zero. By contrast,
the non-gauge-fixed independent Yang–Mills symbol has rank 24 for nonzero
Euclidean covector, with eight gauge zero modes and sixteen physical
polarizations in Lorentzian four-dimensional propagation. The composite
candidate has no perturbative gluon propagator about the trivial selector
vacuum and is strongly degenerate there.

## Characteristic classes and instantons

For the universal rank-three bundle over (S^6),

\[
H^2(S^6)=H^4(S^6)=0,
\]

so

\[
c_1(\mathcal E_{\rm canonical})=c_2(\mathcal E_{\rm canonical})=0.
\]

Its top class is (c_3=2[S^6]), with sign fixed by complex orientation.
Naturality gives

\[
c_2(E_P)=u_\eta^*c_2(\mathcal E_{\rm canonical})=0.
\]

On closed (M_4), the projector instanton number is therefore zero. Local
curvature can be nonzero, and manifolds with boundary can carry boundary
Chern–Simons data, but this does not create a nonzero second-Chern instanton
sector. Eta-knot degree belongs instead to (pi_7(S^7)).

Verdict:

`THE_ETA_PROJECTOR_CONNECTION_CANNOT_SPAN_GENERAL_NONZERO_INSTANTON_SU3_SECTORS`

## Gauge covariance

Changing an orthonormal local frame of (operatorname{Image}P) gives

\[
A^{P\prime}=U^\dagger A^P U+U^\dagger dU,
\qquad
F^{P\prime}=U^\dagger F^P U.
\]

This is valid bundle-frame covariance. It does not add independent physical
connections: (P) and the underlying eta configuration are unchanged.

## Variational and wall-extension audit

If (u) were an independently extended selector, varying
(operatorname{tr}(F_P^2)) would give a degenerate second-order equation for
(u), not an independent SU(3) Gauss equation. For the actual definition

\[
u=\frac{\nabla_n\eta}{\|\nabla_n\eta\|}
\]

on the wall, variation is singular at zero normal gradient. Substitution into
the candidate action introduces second derivatives of eta and generically a
fourth-order eta equation, together with wall-position shape variation.

Normalized-gradient, collar transport, harmonic, nearest-wall, gradient-flow,
and action-derived extensions were audited. None is presently selected by the
action. The candidate is undefined as a global (M_4) connection without that
extension.

## Independent-connection matcher audit

The retained action contains no connection equality multiplier, curvature
matcher, common principal bundle, or color transgression. `Lambda85` and
`Lambda54` match metric incidence/seam data, not gauge connections.

- (A=\Phi_*A^P) removes independent gluon modes and lacks a variational source.
- (F_A=\Phi_*F_P) overconstrains the field and forces the (c_2=0) sector.
- A connection-difference mass term requires a dimensionful coefficient and
  would mass unbroken color.
- A curvature-difference term requires (Phi) and an unselected relative
  normalization.
- A transgression requires a common bundle and appropriate odd-dimensional
  extension absent from the retained action.

The preferred no-new-low-energy-field route is a common higher-dimensional
connection whose two restrictions are derived compatible projections.

## Chirality and flavor

The missing Dirac object is typed, but no index is emitted. The retained
Lorentzian operator is not called elliptic; an APS calculation requires a
compact Euclidean bulk/boundary problem, complete tensor connection, and
self-adjoint domain.

Color transport remains

\[
A^P_{\rm color}\otimes I_{C_3},
\qquad
[P_r,A^P_{\rm color}\otimes I_{C_3}]=0.
\]

Therefore (J_+^{\rm family}=I_3). No (K_{ud}), CKM value, or color-based
weak chirality is introduced.

## Hindsight 20/20

### Validated

- The projector connection and its nonzero SU(3)-valued curvature are real
  induced geometry.
- Generic universal curvature generators close to full SU(3) holonomy.
- Meson and baryon singlets remain covariantly closed.
- Orientation reversal selects the conjugate color bundle.
- Color transport is family central.

### Invalidated

- Nonzero traceless curvature implying a generic QCD connection.
- Full holonomy implying field-space or action equivalence.
- The composite (F_P^2) term supplying perturbative gluons about (du=0).
- The projector bundle spanning nonzero SU(3) instanton sectors.
- Rank-three bundle coincidence supplying an action-owned (Phi).
- Existing metric matchers supplying a color-connection Gauss law.

### Reclassified

The eta projector connection is a restricted polarization-frame/Berry
connection controlling knot color orientation, induced holonomy, conjugation,
and singlet closure. It may be a background or compatible projection of a
future common connection, but it is not the full QCD connection.

### Open

- the common higher-dimensional connection and its two compatible restrictions;
- the wall-to-(M_4) selector/bundle extension;
- coupled eta and independent-SU3 Euler equations and Gauss law;
- the oriented boundary Dirac operator and self-adjoint domain;
- nonradial stability and gauge-dressed singlet solutions after action closure;
- the independent charged-current provenance gate.

Mark III remains blocked and BHSM physical completion is not reached.
