# Gate-7 Arb Magnus-4 discrete propagation

The retained fine graph generator is affine on each stored cell.  Each stored
binary64 generator, source, Gauss weight, time, and quotient frame is inserted
into Arb as its exact dyadic rational.  At 128-bit precision Arb then evaluates

\[
 \exp\!\left(hA_m-\frac{h^3}{12}[A_m,A']\right)
\]

and every product, source contraction, and quotient projection as a ball.
Sixteen aligned substeps are used on a complete fine cell.  The eight Gauss
nodes share outward suffix products, so no source is duplicated.

Raw componentwise propagation over the whole history wraps even though local
roundoff is tiny.  The correct proof coordinates are the retained quotient
multiple-shooting blocks.  The Arb calculation is therefore recentered to the
stored binary correction at each eight-cell macro seam.  All 370 cells and 47
complete/terminal quotient blocks are evaluated.

The maximum Euclidean Arb evaluation radius is `8.62193e-35`.  The maximum
outward difference between this aligned finite operator and the prior
unaligned Magnus-4 proof coordinate is `1.03392e-19`; at the terminal node the
two values are `3.85183e-41` and `2.22225e-21`.  Thus matrix construction,
exponential evaluation, products, contractions, and projections are
negligible relative to the `1e-18` numerical Magnus remainder and the
`1e-13` cone budget.

This result certifies each recentered finite block.  It does not yet compose
the blocks into the global radii polynomial, and it does not bound the
analytic Magnus higher-commutator remainder or signed-source quadrature error.
No action term, source, selector, scale, gate, chord, or physical time
direction is changed.
