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
