# Direct values at the physical Hermite–Simpson midpoint

The stored replay midpoint is not exactly the physical Hermite–Simpson
midpoint. Substituting its cached rate into a physical residual omits a
nonzero term. The direct producer recomputes endpoint rates and constructs

```
z_i = (W x_i, s_i)
m_i = (z_i + z_{i+1})/2 + h_i (f(z_i) - f(z_{i+1}))/8
```

in Arb. Here raw endpoint states, positive diagonal weights, descriptors,
and the binary64 differences of stored arc parameters are fixed operands.
Products `W x_i` are not first rounded in binary64. The state supplied to
the unchanged physical rate graph is `(W^-1 m_i[:98], m_i[98])`, retaining
the full midpoint enclosure. Direct evaluation includes the full nonlinear
midpoint displacement; no Taylor remainder is discarded.

Every endpoint and midpoint evaluation independently verifies the proposed
normalized eigenpair with `verify_eigenpair_box`. Version V2 also verifies
that its eigenvalue interval contains exactly the zero-based index 24 of
the retained real symmetric Hessian, using two outward inertia counts.
The floating spectral gap only helps propose the box. A strict positive
overlap fixes orientation relative to the stored reference. The same original rate graph, action jets,
quadrature, coefficients, and bordered verified solve are used. No factored
integrand designed for point-valued states is applied to interval states.

Version V3 first normalizes the proposed vector center in Arb and recenters
the proposal at that approximation, outwardly preserving its vector radii
and leaving the eigenvalue box unchanged. The independent inclusion proves
this new box from scratch. This is necessary because an eigen-equation
residual alone cannot bound the normalization defect: in the failed V2
endpoint-4 run the squared-norm defect was about `4.60e-117`, while the vector
radii were about `6.29e-125`. Normalizing the center changed its independently
verified inclusion ratio from about `1.44e7` (failure) to `7.73e-10` (success).
No failed certificate is accepted or reinterpreted. Historical common-base
verification keeps its original proposal unless explicitly requested
otherwise; previously computed Hessian rows are not recertified by this fix.
The legacy gap/residual diagnostics remain proposal diagnostics, not proof
inputs. Index, orientation, and normalized inclusion remain mandatory.

The producer uses a separate cache, exact rational midpoint/radius exports,
source/input and runtime bindings, and hashes of the two newly computed
endpoint artifacts for each midpoint. Restoring rational balls may inflate
radii; it always encloses the original. Such restored balls are used as
outer inputs, never as unchanged original eigenpair target boxes. Scientific
point records omit timing and process IDs so independent production can be
compared byte for byte. A second invocation normally validates and reuses
existing points. With `--recompute`, every point is evaluated afresh and its
NPZ hash and complete scientific record must match the prior evidence.
Disagreement preserves the first evidence and the new candidate, then fails.
The reproduction receipt is emitted only if every point was independently
recomputed, rather than obtained from a cache hit.

Run all 371 endpoints followed by 370 midpoints with:

```
python scripts/derive_n12_gate7_direct_physical_values.py --all-points --workers 6 --worker-hour-cap 3
python scripts/derive_n12_gate7_direct_physical_values.py --all-points --workers 6 --worker-hour-cap 3 --recompute
```

Do not overlap this pool with an existing six-worker Hessian pool.

These values remain conditional on the physical interpretation of the
selected eigenpair branch. Pointwise inclusion, verified index and reference
orientation do not prove branch continuation, the physical quotient, or the complete operator oracle. A
physical `Y` certificate additionally requires the exact residual assembly,
signed causal propagation and all associated arithmetic error bounds.
This campaign does not supply `Z1`, central/mixed/neighborhood bounds or
close Gate 7, and does not create any observable prediction.
