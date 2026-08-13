# BHSM v16.27: fresh KKT after the robust multirank step

The v16.26 rank-80 quarter step materially lowers the complete residual but
moves the event component. v16.27 therefore rebuilds the action-plus-event
KKT curvature at that exact accepted state and reports the coordinate,
constraint-multiplier, period, and event residual blocks separately.

This keeps the solve joint: event closure is not optimized as a surrogate at
the expense of action stationarity, and action stationarity is not promoted
while the physical soft-event equation remains open.
