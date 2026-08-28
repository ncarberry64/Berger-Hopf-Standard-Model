# N=12 Gate-7 recentered-cone bordered-response second variation

The first rigorous second-variation majorant is now assembled on the same
24,072 child cells and 3,009 parent cones as the certified zero- and
first-order bordered responses.

For the selected line, differentiating its bordered eigenproblem twice gives

`B psi_2 = -((H_2-lambda_2 I)psi + 2(H_1-lambda_1 I)psi_1, ||psi_1||^2)`.

The last component is the differentiated normalization condition and is not
dropped.  The parent certificate stores one half of the uniform `D4` Hessian
Taylor term.  Twice that term, multiplied by the square of the exact
child-to-parent common-frame lift, bounds `H_2` on each child cell.

The complete internal response then obeys

`K x_2 = f_2 - K_2 x - 2 K_1 x_1`.

All signed terms are assembled before applying the certified bordered solve
bound.  No kinetic, Euler--Dirac, or history inverse is formed.  Only the
external birth/Cauchy source is zero; every retained internal child, contact,
transport, and scalar response remains in `f_2`.

The resulting ambient tube is finite everywhere.  Its largest second
response majorant is approximately `4.413e20`, owned by seam 45 on
`[91.99609375, 92.0]`.  This large number is a conservative ambient
conditioning bound, not a physical instability or a causal-radius result.
The next mandatory operation is the signed Green/reverse-adjoint common-frame
contraction before norms.  Until that contraction closes, the projected
Cauchy tail, causal interval-vector radius, first-hit transfer, and Gate 7
remain open.
