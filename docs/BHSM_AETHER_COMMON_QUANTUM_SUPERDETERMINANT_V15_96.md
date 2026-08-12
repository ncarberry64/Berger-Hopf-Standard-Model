# BHSM common proper-cycle quantum superdeterminant v15.96

The quantum continuation is one graded operator on the physical proper cycle,
not separate gauge and Yukawa corrections:

\[
 P_{\rm cyc}[\Phi;A,H]
 =P_{A\oplus gh}\oplus P_{48\,W}\oplus P_{4\,HS}
 \quad\hbox{on}\quad L^2(S^1_\tau\times S^3_{R_4(\tau)}).
\]

The event endpoints are glued by the already-derived Standard Model bundle
isomorphism.  A uniform proper-time lattice realizes (-\partial_\tau^2),
while the known round-(S^3) spectra realize the spatial blocks.  The
longitudinal gauge and complex ghost determinants cancel mode by mode after
global gauge zero modes are quotiented.

With the single parent heat length, the finite Galerkin functional is

\[
 \Gamma_1^R=-\frac12\operatorname{STr}
 E_1(\ell_\kappa^2P_{\rm cyc})
 =-\frac12\int_{\ell_\kappa^2}^{\infty}\frac{ds}{s}
 \operatorname{STr}e^{-sP_{\rm cyc}}.
\]

Its first Fréchet variation is

\[
 D\Gamma_1[\delta P]
 =\frac12\int_{\ell_\kappa^2}^{\infty}ds\,
 \operatorname{STr}(e^{-sP}\delta P).
\]

The implementation checks this trace identity against an independent centered
difference under a common-radius variation.  Gauge and Yukawa data are then
defined only after solving

\[
 D_\Phi(\Gamma_{\rm cl}+\Gamma_1^R)=0,
 \qquad \mathcal E_{\rm event}[\Phi]=0.
\]

On that one quantum saddle,

\[
 (K_E,K_B)\subset D_A^2\Gamma_q,
 \quad Z_H\subset D_{H^\dagger}D_H\Gamma_q,
 \quad Y_{\rm bare}=D_{\bar\Psi}D_\Psi D_H\Gamma_q,
 \quad Y_{\rm phys}=Z_H^{-1/2}Y_{\rm bare}.
\]

This version evaluates the regulated free spectral seed and its geometry
force.  It does not claim that the interacting source Hessian or coupled
quantum event saddle has already been solved.
