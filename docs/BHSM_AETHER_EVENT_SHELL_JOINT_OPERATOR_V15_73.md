# BHSM v15.73 exact event-shell joint operator

The eta Legendre coefficient is a field on the cap.  The physical common
weight is

\[
 W_t(\rho)=[1-4\sigma_t(\rho)^2][1+X_{\eta,t}(\rho)^3].
\]

The exact gauge-fixed bulk quadratic form and its boundary reduction are

\[
 Q_t[A]=\frac{K_F^{(5)}}2\int_{M_5}W_t|d_AA|^2,
 \qquad
 \langle a,\mathcal N[W_t]a\rangle
 =\min_{BA=a}\frac{2Q_t[A]}{K_F^{(5)}}.
\]

This one variational problem yields both

\[
 K_{A,i}(t)=K_F^{(5)}w_i\mathcal N[W_t]+\Pi_i[W_t],
 \qquad w_i=(5/3,1,1),
\]

and

\[
 B_u(t)=2\frac75\,\chi_{LR,t}^{1/2}
 \mathcal G[W_t]\chi_{LR,t}^{1/2},
 \qquad \mathcal G[W_t]=B\mathcal A_t^{-1}B^\dagger.
\]

The Dirichlet principle gives the exact monotonicity theorem

\[
 0<W_1\leq W_2
 \Longrightarrow
 \mathcal N[W_1]\leq\mathcal N[W_2],
 \qquad
 \mathcal G[W_1]\geq\mathcal G[W_2].
\]

Thus event softening lowers the gauge stiffness and strengthens LR binding in
the same calculation.  Define

\[
 F(t)=\lambda_{\max}(B_u(t))-1,
 \qquad
 t_*=\inf\{t:F(t)=0,\ F(t-\epsilon)<0\}.
\]

At this single \(t_*\), the same \(\Gamma_\partial\) fixes

\[
 g_i^{-2}=\partial_{p^2}\langle a_i,K_{A,i}(t_*;p)a_i\rangle,
 \quad B_u(t_*)h_u=h_u,
 \quad
 Y_u=Z_H^{-1/2}\operatorname{Res}_{h_u}\Gamma_\partial^{(3)}.
\]

The v15.72 replacement of the spatial field by its minimum is reclassified as
a uniform-softening model.  The actual minimum is on an interior
cohomogeneity-one shell, so the outer annulus remains in the DtN problem and
an actual crossing cannot be inferred from the minimum alone.  The next
calculation evaluates this one weighted operator on successive
constraint-solved child slices and locates the common \(t_*\), if present.
