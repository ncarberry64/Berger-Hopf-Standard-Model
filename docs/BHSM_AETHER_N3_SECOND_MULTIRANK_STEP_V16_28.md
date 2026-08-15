# BHSM v16.28: second fresh multirank N=3 step

v16.28 evaluates the four numerical ranks of the freshly rebuilt v16.27 KKT
system at five Newton fractions. Every candidate uses the complete nonlinear
action residual, exact event-multiplier projection, and eta-domain check.

The selection criterion remains the norm of the joint stationarity, period,
and soft-event equations. No block is declared solved in isolation and no
alternative event or mass-normalization mechanism is introduced.
