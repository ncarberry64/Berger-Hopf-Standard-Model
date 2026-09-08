# Continuous adjudication of the stored signed-center radius map

The signed center retains its original finite radius-grid screen. A negative
grid result alone does not establish an obstruction. The additional consumer
uses exactly the stored binary64 coefficients and the original common radius
ceiling. It does not alter the action, center, mesh, tensors, norm, or grid.

For nonnegative coefficients the map is

`F_i(r) = Y_i + sum_j Z_ij r_j + C_i r_L^2 + 2 M_i r_L r_T + T_i r_T^2`.

The continuous search writes `r_i = ceiling exp(x_i)`, `x_i <= 0`, and minimizes
an epigraph bound on `log(F_i(r)/r_i)`. Each such log ratio is a log-sum-exp of
affine functions of x, so the optimization problem is convex. Nevertheless,
an optimizer's success flag is never evidence of a self-map. Each candidate
radius is converted to its exact binary64 rational value and both inequalities
`F_i(r) < r_i` are checked with rational arithmetic. The report retains exact
rational margins. This can recover narrow feasible regions between grid nodes.

A separate negative test iterates from zero using 80-digit Decimal arithmetic
with downward rounding at every nonnegative operation. Monotonicity gives
`lower[n] <= r` for any strict supersolution r. For every n >= 1 the bound is
strict: `lower[n] <= F(r) < r`. If a lower component reaches or exceeds the
declared ceiling, there is no strict supersolution within that ceiling for
this stored polynomial. Equality suffices because the requested inequalities
are strict. Stagnation, an iteration limit, a failed optimizer, or a candidate
without exact positive margins returns UNRESOLVED, never an obstruction.

These conclusions concern the supplied stored polynomial only. A polynomial
upper-bound obstruction does not prove nonexistence of a physical root.
A self-map witness does not itself establish contraction. Physical Hessian
evaluation errors, causal-map construction errors, remaining assembly errors,
and neighborhood remainders retain their separate proof obligations. Gate 7
and full BHSM completion remain false in this consumer's claim boundary.

The producer refuses incomplete signed centers, checks the center data hash
and original ceiling provenance, and preserves the original center report.
Materialize its deterministic report twice after the full center completes.
