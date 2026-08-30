# Gate-7 Hermite--Simpson midpoint graph Jacobians

The direct Hermite--Simpson Newton operator depends on the normalized retained
action field at both endpoints and at the collocation midpoint.  Materialize
the exact cubic midpoint states and evaluate the hybrid action/JAX graph
Jacobian and selected-descriptor gradient on all 370 intervals.

These matrices complete the finite numerical block linearization.  They are
predictors, not interval derivatives or a continuous-center certificate.

`FULL_BHSM_COMPLETE = FALSE`.
