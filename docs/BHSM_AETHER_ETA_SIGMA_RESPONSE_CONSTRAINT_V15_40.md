# BHSM v15.40 — eta-to-sigma material-response constraint

BHSM states that sigma is the material response to formation and environment
geometry. Mathematically, on the reciprocal Hopf join this is

\[
 W_J[f]=\sin^2f\cos^2f,
 \qquad
 Z_J[f]=\int_0^{\pi/2}W_J[f]d\chi,
\]

\[
 \boxed{
 \sigma'(\chi)=\frac{W_J[f(\chi)]}{Z_J[f]},
 \qquad \sigma(0)=-\frac12.
 }
\]

Normalization gives \(\sigma(\pi/2)=+1/2\). The equation is imposed through
the coefficient-free KKT term

\[
 S_{\rm response}
 =\int\lambda_\sigma
 \left(\sigma'-\frac{W_J[f]}{Z_J[f]}\right)d\chi.
\]

The multiplier is nonpropagating and adds no physical field or continuous
coefficient.

This KKT law replaces the independent inverse-Euler \(Z_\sigma\) skin action
in the complete response system. Retaining both would impose the same
eta-to-sigma relation twice and leave the overall \(Z_\sigma\) normalization
unselected. The v15.32 energy and spectrum remain valid statements about the
superseded independent-material subsystem.

Differentiating the constraint gives

\[
 \delta\sigma'
 =\frac{\delta W}{Z_J}
 -\frac{W_J}{Z_J^2}\int\delta W,d\chi,
 \qquad
 \delta W=\frac12\sin(4f)\delta f.
\]

Therefore \(\delta f=0\) forces \(\delta\sigma=0\) on the fixed-endpoint
domain. The v15.32 skin-only translation is a valid negative mode of the
unconstrained material subsystem, but it is not tangent to the complete
response-constrained child. This is removal by an actual action constraint,
not stabilization by eliminating a positive auxiliary block.

For \(f=\chi\), the construction recovers exactly

\[
 \sigma_0(\chi)
 =\frac{2\chi}{\pi}-\frac{\sin4\chi}{2\pi}-\frac12,
\]

and the reciprocal density \((16/\pi)\sin^2\chi\cos^2\chi\).

Consequences:

- sigma is derived on the child solution map rather than varied as an
  independent wall position;
- the physical enclosure mode moves eta, geometry, and sigma together;
- the fixed-profile v15.34 value \(x=-4.78752\) is retained only as an
  unconstrained material-coordinate control, not the physical child scale;
- the zero-current odd-FR domain remains part of the complete child;
- the v15.38 constraint method must be rerun with
  \(\sigma=C_J[f]-1/2\).

The active system is now the nonround Einstein–eta–KKT response problem with
FR expectation energy. `FULL_BHSM_COMPLETE = FALSE` while that joint solution
is being calculated.
