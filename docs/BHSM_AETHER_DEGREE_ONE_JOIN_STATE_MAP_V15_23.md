# BHSM v15.23: degree-one join state-map reduction

## Exact action-owned ansatz

The retained fields admit the cohomogeneity-one Lorentzian reduction

\[
ds^2=-N^2dt^2+C^2(d\chi+\beta^\chi dt)^2
 +A^2d\Omega_{3,u}^2+B^2d\Omega_{3,v}^2,
\qquad
\eta=(\cos f\,u,\sin f\,v),
\]

with \(\sigma=\sigma(t,\chi)\).  These are existing metric, eta, and sigma
degrees of freedom; the reduction adds no field or coefficient.

For the spatial join metric,

\[
\begin{aligned}
R_7={}&\frac6{A^2}+\frac6{B^2}
-\frac6{C^2}\left(\frac{A''}{A}+\frac{B''}{B}\right)
+\frac{6C'}{C^3}\left(\frac{A'}A+\frac{B'}B\right)\\
&-\frac6{C^2}\left[\left(\frac{A'}A\right)^2+
\left(\frac{B'}B\right)^2\right]
-\frac{18}{C^2}\frac{A'B'}{AB}.
\end{aligned}
\]

The eta invariant is

\[
X_\eta=-\frac{(D_t f)^2}{N^2}+\frac{(f')^2}{C^2}
+\frac{3\cos^2f}{A^2}+\frac{3\sin^2f}{B^2}.
\]

The round identity branch

\[
C=R,\quad A=R\cos\chi,\quad B=R\sin\chi,\quad f=\chi
\]

therefore gives exactly

\[
\boxed{R_7=42/R^2},\qquad
\boxed{X_\eta=7/R^2}.
\]

This places the v15.9 degree-one identity map and the nonround metric problem
inside one explicit state-map ansatz.

## Lorentzian kinetic geometry

Let \(H_A=\dot h+\dot u\), \(H_B=\dot h-\dot u\), and
\(H_C=\dot c\).  The Einstein ADM kinetic scalar is

\[
K_{ij}K^{ij}-K^2
=-12\dot c\dot h-30\dot h^2+6\dot u^2.
\]

The three-variable quadratic matrix is full rank before constraints.  In
particular the nonround shape direction has direct velocity Hessian

\[
\boxed{6\kappa_1\sqrt h/N>0}.
\]

The fixed-volume diagnostic \(\dot c=-6\dot h\) yields
\(42\dot h^2+6\dot u^2\), but this relation is not used as a replacement for
the Hamiltonian and momentum constraints.

The exact logarithmic metric momenta invert as

\[
H_A=\frac{p_a-p_b-p_c}{6\kappa_1V},\quad
H_B=\frac{-p_a+p_b-p_c}{6\kappa_1V},\quad
H_C=\frac{-p_a-p_b+5p_c}{6\kappa_1V},
\]

where \(V=CA^3B^3\).  The shift equation is

\[
\boxed{
-p_c'+p_c c'+p_a a'+p_b b'+p_f f'+p_\sigma\sigma'=0.
}
\]

At zero velocity, the metric Hessian is full rank, the eta Hessian is
\(V(1+g\sigma^2)(\kappa_1+X_\eta^3)>0\), and the sigma Hessian is
\(VZ_\sigma>0\).  The only primary degeneracies are therefore the expected
lapse and radial-shift multipliers.

## Radial gauge invariants

Writing \(a=h+u\), \(b=h-u\), the round profile \(f_0=\chi\) supplies three
explicit radial-diffeomorphism invariants:

\[
\boxed{
C_{\rm GI}=\delta c-\delta f',\qquad
H_{\rm GI}=\delta h-\cot(2\chi)\delta f,\qquad
U_{\rm GI}=\delta u+\csc(2\chi)\delta f.
}
\]

The eta perturbation is therefore part of the physical nonround master
coordinate; it cannot consistently be frozen while the metric shape varies.

## Smooth collapse-pole domain

Smoothness on \(S^3*S^3\) imposes

\[
\begin{array}{lll}
\chi=0:&B=0,&B'=C,\quad A'=0,\\
\chi=\pi/2:&A=0,&A'=-C,\quad B'=0,
\end{array}
\]

together with \(f(0)=0\) and \(f(\pi/2)=\pi/2\).

For the diagnostic slice

\[
A=R\cos\chi\,e^u,\qquad B=R\sin\chi\,e^{-u},\qquad C=R,
\]

smooth pole slopes require \(u=O(\chi^2)\) at the first pole and the reflected
condition at the second.

## Fixed-radial truncation audit

The shape-only quadratic operator contains

\[
\mathcal L_0=-\frac1{\cos^3\chi\sin^3\chi}
\partial_\chi(\cos^3\chi\sin^3\chi\,\partial_\chi)
-2(\sec^2\chi+\csc^2\chi).
\]

Near a pole, \(\mathcal L_0(\chi^p)\) begins at order \(\chi^{p-2}\), with
coefficient \(-(p^2+2p+2)\).  It cannot equal an eigenvalue times the same
smooth leading order.  The lowest smooth trial \(u=\sin^2(2\chi)\) gives

\[
\int wu^2=\frac2{35},\quad
\int w(u')^2=\frac{16}{105},\quad
\int w(\sec^2+\csc^2)u^2=\frac4{15}.
\]

At the exact v15.9 radius \(R_c^6=343/(5\kappa_1)\), its unreduced diagnostic
frequency is positive:

\[
\omega_{u,\mathrm{trial}}^2=\frac{16}{3R_c^2}>0.
\]

Thus the v15.9 crossing is not by itself a nonround instability.  More
importantly, the fixed-\(C\) operator does not preserve the smooth pole
eigenfunction domain.  This is not a physical no-go: it proves that the radial
metric, lapse, shift, and their constraints are indispensable companion
variables of the physical master mode.

## Status

`FULL_BHSM_COMPLETE = FALSE`.

The exact next object is:

`ACTION_OWNED_GAUGE_INVARIANT_COHOMOGENEITY_ONE_JOIN_MASTER_OPERATOR_WITH_HAMILTONIAN_CONSTRAINT_ELIMINATION_SELF_ADJOINT_TWO_POLE_DOMAIN_SPECTRUM_AND_NONROUND_BIFURCATING_ETA_SIGMA_METRIC_SOLUTION`

No frozen prediction, empirical input, external frame, removable medium,
field, or continuous coefficient was changed.
