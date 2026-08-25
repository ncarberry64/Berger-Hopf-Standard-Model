# C2 finite-core Weyl coefficient cotangent at z = -1

Direct elimination of the nonuniform finite-element stiffness pencil is
numerically invalid here: adjacent `1/h` terms are as large as `10^48`, while
the birth Schur value is about `10^31`.  Floating-point subtraction produces
negative pivots even though the form is positive.  The retained transfer
form gives a stable inverse-free alternative.

For a scalar constant-coefficient element at real `z<0`, set
`k^2=V-z`, `t=tanh(kh)`.  If `Z_R` is the downstream conormal impedance,

`Z_L=(k t+Z_R)/(1+Z_R t/k)`.

The far Dirichlet form-core edge is initialized analytically by
`Z_L=k/t`; no infinite number is stored.  For the product-Dirac factor form,
the conormal pair `(u,p)` has a two-by-two exponential transfer with
`W=+/- lambda exp(-x)`, and the same boundary elimination is the scalar
Möbius update `(c+Z_R a)/(d+Z_R b)`.

Arbitrary-precision reverse differentiation through these scalar updates
returns the exact piecewise-constant proof-center cotangent with respect to
every element log-radius and proper duration.  Ordinary double-precision
sensitivities are invalid because the true log-radius derivative is about
`10^-31` against an impedance background of about `10^31`.  This evaluates
`M_C2,T(-1)` and its
coefficient derivative adapter on the entire 1,064-segment form core without
forming an inverse or an ill-conditioned Schur subtraction.

At this probe the two product-Dirac channels retain an order-one Weyl split of
`-3.015327765989...` that binary64 cannot resolve against the common
`1.6177e31` impedance.  Their order-one uniform log-radius boundary
cotangents are equal and opposite.  The paired remainder is nonzero at
arbitrary precision, however, and is retained as a decimal rather than rounded
to binary64 zero.  Thus the leading chiral boundary term cancels, not the full
fixed-core response.  No fixed-probe statement is promoted to a full
negative-axis heat cancellation or maximal-tail theorem.

The result is not yet the physical heat-minus-zeta force.  One negative probe
does not synthesize the heat functional, the proof-center coefficients remain
inside nonzero action tubes, the reset-quotient Jacobi pullback is absent, and
the finite prefix has no maximal-tail certificate or physical far endpoint.
Those claim boundaries are retained explicitly.
