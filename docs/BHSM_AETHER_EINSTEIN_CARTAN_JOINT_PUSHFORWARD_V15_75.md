# BHSM v15.75 Einstein–Cartan joint pushforward

The adopted eta-bound Dirac action already contains a parent spin connection,
and the Einstein action fixes its normalization.  The minimal coefficient-free
completion is therefore to vary the spin connection independently:

\[
 S_5=\frac{K_G^{(5)}}2\int W e\,e_A^Me_B^NR_{MN}^{AB}(\omega)
 +\frac{K_F^{(5)}}4\int W\operatorname{Tr}_{16}F^2+S_D[e,\omega,A,\Psi],
\]

\[
 K_G^{(5)}=\kappa_1\operatorname{Vol}(S^3_{R_F}),
 \qquad
 \frac{K_F^{(5)}}{K_G^{(5)}}=\frac{R_F^2}{2},
 \qquad
 W=(1-4\sigma^2)(1+X_\eta^3).
\]

Writing \(\omega=\omega^\circ+C\), contorsion is algebraic:

\[
 S_C=\frac12\langle C,\mathcal M_C[W]C\rangle+\langle C,J_S\rangle,
 \quad
 C_*=-\mathcal M_C[W]^{-1}J_S,
\]

\[
 \Gamma_{EC}=-\frac12\langle J_S,\mathcal M_C[W]^{-1}J_S\rangle.
\]

The axial-current Fierz identity contains the attractive scalar channel

\[
 (\bar\Psi\gamma_\mu\gamma_5\Psi)^2
 \supset4(\bar\Psi_L\Psi_R)(\bar\Psi_R\Psi_L).
\]

After the exact eta-bound zero-mode projection,

\[
 G_{EC}(t)=\frac{c_{EC}}{K_G^{(5)}}
 \int ds\,J\frac{|u_0(s)|^4}{W_t(s)},
 \qquad c_{EC}>0,
\]

where \(c_{EC}\) is fixed by the Clifford convention rather than introduced
as a four-fermion parameter.

Near the interior event shell,

\[
 W_\epsilon(s)=\Lambda_e[\epsilon+c_e(s-s_e)^2+o((s-s_e)^2)],
\]

and the degree-one zero mode obeys \(|u_0(s_e)|>0\). Hence

\[
 G_{EC}(\epsilon)
 =\frac{c_{EC}}{K_G^{(5)}}
 \frac{\pi J_e|u_0(s_e)|^4}
 {\Lambda_e\sqrt{c_e\epsilon}}+O(1)
 \longrightarrow+\infty.
\]

The gauge DtN stiffness remains finite because the exterior annulus retains
positive angular energy. Therefore the total LR eigenvalue necessarily
crosses one at a finite \(\epsilon_{*,f}>0\). At that same slice, the gauge
two-point derivative fixes \(g_i^{-2}\), and the critical composite residue
fixes \(Y_f\). Gauge normalization and nonzero Yukawa generation remain two
derivatives of one physical pushforward.

The next calculation fixes the Clifford coefficient and actual wall overlap,
solves \(\epsilon_{*,f}\), and inserts the resulting composite stress into the
constraint-solved child equations.
