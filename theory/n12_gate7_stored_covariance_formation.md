# Covariance formation and reconciliation

Reconstruct the complete center's local left/cross/right tensor blocks and
require each local tensor hash to equal the assembly-error certificate. The
target local covariances are exact `B B.T`; the adjacent target is exact
`B_right(previous) B_left(current).T`. Their supplied saved center arrays are
midpoints, not assumed exact products. The initial adjacent target is zero.

For each product, compute fresh signed and absolute binary64 products. With
`g=gamma_(2k)`, unit roundoff `u=2^-53`, and `eta=2^-1074`, the componentwise
dot error is bounded by `(g P + b)/(1-g)`, where P is the stored absolute product
and `b=2k eta/(1-2k u)`. This also encloses rounding of P itself. Add the exact
Arb difference between the fresh signed product and the saved midpoint.
Every radius is converted outward to binary64. This includes formation error
and all reconstruction-to-saved differences, without an equality tolerance.

The producer stores componentwise radii for all 1110 local and 370 adjacent
covariances, bound to the saved center data and assembly certificate. It
performs no new physical tensor evaluation. These balls enclose exact Gram
and adjacent products of the reconstructed local tensors; assembly error
remains a separate coefficient when relating those tensors to the exact
stored-input pullbacks.

Causal covariance propagation is still a separate obligation. Its projection
must also retain the exact stored-axis norm: for longitudinal output `e.T z`
and transverse output `(I-e e.T)z`, the squared transverse Frobenius norm is
`trace(C)+(||e||^2-2) e.T C e`. Substituting `trace(C)-e.T C e` assumes an exactly
unit axis and is not justified merely by binary64 normalization.

Physical input/Hessian/direction errors and neighborhood remainder are not
included. No action, mesh, center, or physical prediction changes. Gate 7 and
full BHSM completion remain false.
