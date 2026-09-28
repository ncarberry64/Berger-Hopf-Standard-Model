# Current reset to existing C2 prefix: first overlap refinement

This implements the immediate overlap target in the continuation from
`964b6a67`. The existing force equation consumes the same-base C2 response
in the joint heat-minus-zeta contraction. The goal is to connect to a
certified prefix domain and reuse it; no new completion gate or physical
endpoint is introduced.

## Full-state binding and saved connection guess

The current reset candidate is
`gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz`.
The target is the evaluated 99-dimensional field domain in
`gate7_current_history_20260927/flow_box/arrays.npz`, which owns the existing
prefix coefficient transport. Coordinates are the existing weighted
98-state coordinates followed by the independent signed descriptor.

At the current reset candidate, all 99 coordinates are outside that
target domain. The first failed coordinate is action configuration
coordinate 0: its displacement is `2.3083460199e-6`, while the target
radius is approximately `2.71050545e-20`. The largest state displacement
is about `1.28054`, at action coordinate 54. Radius agreement alone
would therefore not establish this overlap. This says nothing about
whether a connecting trajectory exists.

The already-owned `arb_predictor/path.npz` supplies a nine-step
descriptor-parameterized connection guess from that prefix center to
the reset event. Its SHA256 is checked before use. It is reused in
reverse order as a predictor, not promoted into a flow certificate.
No new 1,222-cell integration, interval-action campaign, or full prefix
rebuild was performed.

The current starting descriptor is the **certified selected eigenvalue**,
`-6.254081396568035e-21`; it is not replaced by zero. The separate
`joint_trial_collar_20260928` packet evaluates an explicitly off-root
event-coordinate trial with `s_event=0` and a retained eigenvalue defect.
That trial packet does not meet this requested reset-to-prefix overlap
certificate and is not used as one. A positive operator history must
respect the existing event/proper-clock conditions in the coupled solve.

## First local chart attempts

`certify_n12_reset_prefix_collar_entry.py` evaluates only subdivisions
of the first reversed predictor segment. It calls the existing branch-24
normalized eigenline and bordered response owner on the proposed domain.
Strict first-exit inequalities would prove inclusion if the field box
and positive descriptor speed were enclosed. No sampled values replace
those inequalities.

| First-segment divisor | First failed local operand |
|---:|---|
| 1024 | Normalized selected-eigenline inclusion on the Cartesian state box |
| 1048576 | Same eigenline inclusion |
| 1099511627776 | The eigenline calculation succeeds, but the descriptor-speed enclosure contains zero |

These failures are local representation results. They neither exclude a
physical connection nor authorize rebuilding the entire prefix. In
particular, continuing with trillions of Cartesian subdivisions would
not be an appropriate response to this dependency loss.

## Correlated directional data now evaluated

The new producer `build_n12_collar_directional_jet.py` evaluates one
shared current direction, using the same branch, normalization, descriptor
and internal bordered solve. Let `V` be the augmented normalized arc
field and `kappa=V_s>0`. The fixed-descriptor direction and its derivative
are

```
U = V/kappa,                 U_s = 1,
D_s U = (D V[U] - U*D kappa[U])/kappa.
```

Only this one proof direction is generated. The resulting values are

```
kappa = 2.0774511610188984e-10,
D_s kappa = -0.35200362269966257,
||D_s U||_F <= 8.157005258984658e18.
```

The selected-line derivative along U encloses exactly one; the descriptor
component of `D_s U` encloses zero. The complete shared 124-variable first
response replays its normal equations. These are point jet enclosures,
not a uniform Taylor remainder or a certified first collar segment.

The declared q66 directions are the incoming reset tangent at fixed
outgoing C2 query data, as in the current formation stationarity owner.
This proof direction does not replace or discard them. A later moving
launch query requires the transported hit/normal response already in the
existing B/material obligations; it has not been supplied by this single
column. Likewise, active contacts have not been matched numerically by
the radius check and are not zeroed.

## Next consumed calculation

The first local portion needs a correlated fixed-s tube retaining the
common eigenline/hard-response/descriptor-normalization dependence, with
a uniform remainder. Its only purpose is to certify the transition map
into the prefix chart that supplies `M_C2` to the existing joint force.
The point directional jet is the smaller starting representation; it
cannot alone bound off-center solutions. No full history or generic
all-direction higher-order tensor is required by this step.

Until the overlap and consumed derivatives are enclosed, the old prefix
is not a same-base heat operand. No signed complete amplitude row or q66
has been inferred from the coarse fixed-channel heat bounds. Root,
H/B, material response and persistence remain active existing work.

`Gate7_closed=False`. `FULL_BHSM_COMPLETE=False`.
