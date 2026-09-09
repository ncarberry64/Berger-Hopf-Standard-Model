# Stored pullback assembly arithmetic

All operands in this certificate are exact stored binary64 values. A fixed
alternative evaluates `L [X.T Q Y]` with three matrix multiplications: apply L
to Q's output index, then the left input, then the right input. Applying L first
preserves tensor-channel scale separation. It changes no stored center tensor:
the actual center algorithm is reproduced, and the difference between the two
stored results is itself enclosed. The alternative's analytic rounding bound
plus this exact-operand difference bounds the original algorithm's error.

For a length-k dot product in IEEE binary64 nearest rounding with gradual
underflow, use `g=gamma_(2k)` and absolute underflow bound
`b=2k eta sqrt(N)/(1-2k u)` for N output entries, where `u=2^-53` and
`eta=2^-1074`. If P is the stored auxiliary product of the absolute input
matrices, its own rounding gives the signed product's Frobenius error bound
`(g ||P||_F+b)/(1-g)`. This avoids treating the rounded positive product as exact.
The norm of P is independently enclosed. Signed operator norms propagate
previous-stage errors through subsequent multipliers. Symmetrization has
separately bounded addition and scaling errors; its exact operation is
nonexpansive in Frobenius norm.

Large tensor Frobenius norms use a scaled positive sum of squares, with division,
reduction, and underflow errors enclosed by scalar Arb arithmetic at 512 bits.
Overflow, nonfinite input, or an invalid operation-count bound fails closed.
The norm of the exact difference of two stored arrays also includes subtraction
rounding. Tests compare these bounds with independent rational sums and complete
multi-output contractions, including subnormal values.

For each of 370 intervals, reconstruct the original endpoint and midpoint
pullbacks, their final sum, and the sum of the two cross blocks. Enclose every
assembly and addition error. The exact stored polynomial represented by those
blocks differs from the exact-operand local Hessian pullback by at most
`2 E_tensor + E_cross` times the squared block-sup transverse radius. The factor
two accounts for the concatenated endpoint input. Every midpoint operand hash
must match the completed coordinate certificate. Reconstructed local and
adjacent covariances are compared with the complete center's stored arrays.
Every difference is retained with an outward Frobenius bound and both hashes;
no tolerance declares unequal arrays identical. The original center function
itself can reproduce a different last bit in an adjacent matrix product.

The existing signed causal transport encloses the complete-chain effect of
these local errors through exact stored maps. Construction errors in maps and
coordinates and storage errors in tensors are separate additive obligations
with their already documented cross terms. Covariance formation/propagation
rounding and reconciliation to the saved covariance arrays are still separate
obligations. This certificate bounds the reconstructed local tensors and does
not silently assign them the saved center's covariance-based response bounds.
Physical Hessian/direction errors and neighborhood
remainder remain open. Gate 7 and full BHSM completion remain false.
