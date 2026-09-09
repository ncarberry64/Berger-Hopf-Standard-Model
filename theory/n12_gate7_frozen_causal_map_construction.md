# Frozen causal-map construction error

The accepted replay uses the exact inverse of the stored reduced right block,
not the binary64 approximation to the assembled causal map. For each interval,
the target is `P* = -R^-1 (T L V)`, with all supplied binary64 matrices interpreted
exactly. At 512 bits Arb encloses `P* - P`, where `P` is exactly the map in the
completed signed center. An inverse residual below one certifies invertibility;
signed Gram and Frobenius bounds enclose the map error's Euclidean operator norm.
This does not enclose physical evaluation errors in the supplied matrices.

For zero initial state, let `G` propagate source sequences through `P` and let
`DeltaP` act at interval i on node i. The first perturbation is zero because the
initial state is fixed. Transporting the local map-error norms gives a bound
`k >= ||G DeltaP||` in the node block-sup Euclidean norm. All interval indices and
all stored center map bytes must match; no normalization tolerance is used.

For `z* = P* z* + f*` and `z = P z + f`, the error satisfies
`e = G DeltaP z + G DeltaP e + G(f* - f)`.
If `k < 1`, then

```
||e|| <= (k ||z|| + ||G(f* - f)||)/(1-k).
```

The reported multipliers `k/(1-k)` and `1/(1-k)` are rounded outward. The latter
includes interactions between source errors and map-construction errors; these
must not be omitted when combining certificates. Bounds on the exact stored
response and on source errors are separate inputs, not established by this
map certificate. A gain bound at least one is inconclusive, not a physical
obstruction. Although the finite chain is triangular, no fallback finite-series
estimate is needed when this sufficient gain condition succeeds.

This certificate changes no action, mesh, center, norm, preconditioner, or physical
prediction. Output-map construction, physical direction/Hessian evaluation,
pullback assembly, center covariance arithmetic, and neighborhood remainder
remain open. Gate 7 and full BHSM completion remain false.
