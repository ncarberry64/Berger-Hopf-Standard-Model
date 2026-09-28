# Balanced reset collar: usage-limit checkpoint

Work paused at the user's request on 28 September 2026. This continues
`981d5f8bd744e10849a9e34b9bccaa578931183f` on
`theory/gate7-66d-reduced-adjoint-integration`. The saved 1,222-cell prefix,
scientific action producers, physical tolerances and completion scope are
unchanged.

## CLOSED

The previous first actual fixed-s flow segment remains certified at
`T=(15/16)*2^-55`, with its shared endpoint in `flow55_endpoint1`.

A larger **normal graph**, including the induced curve-to-normal response,
is now certified on the proposed `h=2^-45` chart:

```
Y <= 0.879781375789494
Z <= 0.070517307072827
Y+Z < 0.950298682862322 < 1
```

The output packets are under
`artifacts/flagship_integration/reset_prefix_collar_20260928/`:

- `balanced45_proposal{1,2}`: corridor proposed from frozen first jets;
- `balanced45_normal{1,2}`: uniform normal graph and oriented-anchor binding.

The normal proof radius was rescaled by 32. This changes a numerical proof
neighborhood, not a physical tolerance or budget. The chart is parameterized
by the same one-dimensional forward parameter and a 98-dimensional box of
curve remainders, with a 124-dimensional Euclidean normal correction.
These are proof parameters, not new environmental or physical inputs.

## The retained calculation

Recover the signed point reduced-rate Jacobian from the frozen common
endpoint coefficients. If `J` is that Jacobian and `A=abs(J)` is its
entrywise outward majorant, propose

```
b_i = h^2 (abs(U0'_i)/2 + 1),
r   = (I - 4 h A)^-1 (4 b).
```

The positive radii give point ratios 1/4. That resolvent is only a proposal.
Its uniform validity comes from the subsequent action evaluation.

Rescale the already-owned normal response into these radii and use

```
y = y0 + h U0 theta + diag(r) u,
n_hat = n0 + h Dn theta + K u.
```

The raw-state implementation includes the frozen action weights. The
uniform Newton residual is evaluated after preconditioning. The normal
Jacobian is evaluated one repeated Hessian-column pair at a time. Each
pair's action and algebraic normal coefficients are combined with common
parameter identities before curve-box support. Constant and theta matrices
remain signed; curve-linear, normal-correction and nonlinear-action tails
are recorded separately. No dense 99-by-124-by-124 coefficient tensor is
stored.

The 124 normal equations, their signs, normalization and action are
unchanged. The included anchor and positive reference overlap bind the
graph to the frozen selected index-24 branch.

## OPEN

The `h=2^-45` chart has **not** passed a physical flow first-exit test.
The earlier shorter flow certificate is still the only actual trajectory
certificate. Prefix containment, derivative handoff, positive-duration
joint operator realization, signed heat contraction, complete amplitude
row, q66, root and persistence remain open. Both completion flags are false.

## NEWLY LOCALIZED

The larger correlated normal graph is available. The immediate next
calculation is its residual-composed descriptor/numerator first-exit test.
The prepared producer `scripts/certify_n12_balanced_collar_flow.py` has an
algebraically tested numerator adjoint, but its full scientific calculation
was deliberately **not run** before this usage-limit stop.

## INVALIDATED

No frozen scientific result is invalidated. The point-majorant success and
the new normal inclusion must not be reported as a larger certified flow
step or as prefix overlap.

## NEXT

Run only the prepared current-chart flow test:

```powershell
C:/Python314/python.exe scripts/certify_n12_balanced_collar_flow.py --normal artifacts/flagship_integration/reset_prefix_collar_20260928/balanced45_normal1 --out artifacts/flagship_integration/reset_prefix_collar_20260928/balanced45_flow1
```

Inspect descriptor positivity and the full-step first-exit ratios. The
producer can restrict time by an exact dyadic fraction without changing
the certified corridor. Compare the resulting actual step with the frozen
shorter one before making a progress claim. Reproduce any accepted outputs
byte-identically, retain the shared endpoint, and continue only the local
connection until full-state and required-derivative prefix containment.
Then consume the signed joint heat contraction for the same KKT amplitude
row and q66. Do not rerun the prefix or frozen scientific producers.

Validation details and output hashes are in `balanced_checkpoint_validation.json`
in the collar artifact directory. Older untracked experimental drafts are
preserved in place; they are not promoted by this checkpoint.
