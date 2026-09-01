# Gate-7 Hermite--Simpson block Newton predictor

With endpoint and midpoint normalized-field Jacobians fixed on the best second-
Newton center, linearize each Hermite--Simpson residual in its two endpoint
states.  The fixed reset endpoint makes the finite system block bidiagonal, so
the Newton correction is obtained by a forward sequence of 98-dimensional
right-block solves.

The predictor closes only the finite linearized block residual.  Its endpoint
corrections must still be constraint-projected, descriptor-recentered, and
replayed through the nonlinear exact field before any center claim.

`FULL_BHSM_COMPLETE = FALSE`.
