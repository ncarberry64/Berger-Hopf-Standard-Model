# Physical midpoint Hessian error rows

The producer evaluates the existing physical rate Hessian at explicitly named
stored midpoint states and descriptors. Its input directions are the complete
stored 99-column ambient basis. It subtracts the corrected symmetric stored
quadratic tensor in that same basis and saves an outward binary64 ball for
the small discrepancy, rather than rounding the much larger physical tensor
and losing the discrepancy's precision.

For each output component, the physical Hessian is symmetric wherever the
existing eigenline, bordered solve, and normalization guards establish the
evaluation. Therefore 99 upper-triangular rows cover all 4,950 direction pairs.
This uses mathematical Hessian symmetry; it neither relaxes the historical raw
skew test nor replaces a failed ordered-bilinear claim.

Every row export is checked to contain its original Arb discrepancy. Its data
and sidecar bind the midpoint's fingerprint, row, dimensions, precision, source
identity, and payload hash. Reuse fails on a changed fingerprint, payload,
shape, nonfinite value, or negative radius. Full assembly starts with missing
entries and requires every row before applying symmetry. Missing rows are
never treated as zero error.

Workers cache only the action jets and eigenline at their current identical
stored state. A point change reloads them through the original functions.
Source hashes are checked for every row. Runs use at most six numerical
workers, explicitly selected midpoint indices, and an explicit bounded worker
time allowance. A failure stops the owned pool and preserves completed rows
and a failure record.

The first midpoint pilot may be adopted without recomputation only through
the dedicated adoption path. That path pins the original aggregate digest,
verifies every original row digest and source, and requires identical physical
inputs, precision, provenance, and shared computational sources. It copies the
same midpoint/radius arrays into the canonical cache with their legacy origin
attached; it leaves all original files and fingerprints unchanged.

Example bounded reconnaissance:

```sh
python scripts/derive_n12_gate7_physical_midpoint_hessian_errors.py --adopt-first-midpoint
python scripts/derive_n12_gate7_physical_midpoint_hessian_errors.py --midpoints 175,126,1,9,369 --workers 6 --worker-hour-cap 12
```

The output is physical evaluation error at stored operands. Physical direction
construction, output and kinematic map construction, uncertainty in the
background/domain, neighborhood remainders, causal transport, and contraction
remain separate obligations. Completion of selected midpoints is not completion
of all 370 midpoints, the endpoints, Gate 7, or BHSM.
