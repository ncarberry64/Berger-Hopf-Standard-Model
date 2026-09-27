# Node-13 launch-chart binding and native seven-row composition

Continuation of `77a71242`, using Norman's correction that `T_seam_98x73`
was shorthand for the existing 72-family-plus-flow launch chart.

The original launch chart is now identified and reproduced. Its base point
does not coincide with the historical event point used for the native 7x98
derivative. A new first-order native composition has therefore been computed
at the certified fiber-consistent node-13 center. No historical event
derivative is reused across that displacement.

## Launch reconstruction and center comparison

The owner is `C:/Users/carbe/Downloads/bhsm_gate7_layerC_launch_to_child_binding.py`,
functions `reconstruct_family` and `main`, with the corrected scaling and
frozen arrays retained in `gate7_66d_checkpoint_20260926/binding/`.

```
T73 = endpoint_physical_tangent_action[13]
A0 = vstack(lstsq(T0, projected_C2_parameter_lift), zeros(1,72))
A13 = causal_maps_center[12] ... causal_maps_center[0] A0
qflow = lstsq(T73, exact_endpoint_augmented_rates[13,:98])
launch_state = column_stack(A13[:73,:], qflow)
T_launch_old = T73 launch_state
```

The reconstructed `launch_state` is byte-equal to the frozen binding array.
Neither `endpoint_constraint_tangent_action` nor a 66D child basis replaces
this map. The 73 columns are **72 inherited family labels plus one flow
phase**, not already a 66+7 partition.

In the positive weighted action coordinates, the comparisons are:

| Centers | Outward distance upper bound |
|---|---:|
| Historical native event point to corrected node 13 | `3.250423788608` |
| Frozen launch node 13 to corrected node 13 | `2.141481e-14` |
| Older physical-basis node 13 to corrected node 13 | `8.592739e-6` |

The event/current boxes are rigorously disjoint: at least one component has
absolute difference greater than 1.28. This is not a comparison against the
transfer allowance. There is no certificate enclosing both points as one
evaluation center. The current tiny root certificate is reused unchanged.

## First-order transport at the certified center

Let `D` be the frozen current 25x98 constraint derivative and `N` the existing
25 normal-coordinate columns of the certified center chart. With

```
P = I - N (D N)^-1 D,
T_new[:,:72] = P T_launch_old[:,:72],
T_new[:,72] = P X_current,
ds = Dlambda_event T_new,
```

this is the first derivative of the local implicit constraint chart in the
declared normal coordinates. The descriptor is slaved by the owned fiber row
in physical units. No new descriptor coordinate or environment input is
introduced. This is a local chart reparameterization; it is not a newly
certified transport of the historical 72-family derivatives over the entire
history or tube.

The chart has certified rank 73. A fixed midpoint left inverse `R0` gives
`||I-R0 T_new||_F <= 1.995016e-10 < 1`. A direct interval Gram-inverse replay
was unnecessarily pessimistic from repeated coefficient dependencies; the
fixed-left-inverse proof avoids those dependencies without changing the
chart or any tolerance.

`||D T_new||_F <= 8.258754e-12` is the outward coefficient replay enclosure.
The chart change from the historical matrix is at most `3.420558e-6`.
The current rate's normal correction is at most `1.384461e-11`; it is kept
explicit rather than asserted to be an exactly vanishing coordinate change.

## Native response evaluated at that same center

The first five native trace/momentum rows are reused from the existing
node-13 child-interface packet: the functions are the same `Tq` and `P(Y)`,
and its source hash identifies the identical certified state domain.
The event conormal derivative `D(Lq^T radial)` is newly evaluated there.
Its two summands, `DLq^T radial` and `Lq^T D radial`, are both included.
The full action controls the common lift; all ten signed action contributions
remain represented. Only ADM has direct canonical momentum in these retained
coordinates, while the other sectors still affect the common lift and force.

Results:

| Replay | Outward Frobenius upper bound |
|---|---:|
| Conormal direct minus adjoint derivative | `2.957733e-32` |
| Configuration KKT inverse defect | `1.202405e-33` |
| New lift minus existing node-13 lift | `8.735296e-41` |
| Sector-summed five-row composition | `4.505665e-12` |

The saved composition is

```
R_native_launch = J_native_current T_new + explicit_native_shape
shape(R_native_launch) = (7,73)
rows = (trace_1..3, momentum_1..2, event_conormal_1..2).
```

Its norm bound is `261736.501796` in these native parameter coordinates,
with no physical stability or budget interpretation. The fixed material
section is chi=pi/4. The retained native owner has only q,v,m arguments;
state geometry and the moving lift are already differentiated inside J.
Consequently its additional direct shape term is exactly zero. This does
not set a separate, unrepresented environment frame/normal/measure derivative
to zero or infer it from dimensions.

## Scope of the binding

The requested center check rules out calling the old historical event
derivative the node-13 derivative. Re-evaluating the native functional and
transporting the launch chart gives the local composition above. It does
not prove that the native state at node 13 is the restriction of a fixed
external environment to the displaced seam. In particular, moving a base
point from the historical event to node 13 is not itself a material
pullback theorem with external state fixed.

Thus the artifact freezes the requested first-order chart and composition,
but does not silently promote them to the complete fixed-environment
`R_E`. A physical environment identification/transport must preserve the
external-state labels and the same seam/frame conventions before that
promotion. The 66+7 boundary Schur solve and Layer-C rebinding have not been
performed on an unproven environment identification.

Producer: `scripts/bind_n12_gate7_recentered_launch_response.py`.
Packet: `artifacts/flagship_integration/gate7_launch_response_20260927/`.
Tests: `tests/test_gate7_recentered_launch_response.py`.

Both packet outputs reproduce byte-identically in independent validated runs;
`reproduction.json` records their hashes. All **41 focused tests pass** with
`--noconftest` across the new launch-response tests and the five preceding
event-conormal, parent-sector, moving-seam, co-moving-interface and coupled-center
test files.

No center solve, historical endpoint/midpoint proof, Stage-B calculation,
nonlinear slaving or Gate-7 closure calculation was rerun. The only new action
evaluation is the current-center first-order native conormal response.
`8.915423761304125e-7` is unchanged. `Gate7_closed=False` and
`FULL_BHSM_COMPLETE=False`.
