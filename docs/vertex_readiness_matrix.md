# Vertex Readiness Matrix

Machine-readable artifact:

```text
artifacts/BHSM_vertex_readiness_matrix_v0_9.json
```

The readiness matrix summarizes which gates are satisfied per candidate vertex
family. The canonical production basis is ready, but coupling, mass-width,
renormalization, and several interaction/basis attachments remain open.

No vertex is marked FeynRules-ready, UFO-ready, or MadGraph-ready.

## Phase Three-H Follow-On

CKM/PMNS charged-current targets receive bounded collider-interface promotion.
Their FeynRules/UFO/MadGraph readiness remains false. Charged boundary,
neutral, and standalone CP vertices remain blocked.

## Phase Three-I Follow-On

The Phase Three-I theorem audit preserves the bounded CKM/PMNS
collider-interface targets but does not mark any new vertex FeynRules-ready.
`charged_boundary_response_matrix`, `neutral_operator_kernel_BH`, and
`cp_holonomy_phase_attachment` remain blocked by exact missing theorem
objects.

## Phase Three-J Follow-On

Phase Three-J marks CKM/PMNS charged-current families as included in the
minimal bounded subset and keeps production FeynRules/UFO readiness false.
The charged boundary response, neutral kernel, and standalone CP families are
excluded from the subset.
