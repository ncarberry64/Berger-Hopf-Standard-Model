# PO-BH-65 - Charged Hessian Source Audit

Current public status: structural architecture integrated conditional; numerical closure open.

## Scope

This is a charged Hessian source audit. It asks whether existing BHSM
boundary/action/Hessian structures derive `rho_ch=1`, `rho_ch=3`, another
definite value, or no value yet.

It does not solve mass ratios and does not introduce numerical predictions.
It does not use charged-lepton masses, quark masses, CKM, PMNS, neutrino data,
measured alpha, observed mass ratios, anomaly/FTL data, propulsion/anomaly
data, or target values to choose `rho_ch`.

## Source Audit Table

| object | possible source | supports rho=1? | supports rho=3? | supports another rho? | supports qj cross-term? | charged-sector applicable? | neutral/topographic only? | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| minimal isotropic charged closure | absence of charged anisotropy, qj cross-term, or charged j-weighting source | yes | no | no | no | yes | no | `MINIMAL_ACTION_CLOSURE_CANDIDATE` | absence of a source supports rho=1 as minimal closure, not as a derivation |
| base cyclic factor 3 | finite cyclic boundary factor | no | yes | no | no | no | no | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | no action/Hessian term links factor 3 to charged j-direction Hessian weight |
| neutral/topographic Berger anisotropy | neutral/topographic metric, scalar profile, collar, or subsurface mechanism | no | no | yes | yes | no | yes | `OPEN_ALLOWED_NEUTRAL_ONLY` | neutral mixing is allowed but cannot leak into charged Hessian without explicit coupling |
| charged qj cross-term | none found in charged-sector action/Hessian sources | no | no | no | no | yes | no | `FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED` | charged q and j remain separate unless a charged action term derives mixing |

## Charged/Neutral Separation Rule

Charged sectors:

```text
q and j are separate in the charged Hessian unless a charged-sector action term explicitly mixes them.
```

Neutral/topographic sectors:

```text
q and j mixing may be allowed through neutral/topographic geometry, scalar/topographic profile, Berger metric, collar geometry, or subsurface/topographic mechanism.
```

Statuses:

```text
charged_qj_cross_term: FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED
neutral_qj_mixing: OPEN_ALLOWED
topographic_Berger_anisotropy_to_charged_sector: FORBIDDEN_UNLESS_EXPLICIT_COUPLING_DERIVED
```

## Candidate 1 - Minimal Isotropic Closure

```text
rho_ch = 1
N_iso(q,j) = q^2 + j^2
```

Reason: no charged anisotropy source, no qj cross-term source, and no charged
j-weighting operator is found. Therefore the no-hidden-parameter charged
Hessian is identity in the integer-cleared `(q,j)` basis.

Status:

```text
rho_ch_1_minimal_closure: MINIMAL_ACTION_CLOSURE_CANDIDATE
```

This is not marked derived because no action term explicitly gives equal q
and j Hessian weights.

Costs:

```text
lepton: 0,5,18
up: 0,36,65
down: 0,9,20
```

## Candidate 2 - Cyclic Anisotropy

```text
rho_ch = 3
N_cyclic(q,j) = q^2 + 3j^2
```

Reason: the base cyclic closure factor 3 may suggest a charged Hopf/base
j-direction weighting, but no existing action/Hessian term explicitly links
that factor to the charged j-direction Hessian weight.

Status:

```text
rho_ch_3_cyclic_weight: STRUCTURALLY_MOTIVATED_NOT_DERIVED
```

Costs:

```text
lepton: 0,13,36
up: 0,36,67
down: 0,27,28
```

## Candidate 3 - Another Derived Value

```text
rho_ch = rho_action
```

Status:

```text
rho_ch_action_value: OPEN_LOCALIZABLE
```

No existing charged action/Hessian term derives a definite value.

## Candidate 4 - Unresolved

```text
charged_Hessian_anisotropy_rho_ch: OPEN_LOCALIZABLE
```

The action must decide whether `rho_ch=1`, `rho_ch=3`, or another value is
derived.

## General Charged Metric Guardrail

```text
N_ch(q,j; rho_ch) = q^2 + rho_ch j^2
rho_ch > 0
```

For down-sector membership:

```text
0 < rho_ch < 8
```

For down-sector ordering with `(0,3)` before `(4,2)`:

```text
0 < rho_ch < 16/5
```

If a full cross-term is ever introduced:

```text
N_ch(q,j; s,r) = q^2 + 2s qj + rj^2
```

then `s` must be action-derived, not fitted. PO-BH-65 does not introduce `s`
as a live parameter.

## Eta_l Dependency Update

Because `eta_l` depends on the charged cost metric, `eta_l` cannot be
finalized until `rho_ch` is derived.

Statuses:

```text
eta_l_projection_structure: VALIDATED_CANDIDATE
eta_l_exact_value: OPEN
eta_l_depends_on_rho_ch: TRUE
eta_l_fit: FORBIDDEN_AS_DERIVATION
eta_l_8_over_9_trace_route: DOWNGRADED_NUMERICAL_COINCIDENCE
alpha_geom_internal_derivation: OPEN_LOCALIZABLE
Pi_l_value: OPEN_LOCALIZABLE
self_screening_factor_1_minus_alpha_geom: STRUCTURALLY_SUPPORTED_CANDIDATE
```

Measured alpha is not used here as a derivation.

## Validation / Invalidation Ledger

Validated by PO-BH-65:

- charged qj cross-term remains absent;
- charged/neutral Hessian split remains valid;
- `rho=1` remains the minimal closure candidate;
- `rho=3` remains possible only if a cyclic j-weight source is later derived.

Invalidated or downgraded:

- claiming `rho=3` is derived merely because 3 is the base cyclic factor;
- claiming `rho=1` is derived merely because old costs used `q^2+j^2`;
- finalizing `eta_l` before `rho_ch` is derived;
- using neutral/topographic anisotropy as charged-sector anisotropy without explicit coupling.

Still open:

- `rho_ch`;
- action source for charged Hessian;
- `Pi_l`;
- `alpha_geom`;
- `eta_l` exact value;
- target-amplitude action derivation;
- rank-three ladder derivation;
- down-incidence derivation;
- `Z_virt` applicability proof;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.

## Conservative Conclusion

PO-BH-65 audits the existing BHSM boundary/action/Hessian sources for charged
Hessian anisotropy. It preserves `rho_ch=1` as a minimal action-closure
candidate and `rho_ch=3` as a cyclic anisotropy candidate, but neither is
chosen by fit or promoted to fully derived. `rho_ch` remains open-localizable,
and `eta_l` remains blocked on `rho_ch`.
