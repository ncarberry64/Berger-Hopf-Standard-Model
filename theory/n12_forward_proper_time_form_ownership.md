# N12 forward proper-time form ownership

Status: `PROPER_TIME_TEMPORAL_FORM_OWNERSHIP_DERIVED`.

The retained positive boundary lapse defines the single physical clock

\[
 d\tau=N_{\partial}(t)\,dt,
 \qquad N_{\partial}>0.
\]

Pulling the source form to this clock gives

\[
 q_{\rm temporal}[U]=\int_{I_C}\|D_\tau U\|^2\,d\tau.
\]

Consequently, the lapse is not a second local coefficient of the proper-time
source operator. It determines the coordinate-to-proper-time pullback, the
maximal interval, and the representation `R4(tau)`. On the realized interval,
`D_tau` is the canonical covariant derivative. The temporal Laplacian is the
operator represented by the same form,

\[
 \Delta_\tau=D_\tau^*D_\tau,
\]

with the existing nonnegative reset/Wentzell endpoint form when an event is
hit and the Friedrichs closure otherwise. `Delta_tau` is therefore not an
independently selectable matrix.

The historical periodic finite realization satisfies
`Delta_tau=D_tau^*D_tau` to relative residual below `1e-14`. This is retained
only as an algebraic equivalence witness. A separate nonperiodic forward
difference plus nonnegative endpoint-form witness satisfies the identity
exactly, so no periodic endpoint is selected by the theorem.

For compactly supported geometry variations at fixed proper-time domain,

\[
 D_\Phi D_\tau=0,
 \qquad D_\Phi\Delta_\tau=0.
\]

All local bulk geometry dependence in the current forward source
representation therefore enters through `log R4(tau)`, whose exact local
first and mixed-second coefficient jets are already derived. A variation of
the maximal endpoint or endpoint graph belongs to the exterior
`D_Phi M_C` response; treating it as another freely selectable bulk temporal
operator would double count the domain dependence.

This removes `D_tau` and `Delta_tau` from the missing coefficient-oracle list.
It does not supply the maximal-forward `R4(tau)` response or its action Jacobi
variations. The exact remaining owner is an enclosure of that radius-history
Weyl response and its first/second variations, or the equivalent direct
`(M_C,D_Phi M_C,D_Phi2 M_C)` oracle. Gate 7 remains active, Gate 8 remains
locked, and chord 3 remains unauthorized.
