# Gate-7 correction-direction retained-action majorants

The retained action is now bounded through fifth order on a uniform
`3.6e-6` action ball around all 48 finite-history seams, after four input
legs are aligned with the normalized signed Green correction and the output
leg remains the full 98-dimensional action covector.

This certificate uses only the `MixedBound` interface already committed in
`scripts/derive_n12_action_ball_majorants.py`.  Because that file has
protected uncommitted signed-output additions in the working tree, the
wrapper verifies the expected committed SHA-256 and executes the committed
Git blob in memory when the working hash differs.  It neither edits nor
stages the protected file and records both hashes.

The result certifies action derivatives, not graph-field derivatives.  The
selected eigenline, branchwise hard inverse, bordered response, normalization,
and causal Green composition must still be applied with signed correlation
before the outward `D2f` correction-cone source can be claimed.
