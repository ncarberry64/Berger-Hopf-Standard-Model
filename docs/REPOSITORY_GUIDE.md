# BHSM repository guide

Start here to navigate the scientific record. This guide organizes the record;
it does not certify a result or replace a source's action, domain and assumptions.
The complete physical derivation and experimental validation remain open.

## Choose a reading path

| Purpose | Start here | Then follow |
| --- | --- | --- |
| Understand the proposal | [Plain-language account](bhsm_in_plain_language.md) | [Claim boundaries](../CLAIMS.md) and the [Museum](../museum/README.md) |
| Find a scientific topic | [Research topics](RESEARCH_TOPICS.md) | Enclosure/response, mass/flavor, gravity/cosmology, and reproduction routes |
| Review the current scientific architecture | [System integration map](../artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json) | [Current status record](current_bhsm_status.md), [gate ledger](../theory/gate_ledger.md), and the exact source for each claim |
| Find work newer than main | [Open research register](OPEN_RESEARCH.md) | Pinned PR/branch sources; these are separate from merged main |
| Reproduce a result | [Institutional start](INSTITUTIONAL_START.md) | [Quickstart](../QUICKSTART.md), the result's generator, inputs, tests and hashes |
| Review a paper or product | [Blackhole Tracker research start](BLACKHOLE_TRACKER_RESEARCH_START.md) | Paper, product and provenance links from that guide |
| Trace an older result | [Documentation catalog](README.md) and [artifact catalog](../ARTIFACT_INDEX.md) | Exact dated/versioned document and source revision |
| Contribute or reorganize files | [Contributing](../CONTRIBUTING.md) | [Cleanup plan and preservation rules](REPOSITORY_CLEANUP_PLAN.md) |

## What belongs where

Directory names describe a role, not a scientific verdict. A generated certificate
can be essential evidence; a hand-written derivation can still be conditional.

| Record class | Existing homes | Interpretation and maintenance |
| --- | --- | --- |
| Scientific authorities | `CLAIMS.md`, `docs/current_bhsm_status.*`, `artifacts/current_semantics/`, `theory/gate_ledger.md` | Use the matching action/domain and source ledger. A status flag alone cannot establish a physical result. |
| Executable science | `src/`, `scripts/`, `tests/`, `schemas/`, `models/`, `candidates/` | Operators, generators, controls and explicitly candidate model interfaces. Keep source and tests with their reproducibility dependencies. |
| Derivations and research documentation | `theory/`, `docs/`, `audits/` | Includes current and historical work. Version numbers and old headings such as "Current" are scoped to their campaign. |
| Retained historical record | Dated/versioned files throughout those directories, `docs/archive/`, release notes and Git history | Preserve failed controls, superseded assumptions, source hashes and original citations. History is not confined to one archive folder. |
| Generated scientific evidence | `artifacts/`, `data/`, `output/`, `runs/` | Consult [artifact handling](../artifacts/README.md). Retained outputs are not disposable caches. Frozen predictions have their own integrity contract. |
| Papers and manuscript sources | `papers/`, `manuscript/` | Keep source, reviewed PDF, references and provenance together; preserve release identities. A newer build is not automatically a reviewed manuscript. |
| Research products | `products/` | Versioned software snapshots with upstream provenance. Engineering validation and physical validation have different scopes. |
| Museum source and public explanation | `museum/`, `docs/museum/`, `data/museum/` | Explanations, comparisons and simulations link back to their evidence. [Update contract](MUSEUM_SCIENCE_UPDATE.md) governs synchronization; generated site output is not the scientific source. |
| Reproduction and engineering support | `tools/`, `integrations/`, `examples/`, `notebooks/`, `.github/`, `.devcontainer/` | Audits, optional adapters, examples and CI. Choose the bounded test appropriate to the change. |
| Local scratch | Ignored `tmp/`, caches and virtual environments | Keep new scratch work outside retained evidence. Do not infer that an existing tracked file is expendable from its extension. |

The [pinned main inventory](../artifacts/repository_organization/main_inventory_20261110.json)
counts tracked paths without running solvers or downloading every artifact.
It describes main at the recorded commit, not every research branch or local record.

## How to decide which record governs

1. Identify the precise claim, action, physical domain, normalization and state.
2. Follow its source ledger to an exact commit and artifact, including failed or
   conditional controls. Separate bare screens, dressed candidates, conditional
   theorems, numerical diagnostics and physical predictions.
3. Compare later work for an explicit successor on that same domain. A newer date
   alone does not supersede an older theorem; an old missing-operand verdict does
   not erase a later construction.
4. Check the [open research register](OPEN_RESEARCH.md) before assuming main is
   the latest work. GitHub is one part of the record; focused BHSM and Norman Works
   references may resolve a source gap. Private notes require a separate reviewed
   scientific export before inclusion here.

A spectral gap, effective inertia, invariant rest mass and formation threshold
are distinct readouts. A scoped bound or an engineering test must retain its
stated interpretation. See [claim policy](../CLAIMS.md).
