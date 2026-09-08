# Stored rounding through the causal chain

The local stored-rounding certificate provides a uniform coefficient `e_i`
for the error injected after interval `i`: its Euclidean output norm is at
most `e_i r_T^2` whenever both endpoint inputs have norm at most `r_T`.
This already includes the factor two for concatenated endpoint coordinates.
It must not receive a second factor two during causal transport.

For the same exact stored binary64 maps `P_i` used by the signed center,
the error satisfies `z_0=0`, `z_(i+1)=P_i z_i+d_i`. Consequently its uniform
coefficient at node `n` is bounded by

```
sum_(s=0)^(n-1) ||P_(n-1) ... P_(s+1)||_2 e_s.
```

The empty product has norm one. In particular, `P_s` does not multiply
the error injected after interval `s`. No independence assumption is needed
for this triangle bound; source errors may be correlated.

The implementation groups ten fine intervals into each computational block.
Within a block it computes signed suffix products before bounding every
source. Between block boundaries it likewise computes signed products of
whole block maps before taking a norm. A fine node receives its block's
partial error plus the norm of its signed prefix times the preceding
boundary error. This can overestimate the direct full-chain sum because
block source errors have been replaced by balls, but always bounds it.
The grouping changes no action, proof norm, physical interval, or source.

All matrix products and scalar accumulation use 512-bit Arb. For an Arb
matrix enclosure `B`, entrywise absolute upper bounds bound its spectral
norm by the smaller of its Frobenius norm and
`sqrt(||B||_1 ||B||_infinity)`. These bounds include the arithmetic error of
the products themselves; they are not norms of rounded product midpoints.

The producer requires the complete current all-370 local certificate and
the scalar-correction certificate it consumes. It checks their input hashes,
and binds the actual stored causal-map array by its own hash. Execution is
deferred until the local certificate exists and a numerical worker is free;
production materialization must run twice with identical bytes.

The output is an additive quadratic error coefficient for the full output
Euclidean norm. No longitudinal or transverse projector is silently treated
as exactly orthogonal. Any later projection must use its verified operator
bound. This calculation encloses only transport of the local stored addition
and symmetric-projection errors through exact stored causal maps. Physical
Hessian evaluation, map construction, coordinate error, pullback assembly,
center covariance arithmetic, and neighborhood variation remain separate
operands. This certificate does not close Gate 7 or complete BHSM.
