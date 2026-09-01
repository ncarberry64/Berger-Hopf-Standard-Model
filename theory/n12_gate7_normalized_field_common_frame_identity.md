# Gate-7 normalized-field common-frame identity

Write the retained cancellation-preserving graph field as `f=G/||G||` and
`Q=I-f f^T`.  On the already-retained nonzero-field domain, differentiation
gives

`Df[u]=Q DG[u]/||G||`,

and

`D2f[u,v]=Q D2G[u,v]/||G||`

`-((f^T DG[v])Q DG[u]+(f^T DG[u])Q DG[v]`

`+f(DG[u]^T Q DG[v]))/||G||^2`.

Consequently, if `||G||>=g0`, `||DG||<=A1`, and `||D2G||<=A2`, then

`||Df||<=A1/g0`,

`||D2f||<=A2/g0+3 A1^2/g0^2`.

For the BHSM graph

`G=(s c, W(b psi+s h))`,

the first and mixed second derivatives follow by the displayed product rules
in the machine-readable artifact.  All response, eigenline, descriptor, and
configuration terms remain signed vectors or bilinear maps until after they
are placed in the common physical frame.

This identity supplies one bridge for the literal radii constants:

`Y<=Y_center+defect_remainder`,

`Z1<=||I-A L0||_P+C_A delta_J`,

`Z2<=C_A(A2/g0+3 A1^2/g0^2)`.

It derives the correct object and normalization but does not assign numerical
interval values to `g0`, `A1`, `A2`, `delta_J`, or `C_A`.
