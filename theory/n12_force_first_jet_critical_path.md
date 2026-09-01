# N12 force first-jet critical path

Status: `GATE7_FORCE_BASE_AND_FIRST_JET_IS_EARLIEST_OPERATOR_OWNER`.

The zero-source heat-minus-zeta force is a first geometry variation,

`F_h=(1/2) sum_C s_C m_C Tr[exp(-ell^2 P_C) P_C^-1 D_h P_C]`

minus the retained zeta first variation.  Therefore the earliest G7_08
evaluation requires the actual maximal child operator value and its first
physical reset-quotient jet.  It does not require the second operator jet or
the reset-stratum constraint curvature.

This follows directly from the triangular inverse-free Weyl solves:

`P_ii X=P_ib`,

`P_ii X_h=K_ib,h-K_ii,h X`.

Neither equation contains `D_xi2 K`.  The latter enters only the separate
second-jet solve.

The same triangular separation occurs one level earlier in the implicit
Euler--Dirac evolution.  The first vector-field jet solves
`D s_h=b_h-D_h s`; the retained action owns `D_h` through `D3 L`.  The
mixed second jet introduces `D_hk`, owned by `D4 L`.  Thus fourth action
derivatives remain required for the later second-operator-jet/Hessian branch,
but they are not a prerequisite for evaluating the first force covector.

The immediate critical path is consequently:

1. certify the maximal reset-stratum base and first state-Jacobi family to
   the first action-owned event or canonical stop using the retained `D3 L`
   and Dirac-margin controls;
2. assemble `K`, `D_xi K`, or equivalently `M_child`, `D_xi M_child`;
3. evaluate the full projected covector `N_phys^dagger q_rep`.

If that covector vanishes, the classical configuration transfers to the
replacement saddle and the program proceeds to the pair-plus-contact
Hessian.  If it does not vanish, the second operator jet, constraint/reset
curvature, and geometry KKT Hessian are then required to locate the new joint
saddle.  None of those later objects is deleted or assumed zero.

All physical tangent directions, or the equivalent assembled covector, are
required; no reset representative is selected.  No endpoint, action term,
scale, fit, gate, or chord is added.  Gate 7 remains active.
