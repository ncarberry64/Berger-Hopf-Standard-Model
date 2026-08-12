# BHSM replacement geometry force v16.06

At zero sources, diagonalize the same direct-sum cycle operator used for the
gauge and HS derivatives in its round-(S^3) eigenbasis.  For every proper
cycle node (j),

\[
 F^{\rm heat}_j=\frac{\partial\Gamma_{\rm heat}}
 {\partial\log R_j}
 =\operatorname{STr}\!\left[f'(P)
 \frac{\partial P}{\partial\log R_j}\right],
 \qquad f(P)=-\frac12E_1(\ell_\kappa^2P).
\]

The v15.97 orbit extremized the zeta-attached action.  Therefore its explicit
replacement residual is not another independent force; it is

\[
 F^{\rm repl}_j=F^{\rm heat}_j-F^{\rm zeta}_j,
 \qquad F^{\rm zeta}_j=\Delta\tau\frac{59}{30R_j}.
\]

The boundary radius is

\[
 \log R_4={\rm const}+q_0-q_1+q_2
 -\frac12\log\cosh\big(2(q_5-q_6)\big),
\]

so the KKT insertion is the exact chain-rule block

\[
 ({\cal R}_Q)_{j\alpha}=F^{\rm repl}_j
 \frac{\partial\log R_{4,j}}{\partial q_{j\alpha}}.
\]

This is the geometry derivative of the same (M_5\to M_4) functional that
generated the absolute gauge residues and HS/Yukawa kernel.  It is the force
block to be combined with the parent Euler--Dirac Jacobian in the global
replacement solve.
