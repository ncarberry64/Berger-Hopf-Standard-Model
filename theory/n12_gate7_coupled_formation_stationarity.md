# Current coupled formation stationarity

Continuation of `ac5a511b7090e5680a62b4586f33602ce6a31bf6`.
The saved node-13/reset connection is reused without integration or
geometric correction. New work evaluates the **derivative** of the terminal
reset and local material data at its saved two-sided candidate, and binds
the coupled stationarity equations and their correct first-jet assembly.

The stationary incoming history is **not yet solved**. The absent numerical
object is the reduced current incoming formation/contact action covector
and its normal/launch jets. The existing action law is recovered; this is
not a claim that a new environment or interface law is required.

## Current point results

Forward roles are `E1 = incoming parent = second stored half, branch 23`
and `C2 = outgoing child = first stored half, branch 24`.
The candidate coordinates are unchanged. All bounds below are pointwise
Arb enclosures, not a root or history-tube certificate.

| Residual group | Norm upper bound |
|---|---:|
| Four geometric/attachment matching rows | `6.394633e-17` |
| Incoming parent constraints and energy | `1.135374e-14` |
| Outgoing child constraints and energy | `1.776140e-14` |
| Two normalized momentum matching rows | `7.208311e-15` |
| Outgoing selected descriptor, historical proof units | `1.781928e-15` |
| Incoming selected descriptor, historical proof units | `8.861304e-15` |
| Complete 58-row terminal reset | `2.404239e-14` |
| Complete action stationarity | **Not evaluated** |
| Complete dynamic-flux balance | **Not evaluated** |

The small difference from the earlier `2.45e-14` matching diagnostic is
an outward reevaluation and separation of the 58 rows, not a new Newton
solve. The physical signed descriptors still have the frozen small nonzero
candidate residuals. Normalized eigenline inclusion, branch indices and
canonical-lift KKT replays are included in the point packet.

| Current derivative | Row rank | Nullity | Row-scaled condition diagnostic | Right-inverse defect |
|---|---:|---:|---:|---:|
| Incoming-sensitive `32x98` | 32 | 66 | `5433.062` | `1.930e-75` |
| Complete terminal reset `58x196` | 58 | 138 | `8389.849` | `1.154e-98` |

The incoming kernel projector is saved with an annihilator replay bound
`5.420e-75`; a numerical orthonormal `98x66` basis is saved separately.
This is new current-point rank evidence. It does not assign those null
directions to the full stationary problem or classify them as gauge.
No physical time generator or quotient is inferred merely from a count.

An independent high-precision residual secant check on an incoming
configuration direction has relative discrepancies `4.716e-8` and
`1.179e-8` when the step is halved, showing the expected quadratic behavior.
On a reset-kernel direction, absolute discrepancies are `2.329e-11` and
`1.236e-11`. The comparison uses the actual rounded sample displacement.
These are numerical cross-checks, not new certificate tolerances.

## Separate local reactions and orientation

The existing canonical lift, from the complete local action, gives:

| Quantity | Incoming E1 | Outgoing C2 |
|---|---|---|
| Momentum | `(-0.4789486698104311, -0.1929549428298812)` | `(-0.4789486698104239, -0.1929549428298737)` |
| Configuration force | `(-38.48676804494, -1.098728310259)` | `(-1481.477999020, -1043.191451647)` |
| Radial conormal | `(-64.81371582614, -17.58002585086)` | `(-1343.168415171, -947.2970167407)` |

In the forward complete-child convention the local momentum equation is
`P_C2-P_E1=0`. Thus the signed parent and child momentum contributions
are `-P_E1` and `+P_C2`; their unnormalized sum has norm at most
`1.030116e-14`. The reset producer uses the negative of this equation,
with its unchanged normalization. The zero set is the same.

The corresponding complete-child flux equation is

```
G_C2 + DP_C2[X_C2] - F_C2 + G_E1 = 0.
```

`G_C2+G_E1-F_C2` is stored as a **partial term**, never as the full flux
residual. At the reset the supplied signed descriptor is zero, so the
ordinary inverse Euler-Dirac time field cannot be obtained by dividing
the regularized field by that descriptor. The finite regularized arc
derivative of momentum is saved, but it is not substituted for `DP[X]`.
The material boundary limit must be composed with the solved history and
its owned clock; no extra vanishing-pole equation is imposed here.

These local values are not labeled `Lambda_parent` and `Lambda_child`
of the complete reduced joint-history action. Their complete values remain
uncomputed. No external `W_E` or seven new environment inputs are added.

## Smallest terminal unknowns and coupled equations

Treat the 73 current launch/history directions as parameters `p`, not
independent reactions. For a prescribed outgoing reset state, the incoming
terminal state has 98 coordinates and 32 independent conditions:
four configuration/attachment, 25 constraint/energy, two momentum and one
incoming descriptor equation. This leaves 66 incoming terminal directions.

This is only the terminal-state count. Formation amplitude/duration,
coefficient histories, transported response fields and contact variables
belong to the internal history solve. Their elimination cannot be inferred
from reset rank. Momentum and flux are derived outputs or internal reactions,
not independent additions to the 73 physical inputs.

Let `R(p,y)=0` be those 32 terminal equations, retain the other 26 outgoing
rows as compatibility checks, and let `F_hist(p,y,n)=0` contain the owned
incoming dynamics, operator, response, contact and endpoint equations.
After a legitimate internal reduction define `Gamma_red(p,y)` by composing
the **same** complete action with the solved history. The constrained system is

```
F_stationary = [Gamma_red,y + R_y^T mu; R] = 0.
```

Equivalently its tangent equation is `Z^T Gamma_red,y=0`, with
`range Z = ker R_y`. The normal multipliers have dimension 32. The
terminal bordered form therefore has 130 variables **conditional on** the
history reduction; 130 is not a claimed dimension for the unsolved full
history. A legitimate remaining physical/gauge/time kernel must receive
an action-owned parameterization or quotient, not a pseudoinverse selector.

With `L=Gamma_red+mu^T R`, the exact first-jet equation is

```
[ L_yy  R_y^T ] [ y_p  ] = -[ L_yp ]
[ R_y     0   ] [ mu_p ]    [ R_p  ].
```

In particular `L_yy=Gamma_yy+sum mu_a R_a,yy` and
`L_yp=Gamma_yp+sum mu_a R_a,yp`. These moving-normal terms are essential.
The new `formation_stationarity_kkt.py` implements them, preserves all
parameter columns, and allows an explicitly owned quotient/parameter border.
Tests check a curved constraint against an exact stationary branch, invariance
under adding a constraint-normal action term, moving-parameter curvature,
missing-input rejection, and a legitimately parameterized null direction.

The prior endpoint-only `incoming_reset_jet` helper is a special case.
Direct history/clock forcing in `Gamma_yp` cannot be replaced by dependence
on the outgoing endpoint alone. No numerical 73D formation jet is emitted
before the stationary base and its normal inverse are established.

## Exact missing numerical object

The current finite-N law remains

```
Gamma_heat = -1/2 STr E1(ell^2 P),
D Gamma_heat[dP] = 1/2 STr(exp(-ell^2 P) P^-1 dP),
Gamma_replacement = Gamma_heat - Gamma_SM_zeta.
```

The existing source owns the finite-endpoint/reference law, contact terms
and signed adjoint route. The current spectral and C2 packets do not
instantiate the incoming formation operator and its material/normal
pullback. The 66 seed-invisible directions require the current upstream
action; a downstream C2 covector annihilates them by the recovered reset
projection identity. Zero external source does not make that upstream
force zero. An instantaneous local Lagrangian gradient is also not the
on-shell history-action covector.

The precise absent numerical input is

`CURRENT_CENTER_REDUCED_INCOMING_FORMATION_CONTACT_ACTION_COVECTOR_AND_NORMAL_LAUNCH_JETS`:

- `Gamma_red,y`, or its 66 current reset-tangent contractions;
- its constrained normal Hessian;
- the total mixed forcing in the 73 current parameters;
- the current internal history solve/base and material clock that own them.

The underlying law exists. This checkpoint does not assert absent physics,
nor does it assert that the full stationary system is underdetermined:
its force and Jacobian have not yet been evaluated. All 66 saved reset
directions are therefore marked **unresolved upstream reset tangent**,
not automatically physical moduli, gauge or time translation.

The next computation is to instantiate the incoming coefficient/duration
family and signed heat-minus-zeta/contact adjoint **inside the coupled
stationary solve**, using the saved two-sided candidate as its guess.
Then solve the normal intersection and differentiate the bordered system.
Do not substitute a local seven-row balance for those action contractions.

Packet: `artifacts/flagship_integration/gate7_current_formation_stationarity_20260927/`.
It contains source-line provenance, signed local parts, current derivatives,
kernel data, independent secants and repeat records. No Stage B, geometric
connection, old history campaign or C2 prefix was rebuilt. No generic
second operator jet or new boundary condition was introduced.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
