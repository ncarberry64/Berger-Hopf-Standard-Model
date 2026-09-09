# Common-operand arithmetic envelope

Bind the complete reconstructed covariance response and every assembly,
coordinate/storage, output-map, and frozen causal-map certificate to the same
stored maps, center, and exact stored axes. Require complete coverage and every
current input hash; conflicting bindings fail closed.

Let C_L,C_T bound the reconstructed local-tensor response under stored maps.
Let a_L,a_T bound the operator norms of `e.T` and `I-e e.T`. Their values are
computed outward; an exactly unit stored axis is not assumed. The identity
`z=e(e.T z)+(I-e e.T)z` gives `||z||<=a_L C_L+C_T`.

Sum the source-error coefficients transported under the stored maps:

- reconstructed pullback assembly and cross-block addition;
- coordinate error, including its tensor-storage cross term;
- stored tensor projection and scalar addition;
- output-map construction acting on the complete coordinate/storage-corrected tensor.

Call this sum E. If k bounds the complete frozen-map perturbation gain and k<1,
the final uniform response error is

```
D = [k(a_L C_L+C_T)+E]/(1-k).
```

The final transverse-quadratic output coefficients are `C_L+a_L D` and
`C_T+a_T D`. The formula includes the interaction of causal-map error with all
source errors. In particular, use the output certificate's stored-map coefficient
in E; its frozen-map multiplier is applied once, in the combined formula.

An exact stored-polynomial radius screen uses these coefficients and the
existing Y,Z1,central,mixed values. It does not recertify those other values or
prove a physical self-map/contraction. The enclosed arithmetic starts with
the exact supplied tensors, frames, midpoint kinematic maps, ambient derivative,
and frozen preconditioner operands. Physical derivative/direction evaluation,
kinematic-map construction, neighborhood remainder, and final joint contraction
remain separate obligations. This changes no action, mesh, parameter, or
prediction. Gate 7 and full BHSM completion remain false.
