# N=12 asymptotic bordered graph norm

Status: `ACTION_OWNED_BORDERED_GRAPH_PRECONDITIONER_DERIVED_NONLINEAR_RELATIVE_BOUND_OPEN`.

Let

`B_-2=A7+2 H0 E7`

be the physical 74 by 74 bordered recurrence pencil governing the first
`epsilon=R4^-2` lift.  It retains all algebraic multipliers and quotients only
the twelve certified time/lapse chains.  Let `W` be the diagonal weight map
of the common `H6_q x H5_v x H6_m` product chart.  Define

`||X||_graph = ||W^-1 B_-2 X||_2`.

This is an action-owned graph norm.  It does not form or store
`B_-2^-1`, and it does not invert the ill-conditioned kinetic/Dirac block.
The directed Arb theorem already proves that `B_-2` is injective by solving
the particular bordered equation with residual balls containing zero and by
certifying its algebraic multiplier block.

For the first lower-weight lift,

`B_-2 X5=b5`,

so its graph norm is exactly the dual product norm of the action-owned source:

`||X5||_graph=||W^-1 b5||_2`.

Direct Arb evaluation gives a value of order `3.94`.  In contrast, the
coefficient product norm of the same `X5` is of order `5.68e13`.  The ratio is
about `6.94e-14`.  This is not a contradiction: it exposes the weak
high-frequency geometric directions of the bordered operator.  An
unpreconditioned inverse norm would amplify those directions and is therefore
the wrong proof object.

The quantitative nonlinear theorem must now bound the relative graph defect

`W^-1 [B(Y)-B_-2] X`

on the intersection of the geometric product ball and a bordered graph ball.
A Krawczyk/Neumann enclosure may use repeated certified solves with `B_-2`,
but no explicit combined inverse is needed or authorized.  The required
inequality is a strict graph-relative defect below one, together with the
already derived geometric margins and a bound for the inhomogeneous retained
remainder.
