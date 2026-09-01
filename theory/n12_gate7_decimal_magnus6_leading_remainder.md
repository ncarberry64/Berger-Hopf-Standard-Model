# Gate-7 affine Magnus-6 leading-remainder audit

For an affine generator on a symmetric step,

\[
 A(t)=A_m+(t-t_m)B,
\]

the logarithm of the exact ordered exponential through degree five is

\[
 \Omega=hA_m-\frac{h^3}{12}[A_m,B]
 +h^5\left(
 \frac{[A_m,[A_m,[A_m,B]]]}{720}
 -\frac{[B,[A_m,B]]}{240}
 \right)+O(h^7).
\]

The degree-five identity follows by expanding the ordered exponential in
noncommutative words and taking its formal logarithm.  It is an algebraic
identity for the retained piecewise-affine graph generator, not a new action
term or fitted correction.

The complete retained Gauss-8 profile was replayed with this term at PROP8,
PROP16, and PROP32.  At PROP16 the leading-term shift from Magnus-4 is
`3.83489e-19`.  The PROP8-to-16 and PROP16-to-32 increments are
`5.98292e-19` and `2.08195e-18`, giving ratio `0.287372`, not the factor 64
required of a resolved sixth-order truncation regime.  The midpoint
Richardson surrogate also moves slightly farther away when the exact fifth
degree term is added.  Both observations show that binary64 exponential
evaluation has reached its floor and cannot certify the analytic remainder.

Accordingly the exact `Omega5` Lie polynomial is established, but neither it
nor the numerical refinement is promoted to interval tail authority.  The
remaining proof must outward-evaluate this nested-commutator contribution and
the higher remainder in the same correlated quotient frame already used by
the global affine certificate.  Gate 7 remains active.
