# N12 C2 exact-center fixed-descriptor field matrix

On the retained signed descriptor fiber, the action flow is

`F_s=(b Psi+s V_hard)/(c b+s R)`,

with `c=D lambda[Psi]` and `R=D lambda[V_hard]`.  Therefore
`D lambda[F_s]=1` identically.  This identity is the intrinsic time/descriptor
quotient and is checked directly at the final meaningful C2 center.

The selected line, its Kato derivative, `b`, the bordered hard response, and
their derivatives are assembled before any norm is taken.  The moving-cubic
gradient uses

`Dc[v]=D4S[v,Psi,Psi,Psi]+3 D3S[DPsi[v],Psi,Psi]`.

Two one-sided fixed-line slopes evaluate the first term.  The retained `D5`
majorant controls their truncation error.  The one unavailable signed center
contraction, `D2 lambda[V_hard,.]`, is not fitted or silently discarded: its
action-owned operator bound is propagated as an additive matrix remainder.

Projection to `ker D lambda` gives the physical fixed-descriptor tangent
generator.  This is an exact-center theorem only.  A flow box additionally
requires a conjugated interval enclosure of

`Phi_0^-1 (DF_s(Y)-DF_s(Y0)) Phi_0`.

Until that retained `D4/D5` remainder closes, a center matrix is not an event,
canonical stop, endpoint, or Gate-7 completion certificate.
