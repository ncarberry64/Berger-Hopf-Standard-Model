# Current Green mixed/transverse all-endpoint map

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

No historical 48-seam value, new center, fitted split, regulator, scale, or
physical parameter enters this calculation.
