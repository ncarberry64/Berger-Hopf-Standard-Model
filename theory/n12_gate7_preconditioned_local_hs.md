# Fixed preconditioning before interval Hermite–Simpson products

This is an equivalent evaluation of the existing frozen local Newton
operator. It changes neither the physical derivative domains nor the frames,
step, action, physical branch, frozen left block L or frozen right block R.
It supplies no moving-frame derivatives or physical quotient identification.

Let A, M and B be the already enclosed complete physical derivatives at the
left endpoint, actual HS midpoint and right endpoint. Let E0/E1 be the frozen
trial frames and T the frozen test frame. Compute an outward enclosure of
P = R^{-1} T once, carrying its complete Arb uncertainty through all products.
The positive exact step is h. Then the same local blocks satisfy

\[
C=PLE_0,
\]

\[
DL=P(L+I)E_0+\frac h6 PAE_0
+\frac{2h}{3}(PM)\left(\frac{E_0}{2}+\frac h8 AE_0\right),
\]

\[
DR=I-PE_1+\frac h6 PBE_1
+\frac{2h}{3}(PM)\left(\frac{E_1}{2}-\frac h8 BE_1\right).
\]

These expressions follow directly from the original residual convention
r = z1 - z0 - h(F0 + 4Fm + F1)/6 and its actual midpoint chain rule. They
retain the complete descriptor direction and every term of the original
physical derivative matrices. For a fixed initial endpoint, DL is zero as
in the original operator.

The first association tested merely substitutes P in the original expression
R^{-1} T (L - Dr0) E0 and its right counterpart. The second uses the formulas
above, preconditioning M before multiplying its uncertain midpoint chain.
The third combines the endpoint coefficients as

\[
DL=P(L+I)E_0+\frac h3 PME_0
+\left(\frac h6 P+\frac{h^2}{12}PM\right)AE_0,
\]

\[
DR=I-PE_1+\frac h3 PME_1
+\left(\frac h6 P-\frac{h^2}{12}PM\right)BE_1.
\]

All three expressions are equal over exact operands. Their interval
enclosures can differ because repeated intermediate boxes lose correlations.
For example, forming T times an uncertain matrix and then applying R^{-1}
can introduce bounds involving |R^{-1}| |T| where the precomputed fixed
product permits |R^{-1} T|. No narrowed midpoint or discarded radius is used
in the reassociated evaluations.

Tests require all three interval evaluations to contain the original
operator computed at higher precision at corners of a perturbed matrix
family. The numerical diagnostic additionally requires overlap with the
original paired-input local evaluation. Numerical improvement must be
measured, independently reproduced, and kept separate from global
contraction, full path coverage and BHSM completion.

The production consumer evaluates the original association and all three
equivalent associations. For each matrix entry it retains the valid Arb
enclosure with the smallest radius, requiring overlap with the original
evaluation. Every candidate encloses the same entry of the same operator,
so this entrywise choice remains an enclosure of that operator. It also
preserves the sharper original C entries when early preconditioning adds
rounding width to the fixed-only products. This chooses an arithmetic bound,
not a field, mode, frame, physical parameter or empirical match.
