# Gate-7 constraint/descriptor Hermite collocation candidate

Start from the 371 corrected Taylor26-plus-constraint-projection nodes.  At
each preterminal node, recenter the propagated descriptor to the selected
branch-24 eigenvalue and evaluate the retained normalized cancelled action
field.  On the last fine interval, interpolate the two constraint-projected
states, project the interpolant back to the 25-row constraint manifold, and
biselect the numerical branch-24 sign change.  Its midpoint is representative
only; binary64 eigensolver output is not outward root authority.

Relative to the retained DOP853 dense polynomial, join the resulting endpoint
corrections with cubics whose endpoint derivatives equal the retained field.
This is the same endpoint-field-matched construction already used by the
repository's correlated Newton-center audit.  Three Gauss nodes per fine cell
measure the flow defect, action-constraint residual, descriptor-fiber
residual, branch identity, and selected-line gap.

The result is a numerical collocation candidate.  Promotion requires the
existing Taylor--Volterra/Krawczyk machinery to enclose the continuous defect,
nonlinear remainder, constraints, descriptor fiber, and first hit.

`FULL_BHSM_COMPLETE = FALSE`.
