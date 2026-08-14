# BHSM N=3 second complete-child chart reconstruction v18.28

The v18.27 event is tested against the unchanged 14 physical child rows: three
traces, seven local constraints, two attachment momenta and two dynamic-flux
rows.  A fresh numerical Jacobian over all 26 child variables selects a rank-14
local chart and closes every row without adding a global KKT equation.

The reconstructed child retains nonzero velocity and positive eta.  Numerical
row normalization uses local Jacobian row norms and preserves the same zero
set; it is not a new acceptance condition.
