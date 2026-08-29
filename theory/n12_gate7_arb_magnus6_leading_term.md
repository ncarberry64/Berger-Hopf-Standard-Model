# Gate-7 outward finite Omega5 contribution

The exact degree-five affine Magnus polynomial is inserted into every retained
substep:

\[
 \Omega_5=h^5\left(
 \frac{[A,[A,[A,B]]]}{720}-\frac{[B,[A,B]]}{240}
 \right).
\]

Because `B` is constant on a retained affine cell, `[A(t),B]` is constant and
the triple commutator is a quadratic polynomial in the substep midpoint.  The
Arb implementation precomputes that polynomial basis once per cell.  This is
an exact evaluation optimization, not a change of integrator or proof frame.

At 256-bit precision all 47 homogeneous quotient maps, 5,908 fixed
exponentials, 47 zero-initial signed affine source blocks, and 31,019 retained
node-partition source/fundamental exponentials are outward evaluated.  The
Magnus-6 global response radius is `1.17681e-25`.

The direct outward difference between the complete Magnus-6 and Magnus-4
correlated affine responses is `5.70906e-20`; its combined evaluation radius
is `2.22291e-25`.  The existing selected-cone reserve is more than
`9.66e6` times this finite shift.  This replaces the binary64 leading-term
reconnaissance with interval authority for the finite `Omega5` augmentation.

The result does not enclose `Omega7` and higher terms of the exact ordered
exponential, and it does not enclose the signed source-quadrature remainder.
Those two quantities remain the Gate-7 owners before rebuilding the
center-dependent `Z2`, radii, continuous margins, and scalar first-hit Newton
certificate.  No action term, source, selector, scale, gate, or chord changes.
