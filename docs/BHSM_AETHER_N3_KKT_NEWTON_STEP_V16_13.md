# BHSM v16.13: safeguarded N=3 KKT Newton step

This calculation differentiates the v16.12 common-pushforward covector to
assemble the full symmetric 376 by 376 event-KKT Jacobian at the independently
reintegrated N=3 seed.  The soft-event covector is the off-diagonal constraint
block.  The indefinite Newton equation is solved without replacing the event
or separating the gauge and HS/fermion determinants.

The unrestricted direction is restricted in the declared scaled coordinates,
then backtracked.  A trial is admissible only if every node retains positive
eta-Legendre margin and the complete scaled KKT residual decreases.
