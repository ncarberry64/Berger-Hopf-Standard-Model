# Complete stored kinematic arithmetic replacement

Let Xhat be the stored midpoint coordinates, X* the exact normalized midpoint
construction in the exact stored basis, Q the stored symmetric tensor, dQ its
previously certified storage discrepancy, L the stored output map, and L+dL
the exact frozen output formula. The comparison is decomposed as

    (L+dL)(Q+dQ)[X*,X*] - LQ[Xhat,Xhat]
      = L(Q[X*,X*]-Q[Xhat,Xhat])
      + L dQ[Xhat,Xhat]
      + L(dQ[X*,X*]-dQ[Xhat,Xhat])
      + dL(Q+dQ)[X*,X*].

The new complete midpoint construction certificate bounds the first term
after applying L to each tensor block. The earlier storage certificate bounds
the second. Recompute the third with the combined construction/solve error.
Recompute midpoint output errors in the fourth with the combined exact
coordinate norms; preserve the existing endpoint output terms.

This replaces the previous coordinate/storage-cross and output-cross terms.
It does not add a second copy of the old coordinate error. Pullback assembly,
stored tensor discrepancy, signed covariance formation and frozen causal-map
perturbation remain in the envelope. The causal-map perturbation multiplier
applies once to the complete sum, retaining its cross terms.

All 370 ordered point reports are required. Every NPZ hash and operand hash is
checked, and each point's basis, target, coordinates, tensor blocks and output
map must match the earlier coordinate certificate. Source and derivative-file
bindings are rechecked after composition. Incomplete coverage cannot produce
an envelope or a radius witness.

    python scripts/certify_n12_gate7_kinematic_causal_arithmetic_envelope.py

The prior envelope is preserved. The new result targets the same stored
operators with exact midpoint normalization and construction. It does not
certify physical frame inputs, common projector/physical-derivative consistency,
physical Hessian errors, a neighborhood remainder, or contraction. Y, Z1 and
the central/mixed coefficients are not recertified here. A positive stored
polynomial witness remains a restricted arithmetic result, not Gate 7 closure.
