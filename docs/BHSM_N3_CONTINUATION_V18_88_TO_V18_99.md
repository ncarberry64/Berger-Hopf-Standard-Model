# BHSM v18.88-v18.99 N=3 continuation

This local checkpoint continues from the independently promoted v18.87 state.
The square 376-variable KKT system, explicit event multiplier, exact nonlinear
residual, and 14-row-on-26-variable complete-child map are unchanged. No
componentwise acceptance condition or previous-iterate path restriction is
used.

## Exact-response measurements

v18.88, v18.92, and v18.96 independently remeasure the central-difference
response at each accepted source. All three select the stable
`3e-7 / 1e-7` pair. Their maximum relative changes are respectively
`0.004276591285329`, `0.003569065722945`, and `0.003470002789899`.

## Independently evaluated merit states

The bounded GMRES objects in v18.89, v18.93, and v18.97 are retained only as
local geometric probes. Every solver interpretation is invalidated
(`info=1`; exact response mismatches remain large), so none is asserted to
be a Newton solve. Bidirectional exact nonlinear evaluation nevertheless
finds the following admissible-eta merit reductions:

| Probe | Orientation / alpha | Exact norm | Reduction |
| --- | ---: | ---: | ---: |
| v18.89 | positive / `0.03125` | `0.801699023846746` | `0.002551787243600` |
| v18.93 | negative / `-0.00390625` | `0.801684037952532` | `0.000014985894213` |
| v18.97 | positive / `0.03125` | `0.801038620295453` | `0.000645417657079` |

Individual residual blocks are not required to decrease monotonically.
Promotion is decided only by independently recomputed total merit, eta
admissibility, and the complete-child gate.

## Complete-child reconstruction and promotion

v18.90-v18.91, v18.94-v18.95, and v18.98-v18.99 each recompute a fresh child
from all 26 child variables. Every local chart has rank 14, and every promoted
state passes trace, seven-constraint, attachment-momentum, eta, two-scale flux,
and positive-duration persistence checks:

| Promotion | Accepted norm | Flux envelope | Persistence constraint max | Persistence eta min |
| --- | ---: | ---: | ---: | ---: |
| v18.91 | `0.801699023846746` | `1.2428994899e-5` | `6.5801e-11` | `0.999982756675074` |
| v18.95 | `0.801684037952532` | `4.6201525300e-6` | `6.5409e-11` | `0.999981715234097` |
| v18.99 | `0.801038620295453` | `1.2776562404e-5` | `6.4407e-11` | `0.999982803097521` |

Nonzero relative motion and time dependence persist in every child. The exact
376-row residual remains nonzero, so `N3_EXACT_KKT_CLOSURE` and
`FULL_BHSM_COMPLETE` remain false.

The active dependency remains physically admissible exact descent to
`F376=0`. GitHub publication, the long regression, and USB archival are
deferred until a materially larger scientific milestone.
