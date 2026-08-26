# Gate-7 one-seam full graded finite-core heat bound

Status: `FULL_GRADED_ONE_SEAM_FINITE_CORE_HEAT_SEED_SUPPRESSED_IN_LOG_SPACE`.

The direct AE2 descriptor makes the finite-core temporal domain a single
interval from the external E0 Dirichlet trace through the internal E1/C2 seam
to the far C2 Friedrichs-core Dirichlet trace. The seam is not a boundary and
is represented once. Consequently the Dirichlet Poincare estimate uses the
complete finite-core proper duration `T`:

`||D_tau u||^2 >= (pi/T)^2 ||u||^2`.

The retained scalar, de Rham, HS, and transverse-gauge contacts are
nonnegative. For a scalar angular value `c`,

`P_c >= (pi/T)^2 + c exp(-2 x_max)`.

For a Weyl eigenvalue `lambda=n+3/2`, the AE2 first-order form is globally
factorized as `A_chi=D_tau+chi lambda exp(-x)`. Because both exterior traces
are Dirichlet and `x` is absolutely continuous on the certified compact
core, integration by parts gives

`A_chi^* A_chi >= (pi/T)^2 + lambda^2 exp(-2 x_max)
                         - lambda exp(-x_min)||D_tau x||_infinity`.

The internal reset has no extra fermion surface term, and the common reset
frame preserves this form. Thus the estimate applies to both chiralities
without splitting the E1/C2 seam into artificial one-sided boundary graphs.

Min--max and `j^2 >= 1+3(j-1)` yield the temporal heat bound

`sum_(j>=1) exp(-(pi j/T)^2)
 <= exp(-(pi/T)^2)/(1-exp(-3(pi/T)^2))`.

Multiplying it by the absolute retained angular ledger gives a convergent,
explicit full graded bound:

`4 sum_(m>=1) m^2 exp(-a m^2)` for HS,

`24 sum_(m>=2) (m^2-1) exp(-a m^2)` for transverse gauge,

`48 sum_(n>=0) (n+1)(n+2) exp(-a(n+3/2)^2+b(n+3/2))`
for the absolute Weyl contribution, where `a=exp(-2x_max)` and
`b=exp(-x_min)||D_tau x||_infinity`.

The same estimate bounds the trace norm of the complete graded heat seed by
one half of this heat-trace bound divided by the common positive form gap.
It therefore closes the full angular sum and the complete finite-core seed in
natural log space without diagonalization or floating-point promotion of
underflow to exact zero. The common-scale heat force, which equals minus the
graded heat trace by the retained moving-duration Ward identity, inherits the
same enclosure; its zeta contribution remains exactly zero in that direction.

This theorem is uniform on the certified incoming amplitude box and the
1,222-segment C2 parameter tube. It neither selects a history member nor
promotes the far proof edge to an endpoint. It does not contract the seed
with the signed non-scale geometry jet, and it supplies no maximal C2 tail.
Those remain the Gate-7 owner before the projected KKT root.

No internal response is zeroed, no seam source is added, and no selector,
scale, recurrence condition, gate, or chord is introduced.
