# N12 C2 pole-free regularized Jacobi bound

The first C2 launch used a safe but cancellation-destroying derivative bound
for the hard Euler--Dirac solve.  The exact selected-line decomposition gives
a sharper action-native identity.  The hard rate is

`r_h=(Q D Q)^-1 Q b`,

and its Kato-covariant derivative differentiates only the hard inverse.  The
soft-source derivative can likewise be written in terms of `r_h`, selected-to-
hard coupling, and a correction proportional to `lambda`.  Neither identity
contains `1/lambda` or `1/lambda^2`.

Structured retained-action contractions bound the hard third derivative and
selected-to-hard coupling on the existing launch ball.  A scalar
self-consistency inequality then closes the hard Jacobi bound.  Substitution
into the signed-eigenvalue reparametrized vector field gives a finite uniform
Jacobi generator that strictly improves the previous crude projector-times-
full-source estimate.

This is a proof-coordinate improvement only.  It changes no action equation,
selected branch, reset family member, physical scale, or endpoint semantics.
