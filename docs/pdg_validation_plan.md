# BHSM PDG Validation Plan v0.1.0

BHSM v1.0.1 does not claim empirical validation. Validation plots require a
pinned external target table, such as a PDG-style reference table with source,
release, scheme, scale, uncertainty, and units.

The required template is:

```text
data/pdg_targets_template_v0_1.json
```

This template intentionally contains no numeric validation values. It is a schema
for future target data.

## Required Target Metadata

Each target row should include:

- `pdg_release`
- `source_reference`
- `quantity_name`
- `sector`
- `pdg_value`
- `pdg_uncertainty`
- `unit`
- `scheme`
- `scale`
- `bhsm_artifact`
- `bhsm_value`
- `comparison_status`
- `notes`

## Validation Rule

Validation comparisons must be one-way:

```text
released BHSM artifact -> external target comparison
```

External target values must not feed back into BHSM constants, modes, boundary
operators, thresholds, tolerances, or frozen prediction artifacts.

## Plot Generation

Use:

```powershell
python tools/generate_pdg_validation_plots.py --targets path/to/pdg_targets.json --output-dir outputs/pdg_validation
```

The tool exits cleanly when no real target rows are supplied. It must not
generate fake validation plots.

## Required Future Plots

Once real pinned targets are supplied, candidate plots include:

- BHSM versus PDG value with uncertainty bars;
- relative residual by sector;
- scheme/scale-labeled residual table;
- comparison-status summary.

Until pinned targets exist, all such plots remain not generated.
