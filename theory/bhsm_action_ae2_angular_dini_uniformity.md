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
for every positive nonasymptotic tail; a quantitative angular barrier estimate
is still needed.  Nor does the current retained action prove optical
completeness: the maximal-flow dichotomy selects no outcome and supplies no
global `S2`, speed, or domain-margin bound.

The other native route would be an already action-owned forward relative
reference with a source-contracted relative trace-class theorem.  The current
BRST grading cannot replace it because the physical leading spatial heat
coefficient is `-5sqrt(pi)`, and the certified cohomogeneity-one spatial
Galerkin tail is a different index and norm.  No reference, counterterm,
phase, selector, or action term is inserted here.

`FULL_BHSM_COMPLETE=false`.
