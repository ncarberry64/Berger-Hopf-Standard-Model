# N12 constraint-projected replacement saddle

Status: `EXACT_CONSTRAINT_TANGENT_FORCE_CRITERION_DERIVED_JOINT_PHYSICAL_SADDLE_OPEN`.

Let the retained event-child constraint surface be `C(y)=0`, let
`J=D C(y)`, and let the columns of `N` be an orthonormal basis of `ker J`.
At a constrained root of the classical action, replacing the zeta term by
the heat functional changes the geometry covector by

`q_rep=D_y Gamma_heat-D_y Gamma_SM_zeta`.

The same configuration remains a root of the replacement action exactly
when

`N^dagger q_rep=0`.

Equivalently, the replacement load can be absorbed by a change of KKT
multiplier,

`q_rep+J^dagger(lambda_rep-lambda_class)=0`.

Thus ambient `q_rep=0` is sufficient but not necessary.  A nonzero force in
the constraint-normal space is not a physical tangent force.  This
distinction is mandatory for the set-valued reset relation: selecting an
arbitrary child representative and testing an ambient component would add a
selector not owned by the action.

The actual fixed-event child reset Jacobian is `31 x 98`, has rank 31, and
has a 67-dimensional tangent kernel.  Its boundary `log R4` covector has
tangent projection norm `0.1847862958485751`.  This proves that the reset
fiber contains genuine geometry-changing directions; it does not establish
the value or sign of the unknown quantum force.  A constructed nonzero row-
space covector has zero tangent projection and is absorbed by a multiplier,
which directly verifies the theorem on the certified Jacobian.

If `N^dagger q_rep` is nonzero, the physical task is the joint constrained
saddle

`D Gamma_total(y)+J(y)^dagger lambda=0`, `C(y)=0`.

Its linearized tangent correction obeys

`(N^dagger H_total N) delta_xi=-N^dagger q_rep`.

The independently assembled bordered system

`[[H_total,J^dagger],[J,0]][delta_y,delta_lambda]^T=[-q_rep,0]^T`

produces the same ambient correction on the certified reset Jacobian.  This
cross-check never forms an inverse of the ambient Hessian or kinetic block.

The required `H_total` is the geometry/reset KKT Hessian used to locate the
zero-source saddle.  It is distinct from the downstream pair-plus-contact
source Hessian `D_A^2 Gamma`.  Gate stages G7_08 and G7_09 are therefore
mathematically coupled, but no new gate is introduced.

The current broad negative-axis AE2 seam intervals do not determine the
projected heat-minus-zeta trace covector or the geometry KKT Hessian.  The
next required object is the actual joint finite-history operator with its
complete geometry/reset jet and constraint-reduced Hessian.  Neither the
projected force, its sign, nor the same-action saddle is closed here.

`FULL_BHSM_COMPLETE=false`.
