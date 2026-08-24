# N12 forward Euler--Dirac variation bounds

Status: `LOCAL_SECOND_STATE_JACOBI_AND_LOG_RADIUS_TUBE_DERIVED`.

The retained acceleration and multiplier rate are defined implicitly by one
gauge-fixed Euler--Dirac solve

\[
 D(Y)s(Y)=b(Y),\qquad D=L_{zz},\qquad b=E L_q-L_{zq}v,
\]

where `z=(v,m)`. For two action directions, differentiating this equation
without forming an inverse derivative gives

\[
 s_h=D^{-1}(b_h-D_hs),
\]

\[
 s_{hk}=D^{-1}(b_{hk}-D_{hk}s-D_hs_k-D_ks_h).
\]

Every jet reuses the same action-owned Dirac factorization. `D_h` is owned by
the action third variation and `D_hk` by the fourth variation. Since
`b=E L_q-L_zq v`, for unit straight directions

\[
 \|b_{hk}\|\leq 3\|D^3L\|+\|D^4L\|\,\|v\|.
\]

Applying the already-certified child action-ball majorants yields a finite
local bound `||D2V|| <= 5.107983341888882e38`. On the guaranteed local
duration `6.301881201051695e-30`, unit first Jacobi data obey
`||J_h|| <= 1.000247815627679`, while zero-initial mixed data obey
`||J_hk|| <= 3220187076.317866`. Pullback through the exact radius functional
then gives finite first and mixed `log R4` bounds. These constants are large
but rigorous consequences of the existing conservative action ball; they are
not fitted thresholds or acceptance gates.

This closes the second state-Jacobi algebra and a certified local tube. It
does not cover the maximal forward component. The next task is to make the
continuum theorem's `C(B,delta)` bounds explicit for `DV,D2V`, propagate the
cocycles across bounded-margin recenterings, and then enclose the fixed-channel
Weyl and terminal/Friedrichs graph jets. Terminal return remains unnecessary,
Gate 7 remains active, Gate 8 remains locked, and chord 3 is unauthorized.
