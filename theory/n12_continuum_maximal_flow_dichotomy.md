# Continuum maximal-flow continuation alternative

This theorem extends the certified local continuum Euler--Dirac child flow;
it does not construct or sample a new trajectory.

Let

\[
S_2=H^2_q\times H^1_v\times H^2_m,
\qquad
X_E=H^1_q\times L^2_v\times H^1_m,
\]

with the existing trace-compatible gauge quotient and mixed Euler--Dirac
graph domain.  Let \(\mathcal U_\infty\subset S_2\) be the already-required
open child domain: positive spatial metric and lapse, positive eta-Legendre
margin, finite action/inertia, and invertible gauge-fixed Euler--Dirac block.
No new acceptance condition is added.

For (B<\infty\) and \(\delta>0\), write \(K(B,\delta)\) for the part of this
domain on which

\[
\|Y\|_{S_2}\leq B
\]

and every existing metric, lapse, eta, inertia, and Euler--Dirac inverse
margin is at least \(\delta\).  In one spatial dimension (H^2\) is a Banach
algebra and embeds in (C^1\).  The retained action coefficients are finite
compositions of multiplication, differentiation, exponentials, polynomial
eta terms, the positive inertia reciprocal, and the gauge-fixed
Euler--Dirac inverse.  The Moser product/composition estimates and

\[
A^{-1}-B^{-1}=A^{-1}(B-A)B^{-1}
\]

therefore give finite constants depending only on (B,\delta\), and the
frozen retained-action coefficients:

\[
\|V(Y)\|_{X_E}\leq C(B,\delta),\qquad
\|V(Y)-V(Z)\|_{X_E}
 \leq L(B,\delta)\|Y-Z\|_{S_2}.
\]

The existing source-restricted indicial estimate treats the noncompact pole
block, while the compact Euler--Dirac remainder and trace-compatible
Galerkin projector have a tail tending to zero uniformly with the same
(B,\delta\)-dependent coefficient bounds.  Repeating the already-certified
Galerkin/Duhamel construction at any center in (K(B,\delta)) gives a
uniform positive local duration \(\tau(B,\delta)>0\).  This is a recentering
of the retained local theorem, not a finite numerical ball cover.

Let (Y:[0,T_{\max})\to\mathcal U_\infty\) be the unique maximal continuum
child flow from the certified anchor.  If (T_{\max}<\infty\) and neither the
strong norm nor an existing domain margin degenerates, then the trajectory
eventually lies in some (K(B,\delta)).  The uniform duration above extends
the solution past (T_{\max}\), a contradiction.  Hence finite maximal time
implies at least one of

1. \(\limsup_{t\uparrow T_{\max}}\|Y(t)\|_{S_2}=\infty\);
2. an existing metric, lapse, eta, inertia, trace/gauge, or other child-domain
   margin tends to zero;
3. the gauge-fixed Euler--Dirac inverse norm diverges.

This proves the continuum continuation-or-domain-exit alternative without a
coercive charge.  On the simple ordered-event eigenline locus, the existing
identity

\[
\dot e_{\rm ord}
=\langle\psi,DH(Y)[V(Y)]\psi\rangle
\]

holds up to the first event zero, physical/strong-domain exit, Dirac
singularity, or loss of the selected eigenline's simplicity.  The theorem
does not select which outcome occurs.  That selection now requires an
action-derived sign or integrated bound for this displayed transport
integrand on the maximal admissible child component; numerical trajectory
campaigning is not a proof of that bound.
