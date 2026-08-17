# BHSM v18.74-v18.83 N=3 continuation and flux-gated fallback

## Source and unchanged solve

The source is the independently promoted v18.73 state with exact 376-row norm
`0.807144219141348`. The physical problem remains the square 376-variable KKT
system with explicit event multiplier. The complete-child map remains 14 rows
on 26 child variables and adds no global equation. No componentwise
monotonicity or previous-iterate-path condition is imposed.

## v18.74-v18.77 accepted continuation

v18.74 remeasures the exact-residual response and validates the common
`1e-6 / 3e-7` plateau. v18.75 scans both orientations of a new action-owned
geometric probe. Its GMRES interpretation is invalidated (`info=1`, exact
linear residual `1.185723813381779`, response mismatch
`0.921161889826758`), but the independently evaluated negative
`alpha=-0.03125` line state lowers the exact norm to `0.806818034168188`.

v18.76 reconstructs a fresh rank-14 complete moving child. v18.77 then
independently passes exact merit, eta, two-scale flux, and positive-duration
persistence:

- merit reduction: `0.000326184973161`;
- event magnitude: `0.083668380330887`;
- global eta minimum: `0.774108263940826`;
- flux envelope: `1.3802293928e-5`;
- persistence duration: `1e-4`;
- nonzero relative evolution: retained.

## v18.78-v18.83 primary rejection and fallback promotion

v18.78 again validates the common `1e-6 / 3e-7` response plateau. v18.79
invalidates its GMRES interpretation (`info=1`, exact linear residual
`1.483886513089056`) while finding a positive `alpha=0.015625` exact-merit
state with norm `0.804728752733494`. Its fresh v18.80 child closes all 14 local
rows. v18.81 nevertheless rejects promotion because the independently
recomputed two-scale flux envelope is `2.3188127181e-5`, above the unchanged
`2e-5` gate. The gate is not relaxed.

The next-lowest already measured exact-merit state, positive
`alpha=0.0078125`, is then tested rather than inventing a new rule. v18.82
reconstructs its fresh rank-14 child. v18.83 independently passes the full
promotion gate:

- exact norm: `0.80554785212226`;
- reduction from v18.77: `0.001270182045928`;
- event magnitude: `0.083598507276914`;
- global eta minimum: `0.774215156076363`;
- trace / constraints / momentum: `2e-15 / 1.78e-13 / 3.4902e-11`;
- independent two-scale flux envelope: `1.1596040404e-5`;
- child eta minimum: `0.999990906516603`;
- persistence constraint maximum: `6.5553e-11`;
- persistence eta minimum: `0.999988182085241`;
- nonzero relative evolution: retained.

The lower-norm primary state remains rejected. The latest accepted state is
v18.83. The exact global residual is still nonzero, so `N3_EXACT_KKT_CLOSURE`
and `FULL_BHSM_COMPLETE` remain false.
