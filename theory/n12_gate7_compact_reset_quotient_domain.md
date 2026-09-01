# N12 Gate-7 compact reset-quotient domain

Status: `COMPACT_NONEMPTY_AE2_RESET_QUOTIENT_DOMAIN_CERTIFIED`.

The retained terminal event-to-child reset map has 58 normal equations in
the 196-dimensional event-child product.  Its certified normal section has
dimension 58, so its tangent has dimension 138.  Projection of that tangent
to the forward-swapped C2 seed has rank 72.  Let `L` be the action-orthonormal
lift of those 72 projected directions and `N` the certified normal basis.

The previously certified normal radii data are

`Y0 = 4.2616140636730716e-15`,
`Z0 = 0.013997597887149837`, and
`Z2 = 22988090712.82265`

on the retained action ball of radius `1e-10`.  For a tangent parameter
`||xi||<=rho`, tangency removes the linear parameter residual.  The same
retained second-derivative majorant therefore gives

`Y(rho) <= Y0 + Z2*rho^2/2`,

`Z0(rho) <= Z0 + Z2*rho`,

and the parameter-dependent radii polynomial

`p_rho(r)=Y(rho)+Z0(rho)r+Z2*r^2/2-r`.

At `rho=1e-12`, this polynomial is strictly negative at the recorded normal
graph radius, and the joint tangent-plus-normal radius remains strictly
inside the existing `1e-10` action ball.  The contraction is uniform in the
entire closed parameter ball.  Hence the zero set is a smooth normal graph
over

`K_rho={xi in R^72: ||xi||_2<=rho}`.

This radius is a proof-domain radius inside an already retained action ball;
it is not a physical scale.  The complete ball is retained.  No point in it
is promoted to a preferred physical reset member.

The parameter-dependent derivative bound also controls the normal-graph
first jet.  Subtracting it from the existing forward C2 projection singular
margin leaves a strict positive uniform lower bound.  Thus the quotient map
has rank 72 throughout `K_rho`.  The larger retained terminal root ball
already carries selected-line simplicity, Legendre positivity, reset normal
regularity, and the two-sided forward orientation.  Direct geometry
covectors additionally preserve positive lapse, positive radius, and positive
initial proper radius rate on this smaller compact family.

This closes only the compact reset-domain input to a degree or covering-map
argument.  It does not propagate `K_rho`, prove capture, or prove a first
stop.  Gate 7 remains open for one finite boundary-controlled flow/first-hit
map of the whole domain, with strict capture-tube inclusion, nonzero degree
and boundary exclusion, or an actual retained stop.
