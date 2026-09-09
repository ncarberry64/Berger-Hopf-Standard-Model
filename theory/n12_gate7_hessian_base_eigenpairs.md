# Common eigenpair verification for completed Hessian points

Original, factored-integrand and bulk-transfer Hessian producers all prepare
the same original base action jets and eigenpair before changing contraction
scopes. Their source-bound row caches do not by themselves supply the newer
independent normalized-eigenpair inclusion and spectral-index proof.

The companion producer first validates a complete 99-row cache against its
current exact input/source fingerprint. It reconstructs only the original
common preparation at the row producer's 256-bit precision, then verifies
those original eigenpair balls at 512 bits. Independent normalized inclusion,
positive reference overlap, and outward inertia counts identifying index 24
are all required. It never calls a physical Hessian row worker.

This is a reconstruction of the unchanged deterministic common preparation,
not a read of historical worker memory. The original row input arrays,
backend sources, and action provenance must agree. The report binds every
raw row and metadata file and exports the common reduced Hessian, eigenvector
and eigenvalue as exact rational midpoint/radius arrays. Serialization may
outwardly inflate reconstructed balls; the inclusion test uses the original
in-memory proposals, and its report retains their exact target radii.

Independent reproduction reconstructs the base again and requires identical
NPZ hashes and scientific records. On disagreement the previous evidence and
new candidate remain available. A missing row blocks verification; a failed
eigenpair or inertia check is retained as a failure, not silently discarded.

Example for a completed bulk point:

```
python scripts/certify_n12_gate7_hessian_base_eigenpairs.py --backend bulk --midpoints 13 --workers 1
python scripts/certify_n12_gate7_hessian_base_eigenpairs.py --backend bulk --midpoints 13 --workers 1 --recompute
```

Use one backend per process and do not overlap a new pool with an existing
six-worker numerical pool. The common-base companion does not replace the
row-cache proof, derive the physical mode-selection rule, or establish branch
continuation, neighborhood bounds, the physical quotient, a root, or Gate 7.
Other endpoints and midpoints require their own evidence.
