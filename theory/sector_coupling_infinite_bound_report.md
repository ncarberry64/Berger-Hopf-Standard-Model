# BHSM v2.1 Sector-Coupling Infinite-Basis Bound

Status: `SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL`
Theorem complete: `False`
Method: Schur row/column bound plus relative domination by A0 on fixed-label sector blocks
Independent of k_max: `True`
Finite-scan evidence used: `False`

| Quantity | Value |
| --- | --- |
| connects | `distinct charged sectors at fixed (k,j,q,chi)` |
| preserves | `k, j, q, chirality` |
| vanishes on formal kernel | `True` |
| row support bound | `2` |
| column support bound | `2` |
| max weight bound | `0.007810506742754974` |
| Schur row-sum bound | `0.015621013485509948` |
| Schur column-sum bound | `0.015621013485509948` |
| relative a_K | `0.015621013485509948` |
| relative b_K | `0.0` |

## Assumptions

- The complete sector-coupling rule has the same fixed-label sparse support as the formal-kernel scaffold.
- The sector-coupling weights are uniformly bounded by the stated scaffold weight.
- The diagonal reference action dominates the fixed-label sector-coupling quadratic form.

## Open Obligations

- derive the fixed-label sparse sector-coupling rule from the complete twisted Dirac/bundle operator
- prove the uniform weight bound in the complete infinite basis
- prove compatibility with the final formal complement projector

## Limitations

- The bound is independent of k_max under the scaffold rule, but the rule is not yet derived from the complete operator.
- This is not a proof of the full H_T theorem.
