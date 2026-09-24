# Local state compression with common-parameter restoration

This is an optional enclosure evaluator. Its remainders must be assessed
before selecting it for a closure calculation.

Consider an affine local state or non-input action leg
`v(theta) = c + a theta + e`, with `|e| <= r`, on the original product
domain. Choose the exact outward bound `w = support_D(a)`. For `w>0`, set
`z=(a theta)/w`; then `|z|<=1` on the entire original domain. Represent the
local operand as `c+w z+e`. Zero-width operands require no new coordinate.
Different operands may use independent local coordinates for the purpose
of bounding nonlinear remainders. This enlarges the local remainder domain;
it never removes an original physical state.

Run the original Taylor arithmetic on these local scalar coordinates. The
resulting affine coefficients are restored to the original common parameters
using the full matrix with rows `a/w`. Arb multiplication encloses all
coefficient roundoff. Its interval overhang does not require extrapolating
the local nonlinear remainder: the actual normalized operands lie in the
unit box by the independently established support bounds `w`.

For an input-linear Taylor model `c u + z^T A u + remainder`, the restored
state/input matrix is `T^T A`, where `z=T theta`. Its common input map is
then restored by the existing local input evaluator. The two pullbacks keep
every original state and input coefficient.

Each quadrature-node bulk and inertia jet is restored **before** summing
nodes and inverting the global inertia. The boundary uses the original
uncompressed evaluator. Thus the retained affine correlations across the
action survive; only the explicitly bounded nonlinear remainder uses the
local independent coordinates.

`local_state_input_taylor_action.py` implements this construction and pins
the underlying input arithmetic. The test compares common affine
coefficients against the existing evaluator and verifies full action
enclosures at original-domain states with varying action legs. A small
remainder or a successful benchmark alone is not a full vector certificate.
