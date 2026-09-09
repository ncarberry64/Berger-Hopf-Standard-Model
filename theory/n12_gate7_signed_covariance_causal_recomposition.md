# Signed covariance recomposition

The covariance formation certificate encloses exact Gram and adjacent products
of the reconstructed local tensor blocks about the saved center arrays. Here
all 370 exact stored causal maps are composed at 512 bits. No map-construction
error or physical input error is implicitly included.

Let R_i,L_i,O_i be right, left, and cross-block covariance balls, and A_i the
previous-right/current-left adjacent covariance. Before taking a norm, complete
the shared input node in the coordinate frame after map P_i:

```
D_(i-1) = P_i R_(i-1) P_i.T + L_i + P_i A_i + A_i.T P_i.T.
```

At target node n, transport each completed D and each O by its full signed
suffix G. The final R_(n-1) remains pending at the target. Forming the suffix
before applying covariance uncertainty prevents wide independent interval
entries from being recursively propagated through every map. It preserves
shared-node cancellation and includes every original diagonal and cross block.
Target nodes are independent and are distributed across six numerical workers
in interleaved groups. Each group retains all causal maps and source covariances.
Uncomputed nodes are null, not zero; the parent rejects missing or duplicate
targets and assembles every node in canonical order. Parallel completion order
does not enter the numerical report.

For an output axis e, compute Gram `G.T G` and `w=G.T e`. Then longitudinal
squared Frobenius norm is `w.T C w`, trace is `tr(Gram C)`, and transverse squared
norm is `tr(Gram C)+(||e||^2-2) w.T C w`. This is exactly the projection
`I-e e.T`, even when stored normalization does not yield an exactly unit vector.
Sum outward square-root bounds for all source blocks at each target. No negative
upper bound is silently clipped; inconsistent covariance enclosures fail closed.

The result bounds the complete reconstructed local-tensor response. The separately
certified assembly errors must still be added to relate it to exact stored-input
pullbacks, followed by the coordinate, tensor-storage, output-map, and frozen
causal-map terms with their cross terms. Physical derivative/direction errors,
kinematic construction, neighborhood remainder, and final two-radius contraction
are not proved here. No action or prediction changes; Gate 7 remains open.
