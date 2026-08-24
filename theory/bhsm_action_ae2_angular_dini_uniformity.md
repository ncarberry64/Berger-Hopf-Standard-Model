# AE2 angular source-Dini uniformity audit

The fixed-channel compact-source theorem remains closed.  Its trace-norm
bound is not automatically uniform in the internal `S3` Dirac level, so the
angular direct sum is a separate Gate-7 obligation.

Let `r=1/R4`, `I=integral_0^infinity r`, and consider positive chirality
`s_mu=mu*r`.  The exact zero-transfer solution has far amplitude
`exp(-mu*I)`.  When `I<infinity`, delta normalization therefore contributes

`N_mu^2=(2/pi)exp(2mu I)`.

For a nonnegative compact log-radius source with
`H=integral_delta^L h(t)r(t)dt>0`, assume only
`r(t)<=r_max` on `[0,delta]`.  If
`mu>=1/(2r_max delta)`, the exact transfer derivative gives

`C_mu >= ((2/pi)(1-exp(-1))H/r_max)exp(2mu I)`.

Here `C_mu` is the small-threshold source-Dini coefficient in that fixed
channel.  Every coefficient is finite, fully consistent with the preceding
theorem.  But the positive Weyl levels satisfy
`mu_n=n+3/2` with degeneracy `48(n+1)(n+2)`, so the absolute angular terms do
not even tend to zero when `I` is finite.

The smooth positive non-power history `R4(tau)=exp(tau)` is a sharp witness.
It has bounded logarithmic derivative, strict monotonicity, smooth local
coefficients, and optical length `I=1`.  Thus bounded logarithmic derivative,
eventual monotonicity, and local BV do not close the angular sum.  This does
not reopen any exact power-tail fixed-channel result.

Angular finiteness therefore excludes finite optical length on an infinite
regular history.  The necessary geometric condition exposed here is

`integral_0^infinity d_tau/R4(tau)=infinity`.

This audit does not yet prove that optical completeness alone is sufficient
for every positive nonasymptotic tail.

It does close a strictly weaker-than-power-law sufficient class.  Suppose
that, after the compact source interval, the proper-time radius obeys

`0 <= D_tau R4 <= v < infinity`.

Then `R4(tau)<=R_L+v(tau-L)`, so the optical length diverges.  For positive
chirality,

`V_plus=s_mu^2-D_tau s_mu=s_mu^2+mu(D_tau R4)/R4^2 >= s_mu^2`.

Until the linear envelope reaches `mu/(2k)`, one has `s_mu>=2k`.  The
one-dimensional Agmon comparison therefore gives

`A_plus,mu(k)>=(sqrt(3)mu/(2v))log(mu/(2kR_L))`.

For negative chirality and `mu>=2v`,

`V_minus=s_mu^2+D_tau s_mu>=s_mu^2/2`.

On the same range `s_mu>=2k`, this gives the direct partner bound

`A_minus,mu(k)>=(mu/(2v))log(mu/(2kR_L))`.

The compact-source transfer and every retained finite-order vertex contribute
at worst `exp(C_source mu)(1+mu)^d`.  The squared barrier factor is
`exp(-2A_mu(k))`, whose root-test logarithm tends to minus infinity.  It thus
beats the quadratic Weyl degeneracy, every fixed polynomial vertex loss, and
every compact-source exponential `exp(C_source mu)` in both chiralities. A
bounded radius (`v=0`) is the already-gapped limiting case. No exact power law
or regular variation is assumed.

This is a conditional angular-barrier theorem, not a theorem about the actual
N12 history.  The current retained action still does not prove the eventual
sign and upper bound `0<=D_tau R4<=v`: the maximal-flow dichotomy selects no
outcome and supplies no global `S2`, speed, or domain-margin bound.  Gate 7
therefore remains open at the action-to-radius-history edge.

The other native route would be an already action-owned forward relative
reference with a source-contracted relative trace-class theorem.  The current
BRST grading cannot replace it because the physical leading spatial heat
coefficient is `-5sqrt(pi)`, and the certified cohomogeneity-one spatial
Galerkin tail is a different index and norm.  No reference, counterterm,
phase, selector, or action term is inserted here.

`FULL_BHSM_COMPLETE=false`.
