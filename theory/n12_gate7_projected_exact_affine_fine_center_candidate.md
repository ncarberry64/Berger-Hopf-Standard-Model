# N12 Gate-7 projected exact-affine fine-center candidate

The current center cannot be obtained by projecting the native DOP853 path
alone.  First compose the certified 256-bit Taylor26 signed-source response
with the native base and reconstruct the coupled descriptor as the retained
direct descriptor term plus `Dlambda` applied to the exact-affine state
response.  Only then apply the action constraints.

At each of the 371 fine nodes, form the direct 25-row action constraint
differential and take one minimum action-norm Newton step.  The resulting
states are a discrete constraint-accurate candidate carrying the certified
exact-affine source response and its outward evaluation radius.

The Newton projection is larger than the existing final nonlinear cone radius,
so that cone, the descriptor-fiber equality, and the first hit cannot be
inherited.  A dense flow-defect rebuild and a constraint/fiber-augmented
collocation or shadowing theorem are required before the center is promoted.

`FULL_BHSM_COMPLETE = FALSE`.
