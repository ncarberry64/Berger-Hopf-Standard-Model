# RG / Scheme Transport Interface v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This interface records the transport stages needed before BHSM operator-side
outputs can be compared in a scheme/scale-aware way. It does not implement
physical running formulas or use empirical inputs.

## Stages

```text
BARE_MODE_LEDGER
ACTION_KERNEL_SELECTED
SUPPRESSION_DRESSED
BRIDGE_DRESSED
THRESHOLD_DRESSED
RG_TRANSPORT_PENDING
SCHEME_ALIGNED
COMPARISON_READY
```

Current BHSM readiness stops at:

```text
RG_TRANSPORT_PENDING
```

Nothing is marked `SCHEME_ALIGNED` or `COMPARISON_READY`.

## Sector Readiness

| sector | source operator | readiness | comparison |
| --- | --- | --- | --- |
| charged lepton | `charged K_l` | `RG_TRANSPORT_PENDING` | not ready |
| up | `charged K_u` with up `(6,0)` `ln 2` | `RG_TRANSPORT_PENDING` | not ready |
| down | `charged K_d` | `RG_TRANSPORT_PENDING` | not ready |
| neutral | symbolic `K_nu` | `RG_TRANSPORT_PENDING` | not ready |

## Statuses

```text
RG_transport_interface_v1=STRUCTURAL_SCAFFOLD
charged_RG_transport=OPEN_LOCALIZABLE
neutral_RG_transport=OPEN_LOCALIZABLE
scheme_transport=OPEN
common_scale_comparison=OPEN
comparison_ready_predictions=OPEN
numerical_closure=OPEN
```

Frozen predictions changed: no.

Official predictions changed: no.
