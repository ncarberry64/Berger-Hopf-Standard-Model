# Gate-7 common-scale heat-zeta Ward reduction

Status: `GATE7_COMMON_SCALE_HEAT_ZETA_FORCE_REDUCED_TO_GRADED_HEAT_TRACE`.

The physical common-scale direction changes both radius and proper duration:

`R4(a)=exp(a)R4`, `d tau(a)=exp(a)d tau`.

After pulling every history back to its normalized proper-time domain, each
retained scalar, factorized-Dirac, gauge, ghost, Weyl, and HS positive
operator has weight two,

`P_C(a)=exp(-2a)P_C`.

The parent heat length `ell_kappa` is a retained action parameter and is held
fixed under this geometry variation.  Therefore

`D_a[-(1/2) STr E1(ell_kappa^2 P(a))]`

`= -STr exp(-ell_kappa^2 P)`.

This is the complete common-scale heat-force contraction.  It is equivalent
to pairing the ordinary heat covector with `D_a P=-2P`, but it requires no
pathwise geometry Jacobi or noncommuting operator jet.

The attached Standard-Model zeta/Casimir term is

`Gamma_SM_zeta=-(59/30) integral d tau/R4`.

Its fixed-duration radius derivative is not the complete physical
common-scale derivative.  The proper measure changes by the same factor as
the radius, so

`d tau(a)/R4(a)=d tau/R4`

and `D_a Gamma_SM_zeta=0`.  Hence, at the retained local-action root, the
common-scale replacement correction is exactly

`D_a Gamma_replacement=-STr exp(-ell_kappa^2 P)`.

The theorem closes the contraction formula, not its current N12 number.  The
actual graded heat trace still requires the sharp joint positive
self-adjoint operator, including the incoming arm and the maximal C2 seam.
The non-scale reset quotient force sector remains open.

HINDSIGHT: the apparent zeta common-scale force was incomplete bookkeeping;
the moving-duration product rule cancels it exactly.  No fitted scale,
selector, endpoint, recurrence, new gate, or new physical direction is
introduced.

`FULL_BHSM_COMPLETE=false`.
