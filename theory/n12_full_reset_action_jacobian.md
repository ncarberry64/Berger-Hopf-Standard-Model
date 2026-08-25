# N12 full reset action Jacobian

## Scope

This certificate differentiates the unchanged N12 event-to-child reset
residual in the diagonal action coordinates used by the direct checkpoint.
It adds no action term, endpoint condition, selector, scale, gate, or chord.
Its purpose is numerical-coordinate rigor: replace the subtractive paired
finite-difference Jacobian by a reusable analytic Jacobian before attempting
intrinsic continuation on the finite encapsulation stratum.

## Row ledger

For one sector, let `W` be the retained action-coordinate weight and let
`g,H,T` be the raw action gradient, Hessian, and the already certified third
variation.  The 57 reset rows are

1. 24 multiplier Euler--Dirac constraints and one canonical-energy row at
   the event;
2. the transported simple ordered-event eigenvalue;
3. three linear traces and the nonlinear attachment trace;
4. the same 25 constraints at the child; and
5. the two components of the canonical-momentum mismatch.

The constraint derivative is obtained directly from `H`.  If `u` is the
selected normalized eigenvector of the raw reduced Hessian, its
action-coordinate representative is `u_A=Wu`, and

```text
D lambda[h] = T_A[u_A,u_A,h].
```

The boundary rows use the exact derivative of the retained attachment chart.
The momentum derivative uses

```text
L = A^-1 K^T (K A^-1 K^T)^-1 T_2,
p = L^T g_v,
Dp[h] = DL[h]^T g_v + L^T Dg_v[h],
```

with both linear solves differentiated analytically.  No dense matrix inverse
and no numerical differentiation is used.

## Fixed normalization

The boundary inverse square root, momentum square root, ordered-event scale,
and transported branch reference are not recomputed or fitted during this
derivation.  They are the existing action-owned N6-to-N12 reset-chart data.
Only the residual derivative changes with a recentered event/child state.

## Claim boundary

Full row rank at the accepted checkpoint proves that the local reset set is a
regular 139-dimensional stratum there.  It does not prove that this stratum
contains a finite terminal child, that intrinsic continuation remains regular
globally, or that Gate 7 closes.  Those remain the next existence problem.

