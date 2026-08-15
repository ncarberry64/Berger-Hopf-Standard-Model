# BHSM v18.70-v18.73 fifth bidirectional N=3 continuation

## Source

The source is the independently promoted v18.68 state with unchanged exact
376-row norm `0.811248056430707` and positive global eta.

## Response and probe

v18.70 remeasures the direct exact-residual response. The finest common stable
pair is `1e-6 / 3e-7`, with maximum relative response change
`0.001759445476962` and maximum event-row change `9.202930085e-6`. Finer pairs
leave the measured plateau and are not used.

v18.71 scans both orientations of one bounded action-owned geometric probe.
The GMRES run does not solve the Newton equation (`info=1`, 40 iterations,
direction-scale mismatch `0.543343993749443`) and its Newton interpretation is
`INVALIDATED`. Independently evaluated exact nonlinear merit selects the
positive `alpha=0.25` state:

- exact norm: `0.807144219141348`;
- reduction: `0.004103837289358`;
- global eta: `0.774053610471969`.

## Complete-child gate and promotion

v18.72 reconstructs all 26 child variables on a fresh rank-14 chart. The
initial Jacobian-norm solver scaling stopped just outside the existing
constraint tolerance, so the numerical solve was conditioned by the already
retained row tolerances. This changes no equation or zero set. The completed
child has trace `0`, constraint maximum `2.8e-14`, momentum norm `1.49e-11`,
local dynamic-flux norm `1.106066377e-6`, positive child eta, and nonzero
velocity norm `9.30336922281793`.

v18.73 independently recomputes and passes the full promotion gate:

- exact norm: `0.807144219141348`;
- event magnitude: `0.083752222964491`;
- global eta: `0.774053610471969`;
- child rank: `14`;
- trace / constraints / momentum: `1e-15 / 2.9e-13 / 1.9017e-11`;
- independent two-scale flux envelope: `5.637086789e-6`;
- persistence duration: `1e-4`;
- persistence constraint maximum: `6.5379e-11`;
- persistence eta minimum: `0.999974619528007`;
- nonzero relative evolution: retained.

`N3_EXACT_KKT_CLOSURE` remains open because the exact 376-row residual is not
zero. `FULL_BHSM_COMPLETE = FALSE`.
