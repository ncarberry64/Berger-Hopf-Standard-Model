# Production Vertex Table Candidate

Machine-readable artifact:

```text
artifacts/BHSM_production_vertex_table_candidate_v0_9.json
```

Candidate vertex families:

- `q_charged_current_CKM_BH`
- `lepton_charged_current_PMNS_BH`
- `charged_boundary_response_matrix`
- `neutral_operator_kernel_BH`
- `cp_holonomy_phase_attachment`

The CKM and PMNS charged-current targets preserve BHSM-derived mixing sources
and standard target-current Lorentz structures. They remain blocked by
scheme, mass-width, renormalization, and runtime parameter requirements.

The charged boundary source preserves `C_ch_boundary` as a boundary-source
matrix only and remains blocked by the missing `X_ch` operator. The neutral
kernel preserves `K_nu` as a boundary-source matrix only and remains blocked by
the neutrino basis/scale convention. The CP holonomy term preserves
`delta_BH = pi/3` as a phase source only and remains blocked by missing
interaction attachment.

## Phase Three-H Follow-On

Phase Three-H partially promotes the CKM/PMNS charged-current target vertices
as bounded collider-interface targets. The charged boundary response remains
blocked by missing `X_ch`, the neutral kernel remains blocked by missing
neutrino basis/scale, and standalone CP holonomy remains blocked by missing
`O_int`.

## Phase Three-I Follow-On

Phase Three-I adds theorem-closure audits for `X_ch`, neutrino
Dirac-Majorana basis/scale, and standalone CP `O_int`. No new production
vertex is promoted to FeynRules-ready status. The production vertex table
remains incomplete until the charged boundary response, neutral kernel, and
standalone CP interaction theorems close.

## Phase Three-J Follow-On

Phase Three-J includes only `q_charged_current_CKM_BH` and
`lepton_charged_current_PMNS_BH` in a bounded collider-interface Lagrangian
subset. The other Phase Three-G vertex families remain excluded.
