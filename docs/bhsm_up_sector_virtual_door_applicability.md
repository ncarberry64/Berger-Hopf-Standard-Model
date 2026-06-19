# PO-BH-66 - Up-Sector Virtual Door Applicability Audit

Current public status: structural architecture integrated conditional; numerical closure open.

This audit asks whether the existing BHSM repository proves that the released
middle-up virtual correction samples a two-door virtual pair. It does not alter
the frozen release and does not use observed masses, CKM values, PMNS values,
neutrino data, measured alpha, or target ratios to justify the factor.

## Candidate Virtual Pair

The candidate colored weak virtual pair is

```text
V_pair^u = span{door_u, door_d}
```

where

```text
door_u = colored upper/up-compatible virtual channel
door_d = colored lower/down-compatible virtual channel
```

Therefore

```text
dim(V_pair^u) = 2
```

The candidate up-admissibility projector is

```text
A_virt^u door_u = door_u
A_virt^u door_d = 0
```

so

```text
rank(A_virt^u) = 1
dim(V_adm^u) = 1
```

The dimension ratio is then

```text
Z_virt^{u,2} = rank(A_virt^u) / dim(V_pair^u) = 1/2
```

## Source Audit Table

| object | source file | evidence found | supports two-door pair? | supports one admissible door? | supports up-sector applicability? | uses observed masses? | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Z_virt dimension ratio ledger | `docs/bhsm_eta_projection_no_overfit.md` | states one allowed virtual door out of two possible doors and records the dimension ratio | yes | yes | no | no | `STRONG_DERIVATION_CANDIDATE` | the dimension-ratio route is explicit, but applicability to the actual up-sector correction is a remaining proof obligation |
| sector projector Hessian fork audit | `data/bhsm_sector_projector_hessian_fork_audit.json` | records `Z_virt_u2_dimension_ratio` and lists virtual-pair applicability proof as remaining open | yes | yes | no | no | `OPEN_LOCALIZABLE` | machine-readable audit keeps applicability proof open |
| pure-fiber rank-half rule | `theory/pure_fiber_rank_half_rule.md` | records rank-half rule for mode `(6,0)` and asks to derive locality to middle-up mode | yes | yes | no | no | `STRUCTURAL_SUPPORT_WITH_OPEN_LOCALITY` | rank-half structure is documented, but locality/applicability remains open |
| boundary projection channel theorem | `theory/boundary_projection_channel_theorem.md` | records pure-fiber one-half as structural candidate and keeps locality to `(6,0)` open | yes | yes | no | no | `STRUCTURAL_SUPPORT_WITH_OPEN_LOCALITY` | supports the rank-half candidate while preserving the open applicability proof |
| boundary flux quantization analogy | `theory/pure_fiber_double_branch_consequence.md` | says boundary-flux language is compatible by analogy with a two-branch pure-fiber orientation space for `(6,0)` | yes | no | no | no | `ANALOGY_NOT_DERIVATION` | explicitly says it does not derive the double branch or rank-one projection |
| frozen dressed branch guardrail | `docs/frozen_predictions.md` | freezes `Z_virt^{u,2}=1/2` only on `c/t` | no | no | yes | no | `FROZEN_RELEASE_SCOPE_ONLY` | records released scope but is not a derivation source for the virtual pair |

## Applicability Gate

The audit verifies the formal candidate ratio:

```text
dim(V_pair^u) = 2
rank(A_virt^u) = 1
Z_virt^{u,2} = 1/2
```

However, it does not find an existing repository source proving that the
relevant up-sector virtual correction samples `V_pair^u`. Therefore:

```text
Z_virt_u2_dimension_ratio: STRONG_DERIVATION_CANDIDATE
Z_virt_u2_applicability: OPEN_LOCALIZABLE
```

Allowed conservative claim:

```text
BHSM has a virtual-door dimension-ratio route for Z_virt^{u,2}=1/2.
```

Not claimed:

```text
BHSM derives Z_virt^{u,2}=1/2 as a fully applicable correction.
```

## Validation / Invalidation Ledger

Validated:

- `Z_virt` has a clean dimension-ratio route if the two-door pair applies.
- The ratio is independent of observed masses.
- The physical interpretation is one allowed virtual door out of two possible doors.

Invalidated or downgraded:

- claiming `Z_virt` is fully derived without an applicability proof;
- using charm/top or up/top to justify the factor;
- treating the ratio as a fitted correction.

Still open:

- applicability of the two-door pair to the relevant up-sector virtual correction;
- `rho_ch`;
- `eta_l`;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.

## Guardrails

No frozen predictions are changed. No official predictions are changed. The
released `BHSM_DRESSED_V1_CANDIDATE` scope is not modified. No observed quark
masses, charm/top ratio, up/top ratio, CKM values, PMNS values, neutrino data,
measured alpha, or empirical target values are used to select the factor.

## PO-BH-67 Dependency Trace Update

PO-BH-67 traces the actual dressed-branch dependency path:

```text
build_bhsm_dressed_v1_candidate
  -> pure_fiber_middle_up_rule()
  -> apply_virtual_dressing(model, (rule,))
```

The source rule is local to the pure-fiber middle-up mode `(6,0)` and uses
internal mode/boundary data (`j=0`, `q=6`, `Omega_u=6`) plus the
`WEAK_DOUBLE_PROJECTION` candidate source. The trace does not find an explicit
dependency from that actual dressing source to the two-door pair
`V_pair^u=span{door_u,door_d}`. Therefore `Z_virt_u2_applicability` remains
`OPEN_LOCALIZABLE` and the dimension ratio remains a
`STRONG_DERIVATION_CANDIDATE`.
