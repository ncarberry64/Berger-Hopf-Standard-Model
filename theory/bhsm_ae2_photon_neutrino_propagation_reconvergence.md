# BHSM-AE-2.0.0 photon/neutrino propagation provenance audit

Status: `PARTIAL_SHARED_GEOMETRY_NO_NEUTRINO_OPERATOR_PROMOTION`.

This sprint audits existing action and theorem objects. It introduces no new
term, coefficient, scale, particle, endpoint, or physical momentum label.

## Exact common geometry

The current transverse gauge/de Rham and product-Dirac sectors propagate on
the same positive-lapse forward history, use the same radius history
(x(\tau)=\log R_4(\tau)), and meet at the same AE2 reset-glued bundle seam.
They are not the same representation or the same reduced operator. The exact
retained reductions are

\[
 -\partial_\tau^2+c_\rho e^{-2x}
\]

for scalar/de Rham channels and

\[
 A_\lambda^*A_\lambda,\qquad
 A_\lambda=\partial_\tau+\chi\lambda e^{-x}
\]

for the fermion channels. The schematic universal operator proposed for the
reconnaissance is therefore not recovered as one exact action formula. In
particular, the factorized Dirac form is not expanded by inventing an
independent (s'(\tau)) coefficient, and the gauge sector retains a distinct
transverse quotient and Wentzell domain.

## Photon

The representation theorem derives (Q_{\rm em}=T_n+Y_{BH}), and the
conditional electroweak block has the exact null vector
((0,0,g_1,g_2)). This is not yet the complete physical photon theorem. The
current action has not traced that vector through the full constraint-reduced
transverse/coexact quotient, reset domain, normalization, and physical
quadratic operator. The exact status is therefore
`OPEN_MISSING_ACTION_DERIVED_PHOTON_NULL_CHANNEL`.

The positive transverse-gauge Wentzell margin is an interface/domain
impedance. It is not a photon mass and cannot be used to infer
(\Mu_\gamma^2>0).

## Neutral carrier and stiffness

AE2 owns (D_{AE2}), its reset transmission graph, and
(\operatorname{Dom}(D_{AE2}^2)). A finite neutral representation label
(P_\nu=(1-C)(1+\sigma)/2) also exists. The required rank-three physical
projector does not. The frozen family attachment contains
(F_\ell\oplus F_u\oplus F_d), not (F_\nu), and its own action audit records
the spectral intertwiner as missing. Thus

\[
 P_\nu^{(3)}D_{AE2}^2P_\nu^{(3)}
\]

is a target, not a derived operator.

The historical (K_\nu) is only a boundary seed and has a negative
eigenvalue. It is not a positive propagation-stiffness or mass matrix. The
later formula

\[
 \mu_\nu=\sqrt{A_\nu/Z_\nu}\,K_{\rm neutral,eff}
\]

is explicitly conditional: (A_\nu), (Z_\nu), and the physical curvature
map remain missing. The v6.6 representative (K_{\rm prop}) likewise records
that its action source is not derived. The minimal v6.7 light block is the
threefold zero matrix, so it supplies neither a splitting nor a preferred
neutral eigenbasis.

## Phase, PMNS, and CP

The stored (L/E) law is a conditional high-energy template. A physical
derivation still requires the same action-owned stiffness to control mass,
relative phase, oscillation, and group velocity, together with owned
translation/energy and momentum maps. Gate-7's native variable (z) is not
(p^2). The current splitting ratio is open; the zero light block would give
an undefined (0/0), not a prediction.

The stored PMNS matrix uses a canonical charged-diagonal convention. Neither
(U_\ell) nor (U_\nu) has been obtained by diagonalizing current
action-derived response operators, so (U_{PMNS}=U_\ell^\dagger U_\nu)
remains open. The retained (e^{i\pi/3}) holonomy is a flavor seed only. It
does not attach to an action-owned neutrino stiffness, does not define a
Jarlskog invariant without the missing bases, and cancels from the exact
Gate-7 threshold denominator as a common reset-frame phase.

## Gate-7 reconvergence

The neutral kinetic representation is a subcarrier of the same full AE2
Spin times (G_{SM}) Dirac bundle used by Gate 7. This establishes partial
shared geometry. It does not establish the missing three-slot neutral
projector or allow any historical neutrino matrix, momentum interpretation,
or CP seed to be transferred into Gate 7.

Gate 7 is unchanged and remains active at `G7_07_ANGULAR_UNIFORMITY`. Frozen
predictions are unchanged. `FULL_BHSM_COMPLETE = FALSE`.

The highest-upstream newly exposed dependency is an action-derived neutral
rank-three invariant-subundle projector commuting with (D_{AE2}),
(D_{AE2}^2), the reset lift (U_R), and the gauge/BRST action.
