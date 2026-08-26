# Gate-7 direct zeta coefficient cotangent

Status: `DIRECT_ZETA_COEFFICIENT_COTANGENT_CLOSED_ON_FINITE_CORE_FAMILY`.

The retained replacement functional contains

`Gamma_SM_zeta=-(59/30) integral exp(-x(tau)) d tau`.

This is an internal action term, not an external source. On a linear
finite-core element with endpoint log radii `x_j,x_(j+1)` and proper duration
`h_j`, its contribution is evaluated exactly as

`I_j=h_j integral_0^1 exp(-(1-s)x_j-s x_(j+1)) ds`.

Differentiation before any history member is selected gives strictly positive
node-log-radius components of `D Gamma_SM_zeta` and strictly negative
moving-duration components. The implementation uses the analytic exponential
moments, with a cancellation-safe series at equal endpoint radii. It therefore
does not insert a quadrature cutoff or an external force value.

For every member of the certified C2 coefficient tube, global radius and
duration intervals give componentwise enclosures:

`(59/60) exp(-x_max) sum_adjacent h_lower
 <= D_(x_j) Gamma_SM_zeta
 <= (59/60) exp(-x_min) sum_adjacent h_upper`,

and

`-(59/30)exp(-x_min)
 <= D_(h_j) Gamma_SM_zeta
 <= -(59/30)exp(-x_max)`.

The same integral supplies the compact incoming formation-arm zeta load. It
is routed through the upstream history adjoint and is not added as a seam
source. At every exact member, simultaneous common scaling
`delta x_j=1, delta h_j=h_j` cancels identically, reproducing the retained
moving-duration Ward identity.

The direct one-seam full graded heat seed is separately enclosed in log space.
This result closes the exact zeta part of the finite-core coefficient source;
it does not promote the heat term to zero, select the proof center, execute the
unknown interval state-transition adjoint, or close the maximal C2 tail.

No internal response is zeroed or double-counted. Gate 7 remains open, Gate 8
remains locked, chord 3 remains unauthorized, and `FULL_BHSM_COMPLETE=false`.
