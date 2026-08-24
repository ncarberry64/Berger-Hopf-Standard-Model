# N12 forward resolvent-to-heat synthesis audit

Status: `SINGLE_NEGATIVE_z_PROBE_NOT_SUFFICIENT_FOR_RETAINED_HEAT_FUNCTIONAL`.

The native forward Weyl family is a valid compression of exterior history,
but Gate 7 is owned by the retained heat-regulated functional

\[
 \Gamma_{\rm heat}(P)
 =-\frac12\operatorname{STr}E_1(\ell_\kappa^2P).
\]

Its first variation is

\[
 D\Gamma_{\rm heat}[P_h]
 =\frac12\int_{\ell_\kappa^2}^{\infty}
   \operatorname{STr}(e^{-sP}P_h)\,ds,
\]

and its source Hessian is the retained noncommuting Duhamel pair plus seagull
contact expression. Thus the zero-source geometry force and pair/contact
Hessian require controlled functional calculus over the spectrum. They are
not values of a single resolvent probe.

An exact finite-dimensional witness makes the distinction concrete. The two
positive matrices

\[
 \begin{pmatrix}2&1\\1&3\end{pmatrix},\qquad
 \begin{pmatrix}29/12&2\\2&5\end{pmatrix}
\]

have the same boundary Weyl value \(M(-1)=11/4\) for
\(M(z)=a-z-b^2/(d-z)\), but different spectra and different values of
\(-\tfrac12\operatorname{Tr}E_1(P)\). Therefore one Weyl value cannot determine
the retained functional.

The scalar/de Rham and product-Dirac comparison theorems remain valid and are
not retracted. Their formulas are parametric for every real \(z<0\), while the
current numeric witness rows are materialized only at `z=-1`. Promoting those
rows directly to \(\Gamma_{\rm heat}\), the weak force, or the gauge Hessian
would be invalid.

A sufficient next object is either a controlled contour/spectral synthesis
from the maximal-forward Weyl family, or a direct heat-semigroup variation
bound, together with the missing BRST angular relative-trace/source-level
tail. No momentum-squared interpretation, reference subtraction, endpoint,
or source profile is introduced. Gate 7 remains active.
