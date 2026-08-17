# BHSM v19.30-v19.41 N=3 continuation

This local batch starts from the validated v19.29 state with exact 376-row
norm `0.793187079982019`. The square KKT equations, event definition,
explicit multiplier, eta domain, complete-child map, flux certification, and
persistence gate remain unchanged.

## v19.30-v19.33

v19.30 validates the `3e-7 / 1e-7` direct-response pair. v19.31 invalidates
its bounded-GMRES interpretation (`info=1`, exact linear residual
`2.33707085706522`, response mismatch `1.0308406557585`) while independent
exact merit selects positive `alpha=0.015625`:

- exact norm: `0.792728134993666`;
- reduction: `0.000458944988353`;
- event magnitude: `0.083534194648883`;
- global eta minimum: `0.774570327494707`.

v19.32-v19.33 reconstruct and promote a rank-14 complete child with flux
envelope `9.317844902e-6`, persistence constraint maximum `6.5358e-11`,
positive eta, and nonzero relative evolution.

## v19.34-v19.37

v19.34 validates the `1e-6 / 3e-7` response pair. v19.35 again invalidates
the solver interpretation and finds a physically admissible but microscopic
exact-merit line state:

- positive `alpha=4.65661e-10`, backtrack 31;
- exact norm: `0.792726003595835`;
- reduction: `2.131397831e-6`;
- event magnitude: `0.083534194646587`;
- global eta minimum: `0.774570327494543`.

v19.36-v19.37 pass the complete-child gate with rank 14, flux
`1.887680536e-6`, persistence constraint maximum `6.5038e-11`, positive
eta, and retained motion. The state is promoted because its independent
physical merit and every unchanged gate pass; the tiny line fraction is not
itself a physical defect.

## v19.38-v19.41

v19.38 validates the `1e-6 / 3e-7` response pair. The next bounded probe
demonstrates that the v19.35 microscopic line fraction was not a persistent
stall. v19.39 retains an invalidated solver interpretation but exact merit
selects positive `alpha=0.0625`:

- exact norm: `0.791308733253912`;
- reduction: `0.001417270341923`;
- event magnitude: `0.083389841296380`;
- global eta minimum: `0.774643000900072`.

v19.40-v19.41 recompute and promote the complete child with:

- rank 14;
- trace / constraints / momentum:
  `1e-15 / 1.84e-13 / 2.634e-12`;
- two-scale flux envelope: `8.278527801e-6`;
- child eta minimum: `1.00000006206233`;
- persistence constraint maximum: `6.3483e-11`;
- persistence eta minimum: `1.00000001502294`;
- nonzero relative evolution: retained.

The microscopic v19.35 line fraction is therefore **RECLASSIFIED** as an
isolated local line result, not a demonstrated infrastructure or physical
blocker. No shake diagnostic, new continuation method, equation, selector, or
gate change is activated.

The exact residual remains nonzero. `N3_EXACT_KKT_CLOSURE` and
`FULL_BHSM_COMPLETE` remain false. GitHub publication, the long regression,
and USB archival remain deferred.
