# Restart-safe direct physical Hessian campaign

Status: executable producer for complete ambient Hessians at individually
selected actual physical HS points. This document does not assert that a
numerical point campaign has run or that full BHSM is complete.

The producer consumes the independently reproduced 741-point direct-value
campaign through the same point-input loader as the direct DF producer.
Endpoints retain their exact stored raw binary64 state. Midpoints retain the
Arb uncertainty of the actual weighted HS construction and its unweighting.
No old stored-midpoint Hessian or selected-pilot cache is adopted.

For each point, six fresh spawned workers evaluate the upper input triangle
of D2f in the exact weighted augmented ambient identity basis. Row i contains
all 99 outputs for input pairs (i,j), j=i..98. The lower input triangle follows
from symmetry of the locally smooth selected rate Hessian. Finite derivative
evaluation, a normalized simple eigenpair, and nonzero denominators are
required; this symmetry does not assert branch continuation through the full
history or the nonlinear proof neighborhood.

Each worker constructs the original action jets and independently verifies
the normalized, positively oriented index-24 eigenpair before installing the
factored/bulk contraction adapters. Its base rate must overlap the matching
paired direct value. That verified base is reused across rows in the same
worker process and physical point. Represented interval states, reference,
precision and source fingerprints remain checked. A new process pool is
created for each independent repeat, so base data is not inherited from the
first computation.

Rows are exported as rational Arb midpoint/radius arrays, never narrowed to
binary64 tensors. The point-specific workspace is
`.direct_physical_hessian_work/{endpoint|midpoint}_NNN`. Each of its 99 rows
has NPZ data and canonical JSON metadata. Restart reuses only matching rows.
Changed data, source/dependency bindings, proof fields, shapes or noncanonical
metadata are rejected. A differing independent row candidate receives a
unique filename, preserving both the original and every failed candidate.

The parent checks the complete source/point bindings on entry and exit;
workers check full point inputs once per process and computation sources per
row. Rehashing the entire upstream value campaign at every Hessian row would
add avoidable I/O and is not used. No point manifest is written before all 99
rows and exactly 198 scientific files have been verified. On repeat, the
manifest must match and all row tasks must report actual recomputation. An
earlier reproduction receipt is retained as history while the new attempt
runs; it is not left presenting success if that new attempt fails.

```text
python scripts/derive_n12_gate7_direct_physical_hessians.py --stage midpoint --index 13 --preflight
python scripts/derive_n12_gate7_direct_physical_hessians.py --stage midpoint --index 13 --workers 6 --worker-hour-cap 8
python scripts/derive_n12_gate7_direct_physical_hessians.py --stage midpoint --index 13 --workers 6 --worker-hour-cap 8 --recompute
```

The same commands accept `--stage endpoint` for endpoint indices 0..370;
midpoint indices are 0..369. The cap is worker-hours, converted to wall time
by dividing by the requested worker count. A producer failure stops its own
pool, retains completed rows and writes a failure record. An external
observer timeout alone is not evidence that the producer or its children
have stopped; inspect their live handles before any recovery.

Tests exercise real rational row serialization, cache reuse, actual repeated
row evaluation with byte-identical output, preserved mismatches, missing or
nonfinite rows, altered proof/dependency metadata, exact complete inventory,
fresh spawn selection and failed-repeat receipt handling. Synthetic campaign
fixtures test orchestration boundaries, not a physical Hessian result.

A complete point manifest is an ambient point-Hessian result only. A consumer
still needs matching paired DF, the physical HS direction maps, frozen frame
and inverse bindings, and complete causal composition. The direct HS second
variation retains the midpoint's own second derivative and the Taylor factor
one-half. Physical quotient identification, neighborhood bounds, operator
and observable dependencies remain open; no physical contraction or Gate7
closure is asserted by this producer.
