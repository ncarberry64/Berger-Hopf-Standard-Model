# BHSM dense proper joint pushforward v15.97

The classical Euler--Dirac orbit is integrated with
\(\Delta t=5\times10^{-4}\), projected onto the lapse, shift, and Hamiltonian
constraints after every step, and sampled every \(0.005\).  The uniform
continuation reaches \(t=0.105\); the independently refined constraint-solved
last-regular state at \(t=0.10602\) completes the approach to the event at
\(t_*=0.1060372\).

Each retained state is passed through one ADM localization calculation:

\[
 K_B(t)=\frac{R_b}{N_b}\int d\chi\,\mathcal KWN\frac{C}{r},
 \qquad
 K_E(t)=\frac{N_b}{R_b}\int d\chi\,\mathcal KW\frac{Cr}{N},
\]

and through the heat-regulated HS residue \(Z_H(R_4(t))\).  One proper-time
measure then gives

\[
 K_B=809.858537,\quad K_E=2514.195062,\quad
 Z_H=0.00176756762,\quad Y=Z_H^{-1/2}I_3=23.7854834I_3.
\]

The maximum independent-grid constraint residual is
\(2.27387\times10^{-4}\).  Gauge normalization and Yukawa normalization are
therefore outputs of exactly the same 24-state \(M_5\to M_4\) quadrature.

