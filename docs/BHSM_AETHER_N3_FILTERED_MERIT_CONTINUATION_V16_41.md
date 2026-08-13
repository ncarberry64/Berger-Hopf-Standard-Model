# BHSM v16.41: spectrally filtered N=3 merit continuation

Hard eigenvalue truncation began trading residual between coordinate and
multiplier blocks. v16.41 therefore tests a continuous rank-aware
Levenberg–Marquardt filter on the same fresh symmetric KKT Jacobian:

`d = -V diag(lambda/(lambda^2+mu^2)) V^T R`.

Four filter scales and seven step fractions are evaluated with the complete
nonlinear residual, exact event-multiplier projection, and eta-domain check.
This changes only the numerical solver, not the action, constraints, event,
field content, or normalization.
