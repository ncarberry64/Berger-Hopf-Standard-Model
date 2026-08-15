# BHSM N=3 exact square-KKT response v18.19

This calculation completes the response audit required after v18.18.  The
physical nonlinear system remains the square 376-variable KKT with explicit
event multiplier.

The validated exact action Hessian supplies the 375 by 375 action block.  The
event is the isolated seventh ordered eigenvalue of the retained terminal
Euler--Dirac Hessian.  Its scalar curvature is evaluated on the exact
37-variable event support and combined with the explicit multiplier column
and event row.  No multiplier projection or residual-row scaling is used.

The assembled matrix is compared with central directional responses of the
unchanged exact 376-component nonlinear residual.  It may propose a Newton
step only if these checks validate.  Physical promotion still requires
independent total-merit reduction, admissible eta, and complete-child
reconstruction/persistence; componentwise monotonicity is not imposed.
