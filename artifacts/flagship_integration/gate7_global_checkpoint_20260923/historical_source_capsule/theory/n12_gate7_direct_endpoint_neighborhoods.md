# Frozen affine endpoint neighborhoods for direct physical HS evaluation

The direct value, Jacobian, and Hessian campaigns evaluate individual physical
HS points. A uniform remainder requires an explicit neighborhood of those
points. This adapter constructs its endpoint coordinate boxes using the same
frozen trial frames and longitudinal axes as the direct quadratic sources.

At node i the domain is z_i + E_i(e_i l_i + t_i), with |l_i| <= r_L and
||t_i||_2 <= r_T. The initial endpoint is fixed. The longitudinal amplitudes
are independent across nodes. The transverse ball uses the complete 74
coordinate directions; it contains the axis-orthogonal transverse subspace.
The stored axis is not assumed to have exact unit norm. Each augmented
weighted coordinate j is enclosed with added radius

    |(E_i e_i)_j| r_L + sqrt(sum_k E_i[j,k]^2) r_T.

All products, sums, absolute values, square roots, and endpoint center products
use outward Arb arithmetic. The signed matrix-vector contraction precedes the
absolute value. Existing center uncertainty is retained. Positive exact frozen
weights convert the first 98 coordinates back to raw state; the last coordinate
is the descriptor and remains unchanged. Rational serialization contains the
computed balls, including any additional radius rounding during reconstruction.

The radii are copied as exact binary64 rational leaves from the existing
incidence artifact's conditional polynomial witness. They are trial inputs,
not a newly established self-map or contraction witness. No measured data or
new calibration enters this construction. All 371 endpoint centers are checked
against the complete independently reproduced direct value inventory. Frame,
axis, weight, radius, source, and runtime bindings are retained.

The remaining uniform calculation must enclose F on these endpoint boxes,
then construct the actual midpoint domain by

    M = (Z_i + Z_(i+1))/2 + h_i (F(Z_i) - F(Z_(i+1)))/8.

Here F(Z) must be a uniform endpoint-rate enclosure. Pointwise rates or
pointwise Hessians alone cannot replace it. The existing outward physical HS
midpoint formula can propagate such rate enclosures when available. Uniform
derivative and eigenbranch validation must subsequently cover both endpoint
and actual midpoint domains. A failure of interval evaluation on the coordinate
box is retained as a method failure; it does not prove the smaller correlated
affine domain is singular.

The endpoint boxes alone establish no uniform rate or remainder. The affine
trial frame does not establish an intrinsic nonlinear constraint chart, moving
frame derivatives, the physical quotient, a finite-history contraction, or
the continuum result. Gate7 and full BHSM completion remain open.

Run `python scripts/derive_n12_gate7_direct_endpoint_neighborhoods.py`, then
the same command with `--recompute`. The repeat rebuilds every domain from
the independently reverified inputs and requires identical data and record
bytes. Old receipts are archived before another attempt; mismatch candidates
are retained. The output is under
`artifacts/flagship_integration/.direct_endpoint_neighborhood_work/`.
