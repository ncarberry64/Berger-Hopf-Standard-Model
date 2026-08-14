# BHSM N=3 resolved exact projected Jacobian v18.08

Directional convergence at the v18.06 state identifies `1e-5` and `3e-5` in
scaled coordinates as the resolved outer-derivative pair.  The inherited
relative `1e-4` step has already entered nonlinear response and is rejected for
this projected v17.61 map.

The exact projected residual Jacobian is therefore rebuilt with the absolute
`3e-5` step and checked against independent directional derivatives at that
same resolved scale.  This changes no physical equation, event definition, or
KKT row.  It repairs only the demonstrated derivative blocker.
