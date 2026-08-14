# BHSM N=3 directional-event merit descent v18.22

The exact action Hessian is validated, while coordinatewise event Hessians in
v18.19 and v18.21 are invalid.  This calculation therefore evaluates only the
event Hessian-vector product required to form the current square-KKT merit
gradient.

The event gradient is differentiated along the physical residual direction at
the v18.20 resolved scaled displacement.  It is combined with the exact action
Hessian, explicit event-multiplier column and event row.  The resulting
Jacobian-vector product is checked directly against central differences of the
unchanged exact nonlinear residual.

No full event Hessian is claimed or reused.  Exact symmetric merit slopes and
trial states are then evaluated without componentwise filters.  Any candidate
remains pending until complete-child reconstruction and persistence pass.
