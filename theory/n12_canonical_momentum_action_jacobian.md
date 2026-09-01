# N12 canonical-momentum action Jacobian

Status: `EXACT_ACTION_COORDINATE_CANONICAL_MOMENTUM_JACOBIAN_DERIVED`.

The retained two-component boundary momentum is

`p=L^T g_v`,

where `g_v=D_v L_action` and the already retained Hessian-minimal lift is

`L=X Y`,  `X=A^-1 K^T`,  `Y=(K X)^-1 T`.

Here `A=D_vv^2 L_action`, `K=(B,D_mv^2 L_action)`, `B` is the exact
attachment-chart Jacobian, and `T` selects its two boundary rows.  For any
action-coordinate direction `h`, differentiation of the two solves gives

`D X[h]=A^-1(D K[h]^T-D A[h] X)`,

`D Y[h]=-(K X)^-1(D K[h] X+K D X[h])Y`,

`D L[h]=D X[h]Y+X D Y[h]`,

and therefore

`D p[h]=D L[h]^T g_v+L^T D g_v[h]`.

All ingredients are already action-owned: `D A` and `D(D_mv^2 L)` are
blocks of the certified third variation, `Dg_v` is a Hessian block, and
`DB` is the analytic curvature of the retained attachment chart.  The
implementation uses linear solves throughout; it forms no matrix inverse and
introduces no differencing step.

At the authoritative N12 event and child states, representative coordinate,
velocity, and multiplier columns agree with independent complex-step
differentiation of the unchanged canonical-pair map.  This removes 196
complex action evaluations from every full reset-Jacobian rebuild and enables
intrinsic reset-manifold recentering without changing the physical quotient.

No equation, action term, reset condition, selector, endpoint, scale, gate,
chord, or frozen prediction is changed.  Gate 7 remains active.
