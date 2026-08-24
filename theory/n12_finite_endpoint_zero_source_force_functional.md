# N12 finite-endpoint zero-source force functional

Status: `EXACT_FORCE_FUNCTIONAL_DERIVED_CURRENT_OPERATOR_REALIZATION_OPEN`.

On any retained positive self-adjoint finite-endpoint realization, the heat
part of the zero-source quantum functional is

`Gamma_heat(P)=Tr[-(1/2) E1(ell^2 P)]`.

For an action-owned geometry variation `delta P`, including one that does not
commute with `P`, cyclicity of the trace gives

`D Gamma_heat(P)[delta P]=(1/2)Tr[exp(-ell^2 P) P^(-1) delta P]`.

The current gauge, ghost, rank-16 Weyl, and HS direct sum is obtained by
summing this expression with its already-retained signs and multiplicities.
The formula is basis independent.  Compact resolvent and the positive
nonzero-sector quotient gap make it finite on the owner-authorized finite
encapsulation domain.

The implementation is checked three ways: against a noncommuting centered
finite difference, under a nontrivial unitary change of basis, and against the
historical force engine on one identical periodic matrix block.  The last
check verifies only the shared matrix-function derivative.  It does not
transfer the historical 24-node periodic value to the current forward
event/child problem.

The fixed-event child Jacobian also shows why the reset relation alone cannot
close this evaluation.  Its 67-dimensional kernel has rank 33 in the child
geometry coordinates (at least 32 after removal of any one time direction),
and the boundary `log R4` covector has a nonzero projection into that kernel.
Thus the reset relation does not hold the operator geometry fixed.  This does
not disprove a separate force-invariance theorem, but invariance cannot be
inferred from reset regularity.

The current numerical force and its sign remain open.  The local pre-event
theorem proves that a finite encapsulation branch exists, but it does not yet
materialize the complete coefficient path, the temporal form matrix, or the
operator geometry jet on that branch.  The reset relation is also set-valued,
and force invariance over its fiber has not been proved.  Selecting one member
or a Robin/periodic endpoint by hand would add unowned physics.

The exact next object is therefore a validated finite-history operator oracle
constructed from the retained Euler--Dirac branch and event/child graph.  It
must supply `R4(tau)`, `D_tau`, the action-owned endpoint form, and
`D_Phi P`.  The reset-fiber variables must either be solved jointly with the
same-action saddle or eliminated by a proved force-invariance theorem.
