# BHSM quantum functional accounting v16.00

The v15.51 constrained orbit already contains the Standard Model zeta vacuum
functional. Therefore the heat superdeterminant of v15.96 cannot simply be
added to that action. The same gauge, ghost, Weyl, and HS species would be
counted twice.

The physical replacement is

\[
 \Gamma_Q=\Gamma_{\rm parent}+\Gamma_{\rm SM}^{\rm heat}[\Phi;A,H,\Psi],
\]

or, using the implemented v15.51 action,

\[
 \Gamma_Q=\Gamma_{\rm attached}^{\zeta}
 -\Gamma_{\rm SM}^{\zeta}[\Phi;0,0,0]
 +\Gamma_{\rm SM}^{\rm heat}[\Phi;A,H,\Psi].
\]

This replacement applies to geometry, gauge, and Yukawa derivatives
together. The dense v15.97 orbit is consequently the collocation seed, not
the final heat-regulated quantum orbit.

Because the determinant acts on the whole proper cycle, it is not an
independent local acceleration. At 24 nodes the unknowns are 24 copies of
the nine geometry coordinates and four lapse/shift multipliers, together
with the period and phase multiplier:

\[
 24(9+4)+2=314.
\]

Stationarity supplies 312 equations; the event equation and cycle phase
condition supply two more. The result is one square 314-dimensional global
hybrid KKT system. Its solution precedes every extraction of
\(K_E,K_B,Z_\Psi,Z_H\), and \(Y\).
