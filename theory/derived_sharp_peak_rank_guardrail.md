# Derived Sharp-Peak Rank Guardrail

In the strict sharp-peak limit, the approximation

```text
I_ij approx Phi0 a_i^* b_j
```

is an outer product. Therefore `rank(I) <= 1`. This means the strict point-sampling term cannot by itself generate three nonzero singular values. Full rank-three Yukawa structure requires additional derived structure such as finite-width moments of the universal profile, internal mode orthogonality/selection, boundary transport, or dressing terms. This is a guardrail against overclaiming the sharp-peak approximation.

Status: `SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL`.
