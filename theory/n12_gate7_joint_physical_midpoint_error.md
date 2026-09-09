# Physical midpoint Hessian error with construction cross terms

At one fixed stored midpoint, complete physical row certificates enclose
E = D2F[S,S] - Q, where S is the exact stored full basis and Q the corrected
stored symmetric tensor. The complete kinematic certificate supplies
||X*-Xhat|| <= d, and the frozen output certificate supplies ||L*-Lhat|| <= e.

First use the signed output-first physical error pullback to bound
Lhat E[X*,X*], including the entrywise E radius and coordinate perturbation.
Then add

    e (||E_mid||F + ||E_radius||F) (||Xhat||2 + d)^2

for (L*-Lhat) E[X*,X*]. This includes the output/coordinate/physical-error
cross term. The correction tensor retains its computed signed center; the
new cross term enlarges its certified Frobenius radius.

The consumer requires a complete 370-point stored kinematic envelope and
all 99 physical rows for every requested midpoint. Physical and kinematic
bases, coordinate arrays, stored targets, output maps, states and tensors
must match. Each certificate is checked under its original hash schema.
Original and factored physical backends use distinct caches and provenance;
their mathematical operand bindings must match the kinematic operands.

    python scripts/certify_n12_gate7_joint_physical_midpoint_error.py --midpoints 0,175,126,1

Use --backend factored only for points computed by the explicitly fingerprinted
factored backend. Missing physical points are never assigned zero error.

This encloses the physical Hessian error at the selected stored midpoints,
with normalized stored kinematics and frozen output arithmetic. The stored
first derivatives and frames still need their physical identification and
common-projector consistency. Endpoint Hessians, remaining midpoints,
neighborhood variation and contraction remain separate obligations. No
physical observable, Museum spectrum or full-completion claim is made.
