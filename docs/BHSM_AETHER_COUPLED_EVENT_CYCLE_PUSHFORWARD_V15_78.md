# BHSM coupled event and one-cycle pushforward v15.78

The gauge normalization and the nonzero left--right sector are not separate
completion conditions.  With the first-order Einstein--Cartan block included,
one parent reduction defines

\[
 \Gamma_{\rm cyc}[B]=\Gamma_{\rm reset}[B(T_*),B(0)]
 +\int_0^{T_*}\!dt\,\Gamma_\partial[W_t;B(t)].
\]

Every four-dimensional residue is a derivative of this functional.  In
particular,

\[
 Z_i^{\rm cyc}=T_*^{-1}\frac{\delta^2\Gamma_{\rm cyc}}{\delta F_i^2},
 \quad
 Z_H^{\rm cyc}=T_*^{-1}\frac{\delta^2\Gamma_{\rm cyc}}
 {\delta D H\,\delta D\bar H},
 \quad
 R_f^{\rm cyc}=T_*^{-1}\frac{\delta^3\Gamma_{\rm cyc}}
 {\delta\bar f_L\,\delta f_R\,\delta H}.
\]

Thus

\[
 Y_f^{\rm cyc}=(Z_L^{\rm cyc})^{-1/2}R_f^{\rm cyc}
 (Z_R^{\rm cyc})^{-1/2}(Z_H^{\rm cyc})^{-1/2}
\]

has no independently adjustable Yukawa normalization.

On the nonlinear up-channel branch, the minimized heat-regulated potential
obeys the envelope identity

\[
 \frac{dV_*}{d\epsilon}
 =-\frac{x_*^2}{2\widehat g^2}\frac{d\widehat g}{d\epsilon}>0.
\]

The condensate therefore drives the same Legendre eigenvalue toward zero. The
strong branch has

\[
 V_*\sim-D\epsilon^{-1/2},\qquad
 m\sim m_0\epsilon^{-1/2},\qquad
 Y\sim Y_0\epsilon^{-3/4}.
\]

Write the event law produced by the constrained KKT vector field as

\[
 \epsilon(t)\sim a(T_*-t)^p.
\]

It follows that \(m=O((T_*-t)^{-p/2})\) and
\(Y=O((T_*-t)^{-3p/4})\), while the gauge DtN residue remains finite.  The
mass insertion is integrable exactly when \(p<2\), and the Yukawa insertion is
integrable exactly when \(p<4/3\).  A transverse frozen approach, \(p=1\),
would satisfy both.  No \(p=4/7\) law is asserted: the Legendre eigenvalue is
a phase-space function and cannot be relabelled as a configuration coordinate
with assumed \(\epsilon\dot\epsilon^2\) kinetics.

The next operation is not a second normalization problem: evaluate the
already constrained KKT vector field on the minimum Legendre eigenvalue to
fix \(p\), then evaluate all residues over that same period.
