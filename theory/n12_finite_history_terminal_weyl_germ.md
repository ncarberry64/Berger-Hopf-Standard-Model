# N12 finite-history terminal Weyl germ

Status: `ACTION_OWNED_TERMINAL_WEYL_LAURENT_GERM_CERTIFIED`.

Let `T>0` be the proper duration of a member of the certified local history
family and let `x_E=log R4(E1)`.  The endpoints remain the free ordered
Calderon traces `(birth,new_event)`.  No endpoint condition is imposed.

For a scalar spatial channel `c`, put

`q_E=c exp(-2 x_E)-z`,

`L=[[1,-1],[-1,1]]`, and

`A=[[1/3,1/6],[1/6,1/3]]`.

Direct expansion of the inverse-free transfer equation and the regular
`b != 0` Weyl chart gives

`M_C(T,z)=T^(-1)L+T q_E A+O(T^2)`.

The fixed-duration coefficient contribution in the retained common-scale
direction `D x=1` is

`D M_C(T,z)=-2T c exp(-2x_E) A+O(T^2)`.

For a factorized product-Dirac channel define

`s_E=chi lambda exp(-x_E)`, `s_dot_E=-s_E D_tau x(E1)`, and
`q_E=s_E^2-z`.  Then

`M_C=T^(-1)L+diag(-s_E,s_E)+T B_E+O(T^2)`,

where

`B_00=(q_E+2s_dot_E)/3`,
`B_11=(q_E-s_dot_E)/3`, and
`B_01=B_10=(q_E-s_dot_E)/6`.

Its fixed-duration common-scale coefficient derivative has constant term
`diag(s_E,-s_E)` and the
duration coefficient obtained from `D s_E=-s_E`,
`D s_dot_E=-s_dot_E`, and `D q_E=-2s_E^2`.  The constant terms cancel
between a chirality pair, while the paired duration response is nonzero.

These are actual action-owned `M_C` and fixed-duration coefficient parts of
the `D M_C` Laurent germs on the
nonempty positive-duration family; no value of the desingularized history
parameter is selected.  They certify nontrivial operator response, but they
do not by themselves evaluate the zero-source heat-minus-zeta force.  That
force is a complete spectral trace of the self-adjoint event-child operator,
not the value or derivative of one Weyl matrix at one spectral probe.  Its
next input is the complete spectral-family assembly (or equivalent joint
forward-operator-adjoint KKT solve) on the same action-owned family.

HINDSIGHT: the Laurent germ and common-scale response are action required.
A single resolvent probe, a terminal boundary condition, and a selected
positive duration are not substitutes for the complete force trace.  The
total physical derivative additionally contains the action-owned moving-
duration term.  For `M=T^(-1)L+C+TB+...`, it is

`D M=-T_h T^(-2)L+D C+T_h B+T D B+...`.

`FULL_BHSM_COMPLETE=false`.
