# Resolved coordinate error in the stored signed center

The complete signed center has a positive radius screen. Its first coordinate
error bound used one infinity-norm solve error for every row of the U/C basis.
Diagnostic transport of that coarse bound gives a coefficient about 3.46e17,
which obstructs the resulting stored upper polynomial. This is a bound
obstruction, not root nonexistence. The old result and diagnostic are retained.

For the same exact binary64 S, M and approximate coordinates A, the new bound
encloses `D = S^-1 M - A` directly with 512-bit Arb. It retains separate U and C
blocks, without changing the basis, center, tensor, or approximation. An inverse
residual below one is checked and all enclosure entries must be finite.

Let a_U, a_C bound the operator norms of A's two row blocks, and e_U, e_C those
of D. Let q_UU, q_CU, q_CC bound the Frobenius norms of the corresponding stored
tensor blocks, including the output index. Expansion of
`(A+D)^T Q (A+D) - A^T Q A` and the matrix Frobenius/operator inequalities give

`E <= q_UU (2 a_U e_U + e_U^2)`
`   + 2 q_CU (a_U e_C + a_C e_U + e_U e_C)`
`   + q_CC (2 a_C e_C + e_C^2)`.

Each operator norm uses the smaller of its Frobenius bound and the square root
of the infinity-norm bound on its signed Gram matrix. The Gram products are
formed in Arb before absolute values. This preserves cancellation without
assuming that any rounded matrix is exactly orthogonal.

The same stored midpoint output map L then gives local uniform quadratic
coefficient `2 ||L||_2 E`. The factor two accounts for concatenating two endpoint
vectors, each of norm at most r_T. Signed products of the same stored causal
maps transport these coefficients with the existing Arb error-transport helper.
Recomputed causal maps must match the completed center's stored maps exactly.
All six historical local operands must match the earlier certificate's hashes.
The historical target uses raw partition axes, whereas the complete center
normalizes those axes before the kinematic map normalizes them again. These
paths can differ in their last bits. The new certificate reproduces the exact
center path and independently bounds its solve error, recording both sets of
operand hashes and every target mismatch. It never uses a tolerance to accept
a changed historical operand, or silently applies the old solve certificate
to a different target. The historical reports remain unchanged.

The report also evaluates a stored polynomial with coordinate and previously
certified storage-error coefficients added outwardly to both transverse
quadratic output coefficients. Because these two errors occur simultaneously,
it also includes their UU cross term:

`E_cross <= (2 a_U e_U + e_U^2) (||L||_2 E_projection + ||L[:,98]||_2 E_addition)`.

This compares storage error transported through exact coordinates with the
earlier storage certificate's transport through approximate coordinates. The
local pair factor two and the same causal transport are then applied. The
old storage certificate's midpoint input/output map hashes must match the
actual center operands exactly. This avoids dropping a product of two error
sources when combining their individual certificates.

That screen still omits physical direction,
Hessian, output/causal-map construction, assembly, covariance, and neighborhood
errors. It cannot close Gate 7 or establish physical contraction. Deterministic
reports must be materialized twice with byte-identical output.
