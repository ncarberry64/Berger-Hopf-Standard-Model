# BHSM FeynRules Export Blockers v0.2

The FeynRules/UFO export path remains blocked by the following missing objects:

- complete 4D collider-ready Lagrangian;
- gauge-fixed Lagrangian;
- field normalization;
- Lorentz structures;
- complete vertex table;
- mass/width scheme;
- renormalization scheme;
- UFO directory;
- MadGraph validation;
- pinned PDG target table for validation.

Machine-readable blocker keys:

```text
complete_4d_lagrangian_missing
gauge_fixed_lagrangian_missing
field_normalization_missing
lorentz_structures_missing
complete_vertex_table_missing
mass_width_scheme_missing
renormalization_scheme_missing
ufo_directory_missing
madgraph_validation_missing
pdg_target_table_missing
```

Current artifact:

```text
artifacts/BHSM_feynrules_export_blockers_v0_2.json
```

These blockers prevent a loadable UFO model and any LHE/HepMC event generation.
