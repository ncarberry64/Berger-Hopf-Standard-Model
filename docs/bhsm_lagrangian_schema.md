# BHSM Lagrangian Schema v0.1.0

The phase-one Lagrangian schema defines what a future collider-ready BHSM 4D
Lagrangian file must contain. It does not provide such a Lagrangian.

Schema file:

```text
schemas/bhsm_lagrangian_schema_v0_1.json
```

Template file:

```text
data/bhsm_lagrangian_template_v0_1.json
```

The template is marked:

```text
NOT_A_PHYSICAL_LAGRANGIAN
STRUCTURAL_TEMPLATE_ONLY
DO_NOT_USE_FOR_EVENT_GENERATION
```

## Required Fields

- `schema_version`
- `model_name`
- `release_basis`
- `lagrangian_status`
- `spacetime_dimension`
- `gauge_groups`
- `fields`
- `parameters`
- `terms`
- `normalization_conventions`
- `gauge_fixing_status`
- `renormalization_status`
- `source_artifacts`
- `empirical_derivation_inputs_used`
- `boundary_predictions_modified_by_comparison`
- `official_predictions_changed`

If no complete 4D collider-ready Lagrangian exists in the repository, validators
must report:

```text
complete_4d_lagrangian_exported = false
event_generation_ready = false
```

Phase Two-A does not change this status. It adds analytical source ledgers that
remain blocked until a real collider-ready Lagrangian is supplied.
