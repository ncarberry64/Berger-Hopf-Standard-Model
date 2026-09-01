# N12 incoming finite-amplitude coefficient enclosure

Let `lambda` be any positive amplitude in the explicit incoming terminal
segment and let `rho` be normalized forward physical time, with `rho=0` at
the reconstructed formation-side edge and `rho=1` at the terminal event.
The regularized denominator certificate gives

`dT_-/dlambda=lambda/(-Delta)`

with `0<d_-<=-Delta<=d_+`.  Hence the retained duration satisfies, uniformly
for every member of the amplitude box,

`lambda^2/(2 d_+) <= T(lambda) <= lambda^2/(2 d_-)`.

The certified action ball also keeps the physical radius rate between
`v_->0` and `v_+`.  Integrating the exact identity `dx/dtau=v` over the
remaining fraction `(1-rho)` of the history therefore gives

`-(1-rho) v_+/(2 d_-) <= (x(rho,lambda)-x_E)/lambda^2`

and

`(x(rho,lambda)-x_E)/lambda^2 <= -(1-rho) v_-/(2 d_+)`.

This is a uniform finite-amplitude enclosure, not an asymptotic ansatz.  It
contains the previously certified quadratic germ.  The corresponding scalar
potential and factorized-Dirac superpotential are represented in logarithmic
relative form, so their positive but sub-floating-point changes are not
rounded into an exact zero.

The same regularized equations give a direct amplitude derivative bound

`|D_lambda x| <= ||D_q x||_* lambda ||qdot||/d_-`.

No Euler--Dirac block is inverted.  The result realizes the incoming compact
coefficient family for every `0<lambda<=lambda_*`; it still does not provide
the non-scale event/child-family Jacobi pullback required by the physical
force contraction.
