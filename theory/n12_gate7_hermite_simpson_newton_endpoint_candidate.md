# Gate-7 Hermite--Simpson Newton endpoint candidate

Apply the solved block-bidiagonal state correction to the best second-Newton
center.  Reproject every endpoint onto the retained 25 action constraints,
recenter the selected descriptor fiber, and recompute the exact endpoint field
and numerical first-stop bracket.

This constructs the endpoint candidate required for a nonlinear dense replay.
It is not yet a continuous orbit, interval shadow, or operator authority.

`FULL_BHSM_COMPLETE = FALSE`.
