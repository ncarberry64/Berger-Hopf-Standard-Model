# N12 C2 translated pole-free segment

Let `s=lambda_event` be the signed selected-eigenvalue descriptor and let
`B_1` be the first translated action ball.  The hard component is evaluated
without a soft-block inverse,

`r_h=(Q D Q)^(-1) Q b`,

and its covariant variation is bounded with the already certified
pole-free identity.  The differentiated soft source and the derivative of
`Delta=c_psi b_psi+s R` then give an inverse-free Lipschitz bound for the
regularized descriptor field on `B_1`.

The endpoint tube from the preceding segment is the initial enclosure.  At
its proof center the retained action supplies `psi`, `b_psi`, and `r_h`.
An Euler predictor uses the midpoint of the certified `c_psi` interval and
the exact center numerator.  The omitted `s R` term and the `c_psi`
half-width are retained as a field-mismatch enclosure.  Gronwall growth plus
the quadratic Euler remainder closes the next endpoint tube.  Neither proof
center is promoted to a physical endpoint or a state selector.

The physical time increment is recovered only after the state enclosure:

`Delta t in ((s_1^2-s_0^2)/(2 Delta_+),
             (s_1^2-s_0^2)/(2 Delta_-))`,

and multiplication by the positive lapse interval gives a strictly positive
proper-time increment.  All stopping margins remain strict, so this segment
certifies continuation but not completed encapsulation.
