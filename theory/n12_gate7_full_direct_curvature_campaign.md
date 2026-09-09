# Full direct physical curvature campaign

`scripts/run_n12_gate7_full_direct_curvature_campaign.py` extends the paired
interval-13 integration seed to complete finite-history physical-point
coverage. It requires that seed and all 741 independently reproduced direct
DF points before starting new Hessians. The full DF wrapper binding is
verified without changing the Hessian producer's original point backend.

The campaign evaluates endpoint 0, then each midpoint i and endpoint i+1,
followed by that interval's twelve LL/LT/TT local source blocks. Every missing
Hessian point is produced with six fresh workers and an eight-worker-hour
cap, then independently recomputed by another fresh six-worker pool. Every
local source interval is independently recomputed in a separate process.
Already paired points and intervals, including the interval-13 seed, are
reused only after their full inventories, source bindings and receipts verify.
An unpaired complete result proceeds directly to its independent repeat.
Partial first-run rows/blocks resume through the existing producers.

After all 741 points and 370 intervals are paired, the controller builds a
complete inventory, independently rereads/reverifies all inputs, and requires
byte-identical inventory materialization. This aggregation repeat is labeled
separately from numerical recomputation, which belongs to the child receipts.
The full causal quadratic consumer then runs and independently repeats over
all 370 intervals. Its existing partial interval-13 component is preserved.

## Execution and recovery

    python scripts/run_n12_gate7_full_direct_curvature_campaign.py

Only one numerical child runs at a time. An operating-system file lock
prevents duplicate controller owners. Before a restart, any recorded child
must have exited: Windows checks the actual live handle and creation time;
POSIX conservatively refuses while its recorded PID exists. A stale lock
file alone does not block resumption. Denied or uncertain process inspection
fails rather than being interpreted as a stopped process.

The controller observes children in intervals of at most 60 seconds. If an
observation window is exceeded, it records that fact and remains attached
until the actual child exits. It never restarts a child because observation
time elapsed. The Hessian producer's own worker-hour cap remains in force.
Failed children and mismatched results preserve their evidence. Logs receive
unique names. A default 16-GiB free-space reserve is checked before every
child; existing data are never deleted to meet it.

The isolated workspace is `.full_direct_curvature_campaign_work`, containing
the live state, owner lock, logs and paired full source inventory. Core source
fingerprints are checked before and after every child. The individual
scientific producers retain their own complete input/source checks.

This is a continuous local computation, not a scheduled task. Successful
completion proves only the declared paired physical-point campaigns and
their fixed-frame finite-history causal composition. Neighborhood Hessian
bounds, the physical quotient, the full operator/observable chain and the
Museum/manuscript release gates remain separate. Gate 7 and full BHSM are
not closed by completion of this numerical campaign.
