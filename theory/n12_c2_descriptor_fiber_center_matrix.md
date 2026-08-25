# C2 fixed-descriptor tangent center matrix

On the exact fiber `lambda_event(Y)=s`, the birth-limit vector field is
`F_0=Psi/c_psi`.  Its action-coordinate derivative is assembled from the
retained D3/Kato eigenline derivative and

`Dc[v]=D4S[v,Psi,Psi,Psi]+3 D3S[DPsi[v],Psi,Psi]`.

The moving-line product rule is essential.  Re-solving a binary64 eigenvector
at displaced states introduces numerical jitter larger than the signed D4
term.  The fixed-line D4 contraction is therefore centrally differenced,
while line motion is supplied by the exact Kato columns.

At the segment-1064 center the full birth-limit matrix has norm about
`5.29e13`, but its fixed-`s` tangent quotient has norm around `1e12`.  Its
centered fundamental growth over descriptor horizon `1e-22` differs from one
by less than `1e-10` in both retained difference scales.

The complete moving cubic and full birth matrix are stable under step
halving.  The much smaller tangent residual matrix is cancellation-sensitive;
it remains diagnostic until the signed fixed-line D4 term and D5 remainder
are interval enclosed.  No sampled center matrix is promoted to whole-ball
authority.
