# N12 C2 regularized launch segment

At the exact C2 birth the selected Euler--Dirac eigenvalue vanishes, so
`u=lambda_event^2` is not an invertible state coordinate.  It is nevertheless
the regular physical-time/readout coordinate because its coordinate-time rate
has the pole-cancelled limit `2 c_psi b_psi`.

Use the signed outgoing eigenvalue `s=lambda_event>=0` as the local state
parameter.  With the reduced Euler--Dirac rate split into its selected and
hard parts,

`z_dot=(b_psi/s) psi + h`,

and `R=D lambda[(q_dot,h)]`, the retained equations become

`dt/ds=s/Delta`, `dq/ds=s q_dot/Delta`,
`dz/ds=(b_psi psi+s h)/Delta`,

where `Delta=c_psi b_psi+s R`.  Thus the birth limit is finite and equals
`(0,0,psi/c_psi)`.  This is only a reparametrization of the retained action
flow; it adds no equation or physical selector.

The certificate combines the already validated terminal root enclosure with
a smaller full-state action ball.  Structured action contractions bound the
variation of `c_psi` and `b_psi`; the fixed-Schur eigenline certificate bounds
the selected line, hard inverse, and eigenvalue derivatives.  The
root-relative tube radius is derived from the inequality keeping `Delta` at
least half of its certified birth product; it is not an imported validation
cutoff.  A strict fraction of that tube then gives an explicit nonzero signed
`s` interval.  The interval is shortened further, when necessary, by the
derived first-Jacobi generator so its Gronwall exponent is at most one half.
This gives positive `u`, coordinate-time, and proper-time intervals together
with a useful finite quotient-Jacobi enclosure.
The quotient-rule bound for the regularized vector field supplies the first
Jacobi generator and its exponential growth enclosure.

The segment edge is a proof-domain edge, not a physical endpoint.  No future
endpoint condition or load is imposed.  The next task is the inverse-free
Volterra transfer and physical quotient jet on this certified segment.
