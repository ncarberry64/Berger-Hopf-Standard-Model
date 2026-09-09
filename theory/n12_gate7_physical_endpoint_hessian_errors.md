# Physical endpoint Hessian error in exact projector coordinates

The signed Hermite--Simpson center uses the stored symmetric endpoint tensor
Q, a 73-dimensional restriction, pulled back by the stored transverse basis
V.T to 74 endpoint coordinates. Its exact stored representative is
`Q[V.T,V.T]`. This includes no claim that the stored V is exactly orthonormal.

The physical endpoint contribution instead uses the frozen trial frame F and
the exactly normalized projector `Pi = I - a a.T/(a.T a)`. Directly enclosing

```text
E = D2(rate)[F Pi, F Pi] - Q[V.T, V.T]
```

therefore includes both the physical Hessian discrepancy and the difference
between the two direction representations. It requires 74 upper-triangular
rows (2,775 pairs), rather than a full 99-direction ambient tensor. The
initial endpoint is fixed and contributes exactly zero; only nodes 1..370
are eligible. Selected nodes never imply full endpoint coverage.

The Arb direction adapter pins the complete existing batched physical graph
and changes exactly its two input-direction leaf conversions. Existing Arb
values, including their radii and information below binary64 resolution,
are preserved. Float leaves retain the parent's original conversion. Every
action contraction, eigenline, bordered solve, and chain-rule operation is
unchanged. The previously validated factored action integrand and sparse
mixed jets remain the numerical backend.

The stored representative is evaluated in Arb from the exact supplied
binary64 Q and V, before subtraction and outward export. Cache metadata bind
the graph, adapter, backend, physical state, descriptor, frame, axis, basis,
tensor, and original kernel/provenance. Hessian symmetry is used only to
assemble a complete selected node from every upper-triangular row.

Subsequent integration must map this 99-by-74-by-74 physical error through
both incident frozen endpoint output maps, include their construction errors,
and account for the common endpoint input in adjacent intervals. Existing
stored assembly/projection arithmetic is a separate error contribution.
Physical frame/constraint authority and neighborhood/contraction bounds
remain open. No measured quantity, action, normalization, or frozen prediction
is changed.

The selected-endpoint pullback consumer implements both incident output maps
with their stored-operand construction errors. A single endpoint quadratic
monomial has coefficient bounded by the mapped tensor Frobenius norm; it
does not need the factor two used for a concatenated pair of endpoint inputs.
The terminal endpoint has only one incident interval. These contributions
are not yet a global causal bound. In particular, the physical midpoint DF
error in the endpoint output incidence remains a separate attachment.

```text
python scripts/derive_n12_gate7_physical_endpoint_hessian_errors.py --nodes 1 --workers 6 --worker-hour-cap 3
python scripts/certify_n12_gate7_physical_endpoint_hessian_pullbacks.py --nodes 1
```
