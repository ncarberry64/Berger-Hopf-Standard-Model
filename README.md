# Berger-Hopf Standard Model (BHSM)

[![CI](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/ci.yml/badge.svg)](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/actions/workflows/ci.yml)
[![Latest archival release](https://img.shields.io/github/v/release/ncarberry64/Berger-Hopf-Standard-Model?label=archival%20release)](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/releases/latest)
[![Current research status](https://img.shields.io/badge/current%20research-v18.58-orange)](docs/current_bhsm_status.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20663419.svg)](https://doi.org/10.5281/zenodo.20663419)

BHSM is an independent artifact-backed computational framework and mathematical-physics research program investigating whether Standard Model structure and particle-like dynamics can be derived from Berger-Hopf boundary/envelopment geometry and a common action architecture.

## Current Public Status -- v18.58

BHSM v17.84-v18.58 derives and executes the missing N=3 event-to-complete-child boundary/BVP map. The global physical problem remains the unchanged square 376-variable KKT system with explicit event multiplier. Candidate events are promoted only after independent reduction of the exact 376-row merit, admissible eta, fresh rank-14 reconstruction from all 26 child variables, two-scale flux closure, and positive-duration constraint-consistent persistence. Nonzero motion and time dependence are retained as physical relative evolution.

The latest accepted state is v18.58. Its exact residual norm is `0.815925953107132`, event magnitude is `0.084105974509345`, and global eta minimum is `0.77423036838536`. Its child flux envelope is `1.194931425e-5` and it persists for `1e-4` with positive eta. The local Krylov/Newton interpretation is invalidated independently and is not used as physics. The N=3 saddle is not solved because the global residual remains nonzero; N=4+, the microscopic generator, one-loop chain, observables, scale, mass, and flavor gates remain open.

`FULL_BHSM_COMPLETE = FALSE`

Exact next object:

`REMEASURE_THE_DIRECT_376_ROW_RESPONSE_AT_V18_58_AND_CONTINUE_BIDIRECTIONAL_EXACT_MERIT_DESCENT_WITH_ETA_AND_RECOMPUTED_COMPLETE_CHILD_PERSISTENCE_GATING`

Read the [v18.58 promotion report](docs/BHSM_N3_SECOND_BIDIRECTIONAL_PROBE_PROMOTION_V18_58.md), [current status](docs/current_bhsm_status.md), [claim boundaries](CLAIMS.md), [gate ledger](theory/gate_ledger.md), and [reviewer reproduction guide](docs/reviewer_reproduction_guide.md).

| Layer | Current status |
| --- | --- |
| Computational framework | Validated software/tests; this does not validate nature |
| Current test corpus | Deterministic v17.84-v18.58 N=3 correspondence and continuation artifacts plus protected historical corpus |
| Internal mathematical program | Event-to-complete-child map derived; simultaneous N=3 saddle remains open |
| Nonlinear Norman cycle | Moving child persists locally; global N=3 root and downstream release/monodromy remain open |
| Scale and flavor | Absolute scale, action-derived CKM, and PMNS remain open |
| Frozen predictions | Unchanged |
| Empirical status | Not established |

Historical v11.x and v14.x campaigns remain preserved in the [documentation index](docs/README.md) and [artifact index](ARTIFACT_INDEX.md); they are evidence layers, not competing current-status declarations.

BHSM has conditional dimensionless neutrino propagation closure, a conditional neutral spectral-mass theorem, and conditional measurement-supported admissible neutral positivity. Physical eV/GeV neutrino mass closure remains open pending a numeric neutral stiffness length sqrt(A_nu/Z_nu), a physical K_neutral,eff map in m^-2, and complete-action derivation of the admissible response cone.

This independent mathematical-physics project investigates whether Berger-Hopf boundary geometry can organize structures associated with Standard Model fields, flavor, generations, interactions, and dimensional emergence. It records calculations and candidate relationships; it has not received empirical validation, completed a derivation or replacement of the Standard Model, or received institutional endorsement.

## Start Here: BHSM in Plain Language

- [BHSM in plain language](docs/bhsm_in_plain_language.md)
- [Public scientific handoff](docs/bhsm_public_scientific_handoff_v6_21_0.md)
- [Scientific contribution ledger](docs/bhsm_scientific_contribution_ledger.md)
- [CERN toy model in plain language](docs/cern_toy_model_in_plain_language.md)
- [STATUS.md](STATUS.md) and [claim boundaries](CLAIMS.md)
- [BHSM v11.6 parent-action current reduction](docs/BHSM_PARENT_ACTION_SPECTRAL_CURRENT_COMPLETION_v11_6.md), [v11.5 flavor-action assembly](docs/BHSM_FLAVOR_ACTION_COMPLETION_v11_5.md), [v11.3 reciprocal attachment](docs/BHSM_RECIPROCAL_CORE_SURFACE_ATTACHMENT_v11_3.md), and [historical documentation index](docs/README.md)
- [Reviewer reproduction guide](docs/reviewer_reproduction_guide.md)
- [Frozen records](docs/frozen_predictions.md), [artifact index](ARTIFACT_INDEX.md), and historical v11.1-v11.3 chronology in the status records

## BHSM Engine on real CMS Open Data

![BHSM Engine CMS Open Data validation](docs/assets/pr98_cms_open_data_animation/pr98_cms_engine_validation_continuous.gif)

The checksum-pinned PR #98 path uses CERN Open Data Record 303, DOI
`10.7483/OPENDATA.CMS.4M97.3SQ9`, to test coordinate transformations on
collision-derived four-vectors. Scope: Engine coordinate-transformation validation only.
It is not detector reconstruction, a BHSM physics test, or CERN/CMS
endorsement. See the [benchmark record](docs/cern_open_data_benchmark.md).

The earlier [near-pole animation](docs/assets/bhsm_boundary_mapping_explainer.gif)
is a synthetic coordinate-stability demonstration, not a detector failure.

## Computational Quickstart (30 Seconds)

BHSM supports Python 3.10 or newer:

```bash
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
make reviewer-smoke
```

On Windows activate with `.\.venv\Scripts\Activate.ps1`. Without `make`, run:

```bash
python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py
python -m bhsm.interface --help
python -m bhsm.interface registry
python -m bhsm.interface physics-status --format markdown
python tools/audit_public_readiness.py
```

See [QUICKSTART.md](QUICKSTART.md) and
[CLI_REFERENCE.md](CLI_REFERENCE.md) for the complete offline review surface.

## Established Artifact-Backed Outputs

The authoritative frozen records remain `BHSM_BARE_V1` and
`BHSM_DRESSED_V1_CANDIDATE`; this handoff changes neither. The repository
also provides a prediction gallery, provenance adapters, theorem-blocker
reports, symbolic action candidates, and deterministic sprint artifacts.

## Candidate And Open Theorem Areas

The live synthesis is in
[current_bhsm_status](docs/current_bhsm_status.md),
[full_bhsm_completion_v1_candidate](theory/full_bhsm_completion_v1_candidate.md),
and [open proof obligations](theory/full_bhsm_open_proof_obligations.md).
These distinguish artifact-backed formulas and conditional response laws from
unproved completion, physical-scale, and empirical claims.

## Engine Validation Versus Physics Validation

Engine tests do not validate BHSM as particle physics. Engine correctness
means tested software and numerical transformations; physics validation
requires independent experimental comparison and successful derivations.

## Runtime-Gated External Tools

ROOT, CERN Open Data downloads, plotting, native compilation, FeynRules, UFO,
MadGraph, and hardware profiling are optional or runtime-gated. They are not
required for the offline reviewer smoke and are not collider-readiness claims.

## What This Repository Contains

Executable interfaces, deterministic artifacts, frozen records, geometric
and variational derivations, theorem-development records, tests, audits, and
optional external-runtime adapters.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/bhsm/interface/` | Python registry, reports, action audits, and interfaces |
| `artifacts/` | Machine-readable evidence and status records |
| `docs/`, `theory/` | Reviewer guides, derivations, and historical handoffs |
| `tests/`, `tools/` | Reproduction tests and offline audits |
| `integrations/` | Optional external-runtime adapters |

## Claim Boundaries

BHSM does not claim a complete physical action, action-derived particle
masses or gauge couplings, a physical neutrino mass, a completed fold kinetic
classification, collider-production readiness, or institutional endorsement.
See [CLAIMS.md](CLAIMS.md).

## Citation and License

Use [CITATION.cff](CITATION.cff). The verified archival DOI is
[10.5281/zenodo.20663419](https://doi.org/10.5281/zenodo.20663419); the latest
GitHub release and DOI snapshot have distinct version labels. Reuse is
governed by [LICENSE.md](LICENSE.md).

For critique or changes, read [CONTRIBUTING.md](CONTRIBUTING.md), use the
[research template](.github/ISSUE_TEMPLATE/research-source.yml) or
[bug template](.github/ISSUE_TEMPLATE/bug-report.yml), and route security
reports through [SECURITY.md](SECURITY.md).

## v10.2 Topological Buoyancy current-action exhaustion

V10.2 imports prior action/domain results and proves `BHSM_CURRENT_PARENT_ACTION_CANNOT_GENERATE_TOPOLOGICAL_BUOYANCY`; it emits no physical depth, force, Newtonian limit, scale, new term, or fitted parameter. See the [full derivation and exact next object](docs/bhsm_topological_buoyancy_action_derivation_v10_2.md).

The authoritative [v7.1 covariant bulk--boundary reduction](docs/bhsm_covariant_bulk_boundary_reduction_functor_v7_1.md) constructs the oriented \(M_8\to M_5\) pushforward on the retained subcategory and adopts a stratified correspondence action for independently owned cap and boundary-localized fields. The dimensionless finite-input core is internally closed; physical scheme/observable transport remains open. The [v14.29 scientific audit](docs/BHSM_VIEW2_SCIENTIFIC_PROOF_AUDIT_V14_29.md) validates a conditional eta-SU3 action/current candidate with no new vector pole, but finds that common-domain action ownership and FR/Dirac matching are open. BHSM remains incomplete at those gates and the nonlinear BVP, confinement/worldsheet, normalization, scale, mass, flavor, and neutrino gates.
