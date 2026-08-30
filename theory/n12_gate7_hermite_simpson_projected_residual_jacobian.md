# Gate-7 projected Hermite--Simpson residual Jacobian adjudication

The first block step reduces the nonlinear Hermite--Simpson residual, but a
current-center second step, a full-step secant damping, and a much smaller
locally sampled trust step all fail.  The exact trust sample shows that the
directional derivative of the complete projected/recentered block residual is
over two orders of magnitude larger than the stored graph model scale.

The hybrid graph Jacobian is therefore rejected as the derivative of the
actual solver map.  The next operator must differentiate the complete
composition: endpoint constraint projection, selected-descriptor recenter,
exact endpoint field, Hermite--Simpson midpoint state, and exact midpoint
field.  Further scalar damping of the same direction is not a proof route.

`FULL_BHSM_COMPLETE = FALSE`.
