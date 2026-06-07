# BHSM v1.3H Twisted Dirac Index Audit

Index status: `INDEX_SCAFFOLD`
Full theorem status: `OPEN`
Theorem complete: `False`

## Index Summary

| Quantity | Value |
| --- | --- |
| Finite scaffold index | `3` |
| Boundary-functional index | `3` |
| Topological index assumption | `3` |
| Target index | `3` |
| Target kernel dimension | `3` |

## Diagonal Bound Summary

| Quantity | Value |
| --- | --- |
| Required Dirac lower bound | `0.8038064161349437` |
| Finite diagonal complement lower bound | `1.4641` |
| Margin | `0.6602935838650562` |
| Passes | `True` |
| First complement mode | `index=18, sector=up, k=0, j=0, q=0, chi=-1` |

## Mirror Summary

Open mirror risk count: `3`

## Limitations

- Finite scaffold index and boundary-functional index are not a full topological index theorem.
- Mirror-mode exclusion remains open in the complete twisted Dirac operator.
- The diagonal complement bound is finite-scaffold evidence, not an infinite-basis theorem.

## v1.3I Mirror-Exclusion Derivation Update

The generated opposite-chirality mirror candidates are excluded by the
model-internal weak chiral projector channel:

| Mirror | Channel | Final |
| --- | --- | --- |
| `mirror_lepton` | `EXCLUDED_BY_CHIRAL_PROJECTOR` | `EXCLUDED` |
| `mirror_up` | `EXCLUDED_BY_CHIRAL_PROJECTOR` | `EXCLUDED` |
| `mirror_down` | `EXCLUDED_BY_CHIRAL_PROJECTOR` | `EXCLUDED` |

The scaffold index remains `3` and `theorem_complete` remains `False`.
The full theorem still requires the topological index theorem and
infinite-basis complement bound.
