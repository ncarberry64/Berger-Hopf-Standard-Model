# BHSM common quantum source response v15.99

For

\[
 f(P)=-\frac12E_1(\ell_\kappa^2P),
\]

the source Hessian is evaluated without assuming that the source vertices
commute with \(P\). If \(P_a=\partial_aP\) and
\(P_{ab}=\partial_a\partial_bP\), then in an eigenbasis of \(P\),

\[
 D_aD_b\operatorname{Tr}f(P)
 =\sum_{ij}f'[\lambda_i,\lambda_j](P_a)_{ij}(P_b)_{ji}
 +\sum_i f'(\lambda_i)(P_{ab})_{ii}.
\]

The second term is the background-covariant seagull/contact vertex. The
implementation verifies the full noncommuting expression against a
two-source centered difference.

All BHSM responses are assigned before sector extraction:

\[
 \Pi_{EE}=D^2\Gamma_1[J_E,J_E;Q_{EE}],\quad
 \Pi_{BB}=D^2\Gamma_1[J_B,J_B;Q_{BB}],
\]

\[
 Z_H\subset D_{H^\dagger}D_H\Gamma_q,\qquad
 Y=Z_\Psi^{-1}Z_H^{-1/2}
 D_{\bar\Psi_L}D_{\Psi_R}D_H\Gamma_q.
\]

The same operator supplies the quantum geometry force
\(D_\Phi\Gamma_1[J_\Phi]\). The remaining calculation is assembly of the
physical radial-times-\(S^3\) vertex matrices on the dense constraint-solved
cycle, not selection of separate gauge or Yukawa coefficients.
