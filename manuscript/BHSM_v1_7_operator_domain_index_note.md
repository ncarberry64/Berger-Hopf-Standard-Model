# BHSM v1.7 Operator-Domain and Index Theorem Note

Branch: `bhsm-v1.7-operator-domain-index`

## Purpose

BHSM v1.7 attacks the upstream theorem chain feeding the full `H_T` no-extra-light-state theorem:

```text
D(D_FK) -> self-adjointness -> dim ker D_twist = 3 -> mirror exclusion -> H_T complement theorem
```

It does not alter the frozen BHSM prediction package, the alpha-anchored geometry, the overlap width, the frozen mode ledger, tolerance bands, the v1.2 action-origin outputs, the corrected v1.3 formal-kernel scaffold, QCD/RG scaffolds, scalar scaffolds, or the virtual dressing rule.

## Corrected Formal Kernel

The corrected formal kernel remains sector-labeled:

```text
K_formal = span{
  |ell,0,0,q=0,chi=-1>,
  |u,0,0,q=0,chi=-1>,
  |d,0,0,q=0,chi=-1>
}
```

The coordinate-first kernel `(0,1,2)` remains rejected for corrected formal-kernel reports.

## v1.7 Status

| Chain Element | Status |
| --- | --- |
| Full operator domain | `SELF_ADJOINT_DOMAIN_OPEN` |
| Relative-bound audit | `RELATIVE_BOUND_CONDITIONAL` |
| Topological index | `INDEX_THEOREM_OPEN` |
| Mirror exclusion | `MIRROR_EXCLUSION_OPEN` |
| H_T dependency | `HT_THEOREM_BLOCKED_BY_DOMAIN` |

## Relative-Bound Result

The current scaffold keeps all listed relative-a estimates below one. The sector-coupling row inherits the structured value:

```text
a_K = 0.015621013485509948, b_K = 0
```

This is a strong conditional relative-bound audit, but not a full Kato-Rellich proof for the complete infinite-basis operator. Hopf, boundary, chirality, sector-coupling, heat-lift, and complement-projector domain preservation still require complete-operator proofs.

## Index and Mirror Result

The scaffold index remains `3`, with one protected formal state in each charged sector. However, the full topological index theorem is still open.

The chiral projector channel excludes generated mirror candidates in the scaffold, but the Higgs-selected `U(1)` mirror channel and boundary-functional mirror channel remain open in the complete operator. Therefore full mirror exclusion is not proven.

## H_T Consequence

The corrected formal-kernel `H_T` scaffold remains strong, but v1.7 classifies the full theorem dependency as:

```text
HT_THEOREM_BLOCKED_BY_DOMAIN
```

This branch does not prove the full `H_T` theorem. It clarifies that the operator-domain/self-adjointness proof must close before the index and mirror results can honestly upgrade the full theorem.

## Limitation

BHSM v1.7 strengthens the theorem dependency audit, but it does not prove the complete operator-domain/index/mirror chain. Final paper preparation remains blocked until the full theorem package is complete.

