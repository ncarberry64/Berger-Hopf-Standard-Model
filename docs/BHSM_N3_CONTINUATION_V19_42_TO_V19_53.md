# BHSM v19.42-v19.53 N=3 continuation

This local batch starts from the validated v19.41 state with exact 376-row
norm `0.791308733253912`. The square KKT equations, explicit event
multiplier, event definition, eta domain, 14-row/26-variable complete-child
map, two-scale flux certification, and positive-duration persistence gate are
unchanged.

## v19.42-v19.45

v19.42 validates the `3e-7 / 1e-7` direct-response pair. v19.43 invalidates
the bounded-GMRES interpretation while independent exact merit selects
positive `alpha=0.0078125`:

- exact norm: `0.791287639528749`;
- reduction: `0.000021093725163`;
- event magnitude: `0.083388323241080`;
- global eta minimum: `0.774641468898163`.

v19.44-v19.45 reconstruct and promote a rank-14 complete moving child with
two-scale flux `8.632529304e-6`, persistence constraint maximum
`6.3616e-11`, and positive eta.

## v19.46-v19.49

v19.46 again validates the `3e-7 / 1e-7` response pair. The invalidated
v19.47 solver interpretation is not used as physics; the independent exact
nonlinear scan selects negative `alpha=-0.03125`:

- exact norm: `0.790602144149231`;
- reduction: `0.000685495379518`;
- event magnitude: `0.083310274137276`;
- global eta minimum: `0.774661240645980`.

v19.48-v19.49 pass the unchanged complete-child gate at rank 14 with flux
`4.149450071e-6`, persistence constraint maximum `6.3476e-11`, positive eta,
and retained nonzero relative evolution.

## v19.50-v19.53

v19.50 validates the `3e-7 / 1e-7` response pair. v19.51 retains an
invalidated solver interpretation, while exact nonlinear merit selects
positive `alpha=0.015625`:

- exact norm: `0.789572774913855`;
- reduction: `0.001029369235377`;
- event magnitude: `0.083243917329097`;
- global eta minimum: `0.774665507148863`.

v19.52-v19.53 recompute and promote a complete moving child with:

- rank 14;
- trace / constraints / momentum:
  `2.2951e-11 / 3.93e-13 / 1.339614e-9`;
- two-scale flux envelope: `3.312690511e-6`;
- child eta minimum: `1.00000092652355`;
- persistence constraint maximum: `6.3733e-11`;
- persistence eta minimum: `1.00000056278308`;
- nonzero relative evolution: retained.

The three accepted steps reduce exact merit by `0.001735958340057` in total.
No equation, selector, componentwise filter, previous-iterate-path condition,
or child acceptance restriction was introduced. The exact residual is still
nonzero, so `N3_EXACT_KKT_CLOSURE` and `FULL_BHSM_COMPLETE` remain false.
GitHub publication, the long regression, and USB archival remain deferred.
