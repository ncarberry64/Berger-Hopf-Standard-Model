# Exact full transverse curvature and center causal vector

The complete retained-action field Hessian was evaluated on all 48 physical
time-transverse frames.  Each seam uses one signed broadcast \(D^4S\)
contraction with component shape \(61\times72\times72\times3\), followed by
the exact eigenline, bordered-response, numerator, and normalization product
rules.  The maximum transverse Frobenius norm is
`212405.77120771355` at node 0, more than `3543` times below the acceptance
ceiling exposed by the signed causal-vector bootstrap.

The full binary64 tensor is retained without down-casting in two
node-contiguous NPZ shards (nodes 0--23 and 24--47).  Sharding only keeps each
reproducibility object below the remote object-size ceiling; the JSON
certificate records both paths and SHA-256 digests.

The raw second bordered tensor has Frobenius norm as large as \(O(10^{10})\).
Its maximum absolute Frobenius residual, `3.15e-4`, is therefore not a proof
failure: after division by the corresponding tensor norm, the maximum
relative residual is below `8e-15`.  The residual adjudication uses this
literal tensor normalization and changes no tolerance, equation, or action
input.

Replaying the signed Volterra vector with the exact action-owned directional,
mixed, and full transverse center curvatures yields a maximum total center
radius below \(10^{-12}\), more than four orders of magnitude inside the
earlier reconnaissance halo used only as a scale comparison.  JAX is no
longer an authority for any center
curvature term.  The remaining Gate-7 radius dependencies are exclusively
outward: the retained \(D^5S\) curvature remainder and the signed Green/step-
map remainder.
