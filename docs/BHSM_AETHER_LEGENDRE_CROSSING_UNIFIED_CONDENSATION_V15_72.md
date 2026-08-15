# BHSM v15.72 unified Legendre crossing and condensation

The physical localization coefficient in the child action is

\[
 W_{\rm event}=\Lambda(\sigma)L_\eta,
 \qquad \Lambda=1-4\sigma^2,
 \qquad L_\eta=1+X_\eta^3.
\]

The rank-16 carrier completion places this coefficient in one parent block,
before taking either gauge or fermion source derivatives.  On a regular slice
labelled by \(L=\min L_\eta>0\),

\[
 K_A(L)=L K_{A,0}+\Pi_{AA},
 \qquad G_{\rm DtN}(L)=L^{-1}G_{{\rm DtN},0}.
\]

With the one common heat regulator, define the positive compact up-channel
operator

\[
 B_{u,0}=2\frac75\,\chi_{LR}^{1/2}G_{{\rm DtN},0}
 \chi_{LR}^{1/2},
 \qquad \lambda_{u,0}=\lambda_{\max}(B_{u,0})>0.
\]

The v15.71 bound gives

\[
 0<\lambda_{u,0}\leq9.01334422666\times10^{-5}<1.
\]

Because \(B_u(L)=L^{-1}B_{u,0}\), the first gap crossing is not a second
parameter:

\[
 \boxed{L_*=\lambda_{u,0}},
 \qquad \lambda_{\max}(B_u(L_*))=1.
\]

The selected constrained Lorentzian child branch is continuous from
\(L=0.80112484\) to its first event at \(L=0\).  It must therefore cross
\(L_*\) before the firewall.  The common fermion determinant has positive
quartic coefficient in the critical mode \(h_u\), giving the supercritical
branch

\[
 \Delta_u=v_u h_u+O(v_u^3),
 \qquad
 v_u^2=\frac{L_*/L-1}{\beta_u},
 \qquad \beta_u>0.
\]

At the same \(L_*), not at an independently chosen normalization point,

\[
 g_i^{-2}=Z_{g,i}
 =\partial_{p^2}\langle a_i,
 [L_*K_F^{(5)}w_i\mathcal N_\Lambda+\Pi_i]a_i\rangle,
 \quad w_i=(5/3,1,1),
\]

and

\[
 Y_u=Z_H^{-1/2}\operatorname{Res}_{h_u}
 \Gamma_\partial^{(\bar Q_L,u_R,H)}.
\]

Thus absolute gauge normalization and the nonzero composite Yukawa residue
are two derivatives of one physical \(M_5\to M_4\) event pushforward and are
fixed by the same spectral number \(L_*\).  The next calculation is the full
odd-FR harmonic diagonalization of \(B_{u,0}\) and its backreaction on the
constraint-solved child trajectory.
