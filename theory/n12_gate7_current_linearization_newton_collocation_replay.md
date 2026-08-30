# Gate-7 current-linearization Newton collocation replay

Apply the same endpoint-field-matched cubic and 1,110-node Gauss-3 replay to
the second Newton endpoint set, which was built from the current-center graph
Jacobian and current seam tangents.  This distinguishes a stale-linearization
failure from failure of the signed Green fixed-point route itself.

Actual defect reduction permits another owner-only Newton iteration.  Lack of
reduction rejects this fixed-point route and sends the center construction to
a direct multiple-shooting or full collocation solve.  No numerical result is
promoted to interval authority.

`FULL_BHSM_COMPLETE = FALSE`.
