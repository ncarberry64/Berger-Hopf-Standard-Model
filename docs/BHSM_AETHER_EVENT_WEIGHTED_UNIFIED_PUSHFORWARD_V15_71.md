# BHSM v15.71 event-weighted unified pushforward

The selected child localization function is inserted once, in the common
rank-16 bulk connection block,

\[
 S_{5,\Lambda}=\frac{K_F^{(5)}}4\int_{M_5}\!\sqrt g\,
 \Lambda(\sigma)\operatorname{Tr}_{16}F_{MN}F^{MN},\qquad
 \Lambda=1-4\sigma^2.
\]

It is therefore impossible in this calculation to change the gauge kernel
without changing the LR current kernel.  They are respectively the boundary
quadratic form and inverse-current contraction of the same weighted operator:

\[
 K_A=K_F^{(5)}\mathcal N_\Lambda+\Pi_{AA},\qquad
 G_{LR}=\bigl(K_F^{(5)}\mathcal N_\Lambda\bigr)^{-1}_{LR}.
\]

On the selected half-cap,

\[
 \sigma(\rho)=-\frac12+\frac\rho\pi-\frac{\sin2\rho}{2\pi},
 \qquad 0\leq\rho\leq\frac\pi2.
\]

The weighted transverse and electric radial equations are

\[
 -\partial_\rho(\Lambda\sin\rho\,u')+
 \Lambda\frac{m^2}{\sin\rho}u=0,
\]

\[
 -\partial_\rho(\Lambda\sin^3\rho\,v')+
 \Lambda\ell(\ell+2)\sin\rho\,v=0.
\]

Because \(\Lambda\sim8\rho^3/(3\pi)\) at the regular pole, the regular
Frobenius exponents are fixed rather than chosen.  Numerical integration of
these exact ODEs gives positive weighted DtN eigenvalues.  Substitution into
the same regulated up-channel gap bound shows that this minimal spatial
weight remains subcritical at the geometric heat scale.  No independent
Yukawa term or gauge rescaling is introduced after that result.

The next term in the same calculation is the Lorentzian event-domain effect:
the actual firewall is selected by the zero of the eta Legendre coefficient
\(1+X_\eta^3\), not merely by the regular spatial weight \(\Lambda\).
