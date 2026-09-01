# Gate-7 outward finite Omega7 contribution

For the retained affine generator, formal noncommutative expansion of the
ordered exponential and its logarithm gives the complete seventh-degree term

\[
\begin{aligned}
\Omega_7=h^7\bigg(&-\frac{\operatorname{ad}_A^5(B)}{30240}
+\frac{[A,[A,[B,[A,B]]]]}{10080}\\
&-\frac{[[A,B],[A,[A,B]]]}{7560}
-\frac{[B,[B,[A,B]]]}{6720}\bigg).
\end{aligned}
\]

Every commutator is formed from the retained graph generator.  Because
`A=A_left+cB` on a cell, the complete expression is precomputed as a degree-
five polynomial in `c` and outward evaluated at each substep.  This changes no
action datum or proof coordinate.

The 47 homogeneous Magnus-8 quotient maps and the complete retained signed
source assembly are evaluated at 256-bit Arb precision.  The global response
radius is `1.30751e-25`.  Comparing the complete Magnus-8 and Magnus-6
assemblies gives identical stored binary midpoints; this is not called an
exact zero.  Their combined Arb radii give the rigorous outward bound
`2.48431e-25` on the finite `Omega7` augmentation, more than `2.22e12` times
smaller than the selected-cone reserve.

Only the finite `Omega7`-augmented operator is certified.  `Omega9` and higher
analytic terms and signed source-quadrature `Y` remain open before rebuilding
the center-dependent `Z2`, radii, continuous margins, and scalar first-hit
Newton certificate.  Gate 7 and `FULL_BHSM_COMPLETE` remain false.
