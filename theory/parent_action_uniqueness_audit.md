# BHSM v1.2C Parent-Action Uniqueness Audit

Status: `UNIQUE_UNDER_BHSM_AXIOMS`
Theorem complete: `False`

| Variant | Status | Recovers ledger | Would change frozen outputs if adopted |
| --- | --- | --- | --- |
| `flip_hopf_orientation` | `FAILS_SM_LEDGER` | `False` | `True` |
| `flip_weak_chirality` | `FAILS_SM_LEDGER` | `False` | `True` |
| `remove_coframe_triplet` | `FAILS_SM_LEDGER` | `False` | `True` |
| `coframe_singlet` | `FAILS_SM_LEDGER` | `False` | `True` |
| `shift_boundary_winding` | `FAILS_SM_LEDGER` | `False` | `True` |
| `swap_weak_component_sign` | `FAILS_SM_LEDGER` | `False` | `True` |
| `trace_u1_dynamical` | `FAILS_SM_LEDGER` | `False` | `True` |
| `disable_higgs_u1` | `FAILS_SM_LEDGER` | `False` | `True` |

## Claim Boundary

BHSM v1.2C audits whether the parent-action scaffold is minimal and unique under the current BHSM axioms. It does not claim full uniqueness of the complete internal action unless competing variants are excluded by explicit tests.

## Limitations

- Uniqueness is only under the current BHSM axioms and tested nearby variants.
- This does not prove global uniqueness of the complete internal action.
