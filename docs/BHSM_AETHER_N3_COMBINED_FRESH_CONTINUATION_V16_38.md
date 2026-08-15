# BHSM v16.38: combined fresh N=3 continuation

This continuation rebuilds the complete action-plus-event Hessian once at the
accepted v16.37 state, records its block and numerical-range audit, and then
uses that identical matrix for the 20-candidate nonlinear multirank bank.

Combining the refresh and step prevents redundant Hessian construction while
preserving every physical safeguard: exact event-multiplier projection,
nonzero event curvature, eta positivity, all constraints, period accounting,
and acceptance by the complete nonlinear residual.

The real-particle target is the common event background required before both
the broken gauge kernel and a persistent electron-like LR mass can exist.
