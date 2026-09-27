# Gate-7 canonical dynamic-flux ownership and native event response

Continuation of `911aac37` on `theory/gate7-66d-reduced-adjoint-integration`.

**The two dynamic-flux equations have an existing owner.** The native event
contribution now has all seven rows, with an outward 7x98 derivative at the
same stored point as the ten-sector packet. The fixed-environment moving-seam
7x73 composition is not yet instantiated. No new environment law is needed
or introduced by this calculation.

## Exact ownership and signs

The v15.39 complete-child mathematical-system module is a ledger, not a flux
evaluator; it imports no canonical scientific evaluator. The executable
complete-child lineage supplies the requested equations:

| Source | Owned operation |
|---|---|
| `aether_n3_required_child_cauchy_flux_v17_93.py:70` | Common action-Hessian constrained configuration/velocity lifts, momentum and force |
| Same module, lines 150–154 | `Dt P - F + Gamma_event + Gamma_child = 0` |
| `aether_n3_child_constraint_cauchy_match_v17_94.py:47` | Action-owned metric radial covector with signed A/B components |
| `aether_n3_complete_child_chart_reconstruction_v18_24.py:38` | Actual complete-child residual assembler |
| Same module, lines 60–69 | Event flux constructed as `Lq_event.T @ radial_event` |
| `aether_n3_constraint_solved_orbit_v16_08.py:82` | Constraint-consistent Euler–Dirac acceleration and multiplier rate |
| `aether_cross_resolution_reconnaissance_v21_35.py:2998,3199` | Generic finite-N extension of those same lifts and residuals |

The new report freezes full source hashes and exact function line spans/text.
The generic extension confirms finite-N representation; it is not used as
the sole authority for the physical equation.

Write `P=L_v^T g_v`, `F=L_q^T g_q`, `Gamma=L_q^T r`, and let `X_c`
be the constraint-consistent child rate. The two flux rows are

```
R_flux = DP_c[X_c] - F_c + Gamma_c + Gamma_e.
DR_flux[u] = D2P_c[X_c,u_c] + DP_c[DX_c u_c]
             - DF_c[u_c] + D Gamma_c[u_c] + D Gamma_e[u_e].
```

Thus the event-side contribution to these rows is `D Gamma_e`, with plus
sign. This does **not** substitute radial flux for the complete dynamic
equation. The child momentum-rate, acceleration and moving canonical lift
remain in that equation, already represented by the child-side packet.
Adding another event momentum-rate term would change this existing owner.
The canonical source is tested by executing its actual residual assembler
with polynomial control dependencies and perturbing the event flux.

For the seven interface rows the native balance is

```
[T q_c - T q_e;
 P_c - P_e;
 Gamma_c + DP_c[X_c] - F_c + Gamma_e].
```

In the previously frozen child reaction convention
`beta_c=[Tq_c,P_c,F_c-Gamma_c-DP_c[X_c]]`, this is
`diag(I5,-I2) beta_c + diag(-I5,+I2) [Tq_e,P_e,Gamma_e]`.
All quantities must first be transported to the same owned frame.

## New outward native computation

Producer: `scripts/derive_n12_gate7_event_conormal_jet.py`.
Packet: `artifacts/flagship_integration/gate7_event_conormal_20260927/`.

The frozen parent-sector gradient/Hessian and five-row derivative are reused.
Only the new configuration-lift contracted D3 is evaluated at that packet's
stored point. No frozen endpoint, midpoint, Stage-B, local closure or sector
producer is rerun. There is no finite-difference approximation.

For the same complete-action 63x63 configuration KKT matrix,

```
Kq Lq = target,
DLq[u] = -Kq^-1 DKq[u] Lq,
D Gamma_e[u] = DLq[u]^T r_e + Lq^T Dr_e[u].
```

The two terms are saved separately. A second, adjoint contraction independently
replays the direct differentiated-lift formula. Both use Arb512 and outward
interval arithmetic. Derivative columns are the same 98 weighted action
directions `W^-1` as the frozen native five-row packet.

| Replay | Outward Frobenius upper bound |
|---|---:|
| Direct minus adjoint conormal derivative | `5.283634e-134` |
| Configuration lift equation | `1.319702e-138` |
| Differentiated configuration lift equation | `1.195236e-130` |
| Configuration KKT inverse defect | `2.789260e-134` |

The conormal derivative norm is at most `209475.108659`; its lift and raw
covector contributions are at most `210566.216979` and `3603.525785`.
These are native-coordinate point bounds, not a physical budget debit or
decay/stability finding. The signed sum is retained before taking a bound.

The ten action contributions retain their common total-action lift. Trace
geometry is included once, not ten times. `complete_child_flux_response.py`
provides the exact signed derivative assembly and sector-preserving material
composition with an explicitly supplied shape term. It does not manufacture
a material map or silently substitute zero for a missing shape derivative.

Both new outputs (`arrays.npz`, `report.json`) reproduce byte-identically in
two independent runs; the hashes are recorded in `reproduction.json`.
All **35 focused tests pass** with `--noconftest` across the new
`test_gate7_event_conormal_jet.py` and the existing parent-sector, moving-seam,
co-moving-interface and coupled-fiber-center test files.

## Precise remaining composition

The requested `T_seam_98x73` has not been identified in the referenced packets.
The located endpoint array `physical_tangent_action` has shape 371x98x73,
but its producer `materialize_n12_gate7_first_hs_newton_endpoint_tangent.py`
constructs nullspaces of the **child** constraint Jacobians. Its own authority
is `DIRECT_NUMERICAL_ACTION_CONSTRAINT_NULLSPACES_NOT_INTERVAL_AUTHORITY`;
its columns are not a declared 66+7 parent material frame.
Multiplying the native event packet by that array would not implement the
fixed-environment pullback requested in the handoff.

The base-point role also remains exactly as frozen in
`gate7_parent_sectors_20260927/role_scope.json`: historical reset
`center_state[:98]` has not been identified as the current fixed environment.
The forward chronology exchanges the historical pair. Neither point is
selected by proximity or by the label "event".

What is needed to instantiate the requested composition is the referenced
fixed-environment material jet with its base-point binding, weighted coordinate
convention, ordered 66+7 columns, and any explicit frame/normal/measure jet
not already included. This is a request for the claimed existing artifact,
not a request for a phenomenological environment law. The user was asked for
its filename while the independent canonical flux work continued.

Once that binding is supplied, assemble the signed seven-row balance above,
including the existing weak `nu_rho D rho_e` feedback exactly once, and solve
its seven reaction columns. No tangent is chosen to match a historical one.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`. The frozen
`8.915423761304125e-7` allowance is unchanged. Layer C has not been rebound
to an unbound material tangent.
