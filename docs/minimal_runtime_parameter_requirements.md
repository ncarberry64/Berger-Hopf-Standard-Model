# Minimal Runtime Parameter Requirements

Machine-readable artifact:

```text
artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json
```

Required runtime or source items:

- `g2_BH_runtime`
- `W_mass_runtime`
- `W_width_runtime`
- `fermion_masses_runtime`
- `fermion_widths_runtime`
- `neutrino_runtime_convention_for_PMNS_labels`
- `renormalization_scale_runtime`
- `CKM_BH_source_matrix`
- `PMNS_BH_source_matrix`

The CKM and PMNS matrices are BHSM source artifacts, not runtime empirical
inputs. Couplings, masses, widths, neutrino label conventions, and
renormalization scale are collider-interface runtime requirements only.

No numerical PDG values or numerical mass/width constants are inserted.
