# Berger-Hopf Standard Model (BHSM) v1.0.0

Current status: BHSM v1.0.0 internal boundary no-fit package complete/exported; external empirical comparison layer separate/open.

```text
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
