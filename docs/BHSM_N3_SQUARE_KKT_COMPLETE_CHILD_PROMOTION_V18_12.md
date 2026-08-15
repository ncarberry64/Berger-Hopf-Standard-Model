# BHSM N=3 square-KKT complete-child promotion v18.12

The physical nonlinear state has all 376 KKT variables, including the explicit
event multiplier.  Individual residual blocks are not required to decrease,
and neither the global step nor the child reconstruction is constrained to the
path taken by the previous iterate.

The promoted trial reduces the independently evaluated total square-KKT norm,
preserves the eta domain, and reconstructs a complete persistent child.  The
child chart is recomputed from all 26 child variables before selecting 14
independent coordinates for the 14 physical boundary rows.  Trust regions,
backtracking and chart selection remain numerical controls rather than BHSM
equations.
