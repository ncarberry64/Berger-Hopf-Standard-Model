# Current formation operator assembly: evaluated endpoint operands

Continuation of `b994615e` on `theory/gate7-66d-reduced-adjoint-integration`.
The package is **incomplete**. This checkpoint performs new current-point
numerical action evaluations; it does not solve formation stationarity.

## Current base and computation

The exact saved binary64 incoming state is
`gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz`,
`joint_state_raw[98:196]`: incoming E1, branch 23. The earlier parent-sector
driver used a different historical point and arm. Only its sector laws and
algorithms are reused. The state weights and frozen Q66 are consumed unchanged.

The ten retained local contributions are reevaluated using Arb512 and the
original spatial quadrature/constants. The saved derivatives are raw local
gradients and local curvature contractions on Q66, **not** the reduced
history-action covector or constrained physical formation Hessian.

| Current local action density contribution | Numerical value |
|---|---:|
| Spatial gravity | 3.1181191129483485 |
| Intrinsic curvature | 20.918888751740663 |
| Cosmological | -14.290614875691 |
| Eta quadratic | -2.5368995167140818 |
| Eta quartic | -3.0058867167911933 |
| ADM kinetic | 0.023952669887569472 |
| Fixed Hopf inertia | -4.490744863107668e-8 |
| Attached scalar vacuum | -0.018737876310532264 |
| Attached vector vacuum | -1.2366998364951294 |
| Attached Weyl vacuum | -0.9556316918371455 |

Their signed sum is checked against an independent invocation of the original
unsplit action at the same state. Outward replay discrepancies are:

- value: `4.900389e-151`;
- raw gradient: `2.565282e-149`;
- local Q66 curvature: `9.285619e-66`.

All replay differences enclose zero. The curvature bound includes the
existing interval uncertainty in Q66. No acceptance tolerance is relaxed.
These are arithmetic checks, not physical root residuals.

## Minimal history dependencies

At this current point, `log R4=-0.005096247328062276` and
`d(log R4)/d tau=0.10661458494851822`. The current endpoint contractions give:

| Endpoint quantity | Frobenius norm upper bound of derivative along Q66 |
|---|---:|
| `log R4` | `2.274547e-70` |
| `log N` | `0.30510099397374957` |
| `d(log R4)/d tau` | `0.17317741469247414` |

The fixed-child reset constraints fix the attached endpoint radius to first
order. They do not freeze lapse or the radius rate. In particular, endpoint
radius equality cannot justify replacing all incoming histories by a common
constant coefficient operator. No Q66 column is discarded.

For compact fixed-channel spectral transfer, the owned reduction consumes
only `x(tau)=log R4(tau)` and proper duration, with their required derivatives.
This compression does not apply to the classical attached action, which
still depends on the spatial fields and fixed inertia along the history.
The numerical dependency ledger distinguishes `SURVIVES`, `CANCELS`,
`SLAVED`, and `REDUNDANT`, with a scope for every statement. An internal
variable marked `SLAVED` is not claimed to have been numerically solved.

## Operator-domain ownership

The current external-source role is
[the retained source-role supersession](n12_gate7_external_birth_source_role_supersession.md).
The birth trace is Dirichlet generating data; it is set to zero after
differentiation. The generally nonzero incoming response is `M_f=M11`.
No pre-E0 arm or new `B_birth` input is required. The older dynamic-birth
graph interpretation must not be reintroduced during assembly.

The incoming history must be generated in its current amplitude/duration
family. The old positive-amplitude proof bounds do not supply that current
numerical family. A finite proof horizon is not a selected physical formation
duration. The saved C2 prefix remains a prefix, not a new physical endpoint
or an evaluated maximal heat response.

## Sector completion state

| Sector / response | Accounting | Value | Covector / Hessian / launch forcing |
|---|---|---|---|
| Classical geometry, eta and Hopf | ACTIVE | Current endpoint density evaluated; history integral pending | Local derivatives evaluated; integrated/reduced derivatives pending |
| Attached Casimir species | ALREADY_INCLUDED | Current endpoint density evaluated | Same local derivative scope; subtract the retained zeta only in complete replacement accounting |
| Graded heat-minus-zeta | ACTIVE | Current joint-history operator pending | Signed current operator and coefficient/duration jets pending |
| Seam / attachment | ACTIVE | Current reset geometry and source-bound local data retained | Moving and mixed history incidence pending |
| Gauge and scalar/topographic contacts | ACTIVE | Current joint spectral form pending | Must enter the same operator and common reduction |
| Pair / mixed contact vertices | ALREADY_INCLUDED | No independent extra action added | Both heat pair and genuine mixed operator contractions retained |
| Momentum reaction | ALREADY_INCLUDED | Existing current local reaction consumed | Not an additional scalar-action summand |
| Dynamic flux reaction | ALREADY_INCLUDED | Separate current conormal, force, and regularized momentum rate consumed | Physical `DP[X]` and complete same-history flux remain pending |
| Reset incidence | ALREADY_INCLUDED | Existing current reset packet consumed | No matching rebuild; current launch/history incidence still needed |
| Descriptor and internal response | INTERNAL_ELIMINATED | Current complete internal base pending | Requires the common internal residual and objective adjoint before physical projection |

## Exact remaining numerical work

`FORMATION_OP_CURRENT.complete` remains false. No numerical `q66`, `H66`,
or `B66x73` is emitted. The remaining construction is the current incoming
coefficient/duration family, its joint incoming/C2 operator with contacts,
and the common internal residual plus normal/launch derivatives. The
existing sector split cannot supply those by summing local endpoint jets.
No stationary solve or first-jet solve has been attempted.

Artifacts are under
`artifacts/flagship_integration/formation_op_current_20260928/`.
`dependencies.json` records each missing operand, producer, expected base,
recentring scope, and the four pre-existing retention paths/hashes. Retention
cleanup is not part of this computation. The interrupted `dependency_run1`
array is preserved; `dependency_run1_complete` contains its complete replay.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
