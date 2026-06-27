# Berger-Hopf Standard Model (BHSM)

BHSM is a research framework for studying Berger-Hopf geometry, frozen internal
prediction artifacts, and candidate links to flavor, boundary structure, and
effective field descriptions.

BHSM currently provides an artifact-backed computational framework with frozen
internal predictions, Python interfaces, prediction registry, CLI reports,
gallery/notebook review tools, provenance-tracked adapters, and theorem-closure
machinery. Its evidence status is computational and artifact-backed;
institutional integration, complete 4D export, and external HEP runtime
validation remain outside the current package.

## What This Repository Contains

- frozen BHSM internal prediction artifacts;
- an offline Python computational interface and prediction registry;
- provenance-tracked adapters for CKM, PMNS, CP phase, boundary constants, and
  mass ratios;
- prediction gallery, plotting, and parse-only notebook review tools;
- explicit theorem blockers and proof-gate machinery;
- a callable symbolic CP `O_int` field/action candidate;
- disabled external HEP workflows awaiting the required theorems and live
  runtime validation.

## Current Public Status

| Area | Status | Summary |
| --- | --- | --- |
| Frozen predictions | `ESTABLISHED` | Versioned internal artifacts remain unchanged. |
| Python interface and CLI | `ESTABLISHED` | Deterministic offline registry, reports, and artifact commands are executable. |
| CKM, PMNS, CP phase, boundary constants, mass ratios | `ARTIFACT_BACKED` | Local artifacts load with provenance. |
| CP `O_int` | `CANDIDATE / OPEN` | A callable symbolic candidate exists; the action-backed production theorem remains open. |
| `X_ch` | `OPEN` | The production interaction theorem is missing. |
| Neutrino physical basis and scale | `OPEN` | The physical basis, dimensional scale, and Dirac/Majorana theorem are missing. |
| FeynRules, UFO, MadGraph | `RUNTIME_GATED` | External validation is deferred until theorem and runtime gates pass. |

[STATUS.md](STATUS.md) is the single source of truth for current area-level
status. Historical README material is preserved in
[docs/archive/README_status_history_pre_v0_7.md](docs/archive/README_status_history_pre_v0_7.md).

## Computational Quickstart

```bash
python -m pytest -q
python -m bhsm.interface registry
python -m bhsm.interface gallery --format markdown
python -m bhsm.interface artifact-sources
python -m bhsm.interface formula-registry
python -m bhsm.interface theorem-blockers
python -m bhsm.interface minimal-action-status
```

See [QUICKSTART.md](QUICKSTART.md) for a runnable walkthrough and
[CLI_REFERENCE.md](CLI_REFERENCE.md) for the complete command table.

## Established Artifact-Backed Outputs

The authoritative frozen records are
[docs/frozen_predictions.md](docs/frozen_predictions.md) and
[docs/frozen_predictions.json](docs/frozen_predictions.json). The frozen branches remain `BHSM_BARE_V1` and
`BHSM_DRESSED_V1_CANDIDATE`; this cleanup changes neither branch.

The adapter layer exposes local CKM and PMNS matrices, the CP holonomy phase,
boundary constants, and frozen mass ratios. Each result carries source path,
source status, and derivation-input provenance. Formula availability does not
upgrade an open theorem.

See [ARTIFACT_INDEX.md](ARTIFACT_INDEX.md) and run:

```bash
python -m bhsm.interface compute-artifact CKM_matrix_BHSM
python -m bhsm.interface compute-artifact PMNS_matrix_BHSM
python -m bhsm.interface artifact-report --anchor W_boson --format json
```

## Candidate And Open Theorem Areas

CP phase attachment to CKM/PMNS structures is artifact-backed. Sprint C adds a
source-traced, callable symbolic CP `O_int` field/action candidate. The v0.8
minimal-action audit identifies its first unresolved object as the
action-derived source, normalized measure, variation, and production rule.

`X_ch` and the physical neutrino basis/scale theorem remain open. Their exact
missing objects are reported by:

```bash
python -m bhsm.interface theorem-blockers
python -m bhsm.interface minimal-action-report --format markdown
```

Long-form mathematical status remains available in
[docs/current_bhsm_status.md](docs/current_bhsm_status.md),
[theory/full_bhsm_completion_v1_candidate.md](theory/full_bhsm_completion_v1_candidate.md),
and [theory/full_bhsm_open_proof_obligations.md](theory/full_bhsm_open_proof_obligations.md).

## Runtime-Gated External Tools

The repository contains review and handoff scaffolds for FeynRules, UFO, and
MadGraph. Current Python review commands run offline and require none of these
tools. External HEP export is a separate future validation workflow after the
relevant theorem objects are established.

## Claim Boundaries

The concise allowed and forbidden claim list is maintained in
[CLAIMS.md](CLAIMS.md). In particular, a W-boson calibration run does not count
W as an independent prediction, and the electron-neutrino comparison is
upper-limit based unless a vetted central reference is explicitly supplied.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/bhsm/interface/` | Python registry, adapters, reports, and theorem-closure interface |
| `artifacts/` | Machine-readable outputs and status records |
| `docs/` | Current guides plus indexed historical handoff documentation |
| `theory/` | Mathematical and theorem-development records |
| `notebooks/` | Parse-only reviewer notebooks |
| `tests/` | Numerical, provenance, claim-boundary, and frozen-integrity tests |

Start with [docs/README.md](docs/README.md) for the documentation map and
[ROADMAP.md](ROADMAP.md) for the next work sequence.

## Citation

Use [CITATION.cff](CITATION.cff) for the repository's current citation
metadata. Release and DOI administration remain separate from this cleanup
branch.
