# BHSM v19.14-v19.21 N=3 continuation

This local batch starts from the validated v19.13 fallback state with exact
376-row norm `0.795953277613514`. The square KKT equations, explicit event
multiplier, event definition, eta domain, complete-child map, flux limit, and
persistence gate remain unchanged.

## v19.14-v19.17

v19.14 validates the common `3e-7 / 1e-7` direct-response pair. v19.15
retains an invalidated bounded-GMRES interpretation (`info=1`, exact linear
residual `1.79662423624176`, response mismatch `1.252018337721`) but its
independent bidirectional exact-merit scan selects negative
`alpha=-0.03125`:

- exact norm: `0.795713884217715`;
- reduction: `0.000239393395799`;
- event magnitude: `0.083699194728613`;
- global eta minimum: `0.774457998426423`.

v19.16 reconstructs a fresh rank-14 child. v19.17 promotes it only after
trace, seven constraints, attachment momentum, eta, two-scale flux, and
positive-duration persistence pass. The flux envelope is
`2.693486298e-6`, the persistence constraint maximum is `6.5664e-11`,
and nonzero relative evolution remains present.

## v19.18-v19.21

v19.18 validates the `1e-6 / 3e-7` direct-response pair. The v19.19
bounded-GMRES interpretation remains invalidated (`info=1`, exact linear
residual `0.846428373290416`, response mismatch `0.431144810074498`).
Exact nonlinear merit independently selects positive `alpha=0.03125`:

- exact norm: `0.795019734745765`;
- reduction: `0.000694149471950`;
- event magnitude: `0.083596533313489`;
- global eta minimum: `0.774487922518948`.

v19.20-v19.21 recompute and promote the complete child with:

- rank 14;
- trace / constraints / momentum:
  `1e-15 / 9.4e-14 / 9.771e-12`;
- two-scale flux envelope: `4.867701812e-6`;
- child eta minimum: `0.999990139952888`;
- persistence constraint maximum: `6.536e-11`;
- persistence eta minimum: `0.999987308681696`;
- nonzero relative evolution: retained.

The temporary environment interruption during v19.19 produced no artifact.
The deterministic probe was restarted from the same v19.17 source with the
repository `src` directory restored to `PYTHONPATH`; no scientific input,
equation, or acceptance condition changed.

The exact residual remains nonzero. `N3_EXACT_KKT_CLOSURE` and
`FULL_BHSM_COMPLETE` remain false. GitHub publication, the long regression,
and USB archival remain deferred.
