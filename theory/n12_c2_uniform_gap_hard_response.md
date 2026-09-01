# N12 C2 uniform-gap hard response

The finite-descriptor correction uses the hard response of the selected-line
complement.  Its mathematical type is a uniformly invertible complement solve,
equivalently represented by the orthogonal Schur block or by the bordered KKT
system with the selected line as border.

The retained ordered-event eigenline theorem already proves a strictly positive
selected-to-complement gap on the whole parent action ball.  Consequently
`||(D_h-lambda)^-1|| <= gap_lower^-1` holds at every point of that ball.  A
second center-based Neumann factor
`1-gap_lower^-1*(D3_center+D4*r)*r` is not needed to establish the same
invertibility.  Its near-zero value in the last scalar box is therefore a
redundant proof exhaustion, not an Euler--Dirac singularity, event, domain
boundary, or selected-line simplicity loss.

Using the uniform gap once, the covariant identities

`V_h=(D_h-lambda)^-1 Q rhs`

and

`nabla V_h=(D_h-lambda)^-1 Q(D rhs-D D[V_h]-D Q[rhs])`

give finite hard-rate and hard-Jacobi bounds.  Inserted into the exact
cancellation

`F_s=Psi/c+s(c V_full-R Psi)/(c Delta)`,

they enclose the finite-`s` correction on the currently occupied physical tube.
No inverse soft eigenvalue, endpoint selector, recurrence condition, fitted
scale, new gate, or chord is introduced.
