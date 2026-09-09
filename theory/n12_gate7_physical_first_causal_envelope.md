# Physical endpoint DF in the causal arithmetic envelope

The endpoint producer encloses the physical first derivative applied to the
exact normalized stored-frame projector at all 370 noninitial endpoints.
The initial endpoint is fixed. Its aggregate requires every node's complete,
unchanged source binding and outward error ball; missing nodes cannot be zero.

For midpoint step h, the change in the coordinate target is
`h/8 [E_D,left, -E_D,right]`. The physical coordinate certificate adds its
signed inverse-basis enclosure to the existing stored construction/solve ball.
The resulting combined bound replaces the stored-only coordinate error.

The causal consumer verifies the complete endpoint aggregate, every midpoint
coordinate certificate, the unchanged basis/approximate coordinates/output,
and the prior complete stored kinematic envelope. It reuses the latter's
certified output-mapped tensor block norms. For U/C coordinate norms aU,aC
and combined errors eU,eC, its local-pair coefficient is

```text
2 [bUU(2 aU eU + eU^2)
   + 2 bCU(aU eC + aC eU + eU eC)
   + bCC(2 aC eC + eC^2)].
```

Storage-coordinate and output-coordinate-storage cross terms are recomputed
at the combined errors. Existing assembly and storage bounds remain included.
The frozen causal-map perturbation is applied once to the complete source sum.
No prior coordinate contribution is added a second time.

This closes the endpoint-first-derivative operand in the midpoint construction
at the exact stored frames. Physical frame authority, full physical Hessians,
neighborhood remainders, and joint physical contraction remain open. The
reported polynomial witness retains prior Y, Z1, central, and mixed coefficients;
it does not recertify them or close Gate 7. No empirical input is fitted.

The separate `certify_n12_gate7_physical_first_hessian_pullbacks.py` consumer
uses the same combined coordinate errors in the already validated physical
Hessian pullback, including output-error times physical-error times coordinate
cross terms. It requires complete selected-point Hessian rows and matching
coordinate operands. Its selected-point results do not stand in for uncomputed
midpoints or endpoint Hessians and are not added to the complete causal envelope
until their required coverage and transport are established.

Reproduce in order, materializing each deterministic aggregate twice:

```text
python scripts/derive_n12_gate7_physical_endpoint_first_errors.py --all-endpoints --workers 6 --worker-hour-cap 3
python scripts/certify_n12_gate7_physical_endpoint_first_errors.py
python scripts/certify_n12_gate7_physical_first_midpoint_coordinates.py --all-midpoints
python scripts/certify_n12_gate7_physical_first_causal_envelope.py
```
