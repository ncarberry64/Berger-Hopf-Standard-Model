# BHSM v16.23: N=3 rank-aware trust-region step

This calculation acts directly on the v16.21 diagnosis. It diagonalizes the
refreshed symmetric 376-variable KKT Jacobian and probes truncated spectral
Newton directions at relative cutoffs from `1e-8` through `1e-14`. Each
direction is restricted to a bank of physical trust radii, the event
multiplier is projected exactly at the candidate base point, and the complete
nonlinear residual and eta-domain condition are evaluated.

No action row, endpoint law, derivative stencil, quadrature weight, field, or
normalization is changed. A residual-reducing candidate advances the same N=3
saddle solve. If no candidate reduces the residual, that is evidence to
redirect to the already measured derivative/quadrature consistency defect,
not a reason to end the BHSM campaign.
