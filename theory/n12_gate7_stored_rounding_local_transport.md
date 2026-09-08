# Local transport of stored tensor rounding

The corrected stored tensor has two separately bounded representation
errors: scalar addition to output 98, and projection onto symmetric
quadratic forms. Let their Frobenius bounds be `a` and `e`, respectively.
For exact stored input and output maps M and L, submultiplicativity gives

```text
|| L [M.T E M] ||_F <= ||M||_2^2 ||L||_2 e,
|| L[:,98] [M.T A M] ||_F <= ||M||_2^2 ||L[:,98]||_2 a.
```

The implementation evaluates the bounds with 512-bit Arb, treating each
binary64 operand as exact. It uses the smaller of the Frobenius bound and
`sqrt(||M||_1 ||M||_infinity)` for each matrix operator norm. The scalar
error retains its actual output column instead of inheriting unrelated
large columns of L. For the midpoint retained block, M consists of the
first 73 rows of the full ambient-coordinate solution. The endpoint map
is the transpose of the stored transverse basis.

The local Hermite–Simpson maps include their existing signed endpoint,
midpoint, and second-incidence coefficients. After transport, the three
local error bounds are added outward. The concatenated endpoint input
has squared norm at most `2 r^2` when each endpoint input has norm at most
r, so twice the resulting tensor bound is a valid local quadratic
coefficient in the existing block-sup domain.

The all-370 producer requires the complete current scalar correction
certificate. It binds every stored map by its binary64 hash and reports
only addition and symmetric-representation error through those maps.
The adjoint evaluation error, physical tensor error, construction of maps,
coordinate-solve error, assembly arithmetic, causal accumulation, and
neighborhood remainder remain separate operands. This local result cannot
close Gate 7 or establish physical predictions by itself.
