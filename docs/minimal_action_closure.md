# BHSM Minimal Action Closure

The v0.8 evaluator tests the local candidate

```text
S_BHSM,min = S_boundary + S_sector + S_phase + S_charged + S_neutral
```

against the action-level proof gates for the three remaining interface
theorems. It reads repository artifacts only.

| Theorem | Result | First missing object |
| --- | --- | --- |
| CP `O_int` | `OPEN_MISSING_ACTION_SOURCE` | Action-derived source with normalized coupling, measure, variation, and production rule |
| `X_ch` | `OPEN_MISSING_FIELD_REPRESENTATION` | Action-derived `X_ch` field representation |
| Neutrino basis/scale | `OPEN_MISSING_PHYSICAL_BASIS` | Map from neutral boundary channels to physical neutrino states |

No theorem is promoted. The disabled author-axiom template records the exact
inputs that could produce a conditional theorem without silently assuming
them. Runtime gates and frozen predictions are unchanged.

```bash
python -m bhsm.interface minimal-action-status
python -m bhsm.interface minimal-action-report --format markdown
```
