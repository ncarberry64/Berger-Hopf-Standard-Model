# BHSM v2.11 Mixed Coefficient Minimality Report

Minimality status: `MINIMALITY_AUDIT_PASSES_UNDER_BHSM_AXIOMS`
Uniqueness status: `UNIQUE_REPRESENTATION_RULE_UNDER_BHSM_AXIOMS`
Theorem complete: `True`

| Variant | Changed rule | Outcome | Status | Limitation |
| --- | --- | --- | --- | --- |
| `coefficient_zero` | set every mixed coefficient to zero | allowed only for Hopf/base vertical-horizontal compatibility, not as universal convenience | `VARIANT_INDETERMINATE_WITHOUT_COMPATIBILITY_AXIOM` | Represented slots must remain represented by existing sectors. |
| `sign_flipped` | flip mixed coefficient orientations | forbidden because no independent orientation coefficient is allowed | `VARIANT_FORBIDDEN_FREE_COEFFICIENT` | A sign flip would create a new free bundle-curvature parameter. |
| `hopf_base_disabled` | remove Hopf/base mixing | breaks the identified complete-connection slot | `VARIANT_FAILS_BHSM_AXIOMS` | The parent connection inventory includes this slot. |
| `boundary_coframe_disabled` | remove boundary/coframe mixing | loses the quark coframe compatibility channel | `VARIANT_FAILS_BHSM_AXIOMS` | The v1.2C coframe triplet channel remains required. |
| `coframe_singlet` | replace coframe triplet by singlet | fails the tested action-origin sector ledger | `VARIANT_FAILS_BHSM_AXIOMS` | This reopens the v1.2C uniqueness failure. |
| `chirality_blind` | remove chirality dependence | reopens mirror-channel risk | `VARIANT_OPEN_MIRROR_RISK` | Mirror exclusion cannot be preserved by a chirality-blind mixed rule. |
| `sector_blind` | remove lepton/up/down dependence | cannot distinguish the sector boundary functionals | `VARIANT_FAILS_BHSM_AXIOMS` | Sector labels are part of the formal kernel. |
| `mirror_allowing` | allow opposite-chirality mixed channel | conflicts with mirror exclusion scaffold | `VARIANT_OPEN_MIRROR_RISK` | No theorem allows this channel. |
| `independent_free_mixed_coefficient` | introduce a new fitted coefficient | violates bundle separation and topographic representation | `VARIANT_FORBIDDEN_FREE_COEFFICIENT` | This is explicitly forbidden by the v2.11 axiom. |

## Limitations

- The audit closes independent coefficient freedom under the BHSM axiom, but does not prove the full H_T theorem.
- Scalar/topographic, projector-domain, and lower-bound dependencies remain separate theorem obligations.
