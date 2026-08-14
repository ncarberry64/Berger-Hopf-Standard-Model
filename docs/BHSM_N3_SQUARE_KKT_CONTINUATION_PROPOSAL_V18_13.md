# BHSM N=3 square-KKT continuation proposal v18.13

This calculation continues directly from the complete-child-promoted v18.12
state.  The physical nonlinear problem remains the square 376-variable KKT
system with its event multiplier explicit.

The inherited v17.58 response matrix is retained only as a trial-proposal
model; its invalidated derivative interpretation is not restored.  Every
trial is independently evaluated with the exact v17.61 action covector and
event equation.  Eligibility uses reduction of the total 376-row physical
merit and an admissible eta domain.  Complete-child reconstruction and
persistence remain mandatory before promotion.

No componentwise residual monotonicity or previous-iterate-path condition is
imposed.  Trust radius and backtracking are numerical reliability controls,
not physical equations.
