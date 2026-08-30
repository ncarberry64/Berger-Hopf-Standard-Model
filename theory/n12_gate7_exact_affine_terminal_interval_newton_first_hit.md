# N12 Gate-7 terminal interval-Newton first hit

The retained endpoint `92.30513924040065` lies strictly on the negative side
of the selected-eigenvalue stop.  It is a sign-bracketing endpoint, not the
physical terminal abscissa of the operator history.

Let `T` be that endpoint, `L(T)` its outward negative selected-eigenvalue
interval, and `D` the uniform negative interval for `Dlambda_24[F]` on the
terminal cone.  Strict monotonicity and the mean-value theorem give

`T_hit in T - L(T)/D`.

This interval lies strictly inside the certified terminal cell.  The already
proved preterminal positivity and strict negative derivative make it the
unique canonical first hit.  The interval midpoint state is stored only as a
representative for downstream finite computations.  It is not labelled a
numerically resolved zero: binary64 eigendecomposition jitters the tiny
selected eigenvalue by more than the root signal.  The outward time interval,
not a floating-point root solve, is the first-hit authority.

All operator histories and duration jets must henceforth terminate at this
first-hit enclosure, not at the negative-side sign-bracketing endpoint.
`FULL_BHSM_COMPLETE = FALSE`.
