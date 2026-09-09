# Full direct derivative campaign with independent batches

The full campaign reuses the direct physical point producer unchanged. An
explicit backend selects `.full_direct_physical_jacobian_work`, adds its own
source hash and workspace identity to the binding, and installs the same
configuration in spawned workers. The selected-pilot cache and its manifests
remain intact. The full local-defect consumer likewise uses a separate output
directory while retaining the original HS and frozen-inverse algebra.

The campaign is divided into 13 fixed groups of at most 29 consecutive
intervals. For each group, the original producer evaluates its endpoints and
midpoints, then independently repeats every selected point. Save both the
resulting `manifest.json` and `reproduction.json` under
`batches/START_END/` before advancing to the next group. A normal cache hit
does not count as independent reproduction. Adjacent groups share one
endpoint; their source bindings and artifact hashes must agree.

The aggregation command verifies every batch receipt against its exact
manifest bytes, the prescribed point lists, exact file inventories, common
source/runtime binding, and current artifact hashes. It requires the union
to contain exactly all 371 endpoints and 370 midpoints, with 1,482 point
files. Only then does it emit a full reproduction receipt. The receipt names
and hashes every supporting batch manifest and independent repetition receipt.
This is a union of actual independent computations, not an inference from
file presence or repeated cache reads.

Example bounded batch (run its independent repeat before the next batch):

```
python scripts/derive_n12_gate7_full_direct_physical_jacobians.py --midpoints 0,1,2 --workers 6 --worker-hour-cap 8
python scripts/derive_n12_gate7_full_direct_physical_jacobians.py --midpoints 0,1,2 --workers 6 --worker-hour-cap 8 --recompute
```

The operator controls the group lists and saves their receipt snapshots;
the full aggregation uses the prescribed groups in its source. After all
13 prescribed groups have genuinely reproduced, run the aggregation twice
and compare its full manifest and receipt bytes:

```
python scripts/certify_n12_gate7_full_direct_df_reproduction.py
python scripts/certify_n12_gate7_full_direct_physical_local_defects.py --all-midpoints
python scripts/certify_n12_gate7_full_direct_physical_local_defects.py --all-midpoints --recompute
```

The measured pilot, not an assumption of ideal core scaling, should guide
worker and time limits. Only one numerical pool may run at a time. A failed
batch remains incomplete; the aggregator cannot promote it. Full pointwise
DF and local C/DL/DR coverage do not by themselves certify the causal Z1
bound, physical quotient, branch continuation, neighborhood, or Gate 7.
