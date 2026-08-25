# N=12 asymptotic geometric product ball

Status: `EXPLICIT_GEOMETRIC_DOMAIN_BALL_DERIVED_EULER_DIRAC_REMAINDER_OPEN`.

In the common `H6_q x H5_v x H6_m` chart, Cauchy--Schwarz gives exact
coefficient-to-pointwise constants for the retained pole-regular bases.  If
the product norm is at most `rho`, then

`|w|,|b| <= C_q0 rho`,

`|dot w|,|dot b| <= C_v0 rho`,

`|log N| <= C_n0 rho`, and `|beta| <= C_s0 rho`.

The corresponding first-spatial-derivative constants are also recorded for
the later Euler--Dirac remainder estimate.  Every squared constant is a
finite exact rational sum because the Sobolev squared weights are integer
powers of `1+omega^2`.

Let rational upper bounds for these constants be denoted by a superscript
`+`, and let `H0^-` be a rational lower bound for
`H0=sqrt(kappa0/42)`.  Define

`rho_geom=min(1/(2 C_q0^+), 1/(4 C_n0^+),`

`             3/(8 C_s0^+), H0^-/(2(1+C_v0^+)))`.

All comparisons used to select this radius are checked with exact rational
arithmetic, including the cube comparison proving `H0^-<H0`.

On this entire product ball:

- the retained exponential metric factors are positive and bounded above by
  two relative to their recentered scale;
- `3/4 <= N <= 4/3`;
- `|beta/N| <= 1/2`;
- `eta_legendre=1+x_eta^3 >= 63/64`, so the leading inertia density is
  positive;
- the boundary expansion satisfies `H4 >= 3 H0^-/8>0`.

The last estimate uses the exact boundary identity

`D_tau log R4=q0_dot-tanh(2 b_boundary) dot b_boundary`

on the retained `u=0` time/lapse quotient.

This is an explicit action-owned **geometric-domain** radius, not yet a
capture radius.  It does not prove that the normalized constraint/kinetic
blocks remain invertible on the whole ball, nor does it bound the complete
nonlinear reduced vector-field remainder.  Those are the only remaining
capture-side estimates before a trapping inequality can be certified.
