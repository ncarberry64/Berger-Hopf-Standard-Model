# BHSM v16.21: refreshed KKT range and endpoint-variation audit

At the exact v16.20 projected state, the full symmetric 376-dimensional KKT
Jacobian is rebuilt with the nonzero event curvature. Its eigenspaces are used
to report rank, right and left nullity, and every numerically relevant
left-null overlap with the residual at four relative tolerances.

The scale rows at free nodes 1, 2, 21, 22, and 23 and the period row are also
checked directly against centered differences of the same discrete action.
The derivative/quadrature pair is separately tested for the summation-by-parts
identity, so a true variational-row error is distinguished from a collocation
boundary-closure defect before any correction is made.
