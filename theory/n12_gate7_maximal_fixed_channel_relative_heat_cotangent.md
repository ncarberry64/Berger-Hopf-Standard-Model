# Gate-7 maximal fixed-channel relative heat cotangent

Status: `MAXIMAL_FIXED_CHANNEL_INCOMING_RELATIVE_HEAT_COTANGENT_DERIVED`.

Fix one retained angular channel and the certified fixed-terminal
incoming-amplitude family.  Let `P_D` be the action-owned maximal C2
Friedrichs operator with zero seam trace used only as the boundary-triple
reference, and let `P_C` be the same child operator with the incoming
compliance `C=C_f` attached through the complete internal event-frame load

`L(z)=U_R^dagger M_C2^max(z)U_R+W_phys`.

This reference does not replace the physical operator and is not counted as a
second determinant.  Krein's resolvent identity gives, up to the fixed
conormal sign convention,

`R_C(z)-R_D(z)=-gamma(z) G_S(z) gamma(z_bar)^dagger`,

where

`G_S(z)=C/(1+C L(z))`.

The difference has rank at most one in each retained scalar channel.  Since
the child, reset frame, and contact are fixed along this amplitude direction,

`D[R_C(z)-R_D(z)]=-gamma(z) (D C)/(1+C L(z))^2 gamma(z_bar)^dagger`.

Thus a separate `D M_C2^max`, `D U_R`, or `D W_phys` is not part of this
direction.  On `z=-kappa^2<0`, positivity gives the already-certified
contraction

`|D G_S|<=|D C|`,

and the Weyl derivative identity identifies the rank-one trace norm with the
Poisson norm squared.

Two semibounded self-adjoint extensions with finite-rank resolvent difference
have trace-class relative heat evolution for every positive heat time.  The
same Krein formula is differentiable in the compliance chart, including the
one-sided Dirichlet limit `C=0`.  Consequently the fixed-channel incoming
heat cotangent is the trace-norm convergent relative functional-calculus
quantity

`D Gamma_heat,h=-(1/(4 pi i)) integral_Gamma exp(-z) Tr(D R_h(z)) dz`.

Because `D_lambda C_f=O(lambda)`, this maximal fixed-channel heat cotangent is
also `O(lambda)` at the zero-length birth limit.  No arbitrary far endpoint
or absolute infinite-volume heat trace is required for this source-contracted
statement.

The direct sum over all angular levels is a separate question.  Rank one per
channel does not imply trace class after the retained quadratic
multiplicities are summed, and the existing angular-uniformity counterexample
still applies.  Therefore this theorem establishes the exact maximal
fixed-channel cotangent and its reverse seed, but neither the full graded
cotangent nor the physical projected Cauchy tail or KKT root.

Only the external Cauchy/birth datum is zero.  No internal response is zeroed,
no reference determinant is added to the action, and no seam force, selector,
endpoint, recurrence condition, scale, fit, gate, or chord is introduced.
