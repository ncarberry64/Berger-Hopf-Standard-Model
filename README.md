# Berger-Hopf Standard Model (BHSM)

BHSM is a research framework for studying Berger-Hopf geometry, frozen internal prediction artifacts,
and candidate links to flavor, boundary structure, and effective field descriptions.

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

BHSM is an artifact-backed computational framework for Berger-Hopf boundary-mode physics. Current public status: structural architecture integrated conditional; frozen predictions unchanged; physical eV/GeV neutrino mass closure remains open; external HEP runtime integration remains gated.

| Area | Status | Summary |
| --- | --- | --- |
| Frozen predictions | `ESTABLISHED` | Versioned internal artifacts remain unchanged. |
| Python interface and CLI | `ESTABLISHED` | Deterministic offline registry, reports, and artifact commands are executable. |
| CKM, PMNS, CP phase, boundary constants, mass ratios | `ARTIFACT_BACKED` | Local artifacts load with provenance. |
| CP/Z6 holonomy | `ARTIFACT_BACKED` | The holonomy and CKM/PMNS phase attachment are local artifact-backed constraints; standalone `O_int` production is a retired target. |
| `X_ch` | `CONDITIONAL_ACTION_THEOREM` | Author ontology defines a charged boundary-response operator; numerical and 4D production closure remain open. |
| Neutrino BHSM mass | `CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE` | Local no-fit artifacts support a dimensionless propagation-threshold response; the eV/GeV scale remains open. |
| Neutral dimensionful scale | `OPEN_MISSING_NEUTRAL_SCALE` | The local audit finds no physical unit anchor, normalized boundary measure, or threshold-to-energy map. |
| Legacy curvature mass bridge | `ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL` | Author-supplied papers provide the geometric matching functional; physical `r_prop` and `k_neutral,eff` remain open. |
| Neutral propagation radius | `CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE` | A symbolic length-domain candidate is defined; no numerical value in metres is derived. |
| Neutral physical curvature map | `CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE` | A symbolic `kappa_curv R_nu` map is defined; `kappa_curv` in `m^-2` remains open. |
| Dimensionful neutrino mass | `DIMENSIONFUL_MASS_NOT_AVAILABLE` | Numeric unit inputs are absent, and the legacy `r^2 k` functional has dimension mass/length under `K=-nabla^2 ln rho`. |
| Neutral mass-gap action | `ARTIFACT_BACKED_MASS_GAP_ACTION` | The scalar topographic action analogue is artifact-backed; its neutral normalization is conditional. |
| Neutral spectral gap | `CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE` | `m_nu c^2 = hbar c sqrt(A_nu/Z_nu) K_neutral,eff`; numeric stiffness length and physical curvature remain open. |
| Neutral kernel positivity | `CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE` | Raw PSD is false; exact copositivity holds on the author-ontology response cone without thresholding. |
| Neutral action normalization | `OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION` | Partial variational boundary/collar action exists; coefficient, measure, profile, and unit normalization remain open. |
| Action-supported response cone | `CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE` | Existing action terms partially support the cone; complete-action derivation remains open. |
| Full-completion audit | `INTEGRATED_CONDITIONAL_ARCHITECTURE_WITH_OPEN_BLOCKERS` | Sixteen categories are inventoried; boundary-measure shape and identity transport have a partial closure. |
| FeynRules, UFO, MadGraph | `RUNTIME_GATED` | External validation is deferred until theorem and runtime gates pass. |

[STATUS.md](STATUS.md) is the single source of truth. Historical README material is preserved in
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
python -m bhsm.interface neutral-spectral-report --format markdown
python -m bhsm.interface neutral-positivity-report --format markdown
python -m bhsm.interface neutral-action-closure-report --format markdown
python -m bhsm.interface neutrino-closure-status --format markdown
python -m bhsm.interface full-completion-status --format markdown
```

The legacy gravitational curvature expression is dimensionally gated because K has units L^-2 and (c^2/G) r^2 K has units M/L, not M.
BHSM does not use the legacy gravitational curvature expression as a direct particle mass formula.
The preferred particle-sector path is the conditional action-normalized neutral spectral gap. No physical neutrino mass is emitted by repository defaults.

The raw neutral kernel is not assumed to be positive semidefinite. BHSM
distinguishes raw kernel positivity, conditional admissible-cone positivity,
and thresholded response nonnegativity.

BHSM has conditional dimensionless neutrino propagation closure, a conditional neutral spectral-mass theorem, and conditional measurement-supported admissible neutral positivity. Physical eV/GeV neutrino mass closure remains open pending a numeric neutral stiffness length sqrt(A_nu/Z_nu), a physical K_neutral,eff map in m^-2, and complete-action derivation of the admissible response cone.

See [QUICKSTART.md](QUICKSTART.md) for a runnable walkthrough and [CLI_REFERENCE.md](CLI_REFERENCE.md) for the complete command table.

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

CP phase attachment to CKM/PMNS structures is artifact-backed. The v0.8 author
ontology classifies CP as a Z6 boundary holonomy constraint and retires the
standalone `O_int` production target. It defines `X_ch` conditionally as a
charged boundary-response operator and the neutrino BHSM mass conditionally as
a propagation-locked curvature response. These are structural theorem statuses;
numerical closure and external HEP runtime readiness remain open.

The v0.9 neutrino module evaluates the conditional dimensionless law
`tau max(0, p g_nu ||K_nu psi||/||psi|| - kappa_nu)`. In BHSM, the neutrino
mass contribution is modeled as a propagation-locked curvature response, not
as an ordinary static rest-mass primitive. No dimensional neutrino mass is
claimed because an artifact-backed neutral eV/GeV scale is absent.

BHSM currently distinguishes dimensionless neutrino propagation closure from physical eV/GeV mass closure.
A physical eV/GeV neutrino mass requires an artifact-backed or explicitly conditional neutral dimensionful scale.
The electron-neutrino upper limit is a comparison reference only and is never used to set the neutral scale.
A dimensionless BHSM response is not, by itself, a physical eV/GeV mass.

Run the offline scale audit with:

```bash
python -m bhsm.interface neutral-scale-candidates --format json
python -m bhsm.interface neutrino-scale-report --format markdown
python -m bhsm.interface legacy-neutral-scale-report --format markdown
python -m bhsm.interface neutral-radius-curvature-report --format markdown
```

The legacy curvature-threshold mass functional supplies a candidate mass bridge, not an empirical neutrino mass prediction by itself. A physical BHSM neutrino mass requires both a propagation/localization scale and a neutral curvature mapping with physical units.

The v1.2 dimensional audit adds a further required gate: the mass functional itself must reduce to physical mass. The currently documented `r^2 k` expression does not pass that gate when `K` has dimension `length^-2`.

The exact evidence boundary is reported by:

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
