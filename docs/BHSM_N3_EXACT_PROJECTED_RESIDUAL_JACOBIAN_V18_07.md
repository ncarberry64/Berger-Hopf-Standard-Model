# BHSM N=3 exact projected residual Jacobian v18.07

The existing independent-column assembly is applied directly to the nonlinear
map used in every v17.61 evaluation.  Each perturbed evaluation recomputes the
exact-local-jet action covector and analytically projects the event multiplier.
Consequently the resulting 376-by-375 matrix includes the complete projection
chain rule by construction.

This correction was authorized by the demonstrated v18.05 blocker: the older
matrix differentiated a different covector and held the projected multiplier
fixed.  No physical action or event equation changes, no KKT row is added, and
the matrix must pass independent directional finite-difference identities
before its Newton trial is considered.
