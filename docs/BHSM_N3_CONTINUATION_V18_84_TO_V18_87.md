# BHSM v18.84-v18.87 N=3 continuation

The source is the independently promoted v18.83 state with exact 376-row norm
`0.80554785212226`. The square 376-variable KKT system, explicit event
multiplier, exact residual, and 14-row-on-26-variable complete-child map remain
unchanged.

v18.84 validates the common `1e-6 / 3e-7` exact-response plateau, with maximum
relative response change `0.001442081450502`. v18.85 scans both orientations
of a fresh action-owned probe. Its GMRES interpretation is invalidated
(`info=1`, exact linear residual `0.812560692491573`, response mismatch
`0.484566123919772`). Independently evaluated exact nonlinear merit selects
positive `alpha=0.0625`:

- exact norm: `0.804250811090346`;
- reduction: `0.001297041031914`;
- event magnitude: `0.083534405469597`;
- global eta minimum: `0.774269378816236`.

v18.86 reconstructs a fresh rank-14 complete moving child. v18.87 then passes
the unchanged promotion gate:

- trace / constraints / momentum: `7.7212e-11 / 1.1452e-11 / 3.903126e-9`;
- independent two-scale flux envelope: `4.071481113e-6`;
- child eta minimum: `0.99999414333419`;
- persistence constraint maximum: `6.1502e-11`;
- persistence eta minimum: `0.999992080081815`;
- nonzero relative evolution: retained.

The exact residual remains nonzero. `N3_EXACT_KKT_CLOSURE` and
`FULL_BHSM_COMPLETE` remain false. Full GitHub regression and USB publication
are intentionally deferred until a materially larger scientific milestone.
