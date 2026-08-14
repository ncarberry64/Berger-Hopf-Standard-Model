# BHSM N=3 exact projected physical-merit gradient v18.10

The v18.05-v18.08 audits demonstrate that independently differenced vector
columns do not assemble into a sufficiently accurate directional Jacobian of
the nested projected residual.  This calculation differentiates the scalar
physical merit `0.5*||F_376||^2` directly in the 375 scaled base coordinates.

The physical action, event equation, residual normalization and 376-row KKT
system are unchanged.  The negative unit gradient is accepted as a response
direction only if independent centered directional differences give the same
negative merit slope.  Any nonlinear trial remains provisional until the
complete-child boundary and persistence gate passes.
