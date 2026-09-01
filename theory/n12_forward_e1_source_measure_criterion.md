# N12 forward E1 source-weighted measure criterion

Status: `SOURCE_WEIGHTED_E1_FIRST_VARIATION_SUFFICIENT_CRITERION_DERIVED`.

For one retained compactly supported geometry direction \(h\), define the
source-weighted graded spectral measure schematically by

\[
 \nu_h(B)=\operatorname{STr}(E_K(B)P_h).
\]

The full unweighted spectral measure and a uniform operator gap are stronger
than necessary for the zero-source first variation. Suppose instead that the
total variation satisfies

\[
 |\nu_h|([0,\Lambda])\leq C_h\Lambda^{1+\varepsilon_h},
 \qquad 0<\Lambda\leq1,\quad\varepsilon_h>0,
\]

and that

\[
 H_h=\int_1^\infty\frac{e^{-\lambda}}{\lambda}
 \,d|\nu_h|(\lambda)<\infty.
\]

On the dyadic interval \((2^{-k-1},2^{-k}]\), the factor \(1/\lambda\) is at
most \(2^{k+1}\). Summation therefore gives

\[
 \int_0^1\frac{e^{-\lambda}}{\lambda}\,d|\nu_h|
 \leq\frac{2C_h}{1-2^{-\varepsilon_h}}.
\]

For the retained unit heat length,

\[
 |D_h\Gamma_{\rm heat}|
 \leq\frac{C_h}{1-2^{-\varepsilon_h}}+\frac{H_h}{2}.
\]

This is a genuine shortest-path reduction: a source-weighted measure estimate
can close the force even when a full uniform spectral gap is unavailable.
The strict excess exponent is essential for this criterion; linear counting
alone gives a logarithmic dyadic divergence.

The theorem does not provide the actual N12 constants and does not yet cover
the pair/contact second variation. The exact next task is to bound the actual
graded source-weighted low- and high-energy measures for the retained weak
geometry directions, then assemble and sign-adjudicate the zero-source force.
