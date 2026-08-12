# BHSM v15.68 — exact Coulomb/Gauss boundary kernel

The transverse coexact kernel is not the complete static current response.
For

\[
 A_\tau(\rho,\Omega)=u_\ell(\rho)Y_\ell(\Omega),
 \qquad -\Delta_{S^3}Y_\ell=\ell(\ell+2)Y_\ell,
\]

the hemisphere Maxwell equation is

\[
 -\partial_\rho(\sin^3\rho\,\partial_\rho u_\ell)
 +\ell(\ell+2)\sin\rho\,u_\ell=0.
\]

The regular boundary-normalized solution is

\[
 u_\ell=N_\ell^{-1}\sin^\ell\rho\,
 {}_2F_1\left(\frac\ell2,\frac{\ell+3}{2};
 \ell+2;\sin^2\rho\right).
\]

Its exact boundary derivative is

\[
 \partial_\rho u_\ell\big|_{\pi/2}
 =\frac{\ell(\ell+2)}{\ell+1},
\]

and therefore

\[
 \boxed{\nu_\ell=rac{\ell(\ell+2)}{(\ell+1)R_4}},
 \qquad \ell\ge1.
\]

Equivalently,

\[
 \mathcal N_0=\Omega-\frac1{R_4^2}\Omega^{-1},
 \qquad
 \Omega=\sqrt{-\Delta_0+R_4^{-2}}.
\]

The constant mode has zero DtN eigenvalue and is removed or constrained by
the global Gauss law. The inverse Coulomb eigenvalues are

\[
 G_\ell=\frac{R_4(\ell+1)}
 {K_F^{(5)}\ell(\ell+2)}.
\]

Together with the transverse result
\(\mathcal N_T=\sqrt{\Delta_1^{\rm coexact}}\), this completes the static
bulk-induced gauge kernel. The v15.66 carrier extension is accordingly
reclassified as the transverse part; the scalar/electric kernel must be used
in the left-right Bethe–Salpeter equation. No local Maxwell term is inferred.
