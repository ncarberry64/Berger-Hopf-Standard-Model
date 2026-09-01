# Gate-7 second Hermite--Simpson Newton line search

The full second block step overshoots its nonlinear residual.  Use the parent
and full-step residual vectors to compute the least-squares secant damping on
`[0,1]`, then scale the already-solved endpoint correction.  The secant model
is routing data; exact endpoint and midpoint replay remains mandatory.

`FULL_BHSM_COMPLETE = FALSE`.
