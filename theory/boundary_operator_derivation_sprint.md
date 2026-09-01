# Boundary Operator Derivation Sprint

P0 blocker: `BOUNDARY_OPERATORS_NOT_ACTION_DERIVED`
Classification: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`
P0 boundary blocker closed: `False`

## Sprint Verdict

The operational formulas are structurally motivated and internally consistent with the supplied BHSM mode ledger, but this sprint did not find a non-fitted action, spectral, or boundary derivation that forces them. The blocker therefore remains open.

## Boundary Operators

| Sector | Equation | Selected modes | Charges | Target satisfied | Status |
| --- | --- | --- | --- | --- | --- |
| `lepton` | `Omega_lepton = -1 q + 2 j = 3` | `(5,2), (9,3)` | `1, 3` | `True` | `ACTION_LINKED` |
| `up` | `Omega_up = 1 q + -2 j = 6` | `(6,0), (10,1)` | `6, 8` | `True` | `ACTION_LINKED` |
| `down` | `Omega_down = 1 q + 4 j = 12` | `(6,3), (8,2)` | `0, 4` | `True` | `ACTION_LINKED` |

## Questions Answered

1. Are these formulas derived from a shared boundary principle?

A shared symbolic phase bookkeeping rule exists, but it is not an action/spectral/boundary derivation.

2. Are the coefficients forced by charge, chirality, Hopf fiber/base split, or sector embedding?

The coefficients are reproduced from assigned Hopf fiber, chirality, weak-component, and coframe factors. The repo does not show that those factors are forced by the complete BHSM action.

3. Are the targets consequences of the selected modes?

The targets equal family index times sector winding multipliers and are satisfied by the selected modes. This is not, by itself, an independent derivation of the targets.

4. Can the formulas be derived from an action variation, spectral condition, boundary condition, or representation constraint?

No non-fitted action variation, spectral condition, self-adjoint-domain condition, or boundary condition was found that forces all three formulas.

5. What additional structure would be required?

A complete internal action/bundle boundary functional, a variational or self-adjoint-domain argument that fixes the Hopf/base coefficients, a derivation of sector winding targets, and a spectral check that no competing boundary functional recovers the same ledger by post-hoc assignment.

## Impact On Other P0 Items

- Helps derive `Z_virt^{u,2}=1/2`: `False`
- Helps derive CKM exponent `1/16`: `False`

## Frozen Output Discipline

- Official frozen outputs changed: `False`
- Frozen sanity: `{'BHSM_BARE_V1_unchanged': True, 'BHSM_DRESSED_V1_CANDIDATE_unchanged': True, 'dressed_branch_changes_only_c_over_t': True, 'u_over_t_unchanged': True, 'ckm_sin_theta_13_unchanged': True, 'changed_rows': [{'quantity': 'c/t', 'bare': 0.008310500554068288, 'dressed': 0.004155250277034144, 'changed': True}]}`

## Sources Inspected

- `theory/boundary_operator_scaffold.md`
- `theory/boundary_operator_action_derivation.md`
- `theory/boundary_operator_completion_attempt.md`
- `theory/proof_gap_report.md`
- `theory/gate_ledger.md`
- `src/boundary_derivation.py`
- `src/mode_selection.py`
- `src/twisted_dirac.py`
- `tests/test_boundary_derivation.py`
- `tests/test_mode_selection.py`
- `tests/test_boundary_operator_closure.py`

## Limitations

- The sprint audits existing BHSM repository evidence only.
- It does not introduce a new internal action or new spectral theorem.
- It does not alter frozen prediction branches or mode ledgers.
- It does not derive Z_virt^{u,2}=1/2 or the CKM 1/16 mixing exponent.
