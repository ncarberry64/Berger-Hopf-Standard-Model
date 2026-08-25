# N12 terminal child-quotient operator jet

Status: `TERMINAL_CHILD_QUOTIENT_CAUCHY_JET_RANK_TWO_CERTIFIED`.

The certified reset tangent has dimension 139.  Its projection to the child
state has rank 73, while the 66-dimensional kernel changes only the prior
event lift.  On an orthonormal basis of this 73-dimensional action-coordinate
child image, differentiate the terminal coefficient data

`x_E=log R4(E1)`, `H_E=D_tau log R4(E1)`.

The resulting map

`A_E:h -> (D_h x_E,D_h H_E)`

has rank two.  Thus the actual terminal scalar and product-Dirac coefficient
jets vary in two independent child directions before the intrinsic time
quotient.  Since that quotient is one-dimensional, it cannot remove all
coefficient variation.  The common scale remains a physical direction.

For a scalar channel the fixed-duration coefficient part is

`D_h M_C=T[-2c exp(-2x_E) h_E] A+O(T^2)`.

For a product-Dirac channel, with `s=chi lambda exp(-x_E)` and
`s_dot=-s H_E`,

`D_h s=-s h_E`,

`D_h s_dot=-s_dot h_E-s D_h H_E`,

`D_h q=-2s^2 h_E`.

These give `D_h C` and `D_h B` in

`M_C=T^(-1)L+C+TB+O(T^2)`.

The total physical derivative is not obtained by fixing duration.  With
`T_h=D_h T`, the exact displayed-order chain rule is

`D_h M_C=-T_h T^(-2)L+D_h C+T_h B+T D_h B+remainder`.

Consequently the terminal action data certify the coefficient portion of
`D_xi K` and `D_xi M_C`, while the total derivative still requires the
action-owned `T_h` and the interior Jacobi path.  Neither is set to zero by
convention.

HINDSIGHT: separating coefficient motion from endpoint-duration motion is
action required.  A fixed-duration derivative is a useful partial jet, not
the total physical common-scale force.

`FULL_BHSM_COMPLETE=false`.
