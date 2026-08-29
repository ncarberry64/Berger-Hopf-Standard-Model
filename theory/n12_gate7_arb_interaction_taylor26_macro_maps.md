# N12 Gate-7 exact affine interaction macro maps

The retained fine-grid graph generator is affine on every cell.  Its large
constant part is handled exactly and its noncommuting part is evaluated in the
interaction frame

`U(t)=exp(A0 t)V(t)`.

For every one of the 5,908 retained PROP16 substeps, a degree-26 interaction
polynomial is evaluated with 256-bit Arb matrices.  Its complete polynomial
ODE residual is summed through degree `26+22`.  The conjugation series is
evaluated through the exact depth-22 nested commutator, after which the
universal bound

`||ad_A X|| <= 2||A||||X||`

closes the infinite tail.  Gronwall then attaches the residual and conjugation
errors before the local map is multiplied into the ambient 98-dimensional
flow.  Projection occurs only at the 47 retained macro constraint seams, where
the physical quotient has dimension 73.

All 47 homogeneous exact-affine quotient maps certify.  The outward extrema
are:

- maximum interaction integral `beta`: `0.021567811917755787`;
- maximum degree-26 residual integral: `2.2377596113841067e-90`;
- maximum local exact-flow error: `6.529925891449844e-79`;
- maximum macro-map component radius: `4.437861941803503e-56`;
- global exact-affine fundamental Frobenius radius:
  `2.8871378515380648e-15`;
- global exact-affine fundamental operator upper: `5342.542842639851`.

The exact-affine and Magnus-8 macro midpoints agree at stored binary64
resolution on all 47 blocks.  Their global midpoints also agree at stored
resolution, and the sum of their outward Frobenius radii is
`3.20867561559206e-15`.  This comparison is a consistency check only; the
interaction residual theorem is the exact-affine authority.

This closes the homogeneous retained-affine carrier.  It does not yet close
the retained unaligned Gauss-8 source suffixes or the independent outward
signed source-quadrature `Y`.  Gate 7 remains active.
