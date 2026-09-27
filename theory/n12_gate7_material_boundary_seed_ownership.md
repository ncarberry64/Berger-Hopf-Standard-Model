# Gate-7 material boundary seeds: what the canonical owner actually supplies

Continuation of `0682b1da`, retaining the `d0586b60` C2 prefix unchanged.
The requested ordinary material derivative uses the **plus** sign:
`D(DGamma[B])[P] = D2Gamma[P,B] + DGamma[DB[P]]`.

The current canonical source supplies two configuration and two velocity
virtual directions. Its seven outputs are a mixed kinematic/canonical port,
not a stored list of seven action-variation directions. This prevents the
requested seven-seed identification from following from the existing
right-inverse calculation alone. It is a missing variational binding, not
a failure of the physical envelope or proof that no such binding exists.

## Exact source relation

In `src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py`:

| Function / lines | Actual definition |
|---|---|
| `_trace_jacobian_at_order`, 2751–2761 | Three geometric configuration traces `Tq` |
| `_attachment_jacobian_at_order`, 2764–2781 | Two attachment differentials `A2(q)` |
| `_boundary_lift`, 2816–2824 | Action-Hessian constrained two-column lift |
| `_canonical_pair_at_order`, 2998–3022 | `P=Lv^T g_v`, `F=Lq^T g_q` |
| `_metric_radial_flux_covector_at_order`, 3133–3159 | Signed radial covector `r` |
| `_child_rows_at_order`, 3199 onward | Trace matching, 25 constraints, momentum matching, dynamic flux |

The earlier executable N3 owner is
`aether_n3_required_child_cauchy_flux_v17_93.py::_canonical_pair`; the new
report binds both sources by hash and records exact current function spans.

The native event output and required child target are respectively

```
g_event = [Tq; Lv^T g_v; Lq^T r],
g_child = [Tq; Lv^T g_v; Lq^T(g_q-r) - DP[X]].
```

Their complete-child balance is
`diag(I5,-I2) g_child + diag(-I5,+I2) g_event = 0`.
The last two rows contain a momentum time derivative as well as the
configuration action derivative. A seven-component action gradient cannot
be substituted for this mixed port without an additional owner identity.

## Current-center reusable data

Producer: `scripts/bind_n12_gate7_material_seed_ownership.py`.
Packet: `artifacts/flagship_integration/gate7_material_seeds_20260927/`.
It consumes frozen arrays; no action or history producer runs.

The current canonical KKT lifts have 63 rows: the first 37 are the virtual
configuration/velocity direction; the other 26 are KKT dual variables,
**not state variations**. In raw state ordering `(q37,v37,m24)` the four
available directions are

```
Bq_a = (Lq[:,a], 0, 0),   Bv_a = (0, Lv[:,a], 0),   a=1,2.
```

The saved `canonical_four_seed_action_98x4` applies the frozen state weights
to these raw directions. No descriptor proof scale is applied.
There is no independent acceleration/flux coordinate in these seeds;
dynamic-flux dependence is through the owned rate `X` and `DP[X]`.

Both use `A2 L=I2`, at the **current** center:

| Check | Outward Frobenius upper bound |
|---|---:|
| `A2 Lq-I2` | `4.813e-43` |
| `A2 Lv-I2` | `2.148e-44` |
| Four-column left-inverse defect | `3.028e-43` |

The four columns have certified rank 4. They are not automatically in the
full 25-constraint physical state kernel: their stored constraint image is
nonzero (Frobenius upper bound `2137.161`). This is consistent with their
definition as canonical virtual directions using 24 multiplier constraints;
it is not a reason to project them by an arbitrary Euclidean map.
One constraint-image entry has certified absolute lower bound `1735.815`;
the nonzero conclusion does not follow from an upper bound alone.
The packet saves their full native event/child `7x4` pairing and constraint
image so this distinction can be reused without another producer.

The attachment's complete first material derivative on all 73 current
launch directions is also saved, with shape `2x37x73`. For
`v=sum_j (-1)^j q_(25+j)`,

```
DA2_0[P]_(25+j) = -2 sech^2(2v) Dv[P] (-1)^j,
DA2_1[P] = -DA2_0[P].
```

This is the derivative of the attachment rows, **not** the full derivative
of the canonical seeds. The latter obeys `K DL[P]=DE[P]-DK[P] L`.
The frozen canonical packets save `L` and contracted output derivatives,
but not the vector-valued `DL` or `DK L`. Output contractions cannot recover
all entries of `DL`. The supplied reusable routine differentiates the KKT
equation with explicit `DK` and `DE`; it never substitutes missing motion
by zero. For these fixed material attachment coordinates, `DE=0`.

## What the seven-column Stage-B duality proves

At its historical node-13 point, the already-owned construction is

```
H_T=T^T H_action T,
beta=diag(1/frozen_row_scale) R23,
L=H_T^-1 beta^T (beta H_T^-1 beta^T)^-1.
```

Replay gives `||beta L-I7|| <= 3.795e-139` on the frozen numerical inputs.
This is an indefinite action-Hessian complement, not a positive-metric or
Euclidean replacement. The replay does not certify historical finite-
difference error or transport the complement to the current center.

Even an exact `beta L=I7` says only that `L` is a coordinate lift. For any
scalar action, `L^T DGamma` is a conjugate covector, not automatically the
coordinate/output `beta(Y)`. Adding a kernel direction to a right inverse
can change that action contraction unless stationarity removes the change.
Even when lift independence follows from stationarity, equality to the
specific native output still needs its own variational identity.

Consequently no `7x7` material change of basis is asserted. Four known
canonical columns cannot supply a seven-column frame by a basis change.
The three geometric traces are not identified with their conjugate forces.

## Exact remaining construction

Derive the variational boundary-pairing identity for the complete joint
action that maps its reduced variation to the native mixed port above.
It must either identify seven actual material directions (possibly in an
already-owned extended boundary formulation, with its constraint variables
explicit), or supply the actual channel-dependent variational operator for
trace, momentum, and dynamic flux. In particular it must explain the three
trace channels and the two `DP[X]` terms, rather than replacing them by seven
arbitrary scalar-action contractions.

Only after that binding can the narrow contracted object
`CURRENT_CENTER_HEAT_ZETA_MIXED_BOUNDARY_LAUNCH_JET_7x73` be evaluated in the
intended physical basis. The earlier adjoint/mixed-operator formulas remain
valid; this checkpoint does not change them or return to separate norms.
The formation/reset/contact contributions have not been set to zero.
The stored C2 prefix is preserved and not substituted for formation history.

`R_history_7x73` and `R_complete_7x73` remain unmaterialized. No material
response promotion, nonlinear work, tolerance change, or closure claim is
made. `Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.

Validation: **48 focused tests pass**, covering the new lift/seed checks,
mixed heat/zeta contractions, native seven outputs, current canonical
reactions, recentered launch, and frozen history transport. Both generated
outputs reproduce byte-identically in two fresh processes; see
`reproduction.json` and `validation.json` in the packet.
