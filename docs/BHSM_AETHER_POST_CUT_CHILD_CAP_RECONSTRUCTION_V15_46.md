# BHSM v15.46 — post-cut child-cap metric reconstruction

## Result

The metric-free v15.45 event data define a new variational problem; they do
not continue the closed-\(S^7\) metric through the eta Legendre firewall.  The
oriented child is the negative-response cap

\[
 \mathcal C_c\simeq B^4\times S^3,\qquad 0\le\rho\le L,
\]

with

\[
 B(0)=0,\quad B'(0)=1,\quad A'(0)=N'(0)=0,\quad f(0)=0,
 \qquad f(L)=\frac{\pi}{4}.
\]

The transported response endpoint order fixes the cap normalization itself:

\[
 \sigma(\rho)=-\frac12+\frac{1}{2Z_c}
 \int_0^\rho \sin^2f\,\cos^2f\,ds,\qquad
 Z_c=\int_0^L\sin^2f\,\cos^2f\,ds.
\]

Thus \(\sigma(0)=-1/2\), \(\sigma(L)=0\), and
\(\Lambda=1-4\sigma^2\) without a new normalization coefficient.

## GHY-completed cap action

In proper-radial gauge, put

\[
 a=\frac{A'}A,\qquad b=\frac{B'}B,\qquad n=\frac{N'}N,
 \qquad X=f'^2+\frac{3\cos^2f}{A^2}+\frac{3\sin^2f}{B^2}.
\]

After the coefficient-locked GHY completion removes the second radial
derivatives, the orbit-volume-normalized gravitational and eta density is

\[
 \mathcal L_c=
 3NA^3B^3\bigl[n(a+b)+a^2+b^2+3ab\bigr]
 +NA^3B^3\left[\frac3{A^2}+\frac3{B^2}
 -\frac{\kappa_0}{2}-\Lambda\left(\frac X2+\frac{X^4}{8}\right)\right].
\]

The fixed odd FR sector adds the Routh term

\[
 -\frac{J^2}{2I},\qquad J^2=\frac14,\qquad
 I=\operatorname{Vol}(S^3)^2\int_0^L
 A^3B^3\Lambda(1+X^3)N^{-1}\,d\rho.
\]

## Constraint reconstruction

No canonical metric momentum is transported by the firewall.  The canonical
zero-input reconstruction is therefore the minimum-norm point on the real
ADM constraint surface.  The lowest regular cap chart is reconstructed from
the action scale, rather than imported from v15.44:

\[
 R_*=\left(\frac{343}{5}\right)^{1/6}=2.0232708255441265,
 \quad A=R_*\cos\chi,\quad B=R_*\sin\chi,\quad f=\chi,
 \quad 0\le\chi\le\frac{\pi}{4}.
\]

Write the extrinsic curvature as a constant mean part plus a radial
trace-free part,

\[
 K^i{}_j=H\delta^i{}_j+T^i{}_j,\qquad
 T^\chi{}_\chi=s,\quad
 T^u{}_u=-\frac{s}{6}+d,\quad
 T^v{}_v=-\frac{s}{6}-d.
\]

The radial momentum constraint is solved identically by

\[
 d=-\frac{s'+\tfrac72(\cot\chi-\tan\chi)s}
 {3(\cot\chi+\tan\chi)}.
\]

The Hamiltonian constraint then fixes

\[
 \frac76s^2+6d^2
 =\frac{42}{R_*^2}+42H^2-\kappa_0
 -2\Lambda F(7/R_*^2)-\Lambda(1+(7/R_*^2)^3)\omega^2.
\]

Minimizing \(|H|\) subject to a real solution, and using the transported
child orientation to choose the contracting sign, gives

\[
 \boxed{H_*=-0.13835753686207958},\qquad
 \boxed{\omega_*=5.103640090572675\times10^{-5}},\qquad
 I\omega_*=\frac12.
\]

At 700 integration points, the minimum TT radicand is
\(-1.5\times10^{-14}\), the maximum Hamiltonian residual is
\(9.1\times10^{-14}\), and

\[
 \min_{\mathcal C_c}(1+X_\eta^3)=6>0.
\]

The post-cut metric child and its Lorentzian Cauchy data are therefore
reconstructed on the controlled cap chart.  The next calculation is its
constraint-reduced monodromy and Floquet persistence; no persistent-particle
claim is made before that calculation.

