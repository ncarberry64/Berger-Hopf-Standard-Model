# AE2 compact-source source-Dini closure

The retained action does not currently prove a global bounded logarithmic
radius derivative, eventual monotonicity, bounded variation, doubling law,
regular variation, or an asymptotic power law.  The exact projection
`x=log R4=q0+u_L-(1/2)log(cosh(2v_L))+constant` has bounded coordinate
derivatives, but the maximal-flow theorem has no global state-speed,
acceleration, coercive-`S2`, or uniform domain-margin bound.  The weakest
action-owned statement is local: on every compact regular admissible interval,
the history and its retained source coefficient have the regularity supplied
by the Euler--Dirac flow.  In particular the weighted compact source below is
of bounded variation.

That local statement already suffices.  In one retained factorized channel,
write

`A=d/dtau+s`, `K=A* A`, `S(t)=integral_0^t s`, and `g=delta s`.

For the natural factorized graph `A u(0)=0`, the exact spectral transfer
equation at `lambda>0` is

`A u_lambda=-lambda T_s u_lambda`,

where `T_s=M_exp(S) V M_exp(-S)` and `Vf(t)=integral_0^t f(r)dr`.  Therefore
the first form vertex satisfies

`D_h q[u_lambda]/lambda=<u_lambda,C_h u_lambda>`,

with

`C_h=-(T_s* M_g+M_g T_s)`.

On the compact source interval `[0,L]`, put `b=exp(-S)` and
`F=exp(2S)g`.  The integral kernel is exactly

`C_h(t,r)=-b(t)F(max(t,r))b(r)`.

If `F` is of bounded variation, then

`F(max(t,r))=F(L)-integral_(max(t,r),L] dF(q)`.

This is a rank-one endpoint kernel plus a Stieltjes integral of the rank-one
kernels `1_[0,q] tensor 1_[0,q]`.  Consequently

`norm_1(C_h)<=norm_infinity(b)^2*(L*abs(F(L))+integral_(0,L] q dVar(F)(q))`.

The right-hand side is finite and uses no coefficient beyond the source
interval.  In the spectral representation,

`d nu_h(lambda)=lambda d mu_C_h(lambda)`.

Thus the zero atom has exactly zero first weight and

`integral_(0,1] lambda^(-1)dabs(nu_h)(lambda)`
`=abs(mu_C_h)((0,1])<=norm_1(C_h)<infinity`.

This closes the fixed-channel factorized infrared problem for every positive
admissible nonasymptotic far tail.  No exact or regularly varying radius
asymptotic is needed.  The prior exact power-tail theorems remain valid but
are now cross-checks rather than coverage requirements.  There is no
admissible counterexample under the retained natural graph, compact support,
and local BV regularity; the sharp proof boundary is loss of one of those
three hypotheses.

The retained `exp(i*pi/3)` CP/Z6 object does not alter this result.  AE2 has no
independent Cayley phase.  A common unitary reset-frame phase multiplies both
the trace and factorized conormal, so it cancels from admittance and leaves
Wronskian norms and the trace-norm denominator unchanged.  It is therefore a
robustness invariance check, not a threshold regulator, and is not inserted
into Gate 7.

The current Gate-7 owner moves to the retained angular/channel sum of the
already finite fixed-channel infrared and high-energy source bounds.  The
spatial Galerkin tail may be used only in its certified spatial role, never as
a temporal tail.

`FULL_BHSM_COMPLETE=false`.
