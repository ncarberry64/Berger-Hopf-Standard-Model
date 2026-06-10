# BHSM v2.15 Projector Graph-Domain Stability Note

BHSM v2.15 closes the projector graph-domain stability gap for the corrected
formal sector-labeled complement projector.  The result proves, inside the
current complete BHSM operator scaffold, that

```text
P_perp D(A0 + V) subset D(A0 + V)
```

where `A0 + V` is the complete BHSM operator package fixed by the v2.13
complete-operator action-uniqueness result and the v2.14 projector commutator
control result.

The proof route is:

1. define `D(A0)`, `D(V)`, `D(A0+V)`, and the corresponding graph norms;
2. use the complete-operator identification/action-uniqueness package and the
   relative-bound estimate `a < 1` to identify `D(A0+V)=D(A0)`;
3. apply v2.14 commutator control termwise;
4. prove graph-norm boundedness of `P_perp` on `D(A0+V)`.

The formal protected kernel remains the sector-labeled lepton/up/down kernel
with finite coordinates `(0,18,36)`.  The old coordinate-first kernel `(0,1,2)`
is not used.

## Termwise Domain Stability

| Term | Domain-stability classification |
| --- | --- |
| `D_diag^2` | `DOMAIN_STABLE_EXACTLY` |
| `V_Hopf` | `DOMAIN_STABLE_BY_COMMUTATOR_CONTROL` |
| `V_boundary` | `DOMAIN_STABLE_BY_COMMUTATOR_CONTROL` |
| `V_chi` | `DOMAIN_STABLE_BY_COMMUTATOR_CONTROL` |
| `K_sector` | `DOMAIN_STABLE_BY_RELATIVE_BOUND` |
| `P_perp_lift` | `DOMAIN_STABLE_EXACTLY` |
| `V_PSD` | `DOMAIN_STABLE_BY_GRAPH_NORM_EQUIVALENCE` |
| `topographic_represented_sector` | `DOMAIN_STABLE_BY_LIFT_SCREENING` |
| `complete_operator_curvature_topographic` | `DOMAIN_STABLE_BY_LIFT_SCREENING` |

## Decision

Final v2.15 result:

```text
PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED
```

Graph-domain theorem status:

```text
PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
```

The full `H_T` theorem is not proven.  The next named theorem gap is:

```text
HT_LOWER_BOUND_TRANSFER_GAP
```

Final paper preparation remains blocked.

## Limitations

This branch closes projector graph-domain stability only.  It does not prove
the full lower-bound transfer, the topological index theorem, or mirror
exclusion.  It does not alter frozen BHSM predictions, canonical constants,
frozen modes, tolerances, or virtual dressing.
