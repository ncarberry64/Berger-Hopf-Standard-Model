# BHSM v16.25: fresh physical KKT after the basin step

The accepted v16.24 state is a nonlinear displacement of radius 400 in the
scaled KKT variables, so the v16.21 tangent is no longer reused. This audit
rebuilds the complete action Hessian, adds the nonzero event-multiplier
curvature, diagonalizes the resulting symmetric 376-variable KKT matrix, and
remeasures its numerical range and truncated Newton direction scales.

This refresh decides the next continuation step inside the unchanged physical
action. It does not promote the unbroken event to a particle result and does
not separate gauge normalization from the rank-16 mass-generating
pushforward.
