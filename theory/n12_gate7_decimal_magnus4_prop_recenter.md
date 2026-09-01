# Gate-7 affine-generator Magnus-4 propagator recenter

On every retained fine interval the stored graph Jacobian is affine in action
time.  If `A_m` is its midpoint and `B=A'`, the two-node fourth-order Magnus
formula is exact through the leading noncommutative term:

\[
 \Omega_4=hA_m-\frac{h^3}{12}[A_m,B].
\]

This uses only the retained graph generator.  It introduces no source,
selector, scale, endpoint condition, or action term.

The complete 371-node Decimal Gauss-8 profile was replayed with this exponent
at PROP8, PROP16, and PROP32.  A numerical reference formed from the already
stable midpoint PROP64/128 second-order sequence shows:

- midpoint PROP16 reference mismatch: `6.68945e-14`;
- Magnus-4 PROP16 reference mismatch: `3.14195e-18`;
- reduction factor: greater than `2.1e4`.

Thus essentially the entire former numerical PROP16 tail is the signed affine
commutator contribution.  With the Magnus-4 mismatch used only as a numerical
proxy, the combined Y/Z1/Z2 radius is `6.92346e-13`, leaving more than
`5.51e-13` of the selected cone and more than nine-fold Y+Z1 inflation
headroom.

The PROP8/16/32 Magnus-4 differences are already at the binary exponential
evaluation floor, so they are not used as an interval tail theorem.  Promotion
of the Magnus-4 center remains open until the higher commutator remainder and
matrix-exponential rounding are outward enclosed in the correlated
multiple-shooting proof frame.  The signed-Y interval theorem remains separate.
