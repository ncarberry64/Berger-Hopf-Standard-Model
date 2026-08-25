# C2 fixed-descriptor cancelled continuation

On the exact descriptor fiber `lambda_event(Y)=s`, write the regularized
action flow as

`F_s=(s qdot, b_psi Psi+s V_hard)/(c b_psi+s R)`.

At birth, `F_0=Psi/c`.  Subtracting before taking norms gives the exact
identity

`F_s-F_0=s (c V_full-R Psi)/(c Delta)`.

This cancels the independent `b_psi` and `Delta` variations that dominated
the isotropic scalar Jacobi estimate.  It also ensures that uncertainty of a
fixed-`s` endpoint is evolved through the fiber Jacobi bound; the full
`c_psi` ball width is not reintroduced as a new center forcing at every
segment.

All bounds use the retained hard inverse, Kato line variation, action D3--D5
majorants, exact descriptor coordinate, and existing lapse/radius margins.
The proof ball and step are derived from joint feasibility and tube closure.
Neither is a physical parameter or endpoint.
