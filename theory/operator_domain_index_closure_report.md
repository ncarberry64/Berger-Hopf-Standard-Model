# BHSM v1.7 Operator-Domain and Index Closure Report

Domain status: `SELF_ADJOINT_DOMAIN_OPEN`
Relative-bound status: `RELATIVE_BOUND_CONDITIONAL`
Index status: `INDEX_THEOREM_CONDITIONAL`
Mirror status: `MIRROR_EXCLUSION_CONDITIONAL`
H_T dependency status: `HT_THEOREM_BLOCKED_BY_DOMAIN`
Theorem complete: `False`
Frozen outputs changed: `False`

## Corrected Formal Kernel

- `|ell,0,0,q=0,chi=-1>`
- `|u,0,0,q=0,chi=-1>`
- `|d,0,0,q=0,chi=-1>`

Rejected coordinate-first kernel: `(0, 1, 2)`

## Relative-Bound Audit

| Term | a | b | Below 1 | Scope | Infinite-basis compatible | Open obligations |
| --- | --- | --- | --- | --- | --- | --- |
| `D_diag_squared` | `0.0` | `0.0` | `True` | definition of base operator | `True` | none |
| `V_Hopf` | `0.0` | `0.0` | `True` | finite/scaffold boundedness | `False` | prove infinite-basis Hopf twist relative boundedness |
| `V_boundary` | `0.0` | `0.0` | `True` | finite/scaffold boundedness | `False` | prove complete boundary functional relative boundedness |
| `V_chi` | `0.0` | `0.0` | `True` | projector scaffold | `False` | prove chirality projector preserves the full operator domain |
| `K_sector` | `0.015621013485509948` | `0.0` | `True` | uniform scan and structured relative-bound candidate through k_max=32 | `False` | upgrade uniform scan to an infinite-basis sector-coupling theorem |
| `P_perp_lift` | `0.0` | `0.0` | `True` | PSD monotone lift | `False` | prove full formal-kernel complement projector and domain stability |
| `PSD_profile` | `0.0` | `0.0` | `True` | PSD construction | `True` | none |

## Index and Mirror Summary

- Scaffold index: `3`
- Target index: `3`
- Chiral channel excludes generated mirrors: `True`
- Higgs-U1 channel closed: `False`
- Boundary-functional channel closed: `False`

## Open Obligations

- prove density and core stability in the complete Hilbert space
- derive the complete Berger twisted Dirac spectral domain
- prove self-adjointness via Kato-Rellich or equivalent relative-bound conditions in the complete operator
- prove the formal kernel/complement split for the complete Hilbert-space operator
- prove infinite-basis Hopf twist relative boundedness
- prove complete boundary functional relative boundedness
- prove chirality projector preserves the full operator domain
- upgrade uniform scan to an infinite-basis sector-coupling theorem
- prove full formal-kernel complement projector and domain stability
- derive the index density/topological charge formula for the complete twisted Dirac operator
- prove no additional hidden protected kernel states exist in the complete Hilbert space
- prove the formal-kernel/complement split independently of finite truncation
- The chiral projector excludes scaffold mirror candidates by internal chirality data.
- The complete operator must still prove no opposite-chirality kernel survives outside this channel.
- derive a chirality-resolved Higgs-selected U1 mirror phase mismatch in the complete operator
- derive v1.2 boundary-functional mirror exclusion from the full kernel boundary problem
- prove no mirror state in H_perp lies below the H_T threshold in the complete operator
- connect mirror exclusion to the full topological index theorem

## Limitations

- v1.7 strengthens the dependency audit but does not close the full domain/index/mirror theorem chain.
- The old coordinate-first kernel (0,1,2) is rejected for corrected formal-kernel reports.
- No frozen predictions, constants, mode ledgers, tolerances, or prior scaffold outputs are changed.
