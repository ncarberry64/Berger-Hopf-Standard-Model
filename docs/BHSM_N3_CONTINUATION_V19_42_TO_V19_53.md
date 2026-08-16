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

## v19.54-v19.62 compact continuation/ownership ledger

- v19.57 accepted: `||F376||=0.788966669806045`, flux
  `1.6446767051e-5`, eta/persistence/motion valid.
- v19.61 accepted: `||F376||=0.788717933323162`, flux
  `1.3575146128e-5`, eta/persistence/motion valid.
- v19.62 exact-F376 ownership audit: **OUTCOME A —
  DISTRIBUTED_DESCENT_CONTINUES**.

Latest exact block ownership:

| Block | L2 norm | Squared fraction | Recent slope/accepted step | Trend |
|---|---:|---:|---:|---|
| scale | 0.311754207109 | 0.156236 | +0.00317161 | growing |
| u | 0.003788056253 | 0.000023 | +0.00000188 | growing |
| w | 0.455733552495 | 0.333871 | -0.00173207 | falling |
| v | 0.227990941407 | 0.083559 | -0.00060070 | falling |
| lapse | 0.000012674527 | <0.000001 | -0.00000002 | falling |
| shift | 0.073123661670 | 0.008596 | -0.00023659 | falling |
| period | 0.502918891951 | 0.406586 | -0.00109375 | falling |
| event | 0.083207698891 | 0.011130 | -0.00004537 | falling |

Stationarity residual is split between interior (`47.89%`) and event-near
(`51.96%`), below the diagnostic `70%` localization threshold; reset-near is
`0.15%`. The total recent slope is `-0.000677488675` per accepted step; the
linear zero estimate is `1164.18` accepted steps and is explicitly naive and
nonphysical. Recent response diagnostics do not establish entry into a local
root basin. No first action-owned blocker is identified, so unchanged N=3
continuation resumes. `FULL_BHSM_COMPLETE` remains false.

## v19.63-v19.68 compact continuation ledger

v19.64 found a primary exact-merit candidate at `0.788121714849599`, but
v19.66 rejected it solely because independently recomputed two-scale flux was
`2.6357431541e-5 > 2e-5`. The unchanged scan's next-lowest candidate,
negative `alpha=-0.00390625`, was reconstructed afresh and promoted at v19.68:

- exact norm: `0.788591183052825`;
- reduction from accepted v19.61: `0.000126750270337`;
- rank / flux: `14 / 1.2296338804e-5`;
- eta, positive-duration persistence, and nonzero evolution: valid.

The rejected primary is not an accepted frontier. `FULL_BHSM_COMPLETE` remains
false; unchanged continuation proceeds from v19.68.

## v19.69-v19.76 compact continuation ledger

Two unchanged cycles pass the full physical gate:

| Accepted state | Exact norm | Reduction | Flux envelope |
|---|---:|---:|---:|
| v19.72 | 0.787400095824 | 0.001191087229 | 1.0854703348e-5 |
| v19.76 | 0.783424601550 | 0.003975494274 | 1.0243076159e-5 |

Both states retain rank-14 complete children, positive eta, positive-duration
persistence, and nonzero relative evolution. Solver interpretations remain
invalidated and unused. `FULL_BHSM_COMPLETE` remains false; continuation
proceeds from v19.76.

## v19.77-v19.82 compact continuation ledger

v19.77 found no pair satisfying the existing direct-response stability gate.
Finer measurement identified a noise floor: `3e-8 / 1e-8` had full-response
change `0.003489198144159` but event-row change `3.36162116662e-4`, above the
`2e-4` numerical audit threshold; smaller steps worsened. v19.78 therefore
used that derivative only as an explicitly invalidated bounded proposal
generator. Independent exact merit remained authoritative.

The primary state (`0.781619005072963`) was rejected at v19.80 for flux
`3.2901650332e-5`. The next-lowest state passed unchanged gates at v19.82:

- exact norm / reduction: `0.781663574515915 / 0.001761027033807`;
- rank / flux: `14 / 1.3073533916e-5`;
- eta, persistence, and nonzero evolution: valid.

No physical equation, threshold, or acceptance rule changed.
`FULL_BHSM_COMPLETE` remains false; continuation proceeds from v19.82.

## v19.83-v19.86 compact continuation ledger

v19.83 recovered the existing response-stability gate at `3e-8 / 1e-8`:
maximum relative response change `0.003786023703974` and event-row change
`1.4482743708e-4`. v19.84 retained the invalidated solver interpretation
but used the validated response only as a bounded proposal generator; independent
exact merit selected positive `alpha=0.0009765625`.

The freshly reconstructed v19.86 state passes all unchanged physical gates:

- exact norm / reduction: `0.777227123413482 / 0.004436451102433`;
- rank / flux: `14 / 7.873542925e-6`;
- trace / constraints / momentum:
  `1.6137e-11 / 3.39e-12 / 3.61245e-9`;
- global / child / persistence eta: positive;
- positive-duration persistence and nonzero relative evolution: retained.

No physical equation or acceptance rule changed. `FULL_BHSM_COMPLETE` remains
false; continuation proceeds from v19.86.

## v19.87-v19.90 compact continuation ledger

v19.87 validates the existing response gate at `1e-7 / 3e-8`. The v19.88
solver interpretation remains invalidated; independent exact merit selects
negative `alpha=-0.0009765625`. The freshly reconstructed v19.90 state passes
the unchanged physical gate:

- exact norm / reduction: `0.777122666596459 / 0.000104456817023`;
- rank / flux: `14 / 7.32986481e-6`;
- eta, positive-duration persistence, and nonzero evolution: valid.

`FULL_BHSM_COMPLETE` remains false; continuation proceeds from v19.90.

## v19.91-v19.94 compact continuation ledger

The existing response gate validates at `1e-7 / 3e-8`; the solver
interpretation remains invalidated. Independent exact merit selects positive
`alpha=0.0078125`, and the fresh child passes every unchanged gate:

- exact norm / reduction: `0.774048801461998 / 0.003073865134462`;
- rank / flux: `14 / 5.997068438e-6`;
- eta, positive-duration persistence, and nonzero evolution: valid.

`FULL_BHSM_COMPLETE` remains false; continuation proceeds from v19.94.

## v19.95-v19.98 compact continuation ledger

v19.95 again reaches the direct-response numerical noise floor and validates
no stable pair. As at v19.78, v19.96 preserves the invalidated source status
and uses a bounded derivative only to generate proposals; independent exact
merit remains authoritative. Positive `alpha=0.00048828125` passes the fresh
unchanged child gate at v19.98:

- exact norm / reduction: `0.770113042159652 / 0.003935759302345`;
- rank / flux: `14 / 1.4745217154e-5`;
- eta, positive-duration persistence, and nonzero evolution: valid.

The response noise floor is numerical and is not a physical blocker.
`FULL_BHSM_COMPLETE` remains false; continuation proceeds from v19.98.

## v19.99-v20.02 compact continuation ledger

The response gate recovers at `3e-8 / 1e-8`; the solver interpretation remains
invalidated. Exact merit selects positive `alpha=0.00048828125`, and v20.02
passes the unchanged child gate:

- exact norm / reduction: `0.769441416391865 / 0.000671625767787`;
- rank / flux: `14 / 5.93116292e-6`;
- eta, positive-duration persistence, and nonzero evolution: valid.

`FULL_BHSM_COMPLETE` remains false; continuation proceeds from v20.02.
