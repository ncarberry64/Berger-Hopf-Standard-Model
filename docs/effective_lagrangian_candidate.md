# BHSM Effective Lagrangian Candidate Ledger v0.3

The Phase Three-A candidate ledger is:

```text
artifacts/BHSM_effective_lagrangian_candidate_v0_3.json
```

It is a term ledger, not a production FeynRules model. Each entry records a
candidate density expression, source artifacts, coefficient symbols and values
where they already exist, and the blockers that prevent production export.

| term | sector | status | UFO status |
| --- | --- | --- | --- |
| `profile_scale_term` | profile scale | `STRUCTURAL_CANDIDATE` | `BLOCKED` |
| `charged_boundary_response_term` | charged | `STRUCTURAL_CANDIDATE` | `BLOCKED` |
| `neutral_operator_term` | neutral | `STRUCTURAL_CANDIDATE` | `BLOCKED` |
| `ckm_mixing_term` | CKM | `SYMBOLIC_PLACEHOLDER` | `BLOCKED` |
| `pmns_mixing_term` | PMNS | `SYMBOLIC_PLACEHOLDER` | `BLOCKED` |
| `cp_holonomy_term` | CP | `SYMBOLIC_PLACEHOLDER` | `BLOCKED` |
| `boundary_transport_term` | transport | `DERIVED_FROM_REPO_ARTIFACT` | `BLOCKED` |

No term is marked production UFO-ready. The ledger intentionally leaves
production Feynman rules blocked until 4D Lorentz/gauge structure and
normalization are supplied.
