# Current Green mixed/transverse post-reset endpoint map

Let `F` be the retained augmented rate, `u_G` the normalized current Green
axis, and `P_T = I - u_G u_G^T` its proof-coordinate complement. This unit
evaluates

`D^2 F(x_i)[u_G, P_T]`

directly at each current endpoint. The implementation differentiates the
selected eigenline, bordered response, normalized field, and scalar readout
in two distinct directions. It broadcasts all transverse columns through one
correlated Arb expression. The identity is checked against the independently
materialized polarization seeds before any all-endpoint promotion.
That audit reproduces the seed centers below `1e-8` absolute and `1e-9` after
unit-floor scaling.  Its independently rounded Arb graphs do not overlap in
every component, so the direct evaluator is authorized for reconnaissance but
does not yet own an outward mixed-map theorem.

The retained center has 371 endpoints, but node 0 is the birth node and its
current Green image is the zero vector.  A normalized Green axis therefore
does not exist there.  The campaign covers nodes 1 through 370 and does not
invent a direction at node 0.

The first adaptive-precision screen rejected 128 bits because its maximum
scaled component radius was approximately `0.3963`.  A 192-bit screen reduced
that maximum below `1.05e-16`; consequently all non-attested continuation
shards use at least 192-bit Arb, while nodes 1 through 80 retain their existing
512-bit evaluations.

No historical 48-seam value, new center, fitted split, regulator, scale, or
physical parameter enters this calculation.

The completed survey contains all 370 defined-axis endpoints.  Its maximum
direct-graph Frobenius upper is `256.52090126938094` at node 9, its maximum
component radius is `5.023633018517515e-15` at node 13, and its maximum
projected-axis annihilation graph upper is `1.2958447643204296e-14` at node
52.  The 192-bit continuation consumed `83.74721061108337` measured CPU hours.
These figures localize the outward owner but do not themselves promote
direct-versus-polarization equivalence.
