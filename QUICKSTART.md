# BHSM Quickstart

Run these commands from the repository root. BHSM supports Python 3.10 or
newer.

## Install

```bash
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows PowerShell uses the same commands except for activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

`numpy`, `scipy`, `sympy`, and `pytest` are core dependencies. Plot and image
generation require the optional `benchmark` extra:

```bash
python -m pip install -e ".[benchmark]"
```

ROOT, native profiling tools, and CERN Open Data downloads are optional and
runtime-gated.

## Reviewer smoke

When GNU Make is available:

```bash
make reviewer-smoke
```

Portable Python equivalent:

```bash
python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py
```

Expected result: three passing tests. This smoke validates software invariants
and the engine/physics claim separation; it is not empirical validation of
BHSM physics.

## Interface and current status

```bash
python -m bhsm.interface --help
python -m bhsm.interface registry
python -m bhsm.interface physics-status --format markdown
```

The `status` subcommand requires a registry key. For example:

```bash
python -m bhsm.interface status W_boson
```

## Public-readiness and integrity checks

```bash
python tools/audit_public_readiness.py
python tools/audit_public_readiness.py --format json
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
python tools/verify_precision.py
```

All commands above are offline. They check current public files, claim
boundaries, repository status, frozen artifact hashes, and numerical
precision.

## Artifact and provenance review

```bash
python -m bhsm.interface gallery --format markdown
python -m bhsm.interface artifact-sources
python -m bhsm.interface formula-registry
python -m bhsm.interface compute-artifact CKM_matrix_BHSM
python -m bhsm.interface compute-artifact PMNS_matrix_BHSM
python -m bhsm.interface artifact-report --anchor W_boson --format json
python -m bhsm.interface cp-o-int-field-action --format json
python -m bhsm.interface theorem-blockers
```

These commands expose internal artifacts with provenance. Loading an artifact
does not upgrade its scientific status.

## Optional full and network workflows

The complete local suite is available with:

```bash
python -m pytest -q
```

The CERN Open Data path requires network access or a checksum-verified cached
sample:

```bash
python -m bhsm.interface.benchmarks.cern_open_data_benchmark --download --summary
```

That path validates coordinate transformations and numerical precision on
published collision-derived vectors. It is not detector reconstruction,
physics validation, or CERN/CMS endorsement.

See the [reviewer reproduction guide](docs/reviewer_reproduction_guide.md)
and [public scientific handoff](docs/bhsm_public_scientific_handoff_v6_21_0.md)
for the evidence model and current frontier.
