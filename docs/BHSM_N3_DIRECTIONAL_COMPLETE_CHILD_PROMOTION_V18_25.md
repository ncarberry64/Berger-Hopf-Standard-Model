# BHSM N=3 directional complete-child promotion v18.25

This calculation performs the final physical gate on the v18.22 exact-merit
candidate.  It imports the independently recomputed v18.24 whole child,
evaluates the resolved dynamic-flux envelope at two central-difference scales,
and evolves ten constraint-projected positive-time steps.

The global solve remains the square 376-variable explicit-multiplier KKT.  No
componentwise monotonicity or previous-path condition is used.  The moving
child is promoted only if trace, all seven constraints, attachment momentum,
two-scale flux, eta hyperregularity and persistence all close.
