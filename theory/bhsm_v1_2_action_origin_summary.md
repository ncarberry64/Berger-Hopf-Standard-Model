# BHSM v1.2 Action-Origin Development Summary

Branch: `bhsm-v1.2-action-origin`

## Main Result

The charged-sector boundary operators are derived from an explicit symbolic sector boundary functional, and that functional is reduced from a symbolic parent internal-action scaffold. Minimality and tested-variant uniqueness audits find the scaffold unique under current BHSM axioms.

## Boundary Operators

```text
Omega_ell = -q + 2j = 3
Omega_u = q - 2j = 6
Omega_d = q + 4j = 12
```

## Status

- Parent-action reduction status: `REDUCED_FROM_PARENT_ACTION`.
- Minimality status: `MINIMAL_UNDER_TESTED_PARENT_TERMS`.
- Uniqueness status: `UNIQUE_UNDER_BHSM_AXIOMS`.
- Theorem complete: `False`.

## Minimality Table

| Term | Required for | Passes |
| --- | --- | --- |
| `I_HOPF` | fiber_q opens | `True` |
| `I_U1` | fiber_q opens | `True` |
| `I_BASE` | base_j opens | `True` |
| `I_WEAK` | base_j opens | `True` |
| `I_COF` | base_j opens | `True` |
| `I_BDY` | target opens | `True` |

## Uniqueness Variant Table

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

## Limitations

- Does not prove global uniqueness of the complete Berger-Hopf internal action.
- Does not compute the full twisted Dirac/bundle spectrum.
- Does not alter frozen v1.0/v1.1 predictions.
- Does not retune any mass or CKM output.

## Correct Claim

BHSM v1.2C audits whether the parent-action scaffold is minimal and unique under the current BHSM axioms. It does not claim full uniqueness of the complete internal action unless competing variants are excluded by explicit tests.
