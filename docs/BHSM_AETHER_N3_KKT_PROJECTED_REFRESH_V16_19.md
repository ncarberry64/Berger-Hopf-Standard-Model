# BHSM v16.19: projected-state event-KKT refresh

This calculation rebuilds the common-action Hessian and nonzero soft-event
curvature at the exact v16.18 multiplier-projected state.  It uses a smaller
trust radius and promotes no event crossing unless the full stationarity
covector closes simultaneously.  A failed step is interpreted through the
refreshed KKT range, not as a terminal no-go.
