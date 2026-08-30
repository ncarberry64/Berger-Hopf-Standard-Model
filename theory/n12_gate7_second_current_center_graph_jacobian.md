# Gate-7 second-current-center graph Jacobian

Rebuild the retained normalized-field graph Jacobian at all 371 endpoints of
the second current-linearization Newton candidate.  This removes the remaining
stale-center linearization from a third signed-Green Newton test.  It remains a
hybrid retained-action/JAX numerical predictor, not interval authority.

`FULL_BHSM_COMPLETE = FALSE`.
