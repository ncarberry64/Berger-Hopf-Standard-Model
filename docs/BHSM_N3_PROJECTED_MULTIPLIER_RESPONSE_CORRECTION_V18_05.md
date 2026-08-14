# BHSM N=3 projected event-multiplier response correction v18.05

Every nonlinear residual evaluation analytically selects the event multiplier
so that the 375 stationarity rows are orthogonal to the event covector.  The
previous reduced Newton matrix held that multiplier fixed and then deleted its
column.  It therefore was not the derivative of the map actually evaluated.

Writing the scaled action covector as `a`, event covector as `e`, event Hessian
as `H`, and projected stationarity residual as `r = a + rho_* e`, the projection
is

`rho_* = -(a.e)/(e.e)`.

If `B = A + rho_* H` is the fixed-multiplier top derivative, differentiating
`r.e = 0` gives

`grad rho_* = -(B^T e + H^T r)/(e.e)`

and the correct top derivative is

`B + outer(e, grad rho_*)`.

This is a rank-one chain-rule correction.  It changes neither the action nor
the event equation and adds no KKT row.  Directional finite differences of the
actually projected nonlinear residual validate the corrected response before
it is used for further N=3 continuation.
