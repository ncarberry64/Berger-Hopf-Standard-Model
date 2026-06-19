# PO-BH-64 - Eta Projection and No-Overfit Ledger

Current public status: structural architecture integrated conditional; numerical closure open.

## Eta_l Correction

The prior `8/9` route is downgraded. It remains a historical diagnostic route
but is not used as the primary derivation.

```text
eta_l_8_over_9_trace_route:
DOWNGRADED_NUMERICAL_COINCIDENCE / DO_NOT_USE_AS_PRIMARY_DERIVATION
```

The current candidate structure is

```text
eta_l = Pi_l * alpha_geom/pi * (1 - alpha_geom)
```

where

```text
Pi_l = charged-lepton boundary projection factor
alpha_geom = internally derived geometric/projection constant
(1 - alpha_geom) = first-order boundary self-screening candidate
```

Statuses:

```text
eta_l_projection_structure: VALIDATED_CANDIDATE
Pi_l_value: OPEN_LOCALIZABLE
alpha_geom_internal_derivation: OPEN_LOCALIZABLE
eta_l_self_screening_factor: STRUCTURALLY_SUPPORTED_CANDIDATE
eta_l_exact_value: OPEN
eta_l_fit: FORBIDDEN_AS_DERIVATION
```

Measured alpha may be used only as comparison/scaffold, not as a derivation.
Do not use CODATA alpha to claim BHSM has derived `eta_l`. Do not fit `Pi_l`
after looking at charged-lepton mass ratios.

PO-BH-65 adds:

```text
eta_l_depends_on_rho_ch: TRUE
self_screening_factor_1_minus_alpha_geom: STRUCTURALLY_SUPPORTED_CANDIDATE
```

Because the charged cost metric remains open, `eta_l_exact_value` remains
`OPEN`.

## Z_virt Dimension-Ratio Path

User-confirmed physical interpretation:

```text
Z_virt^{u,2}=1/2
```

means one allowed virtual door out of two possible doors.

Formal candidate:

```text
Z_virt^{u,2}
= dim(admissible virtual channel) / dim(two-channel virtual pair)
= 1/2
```

Status:

```text
Z_virt_u2_dimension_ratio: STRONG_DERIVATION_CANDIDATE
```

Remaining proof obligation: prove the relevant up-sector virtual correction
samples that two-door global/cosmic virtual pair. It is not called fully
derived here.

## Guardrails

No official `eta_l` value is changed. No frozen prediction is changed. No
observed charged-lepton mass ratio is used to choose `Pi_l` or
`alpha_geom`.
