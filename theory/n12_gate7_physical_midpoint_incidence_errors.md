# Physical midpoint DF in endpoint output incidence

The existing accepted replay certificates enclose midpoint images `D M`,
where D is the physical ambient first derivative and M is the Hermite--Simpson
direction matrix supplied to the Arb direction branch. An invertible selected
99-column matrix C gives the exact identity `D = (D C) C^-1`. This identity
needs a surjective direction map, not a physical interpretation of M itself.
In particular, the old endpoint derivative used to construct M need not equal
the newly normalized endpoint-projector derivative. The same M must be used in
both its images and the inverse reconstruction.

The new consumer verifies the accepted endpoint and midpoint cache attestations,
the original producer's provenance, and matching current midpoint states,
descriptors, weights, reference, and frozen frames. It reconstructs D in Arb
from the same cached images and directions and checks the extra-column residual
identity. No physical action kernel is rerun. The signed error relative to the
stored ambient D midpoint is exported with verified containment.

For the frozen right block R, test frame T, and step h, define `B=-R^-1 T`.
The exact physical endpoint output maps are

```text
L_left  = h B/6 + h^2 B D/12
L_right = h B/6 - h^2 B D/12.
```

These maps are evaluated with the reconstructed physical D before subtracting
the exact stored output arrays. Their bounds therefore include the physical
DF incidence error, output construction rounding, and their products with the
frozen inverse. The combined bounds replace the previous endpoint-output
construction bounds; they must not be added to those old bounds a second time.
Midpoint output `2hB/3` remains covered by its existing construction certificate.

The physical first-derivative causal consumer must apply the combined endpoint
output errors to the complete stored/projection-corrected endpoint tensors.
Physical endpoint Hessian errors must use the same combined output bound.
Complete all-node Hessians, physical constraint/quotient identification,
neighborhood remainders, and contraction remain separate open requirements.

```text
python scripts/certify_n12_gate7_physical_midpoint_incidence_errors.py --all-midpoints
```
