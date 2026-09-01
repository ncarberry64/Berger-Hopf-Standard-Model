# N12 reset time-quotient generator audit

Status: `WHOLE_SYSTEM_TIME_QUOTIENT_COUNT_RETAINED_EXPLICIT_HYBRID_GENERATOR_OPEN`.

The fixed-event child reset Jacobian has a 67-dimensional raw kernel.  The
retained reset theorem separately records dimension 66 after the existing
whole-system time quotient.  These are not the same tangent space, and the
durable checkpoint does not contain an explicit time-generator vector.

The most immediate candidate is the child Euler--Dirac vector field evaluated
at the certified reset state.  It is not the correct generator.  At 48, 96,
and 192 quadrature points its relative residual against the fixed-event reset
Jacobian is stably `0.01135975`, and its relative distance from the raw reset
kernel is stably `0.00358421`.  Advancing only the child while fixing the
event does not preserve the coupled complete-child reset equations.

Orthogonally projecting this vector into the kernel would manufacture a
Euclidean gauge slice; it would not derive the coupled hybrid phase symmetry.
Therefore the raw 67-dimensional nullspace force and bordered-KKT checks
remain valid algebraic witnesses, but they are not promoted to the final
66-dimensional physical quotient.  In particular, the raw `log R4`
projection is not advertised as a quotient observable.

The explicit generator must be derived from the coupled 196-dimensional
event-child hybrid action, with its induced fixed-event quotient, or the
force/Hessian must be formulated intrinsically on that quotient.  This is a
component of the same missing parametric exterior-operator realization, not
a new gate or a new time direction.

`FULL_BHSM_COMPLETE=false`.
