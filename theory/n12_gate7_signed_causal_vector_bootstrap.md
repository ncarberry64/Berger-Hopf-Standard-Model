# Gate-7 signed causal vector bootstrap

The former causal remainder reconnaissance replaced every source and every
Volterra propagator by a norm before summation.  That scalarization produced
a terminal radius near `1.34e-8` and made the generic transverse Frobenius
term appear dominant.

The exact directional vectors and mixed Green/transverse matrices now allow
the physical 73-vector equation to be propagated first:

\[
 v_i=\sum_{j<i}\Delta t_j P_{ij}N_j
 \left(\tfrac12 H_{d,j}c_j^2+H_{m,j}c_jN_j^Tv_j\right).
\]

Only the remaining transverse quadratic contribution is enclosed by a
scalar error radius.  The dependency is strictly lower triangular, so both
the signed vector and the error radius are evaluated explicitly without a
global fixed-point solve.

The maximum signed vector norm is `6.219541168643121e-13`; after the existing
transverse center profile is included as an error bound, the maximum total
center radius is `6.219867042251992e-13`.  This is more than four orders of
magnitude inside the already certified `1.3397010452979786e-8` nonlinear
halo.  The transverse profile could be inflated uniformly by more than
`3.5e3`—to a physical curvature bound above `7.5e8`—before that halo fails.

This center theorem does not promote the prior JAX transverse profile or the
signed Green step maps to outward interval authority.  Its consequence is
that a complete \(72^3\) action tensor is unnecessary: a comparatively loose
retained-action transverse tube and the localized signed Green remainder are
sufficient for the interval bootstrap.
