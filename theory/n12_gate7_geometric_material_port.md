# Gate-7 native port: three geometric and four material rows

Continuation of `4880b779`. **The canonical producer confirms the 3+4
split.** The requirement to find seven scalar-action seeds is retired.
The frozen earlier packets remain unchanged.

The current three-row geometric derivative has been materialized and
replayed. The four material rows require the canonical dynamic-flux
operator, not just a relabeling of four pointwise action contractions.
Their complete heat/zeta/history correction is not yet materialized.

## Source-certified row table

The current generic owner is
`src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py`.
Its `_child_rows_at_order` (3199–3282) assembles the exact native order
`[trace3, constraints25, momentum2, flux2]`. The packet records full
function text, line spans, source hashes, and per-row signs/dependencies.

| Native row | Type | Owner | History derivative route |
|---|---|---|---|
| trace 1 | geometric compatibility | `_trace_jacobian_at_order`, 2751–2761; assembler | `T1 Dq`, plus an explicit frame/section term only if present |
| trace 2 | geometric compatibility | same, `T2` | `T2 Dq` |
| trace 3 | geometric compatibility | same, `T3` | `T3 Dq` |
| momentum 1 | material action reaction | `_canonical_pair_at_order`, 2998–3022 | mixed action contraction with `Bv1`, moving lift, internal adjoint |
| momentum 2 | material action reaction | same | corresponding `Bv2` contraction |
| flux 1 | material dynamic reaction | canonical pair; radial owner 3133–3159; assembler | configuration-force variation minus conormal and complete momentum-rate variation |
| flux 2 | material dynamic reaction | same | corresponding second attachment channel |

All three traces depend directly only on configuration `q`. Momentum and
flux depend on `q,v,m` through their total-action lifts, gradients and rate.
The producer has no explicit joint-history heat/zeta call. Its existing
local action sectors remain included; that observation does not remove
local vacuum terms or set any nonlocal action sector to zero.

Let `P=Lv^T g_v`, `F=Lq^T g_q`, and `G=Lq^T radial`. The source gives

```
event output        = [T q_e; P_e; G_e],
child-required data = [T q_c; P_c; F_c-G_c-DP_c[X_c]],
balance             = diag(I5,-I2)*child - diag(I5,-I2)*event.
```

The same dynamic law is stated by the earlier executable owner
`aether_n3_required_child_cauchy_flux_v17_93.py:150–153`. The source test
executes the actual current assembler with controlled component inputs to
verify each sign and the three geometric rows.

## Complete three-row chain rule on the current chart

`T` is constant at the retained material section `chi=pi/4`.
With raw-state weights `W` and the already-certified current launch jet `J`,

```
R_trace = [T,0,0] W^-1 J,       shape 3x73.
```

| Check | Outward bound |
|---|---:|
| All three rows minus frozen native trace derivative | `1.603e-14` |
| Rank-3 right-inverse defect | `2.245e-19` |
| Radius combination versus frozen spectral first jet | `8.613e-15` |

The three row norm upper bounds are `0.597799`, `0.446883`, and `0.332212`.
All comparisons retain stored radii; these are chart-level enclosures.

The accounting is:

| Contribution | Treatment |
|---|---|
| Fixed material section `T Dq` | Evaluated; already in the local native packet |
| Physical motion of seam/state in `Dq` | Included in the supplied current jet, not removed |
| Additional explicit section/frame derivative | Identically zero in this producer, whose material section is fixed |
| Explicit attachment `DA2` contribution | Identically zero: the three trace equations do not use `A2` |
| Inherited state/history/reset transport | Already inside the 72-label-plus-current-flow chart; not added again |
| New complete joint-normal/formation/reset transport | Not numerically instantiated by this calculation |

There is therefore **no new direct heat/zeta action term in a trace row**.
The evaluated `R_trace` cannot be added again to `R_local_native`. A later
change in the total solved state jet contributes
`Delta R_trace = [T,0,0] W^-1 Delta J_joint`.
Zero direct action dependence does not imply `Delta J_joint=0`.
The additive `R_trace_history` remains unspecified until that total jet is
bound, while the full trace derivative on the current chart is closed.

## Four directions and the actual flux map

The exact permutation from the frozen direction order
`(Bq1,Bq2,Bv1,Bv2)` to `(Bv1,Bv2,Bq1,Bq2)` is saved as a `4x4` matrix;
its inverse defect is exactly zero. It orders the four canonical action
contractions as `(P1,P2,F1,F2)`. It does **not** turn force into flux.

The owned map and its derivative are

```
(P,F) -> (P, F-G-DP[X]),
D(P,F)[u] -> (DP[u], DF[u]-DG[u]-D2P[X,u]-DP[DX u]).
```

This is a differential operation plus the conormal, not a constant `4x4`
basis change. Holding `(P,F)` fixed while changing the momentum-rate jet
changes the native flux. The test suite checks that distinction directly.

At the current center the force-to-flux value offset has norm at most
`1908.920`, with one entry's absolute value at least `1578.133`. Thus
identifying the last two native outputs with `F` already fails at this
center. This is representation accounting, not instability.

The frozen local material derivative is decomposed and reassembled in all
73 columns, retaining `DG`, `D2P[X,u]`, and `DP[DX u]` separately. Its
outward replay residual is `7.637e-8`. This is a signed recombination of
frozen jets, **not an independent action-derivative certificate**: the force
jet was recovered from the same frozen dynamic identity. No tolerance is
changed and this check is not a new heat/history calculation.

## Reduced computational target and remaining inputs

The mathematical work is now separated into

```
GEOMETRIC_TRACE_HISTORY_JET_3x73
CURRENT_CENTER_HEAT_ZETA_MIXED_MATERIAL_LAUNCH_JET_4x73.
```

`src/bhsm/interface/geometric_material_port.py` implements the trace chain
rule, the native differential flux assembly, a streamed four-direction
heat pair, and the four-direction general implicit-objective adjoint.
It introduces no padded trace-action seeds. The supplied mixed blocks must
include the genuine `Tr(Q P_Balpha,j)` term and moving-duration contributions;
the routine adds the explicitly supplied moving-seed term. In particular,
the ordinary moving-seed sign is plus. It does not assume that the history
sector is separately stationary under the complete internal equations.

To produce the numerical material history correction, the current joint
formation/reset/C2 action must supply those four reduced material jets,
the canonical lift motion, and the conormal/momentum-rate terms required
by the native operator above. A pointwise mixed configuration-force jet
alone is insufficient for the dynamic-flux rows. The stored C2-only prefix
does not supply the current formation history or complete reset/contact
normal response. These remain required inputs, not zero-filled sectors.
No extra environment action or phenomenological term is introduced.

The source split is established. The full fixed-environment response is
not promoted; `R_history_7x73` and `R_complete_7x73` remain unmaterialized.
No Stage-B work, interval actions, or 1,222-cell prefix was rerun.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.

Producer: `scripts/bind_n12_gate7_geometric_material_port.py`.
Packet: `artifacts/flagship_integration/gate7_geometric_material_port_20260927/`.
Validation: **59 focused tests pass**. Both outputs reproduce byte-identically
in two fresh processes; exact hashes and the test command are in the packet.
