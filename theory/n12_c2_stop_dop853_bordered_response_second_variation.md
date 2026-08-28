# DOP853 bordered-response first/second-variation tube

On every accepted response cell the complete internal seam response obeys

`K x = f`.

Here `f` is the retained action-owned internal Euler--Lagrange source.  The
external Cauchy/birth source is zero; no internal child, contact, reset, or
gauge response is independently zeroed.  Differentiation along action time
gives

`K x' = f' - K' x`,

`K x'' = f'' - K'' x - 2 K' x'`.

The center computation combines `f' - K' x` before taking a norm.  The
cellwise remainder uses the exact degree-seven Bernstein first- and
second-derivative controls, the retained action derivative majorants, the
certified branch-24 gap, and the already certified uniform bordered inverse.
Selected-line first and second variations are included through the standard
Kato differentiated-eigenpair identities.  No kinetic/Dirac block or history
operator is inverted.

Writing `beta >= sup ||K^-1||`, `R2 >= sup ||f''||`,
`K1 >= sup ||K'||`, `K2 >= sup ||K''||`, `X >= sup ||x||`, and using the exact
center derivative gives

`X1 <= ||x'_c|| + h X2`,

and, whenever `1-2 beta K1 h>0`,

`X2 <= beta*(R2+K2*X+2*K1*||x'_c||)/(1-2*beta*K1*h)`.

When the denominator closes, the center-remainder first-variation tube radius
is `rho_Dx=h X2`.  Independently, the direct differentiated-identity estimate
`X1 <= beta*(R1+K1*X)` gives a finite rigorous first-variation tube without
requiring scalar second-variation closure.  A failed denominator is therefore
a proof-resolution owner: signed/common-frame assembly is applied first, and
refinement requires a separate localized owner analysis.  It is not evidence
of physical instability and does not license a whole-cover replay.  Open
second-variation values are serialized as JSON `null`, rather than a
non-standard infinity literal.

This theorem does not by itself certify the correlated radii-polynomial
inequalities `Y`, `Z1`, and `Z2`, a first-hit transfer, a canonical stop, or
Gate 7.  The cellwise owners identify where the next signed/branchwise
correlated enclosure must be applied.
