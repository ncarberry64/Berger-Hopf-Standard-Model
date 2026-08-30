# Gate-7 current-linearization Newton endpoint candidate

Propagate the measured first-Newton dense defect with the rebuilt 371-node
current-center graph Jacobian, preserving the signed source and using sixteen
substeps per quarter cell.  Project only at the rebuilt current-center macro
constraint tangents.  Add that correction to the current endpoints, directly
replay all endpoint constraints and selected descriptors, and rebuild the
terminal numerical stop bracket.

This second endpoint set tests whether the earlier failed Newton replay was
caused by stale center derivatives and seam projectors.  Its dense defect must
still be measured independently before any convergence or interval claim.

`FULL_BHSM_COMPLETE = FALSE`.
