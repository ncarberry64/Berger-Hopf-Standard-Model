# Frozen Hermite--Simpson output maps

For exact stored operands, set `B=-R^-1 T` and `J=B A`, where R is the same
frozen reduced right block as the accepted replay, T the stored test frame,
A the stored ambient midpoint derivative, and h the stored interval step.
The exact left/right/midpoint output maps are `h B/6 +/- h^2 J/12` and `2 h B/3`.
Arb at 512 bits encloses their differences from the binary64 maps consumed by
the signed center and prior storage/coordinate certificates. Physical errors in
the input matrices and kinematic midpoint-map construction are not included.

Each output difference has an operator bound e and a scalar-column bound es.
Let u,c bound the exact retained/complement coordinate operator norms, including
the independently certified solve error. With tensor Frobenius bounds qUU,qCU,qCC,
full projection error p, and scalar-only addition error s, the mapped error is

```
u^2 [e (qUU+p) + es s] + e [2 u c qCU + c^2 qCC].
```

This applies the output difference to the entire coordinate/storage-corrected
tensor, so it includes all output/coordinate/storage cross terms. Endpoint maps
use c=0 and their exact stored input basis. Every local output-map hash is checked
against the complete stored-rounding certificate. Midpoint norms come from the
certificate for the actual completed-center target; historical raw-axis targets
are not substituted. Endpoint tensor hashes match the corrected representation.

The sum of local Frobenius errors is multiplied by two because the concatenated
endpoint input has squared norm at most twice the squared block-sup radius.
The complete signed stored causal chain transports these local coefficients.
The frozen causal-map source multiplier also bounds this same output-error
response through the exact frozen maps. It does not include the baseline
stored-response error from changing causal maps, which remains a separate term.

This is one arithmetic-error operand. It does not certify physical Hessian or
direction evaluation, physical ambient derivative error, assembly arithmetic,
center covariance arithmetic, or neighborhood remainder. No action, measured
parameter, mesh, or prediction changes. Gate 7 and full BHSM completion remain false.
