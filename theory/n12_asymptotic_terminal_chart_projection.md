# N=12 asymptotic terminal-chart projection

Status: `NONLINEAR_98_TO_74_COMPACTIFIED_TERMINAL_PROJECTION_DERIVED`.

The retained state ordering is `(q,qdot,m)` with dimensions `37+37+24`.
The exact time/lapse-chain quotient keeps the 25 coordinate indices

`q0,w_0,...,w_11,b_0,...,b_11`.

Let `x=log R4(q)` be the exact boundary attachment.  The common-scale
coordinate after subtracting the represented round expanding scale is

`q0_tilde=q0-x+log(RADIUS0/2)`.

Its coordinate-time velocity normal is

`dot q0_tilde=dot q0-Dx(q)[qdot]`.

Together with the retained `w,b` coefficients, their velocities, and all 24
algebraic lapse/shift multipliers, these formulas give the exact declared
74-component target ordering `(a,eta,m)`.  The compactification is evaluated
as

`log epsilon=-2x`

rather than first forming `epsilon=exp(-2x)`.  This is mathematically
equivalent and remains numerically meaningful at the certified Gate-7 scale
`epsilon<10^-2151`, where binary64 exponentiation underflows.

The radius attachment is affine except for the boundary `b` combination.
Consequently its full Hessian and only nonzero third derivative are explicit.
The repository implementation supplies the first and mixed-second jets of
`log epsilon`, normalized epsilon, and all 74 descriptor coordinates.  It
also accepts the mixed second derivative of an upstream state family, so it
can be composed directly with interval multiple shooting or a degree map.

On every exact weight-seven center-family member, the velocity normal is zero.
On a round member the entire 74-vector is zero for arbitrary positive round
scale.  A replay at the certified capture radius therefore reaches the chart
origin without numerical underflow.  The stored finite-core proof center is
far outside the capture tube; that replay is diagnostic only and is not a
selected history.

This closes the terminal transition type and its requested jets.  It does
not propagate the reset family to the terminal chart, certify a later stop,
or solve the Gate-7 force/KKT system.  The sole geometric owner is now the
validated nonempty reset-set connection (or degree/intersection theorem) to
strict tube inclusion or the first retained canonical stop.
