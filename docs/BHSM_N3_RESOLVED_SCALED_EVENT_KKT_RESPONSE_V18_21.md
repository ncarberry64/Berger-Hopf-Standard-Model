# BHSM N=3 resolved scaled-event KKT response v18.21

v18.20 demonstrates that the ordered-event curvature has a resolved plateau in
action-owned scaled coordinates.  This calculation rebuilds the 37-variable
event-support Hessian directly in those coordinates at the measured
`3e-5` scale.

The event block is combined with the validated v18.18 exact action Hessian,
the explicit event-multiplier column, and the event row.  The system remains
376 by 376.  No row is rescaled, no multiplier is projected, and the
invalidated v18.19 uniform-raw event Hessian is not reused.

Five coupled directions, including the complete mixed event support, compare
the assembled response with the unchanged exact nonlinear residual.  Only a
validated response may propose the next Newton step; physical promotion still
uses total merit, eta, and complete-child persistence alone.
