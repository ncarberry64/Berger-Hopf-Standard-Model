# BHSM CLI reference

The current v6.5.0 topological matter-action/global-spectrum audit is
available with:

```powershell
python -m bhsm.interface topological-matter-global-spectrum-status --format json
python -m bhsm.interface topological-matter-global-spectrum-status --format markdown
python scripts/materialize_topological_matter_action_global_spectrum_v6_5_0.py
```

It reports which configuration-space, first-order source, dynamic
polarization, compact domain, global spectrum, transfer, scalar, neutral
phase, and absolute-scale statements are derived, conditional, rejected, or
still open.

The v6.3.0 constructive architecture is available offline in JSON or
Markdown:

```powershell
python -m bhsm.interface particle-chirality-anomaly-status --format json
python -m bhsm.interface particle-chirality-anomaly-status --format markdown
```

The v6.4.0 parent-action/polarization architecture remains available with:

```powershell
python -m bhsm.interface parent-action-polarization-stability-status --format json
python -m bhsm.interface parent-action-polarization-stability-status --format markdown
```

The command reports the conditional particle map, chiral collar result,
physical U(1), exact anomaly closure, connection traces, 1:2:7 rejection,
family mass operator, and symbolic absolute-scale map. It does not modify
artifacts or frozen predictions.

Deterministic v6.3.0 artifacts are regenerated with:

```powershell
python scripts/materialize_particle_chirality_anomaly_normalization_v6_3_0.py
```

Earlier constructive status commands remain available:

```powershell
python -m bhsm.interface scalar-wall-puiseux-fold-status --format markdown
python -m bhsm.interface triality-generation-scale-status --format markdown
```

For prediction-registry and artifact-adapter commands, see
[python_cli.md](python_cli.md) and
[artifact_backed_cli.md](artifact_backed_cli.md).

## v10.3 three-mode relational-envelopment audit

The historical v10.3 status is available without writing artifacts:

```powershell
python -m bhsm.interface three-mode-envelopment-status --format json
python -m bhsm.interface spacetime-removal-depth-v10-3-status --format json
python -m bhsm.interface three-mode-interference-status --format json
python -m bhsm.interface seam-projection-status --format json
python -m bhsm.interface global-scale-anchor-status --format json
python -m bhsm.interface generation-phase-interface-status --format json
```

The earlier `common-envelopment-mode-status`,
`deformation-intertwiner-status`, and `coupled-deformation-rank-status`
commands remain reproducible historical audits. Their one-mode hypothesis is
`INVALIDATED_BY_AUTHOR_ONTOLOGY` and is not the current architecture.

Regenerate every v10.3 artifact with:

```powershell
python scripts/materialize_physical_deformation_domain_v10_3.py
```

## v10.4 constrained spacetime-removal completion gate

```powershell
python -m bhsm.interface spacetime-removal-depth-status --format json
python -m bhsm.interface three-mode-action-status --format json
python -m bhsm.interface global-equilibrium-status --format json
python -m bhsm.interface cosmic-unit-anchor-status --format json
python -m bhsm.interface particle-cycle-status --format json
python -m bhsm.interface physical-mass-mixing-status --format json
python -m bhsm.interface final-completion-status --format json
python scripts/materialize_spacetime_removal_completion_v10_4.py
```

Every status command also accepts `--format markdown`. These commands report
the exact proper-volume constraint no-go, the unselected geometric-extension
decision, and null downstream physical outputs.
