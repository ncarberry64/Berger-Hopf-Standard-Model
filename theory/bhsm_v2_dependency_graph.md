# BHSM v2.0 Integrated Dependency Graph

Theorem complete: `False`
Hidden circularity detected: `False`
Empirical residual dependency detected: `False`

## Nodes

| Node | Status | Depends on |
| --- | --- | --- |
| `alpha_geometry` | `FROZEN_PREDICTION` | `()` |
| `overlap_width` | `FROZEN_PREDICTION` | `()` |
| `mode_ledger` | `FROZEN_PREDICTION` | `('omega_f',)` |
| `omega_f` | `BOUNDARY_FUNCTIONAL_DERIVED` | `('parent_action_scaffold',)` |
| `parent_action_scaffold` | `PARENT_ACTION_REDUCED` | `()` |
| `formal_kernel` | `BASIS_REALIZED` | `('omega_f', 'state_ontology')` |
| `ht_gap` | `SEMI_ANALYTIC_SCAFFOLD` | `('formal_kernel', 'scalar_decoupling')` |
| `scalar_decoupling` | `FINITE_BASIS_SCAFFOLD` | `('state_ontology',)` |
| `virtual_dressing` | `ADOPTION_CANDIDATE` | `('state_ontology',)` |
| `qcd_rg_matching` | `OPEN` | `()` |
| `ckm_cp` | `FROZEN_PREDICTION` | `('mode_ledger', 'alpha_geometry', 'overlap_width')` |
| `pmns_effective` | `FROZEN_PREDICTION` | `('alpha_geometry',)` |
| `state_ontology` | `FINITE_BASIS_SCAFFOLD` | `()` |
| `forbidden_extra_light` | `FORBIDDEN` | `('ht_gap', 'scalar_decoupling')` |

## Edges

| Source | Target | Relation |
| --- | --- | --- |
| `omega_f` | `mode_ledger` | `supports` |
| `parent_action_scaffold` | `omega_f` | `supports` |
| `omega_f` | `formal_kernel` | `supports` |
| `state_ontology` | `formal_kernel` | `supports` |
| `formal_kernel` | `ht_gap` | `supports` |
| `scalar_decoupling` | `ht_gap` | `supports` |
| `state_ontology` | `scalar_decoupling` | `supports` |
| `state_ontology` | `virtual_dressing` | `supports` |
| `mode_ledger` | `ckm_cp` | `supports` |
| `alpha_geometry` | `ckm_cp` | `supports` |
| `overlap_width` | `ckm_cp` | `supports` |
| `alpha_geometry` | `pmns_effective` | `supports` |
| `ht_gap` | `forbidden_extra_light` | `supports` |
| `scalar_decoupling` | `forbidden_extra_light` | `supports` |

## Smallest Remaining Open Obligations

1. Prove the full twisted Dirac / H_T spectrum and infinite-basis complement bound.
2. Prove Index(D_twist)=3 and complete mirror-mode exclusion from the full operator.
3. Prove scalar/topographic decoupling from the full internal action.
4. Complete precision QCD/RG threshold matching for quark mass comparisons.
5. Derive full flavor matrices from the complete action rather than internal-rule screens.

## Limitations

- This graph is a theorem/status ledger, not a completed derivation.
- Frozen predictions remain frozen and are not selected by graph residuals.

## v1.4 Precision QCD/RG Update

The `qcd_rg_matching` node remains `OPEN`. Branch
`bhsm-v1.4-precision-qcd-rg` adds precision-oriented reference-set metadata,
threshold-aware scaffold rows, and uncertainty propagation scaffolds. It does
not close the precision QCD/RG proof obligation.
