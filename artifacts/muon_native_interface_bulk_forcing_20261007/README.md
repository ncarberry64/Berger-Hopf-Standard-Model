# Recovered seven-port, one-column forcing packet

Starting HEAD: 0f13a65082d4df0ba510540a32071bf938c7716e.
Scientific reference: 524ed90689bd5923c249bba2e699abf627e703cd.
PR #465, codex/muon-parent-maxwell-density-review.

The new one-column finite KKT control ran once. Eleven control checks and
twelve targeted tests pass. Its prescribed rational data are arithmetic
controls, not a physical BHSM normal source, impedance, cutoff or anomaly.
The three recovered helpers are original scientific-source bytes. Cached
Gate7 producer calculations were inspected, not replayed.

run_1/cache_roles.json identifies the actual interval13 F_n, launch F_p
and output g_n. run_1/row_identification.json gives the necessary owner row
and dual mapping and its nonstationary gradient terms. The control proves
that a residual-row scaling preserves the solve while changing an uncorrected
impedance. run_1/result.json has null physical b_psi, f_psi, response, z_psi,
r/i, heat and a_mu/g_mu. Missing terms are not zero-filled.

The next consumed operand is one same-owner normal-source Euler column,
including its established seven-port coordinates and the consumed residual
row/dual identification. No full7x73 or Gate7 closure is required.

See theory/muon_native_interface_bulk_forcing_20261007.md for the equations,
cache producers and exact reproduction commands. Fresh output is mandatory.
Input hashes, revision/status, snapshots and the executed control are retained.
validation_scope.json distinguishes physical requirements not evaluated from
passing arithmetic checks. Source-only worktree.patch preserves the introduced
code and equations; publication.json records the verified science commit.
