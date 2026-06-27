# Berger-Hopf Standard Model (BHSM) v1.0.0

Current status: BHSM v1.0.0 internal boundary no-fit package complete/exported; external empirical comparison layer separate/open.

```text
BHSM v1.0.1 status-reconciled release:
internal boundary no-fit package complete/exported;
external empirical comparison layer separate/open.

BHSM v1.0.0 internal boundary no-fit package: COMPLETE_EXPORTED.

The profile scale, charged boundary outputs, neutral/PMNS/CKM/CP boundary outputs, and boundary-scale transport identity are exported as machine-readable artifacts.

External empirical comparison layer: SEPARATE / OPEN.

Empirical data are not used to derive BHSM constants or boundary predictions. External comparisons are one-way tests against the released internal package.
```

The Berger-Hopf Standard Model v1.0.0 repository contains a complete internal
boundary no-fit prediction package. The profile scale, charged boundary
outputs, neutral/PMNS/CKM/CP boundary outputs, and boundary-scale transport
identity are exported as machine-readable artifacts.

External empirical comparison is implemented as a separate comparison-only
layer. Empirical data are not used to derive BHSM constants or boundary
predictions. If external comparison data are absent, the internal BHSM package
remains complete but externally unevaluated.

Short status: BHSM v1.0.0 internal boundary no-fit package complete/exported;
external empirical comparison layer separate/open.

Release phrase: complete internal boundary no-fit prediction package.

Comparison phrase: External empirical comparison is implemented as a separate comparison-only layer.

Derivation phrase: Empirical data are not used to derive BHSM constants or boundary predictions.

This is a public research release for inspection, audit, and reproducibility
discussion. It is not a claim of empirical validation, peer review, or
replacement of the Standard Model.

BHSM is not a proven replacement for the Standard Model.

BHSM does not claim empirical validation.

## BHSM v1.1.0 HEP handoff status

BHSM v1.1.0 packages the internal boundary no-fit release with a bounded minimal collider-interface handoff layer for external HEP-style review.

The handoff layer includes CKM/PMNS charged-current target structures sourced by BHSM artifacts, FeynRules-prep documentation, a disabled minimal FeynRules draft, runtime preflight scripts, Wolfram/FeynRules mapping guides, UFO export runners, MadGraph smoke-test runners, and an institutional validation protocol.

This is not an officially integrated CERN software package. It is not the complete BHSM 4D Lagrangian. FeynRules syntax validation, UFO export/loadability, MadGraph validation, LHE/HepMC generation, Athena integration, and CMSSW integration remain gated until external licensed runtime tools are available and the corresponding scripts pass.

Start here for external review: `docs/hep_review_quickstart.md`.

## Python computational interface

BHSM includes a Python interface for defining hyperspherical/Berger-Hopf
geometry objects, mapping dimensionless geometric tension into physical units,
solving mass-equilibrium equations, and comparing predictions to experimental
references.

The interface separates calibration, prediction, and validation. If a particle
mass is used as the calibration anchor, it is not counted as an independent
prediction in that run. Electron-neutrino comparisons are treated as
upper-limit comparisons unless a vetted central mass reference is supplied.

See:

- `docs/python_interface.md`
- `docs/python_interface_quickstart.md`
- `examples/bhsm_solve_w_and_neutrino.py`

## Python prediction registry and CLI

BHSM includes a Python prediction registry and command-line interface for
inspecting calibration anchors, model predictions, upper-limit comparisons,
frozen internal prediction artifacts, open-theorem blockers, and
runtime-disabled software gates.

The registry is designed to prevent overclaiming. If W is used as the
geometric-to-physical calibration anchor, W is not counted as an independent
prediction in that run. Electron-neutrino comparisons are treated as
upper-limit comparisons unless a vetted central mass reference is supplied.

```powershell
python -m bhsm.interface registry
python -m bhsm.interface status W_boson
python -m bhsm.interface predict --particle electron_neutrino --anchor W_boson
python -m bhsm.interface report --anchor W_boson --particles W_boson,electron_neutrino --format json
```

## BHSM v1.2.0 Python computational interface

The v1.2.0 release candidate consolidates the offline Python computational
interface and prediction registry for computational review. It includes
hyperspherical/Berger-Hopf geometry objects, geometric-to-physical unit mapping,
root solving, reference comparison, registry statuses, CLI commands, and
deterministic reports.

Calibration, prediction, and validation remain separate. If W is used as the geometric-to-physical calibration anchor, W is not counted as an independent prediction in that run. Electron-neutrino comparison remains upper-limit based by default.

Release deployment is currently blocked because the immutable `v1.2.0` tag is
already assigned to an earlier package. It will not be moved or overwritten.

## Collider / CERN Software Readiness

BHSM v1.0.1 is not an Athena, CMSSW, or detector-simulation-ready software
package. It is a released internal boundary no-fit prediction package. A
separate collider-interface layer is required before event generation or
detector simulation. See `docs/collider_readiness.md`.

### UFO / event-generation pipeline status

BHSM v1.0.1 does not yet export a production UFO model, Feynman rules, LHE
files, HepMC files, Athena integration, or CMSSW integration.

The repository now includes a phase-one UFO pipeline scaffold: schemas,
validators, manifest generation, and event-generation readiness checks. These
tools define the required path from an explicit BHSM 4D Lagrangian to Feynman
rules, a UFO model, MadGraph-compatible event generation, and eventual
detector-simulation interfaces.

No collider events are generated unless a real validated Lagrangian,
field-content table, parameter card, vertex table, and UFO export are supplied.

### Analytical export / UFO candidate status

Phase Two-A is attached to the BHSM v1.0.1 status-reconciled release:
internal boundary no-fit package complete/exported; external empirical
comparison layer separate/open.

BHSM now includes a Phase Two-A analytical export layer that maps existing
internal BHSM artifacts into field-content, parameter-card, and vertex-source
ledgers where legitimate repository sources exist.

This is not yet a production UFO model. The candidate UFO builder is gated and
will not produce a loadable physics model unless a complete 4D collider-ready
Lagrangian, field-content table, parameter card, vertex table, and Feynman-rule
layer are validated.

No LHE or HepMC events are generated in this release.

### 4D Lagrangian projection / FeynRules gate status

Phase Three-A attempts an analytical projection from BHSM internal
boundary/operator artifacts to a candidate effective 4D Lagrangian ledger,
field-normalization ledger, vertex-normalization ledger, mass/width scheme
status, renormalization scheme status, and FeynRules/UFO readiness gate.

This is not production UFO readiness. The current result is a candidate ledger
and blocker audit: the complete 4D collider-ready Lagrangian, gauge fixing,
canonical field normalization, vertex normalization, mass/width scheme,
renormalization scheme, complete vertex table, and production parameter-card
conventions remain blocked.

No MadGraph, LHE, HepMC, Athena, or CMSSW readiness is claimed.

### Phase Three-C field dictionary status

BHSM now includes a candidate 4D field dictionary and vertex-source target map.
Internal BHSM boundary coefficients, mixing matrices, neutral operators, and
holonomy phases are mapped to candidate collider-field targets with explicit
provenance.

This does not constitute production FeynRules/UFO readiness. Vector/fermion
normalizations, full gauge/Lorentz structures, mass-width schemes, and
renormalization conventions remain open.

### Phase Three-D canonical current interface status

BHSM now includes canonical field target conventions and chiral current
attachment maps for CKM/PMNS sectors. The scalar/profile normalization source
Z_H = 1 is preserved, while vector and fermion normalizations are treated as
standard target conventions or open BHSM-specific normalization gates.

This does not constitute production FeynRules, UFO, MadGraph, LHE/HepMC,
Athena, or CMSSW readiness. Mass-width and renormalization schemes remain open.

### Phase Three-E normalization and scheme status

BHSM now includes Phase Three-E vector/fermion canonical normalization
convention ledgers, gauge-fixing/coupling scheme candidates, and
mass-width/renormalization open-gate artifacts.

The scalar/profile normalization source Z_H = 1 remains BHSM-derived or
conditionally derived. Vector and fermion target normalizations may be
represented by standard canonical interface conventions, but they are not yet
nontrivial BHSM-derived field-strength predictions.

This does not constitute production FeynRules, UFO, MadGraph, LHE/HepMC,
Athena, or CMSSW readiness.

### Phase Three-G production-vertex and Lagrangian-candidate status

BHSM now includes a candidate production vertex table and symbolic 4D
Lagrangian assembly ledger in the canonical production basis. CKM/PMNS
charged-current target structures are identified using BHSM-derived mixing
sources and standard target-current conventions.

The table is not a production FeynRules model. Charged boundary response,
neutral kernel, and CP holonomy attachment remain blocked by explicit missing
interaction/basis attachments. Mass-width closure, renormalization closure,
complete production vertex table, FeynRules export, UFO loadability, MadGraph
validation, LHE/HepMC generation, and Athena/CMSSW integration remain open.

### Phase Three-H bounded blocker resolution status

BHSM now includes bounded resolution audits for the remaining vertex-table
blockers: X_ch, neutrino basis/scale, and CP holonomy attachment. CKM/PMNS
charged-current target vertices are partially promoted as bounded
collider-interface targets where the canonical production basis, standard
target-current structures, and BHSM-derived mixing/holonomy sources align.

The separate charged boundary response, neutral kernel, and standalone CP
holonomy vertices remain blocked by explicit missing interaction, basis, or
scale theorems. This does not constitute complete 4D Lagrangian export,
production FeynRules readiness, UFO readiness, MadGraph readiness, event
generation, or experiment software integration.

### Phase Three-I interaction-theorem closure status

BHSM v1.0.1 status-reconciled release: internal boundary no-fit package
complete/exported; external empirical comparison layer separate/open.

BHSM now includes direct theorem-closure audits for the final interaction
blockers: X_ch, neutrino Dirac-Majorana basis/scale, and standalone CP O_int
attachment. CKM/PMNS target-current attachments remain bounded
collider-interface targets where standard current conventions, canonical
production basis, and BHSM mixing/holonomy sources already align.

The separate charged boundary response, neutral kernel, and standalone CP
holonomy vertex remain blocked unless their missing interaction, basis/scale,
or O_int theorems are derived. This does not constitute complete 4D Lagrangian
export, production FeynRules readiness, UFO readiness, MadGraph readiness,
event generation, or experiment software integration.

### Phase Three-J minimal collider-interface Lagrangian subset

BHSM v1.0.1 status-reconciled release: internal boundary no-fit package
complete/exported; external empirical comparison layer separate/open.

BHSM now includes a minimal bounded collider-interface Lagrangian subset in
the canonical production basis. The subset includes CKM/PMNS charged-current
target structures sourced by BHSM mixing artifacts and standard target-current
conventions.

The subset explicitly excludes the unresolved charged boundary response,
neutral kernel, and standalone CP holonomy vertices. It is FeynRules-prep only
and does not constitute the complete BHSM 4D Lagrangian, production FeynRules
readiness, UFO readiness, MadGraph readiness, event generation, or experiment
software integration.

### Phase Three-K bounded FeynRules export attempt

BHSM v1.0.1 status-reconciled release: internal boundary no-fit package
complete/exported; external empirical comparison layer separate/open.

BHSM now includes a software-track bounded FeynRules export attempt for the
minimal collider-interface subset. The attempted model covers only
canonical-basis CKM/PMNS charged-current target structures sourced by BHSM
mixing artifacts.

The file is not the complete BHSM 4D Lagrangian and excludes unresolved
charged-boundary response, neutral-kernel, and standalone CP-holonomy vertices.
UFO export, UFO loadability, MadGraph validation, LHE/HepMC generation, and
Athena/CMSSW integration remain gated unless separately validated.

### Phase Three-L FeynRules syntax-runner package

BHSM v1.0.1 status-reconciled release: internal boundary no-fit package
complete/exported; external empirical comparison layer separate/open.

BHSM now includes a FeynRules syntax contract and local export-runner package
for the bounded minimal collider-interface subset. The package prepares local
Mathematica/FeynRules checks, UFO export commands, software environment
preflight, and a MadGraph smoke-test runner contract.

Repository static checks do not equal FeynRules validation. Unless
Mathematica/FeynRules/UFO/MadGraph execution is actually performed and passes,
BHSM remains not UFO-ready, not MadGraph-ready, and not
event-generation-ready.

### Phase Three-M live FeynRules validation status

BHSM now includes a live FeynRules validation attempt layer for the bounded
minimal collider-interface subset. This layer records whether Mathematica,
FeynRules, UFO export, and MadGraph smoke-test tooling were actually detected
and run.

Static checks do not count as live FeynRules validation. Unless the repository
records successful Mathematica/FeynRules execution, the minimal model remains
disabled and BHSM remains not UFO-ready, not MadGraph-ready, and not
event-generation-ready.

### Phase Three-N runtime execution gate

BHSM now includes a runtime execution gate for live Wolfram/FeynRules
validation of the bounded minimal collider-interface subset. The gate records
whether Mathematica/WolframScript, FeynRules, UFO export, and MadGraph smoke
testing were actually detected and run.

If live validation does not run, the minimal model remains disabled. If live
validation passes, only the bounded CKM/PMNS collider-interface subset may be
enabled. The complete BHSM 4D Lagrangian, unresolved charged-boundary
response, neutral kernel, standalone CP holonomy, UFO/MadGraph/event
readiness, and CERN integration remain separate gated items.

### Phase Three-O runtime assets and institutional HEP handoff

BHSM now includes a runtime asset provisioning layer and CERN-like
institutional HEP handoff package for the bounded minimal collider-interface
subset. The package documents how to map or install legal
Wolfram/FeynRules/MadGraph dependencies, run environment preflight, attempt
live FeynRules validation, attempt UFO export, and attempt MadGraph smoke
testing.

This is not experiment-approved integration. It is a reproducible handoff
package for external HEP-style review. The complete BHSM 4D Lagrangian,
charged-boundary response, neutral kernel, standalone CP holonomy, pure no-fit
mass-width closure, and renormalization closure remain separate gated items.

### Phase Three-F production-basis and runtime-parameter status

BHSM now defines a canonical production basis for future FeynRules/UFO
interfaces. In that production basis, vector and fermion fields are represented
with canonical kinetic normalization, so Z_A,prod = 1 and Z_psi,prod = 1 are
basis definitions, not empirical fits and not nontrivial BHSM
wavefunction-renormalization predictions.

BHSM also defines two parameter modes: BHSM_PURE_NOFIT for derivation-only
internal use, and BHSM_COLLIDER_INTERFACE for future runtime detector/event
comparison inputs. Runtime empirical masses, widths, or cards may not modify
BHSM constants, boundary coefficients, mixing matrices, or frozen predictions.

This does not constitute production FeynRules, UFO, MadGraph, LHE/HepMC,
Athena, or CMSSW readiness.

## 1. What Is Complete In v1.0.0

- `BHSM_internal_boundary_package = COMPLETE_EXPORTED`
- `BHSM_boundary_no_fit_prediction_package = COMPLETE_EXPORTED`
- Profile-scale closure values are exported.
- Charged boundary values are exported.
- Neutral, PMNS, CKM, and CP boundary outputs are exported.
- Boundary-scale transport identity is exported.
- External empirical comparison is implemented as a one-way comparison layer.
- Data-absent external comparison is represented as unevaluated, not as an
  internal package failure.

## 2. What Is Not Claimed

BHSM v1.0.0 does not claim:

- empirical proof;
- experimental replacement of the Standard Model;
- validation by DESI or any external survey;
- exact observed particle masses;
- use of empirical data as derivation inputs;
- post-hoc tuning of constants, modes, thresholds, or boundary predictions.

The release claim is narrower: the internal boundary no-fit package is complete
and exported, while empirical comparison remains separate and open.

## 3. Key Frozen Values

| Quantity | Exact value | Numerical value |
| --- | --- | --- |
| `a` | `alpha^{-1}/(12*pi^2)` | canonical alpha-anchored geometry |
| `S` | `1/(4*pi)` | `0.07957747154594767` |
| `Lambda^2` | `1/(4*pi)` | `0.07957747154594767` |
| `r_internal_profile^2` | `1/(4*pi)` | `0.07957747154594767` |
| `r_internal_profile` | `1/sqrt(4*pi)` | `0.28209479177387814` |
| `Z_H` | `1` | `1.0` |
| `kappa_H = mu_H` | `64*pi^5` | `19585.25982625801` |
| `sigma` | `4*pi^(5/2)` | `69.97367331049945` |
| `tau` | `1/(4*pi^(3/2))` | `0.04489678053129164` |

Identity checks:

- `sigma*tau = pi`
- `kappa_H = 4*sigma^2`
- `tau = pi/sigma`

Charged boundary values:

```text
beta_l*tau = kappa_l*tau = 4/(1323*pi^(3/2))
beta_u*tau = 8/(1323*pi^(3/2))
kappa_u*tau = 4/(1323*pi^(3/2))
beta_d*tau = 16/(1323*pi^(3/2))
kappa_d*tau = 4/(3591*pi^(3/2))
```

## 4. Core Artifacts

The release is centered on these machine-readable artifacts:

- `artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json`
- `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json`
- `artifacts/canonical_profile_hessian_theorem_v1.json`
- `artifacts/tau_sigma_boundary_values_v1.json`
- `artifacts/profile_scale_closure_values_v1.json`
- `artifacts/charged_boundary_bridge_values_v1.json`
- `artifacts/charged_outputs_at_boundary_tau_A_local_v1.json`
- `artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json`
- `artifacts/common_scale_boundary_transport_v1.json`
- `artifacts/neutral_operator_no_fit_output_v1.json`
- `artifacts/PMNS_no_fit_operator_output_v1.json`
- `artifacts/CKM_no_fit_operator_output_v1.json`
- `artifacts/CP_no_fit_holonomy_output_v1.json`
- `artifacts/BHSM_external_comparison_target_schema_v1.json`
- `artifacts/BHSM_external_transport_layer_v1.json`
- `artifacts/BHSM_falsification_gates_v1.json`
- `artifacts/BHSM_external_empirical_comparison_package_v1.json`
- `artifacts/BHSM_v1_release_manifest.json`

## 5. How To Reproduce

```powershell
python -m pip install -e .
python -m pytest -q
```

Focused release-package tests:

```powershell
python -m pytest -q tests/test_bhsm_v1_release_package.py
```

Audits:

```powershell
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
```

## 6. How To Cite

Use `CITATION.cff` for citation metadata. Until Zenodo assigns a DOI, cite the
repository release and tag:

```text
Norman P. Carberry. Berger-Hopf Standard Model v1.0.0: Complete Internal
Boundary No-Fit Package. GitHub repository release, 2026.
```

See `docs/how_to_cite.md`.

## 7. Release / DOI Status

- Release version: `v1.0.0`
- Release title: `Berger-Hopf Standard Model v1.0.0: Complete Internal Boundary No-Fit Package`
- DOI status: `PENDING_ZENODO_RELEASE`
- License: all rights reserved; see `LICENSE.md`

After the GitHub release is published, Zenodo should archive the release if the
repository is enabled in the Zenodo GitHub integration. Once Zenodo assigns a
DOI, update `CITATION.cff`, `README.md`, and `docs/how_to_cite.md`.

## 8. Falsification And Comparison Layer

The empirical comparison layer is intentionally one-way:

```text
internal boundary package -> external comparison transport -> residual audit
```

It must not feed empirical values back into BHSM constants, modes, or boundary
predictions. If target data are absent, comparison gates remain
`NOT_EVALUATED_DATA_ABSENT`.

The current public status remains:

```text
internal boundary no-fit package complete; external empirical comparison layer separate/open
```

## What BHSM Is

BHSM is a test-backed Berger-Hopf boundary and topographic research
architecture. This v1.0.0 package exports the internal boundary no-fit package.

Historical pre-v1.0.0 repository-wide status phrase, retained only as context:

```text
structural architecture integrated conditional; numerical closure open
```

## What Is Test-Backed

The repository contains tests and audits for the frozen prediction layer,
boundary package exports, comparison-layer guardrails, release metadata, and
claim boundaries.

## What Is Not Yet Proven

Open proof obligations remain tracked in:

- `docs/current_bhsm_status.md`
- `theory/full_bhsm_open_proof_obligations.md`

## Frozen Prediction Layer

The frozen prediction layer is preserved:

- `BHSM_BARE_V1`
- `BHSM_DRESSED_V1_CANDIDATE`
- `docs/frozen_predictions.md`
- `docs/frozen_predictions.json`

## Candidate Synthesis Layer

The candidate synthesis context remains available at:

- `theory/full_bhsm_completion_v1_candidate.md`
- `theory/full_bhsm_master_equation_map.md`
- `theory/full_bhsm_claim_status_matrix.md`
- `theory/full_bhsm_empirical_gate_plan.md`
- `theory/full_bhsm_candidate_release_notes.md`

## Connected Topographic-Curvature Extension

Connected topographic-curvature and boundary-package extensions remain
documented as source-traced repository components. The v1.0.0 package does not
use empirical target data to alter them.

## Claim Hygiene

Before public statements, inspect:

- `docs/current_bhsm_status.md`
- `docs/claim_boundaries.md`
- `docs/forbidden_claims.md`
- `docs/allowed_public_language.md`
