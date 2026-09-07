# Berger–Hopf Standard Model (BHSM)

[![Scientific CI](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/ci.yml/badge.svg)](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/ci.yml)
[![Institutional checks](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/institutional.yml/badge.svg)](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/institutional.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20663419.svg)](https://doi.org/10.5281/zenodo.20663419)

BHSM investigates whether Berger–Hopf internal geometry and a shared action
can organize particle families, mass hierarchies and interactions. Its
scientific ambition is to explain patterns that are otherwise entered as
separate quantities. Establishing that connection would be significant;
the complete physical derivation and experimental validation remain open.

This repository is the **academic record and reproducible research surface**.
The [BHSM Museum](https://ncarberry64.github.io/Berger-Hopf-Standard-Model/)
is the public-facing collection, with plain-language exhibits and visible
measurement, calculation, comparison and simulation labels. Its permanent
science exhibits cover decays/collisions, magnetic moments, SM predictions,
SM equivalence, force unification and spectral structure. Sandbox comparisons
are supplementary. The [Museum update contract](docs/MUSEUM_SCIENCE_UPDATE.md)
connects reviewed derived results to these same public exhibits.

## Start with your research question

| Audience or task | Entry point |
| --- | --- |
| University, laboratory, reviewer or teaching group | [Institutional start](docs/INSTITUTIONAL_START.md) — portable setup, offline checks and reporting |
| Evaluate the scientific proposal | [Claim boundaries](CLAIMS.md), [current status](docs/current_bhsm_status.md), [theory ledger](theory/gate_ledger.md) |
| Inspect particle-family and mass structure | [Charged-lepton action](theory/ae31_c2_intrinsic_m4_lepton_action.md), [quark normalization gap](theory/ae31_c2_quark_yukawa_normalization_no_go.md) |
| Inspect enclosure and interacting-state construction | [Existing-state integration](theory/ae4_current_c2_physical_enclosure_state_integration.md), [response integration](theory/ae4_event_response_jet_integration.md) |
| Examine the sandbox comparisons | [Complete source snapshot](docs/museum/sandbox_comparison_source_2026-09-02.md), [machine-readable values](data/museum/bhsm_sandbox_comparison_20260902.json) |
| Reuse an external-runtime adapter | [Integration guide](integrations/README.md), [CERN ROOT](integrations/cern-root/README.md) |

## Scientific structure and present limits

The retained historical mode screen uses the Berger scalar-spectrum proxy

```text
lambda(k,j;a) = a²(k−2j)² + 2((2j+1)k−2j²)
m_i/m_3 = exp(−lambda_i/(4π)).
```

This is a conditional geometric hierarchy screen. Mode selection, action
ownership, normalization and the physical observable map must each be
established; a numerical match alone is not a prediction. Later action and
domain constructions retain their own explicit authority and scope.

| Question | Current authority |
| --- | --- |
| Families and local enclosure | Existing family/mode fibers and the action-owned local carrier are reused; they are not rebuilt for each downstream calculation |
| Charged leptons | A family-noncentral Yukawa operator and conditional local mass shells exist; global dressed poles and the matched-parent energy readout remain open |
| Neutral and quark sectors | Existing response and ratio structures are retained; the physical neutral propagator/intertwiner and quark normalization maps remain open |
| Common interacting solution | Six-sector assembly and response handoffs exist; compatible physical block values and full event/Noether balance remain open |
| Gate 7 | `ACTIVE_NOT_CLOSED`: the frozen-center causal certification and two-radius proof remain on the established computation track |
| Full physical completion | `FULL_BHSM_COMPLETE = FALSE` |

The [canonical system map](artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json)
links the current dependencies. The merged full-field boundary research is
scoped to its retained action/domain; local assembly is not a substitute for
its missing physical reset and interface data.

## Portable first run

Use Python 3.12 for the institutional baseline; the core declares Python 3.10+.
No GPU, ROOT, commercial algebra system, cloud account or detector download is
required for this path.

```bash
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
python -m venv .venv
# POSIX: source .venv/bin/activate
# PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e .
python tools/institutional_check.py --smoke --json tmp/institutional-check.json
python -m bhsm.interface physics-status --format markdown
```

The check is offline after installation and bounded to a small test set. It
reports dependency versions, revision, frozen-file integrity and scientific
status; it starts no proof campaign. See [QUICKSTART.md](QUICKSTART.md) for
activation-free commands and [institutional setup](docs/INSTITUTIONAL_START.md)
for Conda, containers, Jupyter, clusters and offline environments.

## Reproducibility and comparison policy

Every scientific output must identify its action, domain, inputs, source
revision and claim class. Measured masses and mixing values must not select
an upstream branch, mode, coefficient, normalization or correction. Frozen
predictions remain unchanged. The sandbox snapshot is comparison-only and
its supplied reference markers are not independently verified measurements.

### Engine Validation Versus Physics Validation

Engine tests do not validate BHSM as particle physics. CERN Open Data tests verify coordinate transformations on real collision
four-vectors. They do not establish BHSM physics, detector reconstruction,
collider-production readiness or institutional endorsement. Computational
and research achievements are collected in one separate Museum exhibit.

## Repository map

| Path | Contents |
| --- | --- |
| `src/bhsm/interface/` | Scientific operators, conditional models and reporting interfaces |
| `theory/`, `docs/` | Derivations, authority boundaries, reviews and source provenance |
| `artifacts/` | Machine-readable evidence, certificates and open-gate records |
| `tests/`, `tools/` | Focused reproduction, integrity audits and institutional checks |
| `integrations/` | Optional ROOT, container and external-runtime adapters |
| `museum/` | Public exhibits; comparison data never feed the scientific solvers |

## Citation and permission

Norman P. Carberry · [ORCID](https://orcid.org/0009-0000-6650-3485).
Cite [CITATION.cff](CITATION.cff), the relevant artifact and the exact revision.
The archival DOI [10.5281/zenodo.20663419](https://doi.org/10.5281/zenodo.20663419)
identifies the recorded archive; it is not a claim that the current research
is complete.

[LICENSE.md](LICENSE.md) reserves commercial rights. The separate
[academic evaluation permission](ACADEMIC_USE.md) permits noncommercial
research, verification, review and teaching without an individual request.
Third-party assets retain their own licenses. This is not an open-source
license. Contributions and critiques follow [CONTRIBUTING.md](CONTRIBUTING.md).

<details>
<summary>Historical checkpoint compatibility</summary>

The v18.73 rolling checkpoint recorded corrected-Rayleigh descent of the
376-variable system, complete-child reconstruction, eta admissibility and
persistence at residual `0.777030406838571`. It is a historical result, not the
current frontier. The former README and its detailed chronology remain in Git
history. Frozen predictions and their hashes are preserved.

</details>
