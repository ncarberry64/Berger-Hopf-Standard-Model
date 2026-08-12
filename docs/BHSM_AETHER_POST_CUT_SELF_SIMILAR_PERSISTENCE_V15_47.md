# BHSM v15.47 — post-cut self-similar persistence test

The v15.46 cap Cauchy data admit a closed one-scale persistence test.  Under
self-similar evolution the transverse-traceless momentum is conserved, so

\[
 \|T\|^2(R)=\|T\|_*^2\left(\frac{R_*}{R}\right)^{14},\qquad
 \omega(R)=\frac{J}{I(R)},\qquad J=\frac12.
\]

The averaged Hamiltonian constraint is therefore

\[
 \frac{\dot R^2}{R^2}=\mathcal G(R)
 =\frac1{21}\left[\frac{\kappa_0}{2}
 +\langle\Lambda F(7/R^2)\rangle
 +\langle\rho_{\rm FR}\rangle-\frac{21}{R^2}
 +\frac12\langle\|T\|_*^2\rangle
 \left(\frac{R_*}{R}\right)^{14}\right].
\]

At the reconstructed slice,

\[
 \mathcal G(R_*)=0.0191428080=H_*^2
\]

within the numerical constraint tolerance.  A bounded minimization and a
logarithmic scan show that \(\mathcal G\) remains strictly positive and has no
turning point.  The contracting v15.46 branch therefore does not close into a
self-similar periodic orbit.

This decides the one-scale sector.  It does not discard the child or introduce
another candidate ontology: the retained cap action already contains the
nonround \(A/B\) shape, response-interface, and boundary-traction degrees of
freedom.  Those variables now define the unique remaining persistence and
Floquet calculation.

