# Institutional start

This is the entry path for independent physics groups, research software
teams, reviewers and teachers. Start with the scientific claims and the
bounded offline check before choosing a heavier runtime.

## Permission and scientific scope

The [academic evaluation permission](../ACADEMIC_USE.md) allows noncommercial
research, verification, review and teaching, including cluster execution and
private collaboration. Commercial use and broader redistribution require
separate permission. Dependencies and external datasets retain their licenses.
This restricted permission is not an open-source license.

The repository contains conditional models, mathematical results, historical
screens and software demonstrations. Passing tests is not empirical validation.
Gate 7 remains active and full physical completion is open. Begin with
[CLAIMS.md](../CLAIMS.md), the [current system map](../artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json)
and the [definition of done](BHSM_1_0_DEFINITION_OF_DONE.md).

## Choose an environment

| Environment | Supported entry path | Optional additions |
| --- | --- | --- |
| Linux / macOS | Python virtual environment, commands below | ROOT or native C++ adapters |
| Windows | PowerShell with the environment's Python executable | CMake/MSVC and separately installed ROOT |
| Conda / managed laboratory workstation | `conda env create -f environment.yml` | Institution-managed package mirrors |
| Docker / Podman | `integrations/institutional/Dockerfile` | Mounted output directory; no GPU needed |
| VS Code / Codespaces | `.devcontainer/devcontainer.json` | Uses the same institutional container |
| Jupyter | Install JupyterLab separately in the environment | Existing notebooks and JSON/NPZ artifacts |
| HPC / offline network | Prepare wheels on a compatible connected host | Scheduler allocation and optional exact arithmetic |

Python 3.12 is the common baseline. CI exercises core onboarding on Linux,
macOS and Windows; see the actual workflow result for the tested revision.
An optional runtime being unavailable must not prevent core review.

## First run without shell activation

Clone the repository or unpack a source snapshot that includes `src`, `tests`,
`tools`, `docs`, `theory` and `artifacts`. Work from its root. On POSIX:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python tools/institutional_check.py --smoke --json tmp/institutional-check.json
.venv/bin/python -m bhsm.interface physics-status --format markdown
```

On Windows PowerShell, activation-policy changes are unnecessary:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe tools/institutional_check.py --smoke --json tmp/institutional-check.json
.\.venv\Scripts\python.exe -m bhsm.interface physics-status --format markdown
```

Use an available Python 3.10+ executable instead of `py -3.12` when needed.
The readiness check returns exit code 0 on success and 1 on failure. Its JSON
records package versions, the revision when Git metadata exists, frozen-file
hashes and the scientific boundary. The smoke run has a 180-second timeout
and performs no network request, shard solve or expensive historical campaign.

## Optional profiles

```bash
python -m pip install -e ".[benchmark]"   # plots and existing display checks
python -m pip install -e ".[rigorous]"    # python-flint / Arb certificate work
python tools/institutional_check.py --profile rigorous --json tmp/rigorous-check.json
```

JAX acceleration, ROOT, FeynRules, Wolfram and MadGraph are separate opt-in
surfaces. They are not prerequisites for inspecting the evidence. Consult
[integrations](../integrations/README.md) and the existing
[HEP environment preflight](../scripts/setup/README.md) before a licensed or
institution-managed runtime. The environment is not a ready-made detector
simulation or a fully instantiated Standard Model event generator.

## Containers and clusters

```bash
docker build -f integrations/institutional/Dockerfile -t bhsm-review .
docker run --rm --network none bhsm-review
```

Podman accepts the same build and run arguments. Docker builds require package
access; the default container command runs offline. Its image includes source
and retained evidence, so it is larger than a minimal Python runtime. The
container definition is checked in; actual build support is reported by CI.

Large retained research inputs are individually listed with exact hashes in
`data/retained_large_research_artifacts.json`. The publication audit accepts
only those reviewed bytes; new or changed large files still require review.

On a scheduler, submit the bounded command first using one CPU and the
institution's normal Python environment. For reproducible BLAS behavior, the
institutional CI uses one thread for `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`
and `MKL_NUM_THREADS`. Do not start all historical tests or proof workers as an
installation check. Any expensive campaign needs its own resource estimate,
retained action/domain, frozen center and restart policy.

For an offline deployment, collect the source snapshot and wheels on a host
matching the target Python, operating system and architecture:

```bash
python -m pip download --dest wheelhouse numpy scipy sympy mpmath pytest setuptools wheel
python -m pip install --no-index --find-links wheelhouse numpy scipy sympy mpmath pytest setuptools wheel
python -m pip install --no-index --no-build-isolation --no-deps -e .
```

For strict repeatability, record `python -m pip freeze` from the validated
environment and resolve that exact list into the target wheelhouse. Optional
Arb/ROOT/HEP environments require their own platform-specific dependencies.

## Exchange results without duplicating the science

JSON carries claims, values and provenance; NPZ carries numerical arrays.
Python consumes both directly. ROOT users should use the existing adapter;
Julia, R and MATLAB users may read exported JSON/arrays while leaving the
scientific authority in the shared source. No independently maintained
cross-language physics implementation is promised.

An institutional reproduction should record:

1. Source commit or source-archive checksum and dependency versions.
2. Exact command, inputs, output hashes and relevant action/domain identifiers.
3. Numerical precision, platform and any deviation from the retained setup.
4. Whether the result is a historical screen, conditional theorem, software
   check, comparison or physically promoted prediction.
5. Failures and unresolved gates as well as successful outputs.

The [sandbox comparison](museum/sandbox_comparison_source_2026-09-02.md)
belongs only to the public comparison layer. It must not select upstream
physics. Critiques and failures are welcome through the repository's issue
templates. Include the readiness report with local paths or machine details
removed if your institution treats them as private.
