# N12 C2 common-scale Weyl covariance

Status: `C2_PHYSICAL_COMMON_SCALE_WEYL_PULLBACK_CLOSED_BY_EXACT_COVARIANCE`.

For every finite positive-duration C2 form core, shift every nodal log radius
by the same real parameter `a`, multiply every proper duration by `exp(a)`,
and replace the spectral parameter by `exp(-2a)z`.  The scalar potential
`c exp(-2x)` and the factorized-Dirac superpotential
`chi lambda exp(-x)` then scale with weights two and one, respectively.  Each
local transfer has the exact covariance

`M(x+a, exp(a)h, exp(-2a)z) = exp(-a) M(x,h,z)`.

Finite composition preserves this identity, including a Dirichlet
Friedrichs form-core truncation boundary.  Differentiation at `a=0` gives

`D_x_uniform M + D_h_weighted M - 2 z D_z M = -M`.

Consequently the fixed-`z` physical common-scale coefficient pullback is

`D_common_scale M = -M + 2 z D_z M`.

This is the exact moving-duration contribution; it must not be dropped.  It
also means that no pathwise state Jacobi is needed for this one mandatory
physical direction.  In particular, the adaptive proof-center sequence is
not differentiated: those centers are enclosure representatives, not a
selected physical history.

The arbitrary-precision reverse recurrence now accumulates `D_z M` beside
the nodal-radius and duration cotangents.  Crosschecks on both the 1,064- and
1,222-segment nested cores, in all three retained scalar/product-Dirac
channels and at low, unit, and high negative spectral probes, verify the
identity to the recorded decimal residual.  The proof itself is parametric
for every real `z<0`; the probes are crosschecks, not a heat quadrature.

This closes only the common-scale part of the reset geometry pullback.  The
non-scale reset quotient sector, the sharp incoming `M_f`, and the complete
source-contracted heat-minus-zeta Cauchy tail remain open.  Rank two of the
birth radius Cauchy map does not assert that all other child-history tangent
directions are operator-invisible; no such dimension reduction is used here.

HINDSIGHT: requiring a full pathwise Jacobi for the common-scale component
was overstrong.  Exact form covariance supplies the weaker action-owned
identity actually needed.  No endpoint, selector, scale fit, recurrence, or
new physical direction is introduced.

`FULL_BHSM_COMPLETE=false`.
