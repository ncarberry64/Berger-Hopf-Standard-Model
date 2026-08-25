# C2 derived adaptive proof-ball continuation

Let `A` be the already-certified admissible root radius, `c` the accumulated
center-path upper bound, and `r` the incoming endpoint tube.  The unallocated
radius is `m=A-c-r`.  A local proof-ball share `rho` has radius `rho m`.

Containing the incoming tube requires the exact strict inequality
`rho>rho_min=r/m`.  Increasing `rho` monotonically enlarges every retained
action-majorant ball.  The feasible upper endpoint is therefore obtained by
bisection against the existing strict conditions: hard self-consistency below
one half, positive `c_psi`, `b_psi`, and `Delta`, positive lapse and radius
rate, and the inherited line and domain margins.  The selected proof share is
the midpoint between `rho_min` and the feasible upper endpoint.  It has strict
slack at both ends and is derived from proof geometry, not physics.

The continuation retains the 80-digit signed and tube accumulators and adds
every binary64 center-rounding defect to the tube.  Every accepted segment has
strictly positive signed, physical-`u`, and proper-duration increments.  Any
eventual allocation or action-majorant exhaustion remains a proof-method
boundary, not a physical event or canonical stop.
