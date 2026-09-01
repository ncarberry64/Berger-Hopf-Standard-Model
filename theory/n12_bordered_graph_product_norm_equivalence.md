# N=12 bordered graph/product norm equivalence

Status: `POSITIVE_DIRECTED_GRAPH_TO_PRODUCT_EQUIVALENCE_DERIVED_CONSERVATIVE`.

Let `W` be the common product-norm weight map and set

`B_tilde=W^-1 B_-2 W^-1`.

For `y=W X`,

`||X||_graph=||B_tilde y||_2`, `||X||_prod=||y||_2`.

The directed 128-point Arb assembly, including its exact rational Gauss
remainder in every entry, proves that `det(B_tilde)` excludes zero.  No
inverse is formed.  For a 74 by 74 matrix,

`|det(B_tilde)|=product_i sigma_i`

and every singular value is at most `||B_tilde||_F`.  Therefore

`sigma_min(B_tilde) >= |det(B_tilde)|/||B_tilde||_F^73 =: sigma_det^- >0`.

Consequently,

`||X||_prod <= (sigma_det^-)^-1 ||X||_graph`.

The determinant/Frobenius bound is deliberately conservative; its decimal
exponent is around `-1143`, while a binary diagnostic places the actual
smallest singular value near `5.8e-27`.  Only the directed determinant bound
has proof authority here.  The enormous gap shows that a scalar
submultiplicative nonlinear majorant combined with this fallback equivalence
will produce an extremely small but valid radius.  A useful radius requires
the sharper certified repeated-solve/Krawczyk graph defect already identified.

This theorem supplies a positive norm-equivalence constant without violating
the prohibition on inverting the ill-conditioned kinetic/Dirac block.  It
does not yet bound the nonlinear operator defect or promote a capture
surface.
