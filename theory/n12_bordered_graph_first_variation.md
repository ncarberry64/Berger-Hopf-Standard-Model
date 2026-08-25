# N=12 bordered graph first variation

Status: `DIRECTED_STRUCTURED_D3_GRAPH_JET_CERTIFIED_D4_REMAINDER_OPEN`.

Let `B0=B_-2` be the 74-dimensional physical bordered recurrence and let
`W` be the common `H6_q x H5_v x H6_m` product weight.  For a normalized
product-coordinate direction `e_k`, define

`A_k=(W^-1 B0 W^-1)^-1 W^-1 DB0[W^-1 e_k] W^-1`.

This notation does not authorize or require an explicit inverse.  Each
`A_k` is enclosed by solving the fixed directed Arb bordered system with the
corresponding 74-column right-hand side.  Every computed residual ball
contains zero.

The derivative `DB0` is action-owned.  Its Hessian variation is the sparse
third variation `D3 L7` of the exact local weight-seven action.  The
recurrence is also differentiated through every explicit expansion-rate
coefficient: the top `2 H` block and the `7 H` and `5 H` Euler--Lagrange
blocks.  Omitting those terms would miss the dominant `dot_q0` direction.

The local cubic action tensor has only 60 nonzero symmetric entries, or 295
ordered entries.  A 128-node Legendre-Arb quadrature with an exact inflated
global Gauss remainder encloses every projected cubic coefficient.  The
remainder radius is below `7.48e-20`.

For `y=sum_k y_k e_k`, Cauchy--Schwarz and the Frobenius norm give

`||sum_k y_k A_k||_2 <= ||y||_2 (sum_k ||A_k||_F^2)^(1/2)`.

The directed repeated solves certify

`M3=(sum_k ||A_k||_F^2)^(1/2) <= 2.36904215393145e17`.

Thus the linearized relative graph defect is at most `M3 rho` on a product
ball of radius `rho`; in particular it consumes at most one half at the
directed positive radius

`rho_3^- = 1/(2 M3) >= 2.11055763262940e-18`.

This is a strict improvement over the determinant/Frobenius existence
fallback and proves that the structured first nonlinear jet is finite.  It
does not certify the full nonlinear defect on that ball.  The next theorem
must supply a uniform action-owned `D4 L7` (and lower-weight full-action)
remainder whose contribution is strictly below the unused one-half budget.
Until then no quantitative capture surface or reset overlap is promoted.

No selector, scale, fitted threshold, endpoint, action term, time direction,
gate, or chord is introduced.  Gate 7 remains active, Gate 8 remains locked,
and chord 3 remains unauthorized.
