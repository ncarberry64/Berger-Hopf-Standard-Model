# BHSM v19.22-v19.29 N=3 continuation

This local batch continues from the validated v19.21 state with exact 376-row
norm `0.795019734745765`. The square KKT equations, event definition,
explicit event multiplier, eta domain, 14-row complete-child map, two-scale
flux limit, and persistence gate remain unchanged.

## v19.22-v19.25

v19.22 validates the common `1e-6 / 3e-7` direct-response pair. v19.23
retains an invalidated bounded-GMRES interpretation (`info=1`, exact linear
residual `0.797863988631334`, response mismatch `0.632140224737315`),
while independent bidirectional exact merit selects positive
`alpha=0.03125`:

- exact norm: `0.794780177090688`;
- reduction: `0.000239557655077`;
- event magnitude: `0.083556866414175`;
- global eta minimum: `0.774495283824425`.

v19.24-v19.25 reconstruct and promote a fresh rank-14 child. Its two-scale
flux envelope is `1.1968646078e-5`, persistence constraint maximum is
`6.5264e-11`, persistence eta minimum is `0.999989853702898`, and
nonzero relative evolution is retained.

## v19.26-v19.29

v19.26 validates the finer `3e-7 / 1e-7` direct-response pair. The v19.27
solver interpretation is invalidated (`info=1`, exact linear residual
`2.14423771812804`, response mismatch `1.09282835873508`). Exact merit
independently selects positive `alpha=0.015625`:

- exact norm: `0.793187079982019`;
- reduction: `0.001593097108669`;
- event magnitude: `0.083534732056130`;
- global eta minimum: `0.774496505467421`.

v19.28-v19.29 recompute and promote the complete child with:

- rank 14;
- trace / constraints / momentum:
  `1e-15 / 9.4e-14 / 8.339e-12`;
- two-scale flux envelope: `1.0616945002e-5`;
- child eta minimum: `0.999995803893641`;
- persistence constraint maximum: `6.5285e-11`;
- persistence eta minimum: `0.999994150989665`;
- nonzero relative evolution: retained.

Individual residual components remain free to worsen during coupled steps.
The exact residual remains nonzero, so `N3_EXACT_KKT_CLOSURE` and
`FULL_BHSM_COMPLETE` remain false. GitHub publication, the long regression,
and USB archival remain deferred.
