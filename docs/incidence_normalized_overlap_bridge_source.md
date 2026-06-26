# Incidence-Normalized Overlap Bridge Source v1

Current public status: structural architecture integrated conditional; numerical closure open.

This sprint adds a focused structural theorem-kernel candidate for unifying the
charged and neutral bridge seed magnitudes. It does not change frozen or
official predictions and does not claim numerical closure.

## Candidate Rule

```text
g_sector = O_sector^2 / I_sector
```

Here `g_sector` is the bridge seed magnitude, `O_sector` is the sector overlap
amplitude, and `I_sector` is the total incidence trace for that sector.

## Neutral Calculation

```text
I_nu = 3
O_nu = 1
g_nu = 1^2 / 3 = 1/3
```

Status:

```text
neutral_bridge_seed_1_over_3=DERIVED_CONDITIONAL_ON_NEUTRAL_INCIDENT_TRACE_3_AND_UNIT_OVERLAP
```

The neutral unit overlap and primitive incidence trace localize the already
recorded neutral bridge seed `g_nu=1/3`. Neutral eta/beta/kappa final action
derivation and neutral numerical closure remain open.

## Charged Calculation

```text
I_ch = 21
O_ch = 4/3
g_ch = (4/3)^2 / 21 = 16/189
```

Equivalently:

```text
g_ch = (1/21)(4/3)^2
```

The charged overlap factor is recorded as:

```text
charged_overlap_factor=4/3
motivation=down Hopf multiplier 4 divided by rank-three closure 3
action_source_status=OPEN_LOCALIZABLE
```

Status:

```text
charged_bridge_seed_16_over_189=DERIVED_CONDITIONAL_ON_INCIDENT_TRACE_21_AND_OVERLAP_4_OVER_3
charged_overlap_4_over_3_action_source=OPEN_LOCALIZABLE
```

The exact action-level derivation of `O_ch=4/3` remains open/localizable and is
not upgraded here.

## Ratio Diagnostic

```text
g_ch / g_nu = (16/189)/(1/3) = 16/63
```

## Status Table

| Item | Status |
| --- | --- |
| incidence_normalized_overlap_bridge_rule | PARTIALLY_LOCALIZED |
| neutral_bridge_seed_1_over_3 | DERIVED_CONDITIONAL_ON_NEUTRAL_INCIDENT_TRACE_3_AND_UNIT_OVERLAP |
| charged_bridge_seed_16_over_189 | DERIVED_CONDITIONAL_ON_INCIDENT_TRACE_21_AND_OVERLAP_4_OVER_3 |
| charged_overlap_4_over_3_action_source | OPEN_LOCALIZABLE |
| full_numerical_closure | OPEN |

## What This Localizes

This rule places the neutral bridge seed `1/3` and charged bridge seed `16/189`
under the same incidence-normalized overlap form. It also identifies the
remaining charged-local object as the action source of the overlap factor `4/3`.

## What Remains Open

- exact action derivation of charged overlap factor `4/3`
- final bridge action theorem
- charged same-sector numerical closure
- neutral eta/beta/kappa final derivation
- CKM, PMNS, and CP numerical closure
- comparison-ready prediction package

No observed masses, CKM data, PMNS data, neutrino data, empirical target ratios,
measured alpha values, or experimental values are used as derivation inputs.

Frozen predictions changed: no.

Official predictions changed: no.
