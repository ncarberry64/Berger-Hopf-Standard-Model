# BHSM N=3 strong-damping merit continuation v16.47

This checkpoint rebuilds the exact symmetric physical KKT system at the
accepted v16.46 state and extends the same continuous spectral merit filter
into the stronger-damping regime. This is a solver refinement of the unchanged
376-variable action-plus-event equations, not a new physical mechanism.

All trials are evaluated after exact constraint projection and with the
Sobolev-domain guard. The physical dependency remains simultaneous N=3 parent
stationarity upstream of the single common gauge/rank-16 LR pushforward.
