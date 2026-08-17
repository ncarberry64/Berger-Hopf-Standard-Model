# BHSM v19.00-v19.13 N=3 continuation

This local checkpoint continues from the validated v18.99 state with exact
376-row norm `0.801038620295453`. The square KKT system, explicit event
multiplier, exact residual, eta domain, 14-row-on-26-variable child map,
`2e-5` two-scale flux limit, and persistence gate remain unchanged.

## v19.00-v19.03

v19.00 validates the common `1e-6 / 3e-7` response pair. The v19.01
bounded-GMRES interpretation is invalidated (`info=1`, exact linear residual
`0.777764677776054`, response mismatch `0.673923904697255`), but
bidirectional exact nonlinear merit selects positive `alpha=0.5`:

- norm `0.797947455518253`;
- reduction `0.003091164777200`;
- event magnitude `0.083702285432041`;
- global eta minimum `0.774350684110442`.

v19.02 reconstructs a fresh rank-14 child. v19.03 promotes it with flux
envelope `1.9543818199e-5`, persistence constraint maximum
`6.7137e-11`, positive eta, and nonzero relative evolution.

## v19.04-v19.07

v19.04 again validates the `1e-6 / 3e-7` response pair. The v19.05 solver
interpretation is invalidated, while exact merit selects positive
`alpha=0.03125`:

- norm `0.797206261170734`;
- reduction `0.000741194347519`;
- event magnitude `0.083607896617580`;
- global eta minimum `0.774442950134984`.

v19.06-v19.07 recompute and promote the complete child with rank 14, flux
envelope `5.714962254e-6`, persistence constraint maximum `6.5726e-11`,
positive eta, and retained motion.

## v19.08-v19.13 primary rejection and fallback

v19.08 validates the finer `3e-7 / 1e-7` response pair. v19.09 invalidates
its solver interpretation but finds a lower exact-merit primary candidate at
positive `alpha=0.03125`, norm `0.795262882781664`. v19.10 reconstructs
its rank-14 child. v19.11 rejects promotion because the independently
recomputed flux envelope is `2.4244980204e-5`, above the unchanged
`2e-5` limit. Rank, trace, constraints, momentum, eta, persistence, and
motion otherwise pass.

v19.12 then reconstructs the next-lowest already measured state, positive
`alpha=0.015625`:

- norm `0.795953277613514`;
- reduction from v19.07 `0.001252983557220`;
- event magnitude `0.083604143281612`;
- global eta minimum `0.774473956949660`.

v19.13 promotes this fallback only after the fresh complete child passes:

- rank 14;
- trace / constraints / momentum:
  `1.139e-12 / 2.131e-12 / 1.52609e-10`;
- two-scale flux envelope: `8.051004262e-6`;
- persistence constraint maximum: `6.4859e-11`;
- persistence eta minimum: `0.999977569983478`;
- nonzero relative evolution: retained.

The exact residual remains nonzero. `N3_EXACT_KKT_CLOSURE` and
`FULL_BHSM_COMPLETE` remain false. The active dependency is continued
physically admissible exact descent to `F_376=0`.

The author-supplied history, particle-signature, reconstruction, scale,
decay, and extreme-scale hypotheses are preserved—without implementation or
claim promotion—in the
[v19.03 downstream physical-doctrine ledger](BHSM_DOWNSTREAM_PHYSICAL_DOCTRINE_LEDGER_V19_03.md).
GitHub publication, the long regression, and USB archival remain deferred.
