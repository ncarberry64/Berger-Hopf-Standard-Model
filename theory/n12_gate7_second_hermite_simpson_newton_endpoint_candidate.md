# Gate-7 second Hermite--Simpson Newton endpoint candidate

Apply the second block correction to the first block-Newton center, reproject
all retained action constraints, recenter the selected descriptor fiber, and
recompute exact endpoint fields.  The result remains a numerical candidate
until its collocation midpoint residual is replayed.

`FULL_BHSM_COMPLETE = FALSE`.
