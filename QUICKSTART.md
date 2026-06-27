# BHSM Quickstart

Run from the repository root with the project environment active.

```bash
python -m pytest -q
```

Runs the complete local test suite.

```bash
python -m bhsm.interface registry
```

Lists prediction, comparison, theorem-blocker, and runtime-gate entries.

```bash
python -m bhsm.interface status W_boson
```

Shows the W calibration-anchor policy.

```bash
python -m bhsm.interface gallery --format markdown
```

Builds the default claim-aware prediction gallery.

```bash
python -m bhsm.interface artifact-sources
```

Discovers local machine-readable evidence and provenance sources.

```bash
python -m bhsm.interface formula-registry
```

Lists artifact-backed callables, interface defaults, and open theorem entries.

```bash
python -m bhsm.interface compute-artifact CKM_matrix_BHSM
python -m bhsm.interface compute-artifact PMNS_matrix_BHSM
```

Loads the frozen CKM or PMNS artifact through the provenance adapter.

```bash
python -m bhsm.interface artifact-report --anchor W_boson --format json
```

Builds a provenance-aware report while preserving the calibration policy.

```bash
python -m bhsm.interface cp-o-int-field-action --format json
```

Reports the callable symbolic CP `O_int` candidate and its exact action gap.

```bash
python -m bhsm.interface theorem-blockers
```

Lists each open theorem and its smallest missing object.

All commands above run offline. Live PDG lookup and external HEP tool execution
are optional, separate workflows.

