# First-HS intrinsic tangent endpoint candidate

The intrinsic 73-dimensional block correction is added to the first
Hermite--Simpson endpoint center in weighted action coordinates.  Every trial
endpoint is then passed through the retained nonlinear action-constraint
projection, descriptor recentering, selected branch-24 reconstruction, and
exact endpoint-field evaluation.  No terminal stop adapter is imposed before
the collocation center converges.

This is a numerical candidate.  The following all-midpoint replay decides
whether the intrinsic correction reduces the nonlinear shooting residual.
