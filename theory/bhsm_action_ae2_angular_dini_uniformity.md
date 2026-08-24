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
that, after the compact source interval, the proper-time radius is Lipschitz,

`abs(D_tau R4) <= v < infinity`.

Then `R4(tau)<=R_L+v(tau-L)`, so the optical length diverges.  For positive
chirality,

`V_plus=s_mu^2-D_tau s_mu=s_mu^2+mu(D_tau R4)/R4^2`.

For negative chirality,

`V_minus=s_mu^2+D_tau s_mu=s_mu^2-mu(D_tau R4)/R4^2`.

The two-sided speed bound therefore gives, for both signs and `mu>=2v`,

`V_chi >= s_mu^2/2`.

Until the linear envelope reaches `mu/(2k)`, one has `s_mu>=2k`.  The
one-dimensional Agmon comparison therefore gives

`A_chi,mu(k)>=(mu/(2v))log(mu/(2kR_L))`.

The compact-source transfer and every retained finite-order vertex contribute
at worst `exp(C_source mu)(1+mu)^d`.  The squared barrier factor is
`exp(-2A_mu(k))`, whose root-test logarithm tends to minus infinity.  It thus
beats the quadratic Weyl degeneracy, every fixed polynomial vertex loss, and
every compact-source exponential `exp(C_source mu)` in both chiralities. A
constant radius tail (`v=0`) is the already-gapped limiting case. No radius
monotonicity, exact power law, or regular variation is assumed.

The exact retained finite-`N` radius projection also localizes what would
prove this hypothesis.  If the coordinate, velocity, and multiplier
coefficient norms are bounded globally by `Q`, `V`, and `M`, then

`R4 <= (R0/2) exp(sqrt(1+N) Q)`,

`abs(D_q x[v]) <= sqrt(1+2N) V`,

and `N_boundary^(-1) <= exp(sqrt(N) M)`.  Hence

`abs(D_tau R4) <= (R0/2) exp(sqrt(1+N)Q+sqrt(N)M) sqrt(1+2N)V`.

This is an exact conditional reduction of the radius-speed problem to the
action state and lapse controls; it does not manufacture those controls.

Bounded speed is itself not minimal.  Let `omega` be a nondecreasing outward
speed envelope and suppose, on every outward passage after the source,

`abs(D_tau R4) <= omega(R4)`.

At `R_turn=mu/(2k)`, the two factor potentials obey `V_chi>=s_mu^2/2`
provided `mu>=2 omega(R_turn)`.  On a passage from `R_L` to `R_turn`, the
chain rule gives the Osgood optical estimate

`integral d_tau/R4 >= integral_(R_L)^R_turn dR/(R omega(R))`.

Consequently any envelope satisfying

`omega(R)=o(R)` and `integral^infinity dR/(R omega(R))=infinity`

produces an angular action `mu` times a factor tending to infinity and hence
beats every local `exp(C_source mu)(1+mu)^d` loss.  This is the sharp general
growth condition exposed by this comparison route; oscillations and inward
passages do not invalidate it because only the final outward passage to the
turning radius is used.

An explicit strictly weaker-than-Lipschitz example is

`omega(R)=a+b log(R/R_L)`, with `a>0` and `b>0`.

It permits unbounded radius speed, while

`A_chi,mu(k) >= (mu/(2b)) log(1+(b/a)log(mu/(2kR_L)))`.

Thus the barrier is of order `mu log log mu`, still sufficient by the root
test.  No monotonicity or bounded speed is assumed.

The exact retained uniform-scale structure shows why this weaker condition is
still not kinematic.  Under `q0 -> q0+sigma`, with all non-scale coordinates,
velocities, and lapse/shift coefficients fixed,

`R4 -> exp(sigma) R4`, `D_tau log R4 -> D_tau log R4`, and
`abs(D_tau R4) -> exp(sigma) abs(D_tau R4)`.

Thus an Osgood envelope with `omega(R)=o(R)` requires the dynamical decay
`D_tau log R4 -> 0` along an unbounded outward history.  Positivity of radius
and lapse alone does not give that decay.

This conclusion is also visible directly in the retained action weights.
Before the inverse-inertia quotient, a uniform scale shift gives bulk weights
`7,5,3,1,-1`; the inertia polynomial has weights `7,5,3,1`, the boundary
Casimir has weight `-1`, and the leading ADM kinetic and algebraic terms both
have weight `7`.  Hence there is no scale-weight coercive separation that can
force the logarithmic rate to vanish.  Such a conclusion must come from the
actual constraint-reduced Euler--Dirac flow, not from dimensional scaling.

The complete weight-seven round-radius balance sharpens this obstruction.
On the retained common-scale round ansatz, let `h=q0_dot`. A uniform lapse
symbol `N` is used only to display the conversion to proper time; the owned
constraint below is the zero reduced Legendre energy, not variation of a
constant lapse mode. Since

`integral_0^(pi/4) cos(chi)^3 sin(chi)^3 dchi = 1/24`,

the unchanged ADM plus cosmological sector reduces exactly at weight seven
to

`L7=(R^7/24)(-21 h^2/N-(kappa0/2)N)`.

The already-certified zero reduced Legendre energy and the common-scale
Euler--Lagrange equation give

`21(D_tau log R4)^2-kappa0/2=0`,

`D_tau^2 log R4=kappa0/12-(7/2)(D_tau log R4)^2`.

They have the nonzero expanding equilibrium

`D_tau log R4=sqrt(kappa0/42)`.

Its dominant radius law is exponential and has finite optical length. Thus
the leading retained equations do not merely fail to prove Osgood decay;
they admit the opposite dominant balance. This is not a full-history
existence theorem. A 96-point replay of the complete retained action at
`q0=2,4,6` confirms convergence of the action, zero-energy residual, every
coordinate Euler--Lagrange residual, and every lapse/shift multiplier
constraint to this weight-seven balance. The largest transverse and
multiplier residuals decay with the same relative `R^-2` behavior. Thus the
round trajectory solves the complete weight-seven system at dominant order,
not only its scalar projection. The lower weights `5,3,1,-1`, the
inverse-inertia and boundary terms, transverse linearized stability, and all
regular-domain margins remain uncontrolled. The exact next analytic question
is whether those retained corrections exclude or destabilize this expanding
balance, force an Osgood envelope, or instead drive the history to an
existing event/canonical stop.

The exact quadratic replay also exposes twelve analytic local-time gauge
generators

`z_k=(delta v_u_k=sqrt(kappa0/42), delta log(N)_k=1)`.

They annihilate the weight-seven Euler--Dirac velocity/multiplier block to
machine precision at 96, 192, and 384 quadrature points.  The quadratic
extractor includes the retained response-normal contribution
`+(localization/2)*volume*(beta/N)^2`, which vanishes on the round solution
but is part of the exact transverse Hessian.  The full retained action lifts
the twelve time-gauge kernel directions at relative order `R^-2` (weight
five).  Therefore an ordinary inverse of the leading block is undefined and
cannot be used to promote contamination-scale stability rates.

This is a conditional angular-barrier theorem, not a theorem about the actual
N12 history.  The current retained action still does not prove even the
weaker outward Osgood envelope: the maximal-flow dichotomy selects no outcome
and supplies no global `S2`, velocity-growth, or positive-lapse/domain-margin
bound.  Gate 7 therefore remains open at the action-to-radius-history edge.

The other native route would be an already action-owned forward relative
reference with a source-contracted relative trace-class theorem.  The current
BRST grading cannot replace it because the physical leading spatial heat
coefficient is `-5sqrt(pi)`, and the certified cohomogeneity-one spatial
Galerkin tail is a different index and norm.  No reference, counterterm,
phase, selector, or action term is inserted here.

`FULL_BHSM_COMPLETE=false`.

The later Norman owner ontology restricts realized particle readouts to
finite positive-time completed encapsulation histories or retained canonical
stops.  Accordingly, this infinite-history angular obstruction remains true
mathematically but is closed by scope for physical Gate-7 observables.  The
later desingularized local event branch closes existence of at least one
finite completed-encapsulation history without requiring post-event return.
The current owner is the finite-endpoint zero-source weak geometry force, not
further arbitrary-tail or transverse analysis.
