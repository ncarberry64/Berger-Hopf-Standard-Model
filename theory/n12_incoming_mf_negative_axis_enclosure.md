# N12 incoming compact M_f negative-axis enclosure

The incoming response is the event block `M_f=M11` of the existing compact
two-boundary Calderon map after imposing the retained zero birth-source
reference.  For a scalar channel at `z=-kappa^2`, the corresponding
Dirichlet problem has `u(0)=0`, `u(T)=1`.  If
`0<=V<=Vmax`, form monotonicity gives

`kappa coth(kappa T_upper) <= M_f`

and

`M_f <= K coth(K T_lower)`, `K^2=kappa^2+Vmax`.

For a factorized product-Dirac channel `A=d_tau+W`, set
`w=exp(integral W)u`.  Weighted Cauchy--Schwarz yields

`M_f >= exp(-4 S T_upper)/T_upper`, `S=||W||_infinity`.

The linear trial `u=tau/T` gives

`M_f <= max_T {1/T+S+(S^2+kappa^2)T/3}`

over the two certified duration endpoints.  This estimate is performed in
the factorized form, so no `W'` term or Euler--Dirac block inverse appears.

The finite-amplitude certificate supplies
`T=lambda^2 a(lambda)` with a uniform positive interval for every
`0<lambda<=lambda_*`.  Thus the formulas define a finite pointwise incoming
response for every positive amplitude.  Values at `lambda_*` are recorded
only as reproducible worst-duration cross-checks; the edge is not selected as
a physical history.

In the fermion AE2 sector `W_phys=0` and the pulled-back C2 response is
nonnegative on the negative real resolvent axis.  Therefore the seam

`S_AE2=M_f+U_R^dagger M_C2 U_R`

is strictly positive for every `kappa>0` and every positive amplitude in the
box.  The certificate closes seam invertibility, not the exact spectral
trace, its non-scale geometry derivative, or the heat-minus-zeta force.
