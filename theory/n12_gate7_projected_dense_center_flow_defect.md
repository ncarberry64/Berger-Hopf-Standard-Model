# N12 Gate-7 projected dense-center flow defect

Join the 371 constraint-projected native DOP853 nodes by adding the linear
interpolant of their action-coordinate Newton corrections to the native
seventh-order DOP853 dense polynomial.  This path matches every projected node
and remains close to the native flow candidate.

At each of the 370 cell midpoints, evaluate the direct retained 96-point action
field on the corrected state and propagated signed descriptor.  Compare the
normalized augmented field with the analytic derivative of the corrected
dense polynomial.  Independently evaluate the 25 normalized action constraints
there.

Small constraint residual does not imply a small flow residual.  A nonzero
collocation defect must be corrected by a global or causal Newton system that
includes the constraint and descriptor-fiber rows.  The projected path is not
promoted to a continuous orbit, and its endpoint does not inherit the prior
first-hit theorem.

`FULL_BHSM_COMPLETE = FALSE`.
