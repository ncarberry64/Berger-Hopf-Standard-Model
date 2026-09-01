# N12 C2 desingularized coefficient germ

Status: `C2_PHYSICAL_EVENT_U_COEFFICIENT_GERM_STRICTLY_OUTGOING`.

Let `t` be the retained forward coordinate time, `d tau=N dt` the positive
proper-time lapse conversion, and

`u=lambda_event^2`.

At the actual reset-selected C2 birth the event eigenvalue vanishes, so the
pole-cancelled action identity reduces exactly to

`D_t u(0)=2 c_psi b_psi`.

The certified outgoing event intervals make this quantity strictly positive.
The certified C2 lapse interval then gives

`D_tau u(0)=2 c_psi b_psi/N > 0`.

Thus `u` is an intrinsic one-sided local time coordinate on the outgoing C2
branch.  It is not a new physical clock: it is the square of the already
retained selected event eigenvalue and is used only to remove the Euler--Dirac
soft pole.

For `x=log R4` and `H=D_tau x`, the C2 birth certificate gives `H>0`.
Consequently the inverse-function and chain-rule identities give

`x(u)=x0+[N H/(2 c_psi b_psi)]u+o(u)`

with a strictly positive certified interval for the displayed slope.  The
outgoing C2 radius therefore increases on some nonzero regular one-sided
segment.  Combining this with the channel-transfer germ gives

`T(u)=I+[N/(2 c_psi b_psi)]u G0+o(u)`.

This establishes the correct desingularized coefficient and transfer
directions without choosing a positive history member or a future endpoint.
It also localizes the next numerical theorem exactly.  To replace the germ by
an explicit validated segment, one needs neighborhood bounds for the
pole-cancelled `u`-chart vector field and its first physical quotient Jacobi
map, including variation of `2 c_psi b_psi/N`, `H`, the selected eigenline,
and all retained domain margins.  Those are analytic continuation bounds,
not missing C2 physics.

No validation edge is promoted to an AE2 event or canonical stop.  The full
maximal `M_C2`, zero-source force, saddle, and Hessian remain open.

`FULL_BHSM_COMPLETE=false`.
