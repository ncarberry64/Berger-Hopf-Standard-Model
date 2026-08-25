# N12 directed interval weight-five center lift

Status: `DIRECTED_ARB_WEIGHT_FIVE_CENTER_LIFT_CERTIFIED_UNIFORM_NONLINEAR_REMAINDER_OPEN`.

The round-density-weighted ten-variable weight-seven Hessian and eight-variable
weight-five force have no endpoint singularity. After cancellation, every
coefficient integrand is a polynomial of degree at most two in `chi` times a
finite Fourier polynomial. The largest frequency is at most 110. A direct
coefficient ledger gives per-entry Fourier `l1` bounds below `1e8`; the
certificate deliberately inflates these to `C=1e12` and `W=128`.

For the `n=128` Gauss--Legendre rule on `[0,pi/4]`,

`|f^(2n)| <= C (2n+1)^2 W^(2n)`.

The exact Gauss remainder constant then gives

`E_n <= (n!)^4 C (2n+1)^2 W^(2n) / ((2n+1) ((2n)!)^3)`.

The factor `(pi/4)^(2n+1)` is dropped upward because `pi/4<1`. Thus the
remainder is an exact positive rational, approximately `2.513e-105`, and is
added as a radius to every integrated Hessian and force entry.

Arb 0.9.0 supplies certified Legendre node/weight balls and the preconditioned
74 by 74 ball solve. All 74 residual balls contain zero and all solution
components retain at least 250 bits of relative accuracy. In particular,

`X5_q0 = 66.4943277368407931932423880231179253575100879824070325622...`

with radius below `1.76e-90`, while

`(D_tau q0)_5 = -51.9637619629039320515640007728173736611469754560951981956...`

has radius below `1.38e-90`. The first interval is strictly positive and the
second strictly negative. This is a rigorous sign theorem for the represented
leading weight-five center modulation, without forming the combined
Euler--Dirac inverse.

This does not yet promote a full `R4^-2` stability label. Such a label still
requires a uniform bound for the complete retained lower-weight and nonlinear
remainder on the finite physical-history domain, or an already canonical
event/stop theorem. The finite-history zero-source force remains a separate
Gate-7 owner.

`Gate7=ACTIVE`, `Gate8=LOCKED`, `chord_03_authorized=false`, and
`FULL_BHSM_COMPLETE=false`.
