# N12 C2 bordered hard-response matrix

The hard response and soft source coefficient occupy one bordered solve:

`[D-lambda I, Psi; Psi^dagger, 0] [V_h;b_psi] = [rhs;0]`.

This system is uniformly conditioned by the selected-to-hard gap and never
inverts the soft eigenvalue.  Differentiating the whole bordered system gives
the response matrix

`D(V_h,b)=K^-1(D(rhs,0)-DK(V_h,b))`,

so the selected-line, RHS, and hard-block variations combine before norms are
taken.  Restricting its columns to `ker D lambda` produces the physical
fixed-descriptor response ellipsoid.

The exact-center matrix is not by itself an interval theorem.  Retained mixed
`D4/D5` bounds must still enclose its second variation across the current tube.
Until that remainder closes, the matrix is diagnostic and Gate 7 remains open.
