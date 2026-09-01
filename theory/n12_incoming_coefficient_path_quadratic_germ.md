# N12 incoming coefficient-path quadratic germ

Status: `INCOMING_NORMALIZED_COEFFICIENT_PATH_QUADRATIC_GERM_CERTIFIED`.

Let `lambda_0>0` be the action-owned formation amplitude, let
`T(lambda_0)=a lambda_0^2+o(lambda_0^2)`, and normalize proper time by
`tau=T(lambda_0)s`, `0<=s<=1`.  The terminal event is fixed along this
amplitude germ and the certified incoming terminal proper-radius rate is
`v_E=D_tau log R4(E1)>0`.

The retained Euler--Dirac flow is regular on the local history family.
Consequently its radius rate is continuous and, uniformly in normalized
time,

`x(s,lambda_0)=x_E-(1-s)*a*v_E*lambda_0^2+o(lambda_0^2)`.

This conclusion uses only the certified first terminal Cauchy jet and the
positive duration quadratic law.  It does not require the ill-conditioned
Euler--Dirac acceleration solve.

The corresponding leading channel coefficients are

`c exp(-2x(s))=c exp(-2x_E)*(1+2(1-s)a v_E lambda_0^2+o(lambda_0^2))`,

and

`chi mu exp(-x(s))=chi mu exp(-x_E)*(1+(1-s)a v_E lambda_0^2+o(lambda_0^2))`.

Thus the leading incoming scalar and factorized-Dirac coefficient paths are
action-owned and parametric; no history member or positive amplitude is
selected.  The complete finite-duration path still requires a uniform
inverse-free remainder enclosure on a nonempty positive `lambda_0` box.  A
direct acceleration obtained by inverting the ill-conditioned Euler--Dirac
block is not an admissible replacement for that enclosure.

`FULL_BHSM_COMPLETE=false`.
