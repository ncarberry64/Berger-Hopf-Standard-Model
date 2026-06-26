# FeynRules Export Blocker Table

Machine-readable artifact:

```text
artifacts/BHSM_feynrules_export_blocker_table_v0_9.json
```

Tracked blockers:

- `complete_particle_table`
- `complete_parameter_card`
- `mass_width_scheme`
- `renormalization_scheme`
- `gauge_fixing_scheme`
- `production_coupling_scheme`
- `complete_vertex_table`
- `neutrino_basis_and_scale`
- `X_ch_interaction_operator`
- `CP_interaction_attachment`
- `FeynRules_syntax_export`
- `UFO_loadability_test`
- `MadGraph_smoke_test`

Each blocker remains explicit. The blocker table is a readiness audit, not a
production FeynRules export.

## Phase Three-H Follow-On

Phase Three-H reduces `X_ch`, neutrino basis/scale, and CP holonomy attachment
to bounded partial resolutions or exact missing theorems. The FeynRules export
blocker table remains active.

## Phase Three-I Follow-On

Phase Three-I preserves the FeynRules blocker table as active. It records
`X_ch`, neutrino basis/scale/Dirac-Majorana convention, and standalone CP
`O_int` as exact missing theorem objects for their standalone vertex families.
