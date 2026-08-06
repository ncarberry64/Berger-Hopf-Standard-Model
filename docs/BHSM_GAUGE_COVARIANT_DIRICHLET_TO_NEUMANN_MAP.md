# BHSM v14.30 gauge-covariant Dirichlet-to-Neumann map

## Quadratic theorem

Freeze one self-adjoint fiber mode and a constant normal interval of half-width
\(L\). Let

\[
H_A=-D_A^2+M_{J,m}^2\ge0.
\]

Solving the two cap halves with fixed seam trace and regular/Neumann outer data
gives the exact boundary Hessian

\[
\mathcal N_A=2\sqrt{H_A}\tanh(L\sqrt{H_A}).
\]

Spectral functional calculus proves self-adjointness and positivity. If
\(H_A\mapsto U^{-1}H_AU\), then
\(\mathcal N_A\mapsto U^{-1}\mathcal N_AU\); this is the precise gauge
covariance theorem. Dirichlet outer data replace \(\tanh\) by \(\coth\), so
the endpoint domain is physical input to the effective operator.

For \(z=-D_A^2\) and \(M>0\),

\[
\mathcal N_A=m_0+Zz+c_4z^2+O(z^3),
\]

with

\[
m_0=2M\tanh(LM),
\quad
Z=\frac{\tanh(LM)}M+L\operatorname{sech}^2(LM)>0,
\]

\[
c_4=\frac{L\operatorname{sech}^2(LM)}{4M^2}
-\frac{\tanh(LM)}{4M^3}
-\frac{L^2\operatorname{sech}^2(LM)\tanh(LM)}{2M}.
\]

For \(M=0\), \(m_0=0\), \(Z=2L\), and
\(c_4=-2L^3/3\).

## Schur-complement theorem

For a quadratic Hessian split into trace and bulk variables,

\[
H_{\rm eff}=H_{\partial\partial}
-H_{\partial b}H_{bb}^{-1}H_{b\partial}.
\]

Direct minimization of the implemented positive normal chain agrees with this
formula. The second term is nonzero and is the discrete DtN correction. Thus
varying a naively restricted action is not equivalent to restricting the bulk
Euler equation.

## Parent-action boundary

This theorem is `VALIDATED` for the constant quadratic proxy. It is not yet the
BHSM physical eta DtN map because the following are `OPEN`:

- the physical \(SU(3)\) action on the retained eta bundle;
- a degree-one stationary eta section on the full Hopf preimage;
- the Spin/triality Hessian and its curvature endomorphism;
- the self-adjoint cap domain and zero-mode quotient;
- the nonlinear canonical momentum
  \(w(\kappa_1+X^3)n\cdot D\eta\);
- metric, constraint, and shape variations.

No numerical spectrum or current is promoted from this proxy.
