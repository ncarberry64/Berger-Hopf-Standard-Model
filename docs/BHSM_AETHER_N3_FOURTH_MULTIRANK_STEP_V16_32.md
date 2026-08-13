# BHSM v16.32: fourth fresh multirank N=3 step

v16.32 tests all four numerical ranks of the v16.31 physical KKT at five
Newton fractions. Candidate selection uses the complete nonlinear residual,
exact event-multiplier projection, and eta-domain preservation.

Status is validated only if a candidate lowers the joint residual. The N=3
saddle and downstream common pushforward remain open until simultaneous
closure is actually reached.
