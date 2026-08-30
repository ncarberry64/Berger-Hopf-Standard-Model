# Gate-7 signed-Green current-center graph Jacobian

The first signed Green endpoint Newton step does not reduce the measured dense
defect when propagated by the graph Jacobian frozen on the earlier center.
Therefore rebuild the 98-by-98 reduced descriptor-graph Jacobian at every one
of the 371 constraint- and descriptor-recentered signed-Green endpoints.

The retained action supplies the gradient and Hessian, while the already
cross-checked JAX third tensor supplies the fast derivative predictor.  This
is the minimum center-dependent object needed for the next Newton iteration.
It remains numerical predictor data until retained directional replay and a
between-node interval remainder are attached after convergence.

`FULL_BHSM_COMPLETE = FALSE`.
