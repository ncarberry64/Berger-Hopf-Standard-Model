# C2 finite-prefix terminal-load bracket

Cut the maximal C2 Friedrichs history at the far edge of the certified
1,064-segment prefix.  The omitted nonnegative tail form induces a
nonnegative downstream Weyl load `L_T(z)` at every real `z<0`.  Composing the
element transfers gives one scalar Möbius map

`M_prefix(z;L)=(a(z)L+c(z))/(b(z)L+d(z))`.

Every element transfer has positive denominator on the negative axis and
positive determinant.  Their product therefore satisfies

`D_L M_prefix=(ad-bc)/(bL+d)^2>0`.

It follows exactly that

`M_prefix(z;0) <= M_C2^max(z) <= lim_(L->infinity) M_prefix(z;L)`.

The upper endpoint is the existing Dirichlet form-core truncation.  It is an
order bracket, not a physical endpoint condition.

For the actual proof-center coefficient path, the derivative with respect to
the downstream load differs from one by less than `10^-27` in every retained
fixed channel through negative spectral magnitude `10^32`.  The tiny prefix
therefore transmits, rather than damps, the unknown low-axis tail response.
At `z=-1`, for example, the scalar zero-load value is about `2.49e-31`, while
the Dirichlet limit is about `1.62e31` and the terminal-load derivative is one
to the stored 80-digit precision scale.

Thus complete negative-axis evaluation of the finite prefix does not
determine `M_C2^max`.  The missing object is sharply localized as the actual
maximal downstream load (and its projected cotangent), or alternatively a
genuine later event/canonical stop.  More samples or smaller proof boxes on
the same tiny prefix cannot replace that theorem.
