# BHSM Vertex Source Target Map v0.5

Machine-readable artifact:

```text
artifacts/BHSM_vertex_source_target_map_v0_5.json
```

Mapped target families:

```text
q_charged_current_CKM_BH
lepton_charged_current_PMNS_BH
charged_boundary_response_matrix
neutral_operator_kernel_BH
cp_holonomy_phase_attachment
```

All targets remain source maps:

```text
feynrules_ready = false
ufo_ready = false
```

No production Feynman rules are exported.

Phase Three-D identifies CKM/PMNS chiral charged-current targets with standard
Lorentz structure conventions, while keeping `feynrules_ready = false` and
`ufo_ready = false`.

Phase Three-E keeps these current targets as candidate target maps and adds
scheme-conditional coupling ledgers. The vertex-source map remains
non-production and does not export a complete vertex table.
