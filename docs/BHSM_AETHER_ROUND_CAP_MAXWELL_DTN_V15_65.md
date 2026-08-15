# BHSM v15.65 — exact round-cap Maxwell boundary kernel

Set \(\rho=2\chi\) and \(R_4=R_F/2\). The Euclideanized quotient cap is

\[
 ds_5^2=d\tau^2+R_4^2\left(d\rho^2+\sin^2\rho\,d\Omega_3^2\right),
 \qquad 0\leq\rho\leq\frac\pi2.
\]

Thus its spatial part is a round (S^4) hemisphere whose boundary is the
physical (S^3_{R_4}).

For a static coexact boundary vector harmonic satisfying

\[
 \Delta_1V=m^2V,\qquad m=2,3,\ldots,
\]

the Maxwell radial equation is

\[
 -\partial_\rho(\sin\rho\,\partial_\rho u)
 +\frac{m^2}{\sin\rho}u=0.
\]

The unique regular solution normalized at the boundary is

\[
 u_m(\rho)=\tan^m(\rho/2),\qquad u_m(\pi/2)=1.
\]

Consequently

\[
 \partial_nu_m\big|_{\partial}=\frac{m}{R_4},
 \qquad
 \boxed{\mathcal N_T=(\Delta_1^{\rm coexact})^{1/2}}.
\]

The action-owned bulk connection therefore induces

\[
 S_{\rm DtN}=\frac{K_F^{(5)}}2
 \int_{M_4}\sqrt h\,A_i\mathcal N_TA^i.
\]

This is an order-one nonlocal boundary action, not the order-two local Maxwell
term. It is the exact operator explanation of the smooth-mode mismatch found
in v15.60.

For the geometric diagonal (Sp(1)) connection, every right-handed Standard
Model field is a weak singlet. Hence the left-right scalar channel factor is

\[
 \sum_aT_L^aT_R^a=0.
\]

The exact weak DtN kernel contributes to left-left and vector response but
cannot drive the composite Higgs gap equation. A nonzero left-right kernel must
come from color in the quark channels, hypercharge in charged channels, or a
direct action-owned finite-Dirac/four-fermion term. Their physical
bulk-to-boundary normalizations are the active derivation.
