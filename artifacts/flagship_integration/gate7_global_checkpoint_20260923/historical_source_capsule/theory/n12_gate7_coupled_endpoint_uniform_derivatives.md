# Uniform first derivatives on the complete endpoint tube

The same coupled inverse argument as
`n12_gate7_coupled_midpoint_uniform_derivatives.md` applies to an endpoint's
paired normalized eigenpair and physical response. The input domain is the
original full affine endpoint tube, with its longitudinal interval and complete
transverse ball. Its physical trial radii are unchanged.

The source must include the independently reproduced normalized endpoint field,
whose dependency chain includes the independently reproduced original physical
response and eigenpair. The response box is loaded from that bound chain;
it is not reconstructed from the normalized field's components. The uniform
descriptor comes from coordinate 98 of the endpoint tube's raw segment hull.

Evaluate the original complete first-variation formula on all 99 weighted
augmented basis directions. The first bordered solve uses the paired response;
the two variation solves use the same coupled inverse bound. Include the
configuration-source derivative, the fourth-action descriptor terms and the
normalization derivative. The descriptor direction is retained.

This establishes a first derivative only if the complete numerical evaluation
succeeds and reproduces independently. The result refers to the endpoint tube,
not an actual HS midpoint domain. Combining both endpoint derivatives with the
derivative on the paired actual midpoint domain is still required for a uniform
HS residual derivative. Useful operator bounds, higher remainders, the physical
quotient, Gate 7 and full BHSM completion remain separate dependencies.
