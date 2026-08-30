# Gate-7 augmented fixed-descriptor Newton system

The desingularized collocation variable is the 98-dimensional action state
together with one independently carried signed descriptor.  The first 98
rows use the fixed-descriptor derivative of the normalized cancelled field;
the final row differentiates the normalized descriptor rate.  The latter
contains an action fourth derivative and is evaluated by the JAX realization
only as Newton predictor machinery.  Retained exact endpoint and midpoint
field evaluations remain nonlinear authority.

Each constraint-closed state has a 73-dimensional action-coordinate nullspace.
Adjoining the descriptor axis gives a 74-dimensional correction space.  The
reset endpoint is fixed.  For every Hermite--Simpson interval, the full 99D
residual derivative is assembled first and then reduced by the next endpoint's
74D tangent/descriptor frame.  The descriptor-rate residual is therefore an
explicit solved row; it is not reconstructed by a binary64 eigenvalue.

The unused 25 normal residual components are recorded.  A numerical Newton
contraction does not certify continuous shadowing, interval invertibility, a
rebuilt cone or first hit, Gate 7, or full BHSM completion.
