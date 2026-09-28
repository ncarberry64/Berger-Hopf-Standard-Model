# First current-reset collar flow segment

This continues the same-base collar calculation after `e40a83c3`. It
certifies the **first actual fixed-descriptor state-flow segment**, not
only an affine predictor. It does not yet reach the saved C2 prefix, and
it does not complete its derivative handoff or the joint heat force.
The existing completion scope is unchanged.

The authoritative local outputs are

```
artifacts/flagship_integration/reset_prefix_collar_20260928/
  flow55_curve_normal{1,2}/
  flow55_composed{1,2}/
  flow55_partial{1,2}/
  flow55_endpoint{1,2}/
```

Earlier `flow55_box`, `flow55_descriptor`, `flow55_numerator` and
`flow55_quadratic82{a,b}` packets retain the intermediate bounds and their
source dependencies. They are not alternative successful flow certificates.

## Same physical field and actual curve remainder

Let h0=2^-55, and retain the existing fixed-s direction U0 and its point
derivative U0'. The proposed weighted-state corridor is

```
y(theta) = y0 + h0 theta U0 + rho,
|rho_i| <= r_i = 16 h0^2 (|U0'_i|+1),
theta in [-1,1].
```

The point curvature selects proof radii only. It does not prove the
trajectory lies in them. The uniform normal inclusion and first-exit
inequalities below establish that fact on the final, shorter time interval.
These proof coordinates add no physical or environmental inputs.

The unchanged action field has numerator G and descriptor numerator
delta=b*c+s*R. Its fixed-descriptor state rate is U=G/delta; the common arc
normalization cancels in this quotient. The 124 normal equations are the
same eigenline, normalization, hard response and border equations used in
the preceding checkpoint. No scientific action producer, old prefix cell,
Stage-B derivative campaign or interval-13 proof was rerun.

## Compose before support

For any fixed covectors beta_delta and beta_G, on the actual normal graph
F(y,n)=0 one has the exact identities

```
delta = delta - beta_delta F,
G     = G     - beta_G F.
```

The covectors are midpoint proposals from the current normal adjoint.
Their exactness is not assumed: their anchor defects and the full residual
are retained. These identities preserve the equations and their signs.
The common parameter groups are theta, the 98-coordinate curve box, and
the 124-coordinate Euclidean normal correction ball. Signed action and
normalization terms are composed before taking support in these groups.

| Representation | First-exit result on the full h0 step |
|---|---:|
| Independent normal/output bounds on the curve box | maximum 7.43445e7 |
| Descriptor residual identity | maximum 3.91534e6 |
| Descriptor and required numerator residual identities | maximum 1260.8556 |
| Retain theta^2 alone, tested on worst coordinate 82 | coordinate bound 1138.0518 |
| Also retain the induced curve-to-normal first response | maximum 1.04597810 |

The quadratic pilot did not reduce the mixed normal/curve loss sufficiently.
The missing representation was the normal response to the curve remainder,
not an extra physical equation or a higher-order generic operator campaign.

## The induced normal response

The existing full curve-box normal certificate has Y<=0.511725 and
Z<=7.28895e-5 in its scaled Euclidean norm. Let D contain its normal radii,
R be its fixed Newton preconditioner, and D_rho map unit curve-box
parameters into raw state coordinates. The new first response solves

```
P T = -D^-1 R F_y D_rho,
P = D^-1 R F_n D.
```

The point source and solve are evaluated with the current action and
replay in Arb. This is one local remainder operator, not 98 newly generated
physical history columns. Its box-to-Euclidean bound is

```
sup_|u|inf<=1 ||T u||2 <= 0.000738432344140.
```

Consequently the new predictor

```
n_hat_new = n0 + h0 theta Dn + D T u
```

lies inside the old normal proof ball. Re-evaluating the **combined**
normal residual on this predictor, while reusing the old uniform Z, gives

```
||D^-1 (n_true-n_hat_new)||2 <= 0.000102634890956.
```

This follows from the mean-value identity between the new predictor and
the already-certified true root. Both lie in the same convex old normal
ball, so the intervening Jacobian is covered by the old Z. No independent
sum of internal response norms supplies this bound.

## Certified time restriction

The fully composed rate model on this unchanged corridor gives maximum
first-exit ratio 1.04597809998654 for the complete h0 interval. A component's
bound has the form h0(A+B/2), with A,B>=0: only the known theta=t/h0 term
gets the factor 1/2. Unknown material parameters remain in A.

For T=f*h0, 0<f<=1,

```
h0(f A + f^2 B/2) <= f h0(A+B/2).
```

Choose the exact dyadic fraction f=15/16. This yields

```
T = 2.6020852139652106e-17,
maximum first-exit ratio <= 0.980604468737381 < 1.
```

Together with the uniform normal graph and positive descriptor numerator,
this proves the actual state trajectory remains in the proposed corridor
for this first step. It changes no radius, physical tolerance, model term
or acceptance threshold. It is an ordinary local time restriction of a
proved field enclosure, not an inference from sampled trajectories.

## Shared endpoint, not a new independent box history

The rate model is integrated before support. Its constant and known theta
terms supply the endpoint center. The time averages of the curve-box and
normal-ball parameters remain in the same convex groups. The saved endpoint
therefore retains a 99x222 affine map plus the explicit remaining output
tail. These 222 symbols are proof remainders, not 222 physical coordinates.
No new environmental degrees of freedom are introduced.

All 98 first rate coefficients replay the frozen U0' jet. The shared
endpoint enclosure lies strictly inside the certified curve corridor.
This retains the dependencies needed for the next causal continuation
instead of discarding them into 98 independent endpoint intervals.

## What this does and does not establish

The frozen negative initial selected descriptor is preserved; the current
off-root reset candidate has not been turned into an exact event by
clamping it to zero. A positive proper-duration operator history has not
been certified by this state-flow step. All 99 endpoint coordinates still
fail containment in the old prefix domain. The needed first-variation
transition into that domain remains open.

The next calculation is adaptive continuation of this same correlated
curve/normal representation toward a full-state prefix overlap. The very
short first proof step is not a justification for millions of independent
Cartesian cells or rebuilding the 1,222-cell prefix. Preserve the shared
endpoint and refine the local chart/curve representation where its first
inclusion fails.

Only after the required overlap can the saved prefix enter the same-base
signed heat-minus-zeta contraction. The full constrained amplitude row,
q66, same-action root, H/B products and persistence remain the existing
open obligations. No physical budget debit or instability claim follows
from any of the failed intermediate bounds.

`Gate7_closed=False`. `FULL_BHSM_COMPLETE=False`.
