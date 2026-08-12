# BHSM common gauge--HS pushforward v16.05

The physical object is one boundary functional, not a gauge calculation plus
a Yukawa calculation:

\[
 \Gamma_Q[\Phi;A,H,\Psi]=\Gamma_{\rm parent}[\Phi]
 -\frac12\operatorname{STr}E_1(\ell_\kappa^2P_{\rm cycle}[\Phi;A,H,\Psi]).
\]

The direct-sum operator contains the background one-form/ghost de Rham block,
the three-family rank-16 Weyl block and the complex HS doublet block.  Its
fixed group traces are

\[
 \operatorname{tr}_{3\times16}T^2=(10,6,6),\qquad
 T^2_H=(1,1,0),\qquad C_A=(0,2,3).
\]

Consequently the same Fréchet Hessian supplies

\[
 K_{B,E}^{i}=D^2_{A_i}\Gamma_Q,
 \qquad Z_{fg}=\big[D_HD_{H^\dagger}\Gamma_Q\big]_{p^2},
 \qquad V_{LRH}=D_{\bar\Psi_L}D_{\Psi_R}D_H\Gamma_Q.
\]

On the 24-node dense proper cycle, through angular level six, this gives

| group | \(\delta K_B\) | \(\delta K_E\) |
|---|---:|---:|
| \(U(1)_Y\) | 6.12540768728 | -0.030063151915 |
| \(SU(2)\) | 3.66705443015 | -0.022121259777 |
| \(SU(3)\) | 3.17144699884 | -0.024559045776 |

and

\[
 Z_{\rm pair}=0.00261291148209,\qquad
 Z_{fg}=Z_{\rm pair}\operatorname{diag}(9,9,3,3).
\]

The exact Einstein--Cartan HS transform fixes the bare LR vertex to one.  If
the full four-channel Hessian selects a normalized direction (c), the same
pushforward therefore yields

\[
 Y_f(c)=\frac{c_f}{\sqrt{Z_{\rm pair}
 c^\dagger\operatorname{diag}(9,9,3,3)c}}.
\]

No independent finite gauge counterterm and no independent Yukawa
normalization is introduced.  The dense orbit remains the collocation seed;
these derivatives must next be recomputed on the global replacement saddle,
where the same HS Hessian selects the physical direction.
