# Gate-7 fixed-channel finite-core heat bound

Status: `C2_FIXED_CHANNEL_1064_TO_1222_HEAT_INCREMENT_SUPPRESSED_IN_LOG_SPACE`.

This certificate concerns the three descriptor pencils actually stored at
both C2 resolutions: the scalar `c=3` channel and the two factorized Dirac
channels with `lambda=3/2`.  It does not substitute those representatives for
the full graded joint operator.

Every finite-core trial function is free at the retained birth node and
vanishes at the artificial far Friedrichs edge.  On an interval of proper
duration `T`, the sharp mixed-boundary Poincare inequality is

`||u'|| >= pi ||u||/(2T)`.

For the scalar form this gives

`P >= (pi/(2T))^2 + inf(V)`.

For either factorized Dirac form `q[u]=||u'+W u||^2`, the reverse triangle
inequality gives

`P >= max(0,pi/(2T)-||W||_infinity)^2`.

The bounds use the certified upper endpoint of the total proper-duration
interval.  The Dirac coefficient bound uses the lower endpoint of the
certified global log-radius interval, so it encloses the full stored tube and
not merely the proof centers.  If a generalized pencil has dimension `N`
and gap lower bound `g`, then

`Tr exp(-ell_kappa^2 P) <= N exp(-ell_kappa^2 g)`.

Every result retains the exact-form prefactor/exponent representation
`N exp(-ell_kappa^2 g)` as well as a logarithmic diagnostic.  At exponents of
order `10^54`, binary64 cannot retain the additive `log(N)` term, so the
prefactor is never discarded.  A floating-point zero would only be numerical
underflow and is never promoted to an exact vanishing trace.

The bound proves that the three stored fixed-channel traces and their
1064-to-1222 difference are negligible at the retained unit heat length.
It does not determine the supertrace multiplicities, the incoming `M_f`
realization, the exact event-child seam domain, the non-scale reset quotient,
the full angular sum, or the tail beyond the 1,222-core proof edge.  Gate 7
therefore remains open.

`FULL_BHSM_COMPLETE=false`.
