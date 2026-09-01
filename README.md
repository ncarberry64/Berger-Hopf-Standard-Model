# Berger–Hopf Standard Model (BHSM)

[![BHSM core CI](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/ci.yml/badge.svg)](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/ci.yml)
[![Museum Pages](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/museum-pages.yml/badge.svg)](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/museum-pages.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20663419.svg)](https://doi.org/10.5281/zenodo.20663419)

**One Action · One Scale · One Observable Pipeline**

BHSM is an independent, artifact-backed mathematical-physics research program.
It investigates whether Berger–Hopf geometry can support a reproducible path
from a parent action to particle-physics calculations. It is not presented as
an empirically established theory, a completed Standard Model replacement, or
an institutionally endorsed project.

## Start here

- [Visit the animated BHSM Museum](https://ncarberry64.github.io/Berger-Hopf-Standard-Model/) — the visual, lay-accessible entrance.
- [Read the current scientific status](docs/current_bhsm_status.md) — the canonical human-readable boundary.
- [Inspect the machine status](docs/current_bhsm_status.json) — exact flags and promotion dependency.
- [Use the five-minute reviewer path](docs/reviewer_start_here.md) — assumptions, evidence, tests, and critique route.
- [Reproduce the public interfaces](QUICKSTART.md) — install, run, test, and audit.

These animations live outside it—the scientific README—so this page stays concise;
every museum display links back to its detailed record.

## Current research status

Gate 7 is **OPEN** at the action-owned covariant localization/domain-carrier
and full-field attachment frontier.

```text
UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND = FALSE
PHYSICAL_ENCAPSULATION_IDENTIFIED = FALSE
FULL_BHSM_COMPLETE = FALSE
```

The retained record includes a certified branch-24 first-stop event in the
reduced action state space, a continuum event-child certificate, fermionic
reset-trace matching, and a tensor-factor intertwiner. These are mathematical
or implemented results at their stated scope. They do **not** yet identify a
covariant spacetime enclosure or attach the complete gauge, ghost, fermion, and
scalar/HS field blocks with the required cross-derivatives.

The exact promotion dependency is an action-owned covariant localization and
domain carrier, together with same-action full-field attachment and the
derivatives needed to transport the certified reduced event into a physical
encapsulation. Until then, observable machinery is infrastructure, not a BHSM
physical prediction.

[Full boundary, established results, invalidations, and exact next object →](docs/current_bhsm_status.md)

## How to read claims

| Label | Meaning |
| --- | --- |
| Implemented machinery | Code, interfaces, tests, or artifacts exist. This does not by itself establish physical truth. |
| Numerically demonstrated | A computation exhibits behavior at a stated resolution, interval, dataset, or provisional scope. |
| Physical prediction | A physical readout is frozen behind the no-fit firewall with every required ownership and promotion gate closed. |
| Engine validation | Software-coordinate or invariant behavior was checked; the physics was not thereby validated. |
| Physics validation | Empirical support for BHSM as physics. This is **not** claimed by the repository. |

[Complete public terminology →](docs/public_terminology.md)

## Engine Validation Versus Physics Validation

The CMS Open Data exhibit uses checksum-pinned dimuon four-vectors to validate
coordinate transformations and engine behavior. Engine coordinate-transformation validation only: the benchmark covers 100,000 events and 200,000 unique muon four-vectors from CERN Open Data Record 303 (DOI `10.7483/OPENDATA.CMS.4M97.3SQ9`). Engine tests do not validate
BHSM as particle physics. The exhibit performs no detector reconstruction,
makes no BHSM empirical claim, and implies no CERN or CMS endorsement.

- [CERN Open Data Record 303](https://opendata.cern.ch/record/303)
- [Validation description](docs/pr98_cms_open_data_animation.md)
- [Pinned sample manifest](docs/assets/pr98_cms_open_data_animation/pr98_cms_sample_manifest.json)
- [Authoritative benchmark result](artifacts/cern_open_data_benchmark/results.json)
- [Benchmark tests](tests/test_cern_open_data_benchmark.py)

## Reproduce and inspect

```bash
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
python -m venv .venv
python -m pip install -e .
python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py
python tools/audit_public_surfaces.py
python -m bhsm.interface physics-status --format markdown
```

The primary implementation is Python. JSON/NPZ artifacts carry numerical and
machine-readable evidence; Markdown/LaTeX carry derivations and review notes;
the TypeScript museum is a presentation layer. Optional C++/ROOT and symbolic
adapter surfaces remain runtime-gated and do not imply collider readiness.

## Scientific record

- [Claim-to-evidence matrix](docs/BHSM_1_0_CLAIM_TO_EVIDENCE_MATRIX.md)
- [Current full-field action attachment](theory/bhsm_current_full_field_action_attachment.md)
- [Artifact index](ARTIFACT_INDEX.md)
- [Frozen prediction policy](docs/frozen_predictions.md)
- [Falsification routes](FALSIFICATION.md)
- [Contribution and critique process](CONTRIBUTING.md)
- [Repository size audit](docs/repository_size_audit_2026_09_01.md)
- [Superseded status archive](docs/archive/status/README.md)

## Creator and citation

BHSM is the work of **Norman P. Carberry**, Independent Researcher,
Oconomowoc, Wisconsin, USA. The repository presents the work for inspection,
reproduction, and explicit scientific criticism.

- [ORCID](https://orcid.org/0009-0000-6650-3485)
- [Citation metadata](CITATION.cff)
- [Archival DOI](https://doi.org/10.5281/zenodo.20663419)
- [License](LICENSE.md)

Latest archival release metadata is preserved in the repository and Zenodo.
Current research status is governed only by
[`docs/current_bhsm_status.md`](docs/current_bhsm_status.md) and
[`docs/current_bhsm_status.json`](docs/current_bhsm_status.json).
