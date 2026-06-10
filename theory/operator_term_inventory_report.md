# BHSM v2.7 Complete Operator Term Inventory Report

Status: `OPERATOR_TERM_INVENTORY_BLOCKED`
Theorem complete: `False`
All terms classified: `True`

| Term | Required | Represented by | Classification | Limitation |
| --- | --- | --- | --- | --- |
| `berger_diagonal_kinetic` | `True` | `A0 = D_diag^2` | `DERIVED_AND_INCLUDED` | Does not by itself identify all twisted/bundle perturbations. |
| `hopf_fiber_twist` | `True` | `V_Hopf` | `DERIVED_AND_INCLUDED` | Complete-action derivation is inherited from scaffold terms. |
| `boundary_functional` | `True` | `V_boundary` | `DERIVED_AND_INCLUDED` | Global boundary problem remains linked to complete-operator proof. |
| `chirality_projector` | `True` | `V_chi` | `DERIVED_AND_INCLUDED` | Mirror exclusion remains a separate theorem dependency. |
| `sector_coupling` | `True` | `K_sector` | `REPRESENTED_BY_EXISTING_TERM` | Complete operator source for the coupling is still tied to action-scaffold assumptions. |
| `formal_kernel_complement_lift` | `True` | `P_perp_lift` | `DERIVED_AND_INCLUDED` | Projector graph-domain stability remains conditional downstream. |
| `heat_lift` | `True` | `P_perp_lift` | `DERIVED_AND_INCLUDED` | Exact heat-kernel construction is represented at scaffold level. |
| `psd_profile` | `True` | `V_PSD` | `REPRESENTED_BY_EXISTING_TERM` | Full scalar action proof remains separate from H_T operator identification. |
| `higgs_u1_connection` | `True` | `V_boundary + V_Hopf` | `REPRESENTED_BY_EXISTING_TERM` | Standalone complete mirror channel remains conditional. |
| `trace_u1_nondynamical` | `True` | `excluded from dynamical H_T` | `FORBIDDEN_BY_AXIOM` | Requires retention of the topological/nondynamical axiom. |
| `scalar_topographic_leakage` | `True` | `V_PSD or screened/lifted scalar sector` | `DERIVED_SCREENED_OR_LIFTED` | Full scalar action theorem is not part of this v2.6 operator proof. |
| `mirror_channel_terms` | `True` | `chiral/Higgs-U1/boundary channels` | `REPRESENTED_BY_EXISTING_TERM` | Full mirror theorem remains conditional. |
| `lichnerowicz_bundle_curvature_remainder` | `True` | `not represented by a proven existing term` | `OPEN` | Single missing complete-operator identification theorem gap remains: BUNDLE_CURVATURE_REMAINDER_FORMULA_AND_BOUND_GAP. |

## Required Open or Missing Terms

- `lichnerowicz_bundle_curvature_remainder`

## Limitations

- Every listed term has an explicit classification.
- The Lichnerowicz/bundle-curvature remainder is not hidden; v2.7 keeps it open until a formula/bound theorem is supplied.
