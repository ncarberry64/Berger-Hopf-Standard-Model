# Gate 7 minimal ordered-event transport scalar

Write the retained state as \(Y=(q,x)\), where \(x=(v,m)\) contains
velocity and the existing lapse/shift multipliers.  For the retained action
\(L\), the Euler--Dirac system has

\[
 D=L_{xx},\qquad
 b=(L_q,0_m)-L_{xq}v,\qquad
 a=D^{-1}b,\qquad V=(v,a).
\]

On a regular simple selected event line,
\(D\psi=e_{\rm ord}\psi\), \(\|\psi\|=1\).  Splitting the exact eigenvalue
derivative before taking norms gives

\[
 \dot e_{\rm ord}=G_0+Q,
 \qquad
 G_0=L_{xxq}[\psi,\psi,v],
 \qquad
 Q=\alpha(D^{-1}b),
\]

where

\[
 \alpha[h]=L_{xxx}[\psi,\psi,h]
 =\langle\psi,D_xD[h]\psi\rangle.
\]

This is strictly weaker than controlling \(\|D^{-1}b\|\): Gate 7 sees only
one signed mixed resolvent matrix element.

With \(P=\psi\psi^T\), \(Q_\perp=I-P\), and
\(S=Q_\perp(D-e_{\rm ord})^{-1}Q_\perp\), the exact selected-line split is

\[
 Q=\frac{c_\psi b_\psi}{e_{\rm ord}}
   +\langle Q_\perp\alpha^\sharp,SQ_\perp b\rangle,
\]

where \(c_\psi=\alpha[\psi]\) and \(b_\psi=\langle\psi,b\rangle\).  Hence

\[
 \frac{d}{dt}e_{\rm ord}^2
 =2c_\psi b_\psi+2e_{\rm ord}R_{\rm ext},
 \qquad
 R_{\rm ext}=G_0+
 \langle Q_\perp\alpha^\sharp,SQ_\perp b\rangle.
\]

The pole product and this squared-event identity are already certified in the
local terminal chart.  The remaining global owner is the exterior remainder
\(R_{\rm ext}\), together with preservation or control of
\(c_\psi b_\psi\) before chart entry.

## Three exact representations

The adjoint equation

\[
 D^*z=\alpha^\sharp
\]

gives \(Q=\langle z,b\rangle\).  It preserves cancellation in the final
source pairing, but no retained global theorem controls its sign or
accumulation.

The bordered operator

\[
 \mathcal B_Q=
 \begin{pmatrix}D&b\\ \alpha&0\end{pmatrix}
\]

has scalar Schur complement \(-Q\).  At finite Galerkin order only,
\(Q_N=-\det(\mathcal B_{Q,N})/\det(D_N)\).  The selected-line Feshbach
reduction above isolates the action-owned pole from the hard complement.  No continuum determinant is
asserted.  The continuum-safe object remains the signed resolvent matrix
element \(\langle\alpha^\sharp,D^{-1}b\rangle\).  Pointwise invertibility
identifies its possible Euler--Dirac stopping locus but does not bound it
uniformly.

Finally, substitution of the Euler--Dirac equation gives the action-jet form

\[
 Q=L_{xxx}\!\left[
   \psi,\psi,
   L_{xx}^{-1}\big((L_q,0_m)-L_{xq}v\big)
 \right].
\]

This substitution is the equation itself; it does not annihilate or sign the
cubic action contraction.  The identically zero reduced Legendre energy does
not control it.  Thus the adjoint, bordered-Schur, and action-jet
representations all reduce to the same explicit uncontrolled scalar.  This is
a proof-route no-go within the audited inventory, not an incompatibility of
the retained action.

## Finite-hitting discriminator

For \(e_{\rm ord}>0\), an inequality

\[
 \dot e_{\rm ord}\le-\varphi(e_{\rm ord}),\qquad \varphi(s)>0,
\]

forces an event by time

\[
 T_*\le\int_0^{e_0}\frac{ds}{\varphi(s)}
\]

or an existing canonical stop first, provided the integral is finite.  For
\(\varphi(s)=cs^p\), this forces finite hitting when \(p<1\).  When
\(p\ge1\), the integral diverges and an infinite asymptotic event-free history
is compatible with the rate.  Boundedness of \(Q\), or monotonicity without a
finite integral rate, is therefore insufficient.

The existing local theorem already forces finite hitting after entry into the
certified terminal chart, so no new control of the pole is required there.
No retained artifact presently forces that chart entry.  The next lemma is
now precise: outside the terminal chart, control the signed combination
\(c_\psi b_\psi/e_{\rm ord}+R_{\rm ext}\) strongly enough to force chart
entry while preserving the hard gap and existing chart margins, certify an
existing stop, or prove a global event-free lower bound.
