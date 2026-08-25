# N12 compact finite-history operator and two-boundary Weyl jet

Let `H_fin` be the nonempty local family certified by the chronology

`E0 -> C1 ->[T>0] E1 -> C2`.

For each regular member, proper time and the two endpoint labels are intrinsic.
Write `x_xi(tau)=log R4(tau;xi)` for the radius coefficient obtained from the
retained action solution.  The compact quadratic operators in a fixed round
spatial channel are

`K_c(xi)=-D_tau^2+c exp(-2 x_xi)`

and, for the factorized product-Dirac block,

`K_lambda,chi(xi)=A_lambda,chi(xi)^* A_lambda,chi(xi)`,

`A_lambda,chi=D_tau+chi lambda exp(-x_xi)`.

These formulas are the weight-resolved quadratic action.  They do not invert
the Euler--Dirac kinetic block.  For a history tangent `h=D_xi x[h]`,

`D K_c[h]=-2 c exp(-2x) h`,

`D A[h]=-chi lambda exp(-x) h`,

`D K_lambda,chi[h]=(D A[h])^* A+A^* D A[h]`.

The boundary space is the ordered pair `(birth,new_event)`.  Its conormal is
`(-p_birth,+p_new_event)`, where `p=D_tau u` in a scalar channel and `p=A u`
in a factorized Dirac channel.  Both endpoint traces are free Calderon data;
no Dirichlet, Neumann, Robin, periodic, terminal-return, or validation-cutoff
condition is imposed.

For the fundamental transfer

`(u_1,p_1)^T = [[a,b],[c,d]] (u_0,p_0)^T`,

the regular `b != 0` chart gives the exact two-boundary Weyl matrix

`M_C=[[a/b,-1/b],[c-da/b,d/b]]`.

The transfer and its first and mixed geometry jets satisfy a triangular
variational ODE.  Consequently `M_C`, `D_xi M_C`, and `D_xi D_eta M_C` are
obtained by scalar products and solves on the `b` chart, without forming an
operator inverse.  The Wronskian identity `ad-bc=1` makes this matrix
Hermitian on a real negative-axis resolvent probe.

Endpoint-time motion is part of the physical jet.  On normalized proper time
`s in [0,1]`, `tau=T(xi)s` and the generator is `T(xi)G(xi,s)`.  Its mixed jet
is

`D_hD_k(TG)=T_hk G+T_h G_k+T_k G_h+T G_hk`.

Thus varying duration is carried by the same action family; it is neither a
cutoff nor a fixed external parameter.

Exact internal gauge directions have zero induced coefficient and endpoint
variation.  A common translation of the proper-time origin is absent from
this intrinsically endpoint-labelled representation, so the construction is
already on the time quotient.  The common-scale direction is not removed:
it has `D x=1` and acts nontrivially on every nonzero spatial channel.  It
therefore remains a physical force and Hessian direction.

The certified terminal reset root supplies the endpoint/event-child stratum,
its full rank-57 reset normal, its 139-dimensional tangent, and its
73-dimensional child projection.  The remaining numerical input for an
actual value of `M_C(xi)` is the action-generated coefficient path
`x_xi(tau)` and its Jacobi path on this already-proved finite-history family.
That is an operator-realization task, not a reopening of history existence or
reset/recurrence semantics.

HINDSIGHT: the compact two-boundary action form, its moving-duration jet, and
the physical common-scale response are BHSM-action requirements.  A separate
explicit time-slice generator is not required for the first force because the
proper-time endpoint-labelled representation is already intrinsic.  A free
terminal boundary condition and recurrence were historical/imported
requirements and are not part of this operator.

`FULL_BHSM_COMPLETE=false`.
