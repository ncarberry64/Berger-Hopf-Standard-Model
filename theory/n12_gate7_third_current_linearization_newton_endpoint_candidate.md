# Gate-7 third current-linearization Newton endpoint candidate

Apply the signed-Green residual correction a third time, using graph Jacobians
and 73-dimensional constraint tangents rebuilt on the second Newton center.
Every endpoint is constraint-projected and its descriptor is recentered from
the retained selected eigenline before the dense residual is replayed.

This is a numerical Newton candidate.  It does not supply interval shadowing,
an outward first hit, a nonlinear 72-direction carrier, or a force oracle.

`FULL_BHSM_COMPLETE = FALSE`.
