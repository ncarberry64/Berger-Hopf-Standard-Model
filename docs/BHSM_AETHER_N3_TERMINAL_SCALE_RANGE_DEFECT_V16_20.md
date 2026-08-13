# BHSM v16.20: endpoint-scale/period KKT range defect

After the v16.19 projected-state refresh, the event multiplier is again
projected exactly at fixed orbit.  The constraint-multiplier stationarity block
is already below (2\times10^{-2}), while the dominant coordinate residuals are
the scale coordinates at the first and last free collocation nodes,
accompanied by the period equation. Thus the next upstream object is the
endpoint-scale/period range of the same anchored common-pushforward KKT
Jacobian. No new event, boundary condition, or Yukawa normalization is
introduced.
