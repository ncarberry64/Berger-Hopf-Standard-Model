# BHSM v15.50 — action-owned diagonal \(Sp(1)\) attachment

The reconstructed spatial child is \(B^4\times S^3\). In join coordinates,
simultaneous right multiplication

\[
 (u,v)\longmapsto(uq,vq),\qquad q\in Sp(1),
\]

is free, including at the regular pole. It therefore defines the global
quotient

\[
 Sp(1)\longrightarrow B^4\times S^3\longrightarrow B^4,
\]

and its material boundary reduces as

\[
 (S^3_u\times S^3_v)/Sp(1)_{\rm diag}=S^3.
\]

Thus the actual reduced domains are \(M_5=\mathbb R_t\times B^4\) and
\(M_4=\mathbb R_t\times S^3\).

Put \(S=A^2+B^2\),
\(\delta=\theta_u-\theta_v\), and

\[
 \omega=\frac{A^2\theta_u+B^2\theta_v}{S}.
\]

Then the parent metric obeys the exact square completion

\[
 A^2|\theta_u|^2+B^2|\theta_v|^2
 =S|\omega|^2+\frac{A^2B^2}{S}|\delta|^2.
\]

Consequently

\[
 L_F=\sqrt{A^2+B^2},\qquad
 R_4=\frac{AB}{\sqrt{A^2+B^2}},
\]

and, with \(x=\log(B/A)\),

\[
 \boxed{\frac{R_4}{L_F}=\frac1{2\cosh x}}.
\]

The mechanical curvature is

\[
 F_\omega=d\lambda\wedge\delta
 -\frac{\lambda(1-\lambda)}2[\delta,\delta],
 \qquad \lambda=\frac{A^2}{A^2+B^2}.
\]

Fiber integration of the parent Einstein term fixes

\[
 \mathcal L_5\supset-\frac14K_F F_\omega^aF_\omega^a,
 \qquad
 K_F=\frac{\kappa_1}{2}\operatorname{Vol}(S^3_{L_F})L_F^2.
\]

There is no new coefficient. The background \(F_\omega^2\) contribution is
already part of the parent scalar curvature used in the cap equations, so it
must not be added again as a classical pressure. The new, non-double-counted
backreaction is the gauge-fixed and spin-glued quantum determinant of the
attached fields on the derived \(M_4\).
