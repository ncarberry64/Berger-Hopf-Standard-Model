# BHSM v16.17: second refreshed event-KKT curvature

The v16.16 soft-event crossing is not treated as a solution because the full
stationarity residual remains nonzero.  This calculation rebuilds both the
common-action Hessian and the nonzero event-curvature block at that exact
state, then resumes safeguarded Newton--SR1 continuation.  Promotion requires
simultaneous closure of stationarity and the soft-event equation.
