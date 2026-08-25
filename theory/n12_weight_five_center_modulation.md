# N12 weight-five center modulation

Status: `EXACT_WEIGHT_FIVE_CENTER_FORCE_OPERATOR_DERIVED_COEFFICIENT_SOLUTION_AND_UNIFORM_REMAINDER_OPEN`.

The first lower-weight term about the round expanding balance is now
separated directly from the retained action. It is exactly the sum of the
spatial-gravity term, the `3/A^2+3/B^2` curvature term, and the linear
identity-response curvature term `-localization*x_spatial/2`. It has uniform
scale weight five and no velocity dependence. ADM kinetic and cosmological
terms are weight seven; inverse inertia and the boundary Casimir are not
included in this weight-five component.

Put `epsilon=R4^-2`. Since `D_tau epsilon=-2H0 epsilon`, the first particular
center correction has descriptor exponent `sigma=-2H0`. On the 25-coordinate
physical quotient its exact inverse-free equation is

`(A7+2H0 E7) X5=(0,-D_q_phys L5,-D_m L5)`.

This is the requested singular Feshbach/Dirac lift in bordered KKT form. The
combined weight-seven Euler--Dirac block is not inverted. The exact spectrum
already proves that `-2H0` is neither a center nor a stable root, so the
physical bordered equation is algebraically unique.

The current N12 coefficient representation is nevertheless badly
conditioned: the float64 bordered matrix has condition number about
`3.69e11`. Therefore its coefficient solution, and any numerical eigenvalue
of relative order `R4^-2`, is not promoted. A high-precision or analytically
preconditioned nullspace/KKT evaluation is the next reproducibility object.

Formally, if a uniform full asymptotic expansion exists without an event or
domain stop, the equation gives
`D_tau log R4=H0+O(R4^-2)` and finite center drift, hence `H4->H0>0` on that
mathematical branch. This is not yet a theorem for the full retained
remainder. It neither excludes an event/stop nor proves Osgood decay. Under
the owner ontology, an infinite nonencapsulating continuation remains
nonrealized and outside the particle observable domain.

The physical finite-history Gate-7 force remains separately open on the
action-owned two-sided Calderon oracle.

`FULL_BHSM_COMPLETE=false`.
