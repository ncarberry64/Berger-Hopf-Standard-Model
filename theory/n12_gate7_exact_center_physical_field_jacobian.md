# N12 Gate-7 exact-center physical field Jacobian

At every corrected exact-center macro node, rebuild the 25 action constraint
rows: the 24 multiplier Euler--Dirac rows and the differential of zero
Legendre energy.  Their action-coordinate nullspace has dimension 73.  Align
it by orthogonal Procrustes transport to the retained physical frame so the
frame does not acquire arbitrary QR rotations.

On each aligned frame, differentiate the complete normalized action field.
The selected eigenvalue, selected line, hard bordered response, numerator,
and normalization are all differentiated before projection.  Batched JAX
directional third derivatives accelerate the same retained 96-point action
formula; no full kinetic Euler--Dirac inverse is formed.

The result is the direct center matrix `T^T DF T` and the ambient action
matrix `DF T` on all 48 macro nodes.  These discrete center matrices are not
yet a continuous outward propagator.  Promotion requires refined within-seam
evaluation and a remainder enclosure using the existing `D2F` and `D3F`
tubes.  `FULL_BHSM_COMPLETE = FALSE`.
