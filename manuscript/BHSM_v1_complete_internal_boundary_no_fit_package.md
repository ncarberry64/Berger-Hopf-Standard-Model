# The Berger-Hopf Standard Model v1.0.0: A Complete Internal Boundary No-Fit Prediction Package

Norman P. Carberry  
Independent Researcher, Oconomowoc, Wisconsin, USA

Release version: v1.0.0  
Release status: internal boundary no-fit package complete; external empirical comparison layer separate/open.

## Abstract

This work reports the v1.0.0 release of the Berger-Hopf Standard Model
repository as a complete internal boundary no-fit prediction package. The
release exports profile-scale constants, charged boundary outputs,
neutral/PMNS/CKM/CP boundary outputs, and a boundary-scale transport identity
as machine-readable artifacts. External empirical comparison is implemented as
a separate comparison-only layer and is not used to derive the internal
package.

## 1. Introduction

The Berger-Hopf Standard Model (BHSM) repository is organized around a
derive-freeze-compare discipline. Internal boundary quantities are derived or
declared under explicit source-traced assumptions, exported as frozen
machine-readable artifacts, and then compared externally only through a
separate comparison layer.

Version v1.0.0 packages the current internal boundary no-fit output as a
release artifact. The release does not report empirical validation. It reports
that the internal boundary package is complete and exported, and that the
external empirical comparison machinery is present but separate.

## 2. Motivation and Scope

The purpose of this release is to make the BHSM boundary package inspectable.
The package includes profile-scale closure, charged boundary outputs, neutral
operator output, PMNS/CKM/CP boundary outputs, and boundary-scale transport.
Each item is exported so that subsequent empirical comparison can be performed
without altering the internal derivation.

The scope is deliberately narrow:

- no empirical data are derivation inputs;
- no frozen prediction files are changed by this release;
- no empirical comparison result is claimed when target data are absent;
- comparison gates are data-absent rather than failed when target data are not
  supplied.

## 3. Frozen Constants and Author-Supplied Axioms

The release preserves the alpha-anchored geometry and universal overlap width:

```text
a = alpha^{-1}/(12*pi^2)
S = 1/(4*pi)
Lambda^2 = 1/(4*pi)
```

The internal profile radius is identified with the same scale:

```text
r^2 = S = Lambda^2 = 1/(4*pi)
r = 1/sqrt(4*pi)
```

The profile normalization and Higgs/profile stiffness are:

```text
Z_H = 1
kappa_H = mu_H = 64*pi^5
```

The boundary width and response scale are:

```text
sigma = 4*pi^(5/2)
tau = 1/(4*pi^(3/2))
```

Numerically:

```text
kappa_H = 19585.25982625801
sigma = 69.97367331049945
tau = 0.04489678053129164
```

The internal identity checks are:

```text
sigma*tau = pi
kappa_H = 4*sigma^2
tau = pi/sigma
```

## 4. Internal Boundary Geometry

The internal boundary geometry is represented in the release by profile-scale
and charged-boundary artifacts. The completion status is:

```text
BHSM_internal_boundary_package = COMPLETE_EXPORTED
BHSM_boundary_no_fit_prediction_package = COMPLETE_EXPORTED
```

This release does not reopen the upstream derivation history. It records the
exported package and its claim boundaries.

## 5. Profile-Scale Closure

The profile-scale closure is represented by:

```text
artifacts/canonical_profile_hessian_theorem_v1.json
artifacts/tau_sigma_boundary_values_v1.json
artifacts/profile_scale_closure_values_v1.json
```

The package-level statements are:

```text
r_internal_profile^2 = 1/(4*pi)
Z_H = 1
kappa_H = mu_H = 64*pi^5
sigma = 4*pi^(5/2)
tau = 1/(4*pi^(3/2))
```

These are internal BHSM package outputs. They are not fitted to observed masses,
Higgs data, gauge values, CKM data, PMNS data, CP data, or cosmology residuals.

## 6. Charged Boundary Output Package

The charged boundary bridge and boundary-output artifacts are:

```text
artifacts/charged_boundary_bridge_values_v1.json
artifacts/charged_outputs_at_boundary_tau_A_local_v1.json
artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json
```

The exact charged boundary values are:

```text
beta_l*tau = kappa_l*tau = 4/(1323*pi^(3/2))

beta_u*tau = 8/(1323*pi^(3/2))
kappa_u*tau = 4/(1323*pi^(3/2))

beta_d*tau = 16/(1323*pi^(3/2))
kappa_d*tau = 4/(3591*pi^(3/2))
```

The release is no-fit at the boundary scale. It does not assert that these
internal values are already a completed empirical mass comparison.

## 7. Neutral, PMNS, CKM, and CP Boundary Outputs

The neutral and mixing/phase artifacts are:

```text
artifacts/neutral_operator_no_fit_output_v1.json
artifacts/PMNS_no_fit_operator_output_v1.json
artifacts/CKM_no_fit_operator_output_v1.json
artifacts/CP_no_fit_holonomy_output_v1.json
```

The PMNS, CKM, and CP outputs are boundary operator outputs under the release
package. Their empirical evaluation belongs to the external comparison layer.
The release does not claim external agreement.

## 8. Boundary-Scale Transport Identity

The boundary-scale transport artifact is:

```text
artifacts/common_scale_boundary_transport_v1.json
```

At the BHSM boundary scale:

```text
T_total(mu_BH_boundary -> mu_BH_boundary) = 1
```

This is an internal boundary-scale identity. External transport to published
schemes, scales, and uncertainty models remains part of the separate
comparison layer.

## 9. External Empirical Comparison Layer

The external comparison layer is represented by:

```text
artifacts/BHSM_external_comparison_target_schema_v1.json
artifacts/BHSM_external_transport_layer_v1.json
artifacts/BHSM_falsification_gates_v1.json
artifacts/BHSM_external_empirical_comparison_package_v1.json
```

The release status is:

```text
external_empirical_comparison_package = IMPLEMENTED_COMPARISON_ONLY_LAYER
external_empirical_comparison_status = DATA_ABSENT_OR_DATA_OPTIONAL
```

The layer is one-way:

```text
internal boundary package -> external comparison transport -> residual audit
```

It may evaluate the package but may not modify the internal package.

## 10. Reproducibility and Machine-Readable Artifacts

Install and test:

```powershell
python -m pip install -e .
python -m pytest -q
```

The completion manifest is:

```text
artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json
```

The v1.0.0 release manifest is:

```text
artifacts/BHSM_v1_release_manifest.json
```

The release manifest records:

```text
empirical_derivation_inputs_used = false
boundary_predictions_modified_by_comparison = false
official_predictions_changed = false
doi = PENDING_ZENODO_RELEASE
```

## 11. Falsification Criteria

The release is falsifiable because it freezes internal outputs before external
comparison. The falsification gate artifact is:

```text
artifacts/BHSM_falsification_gates_v1.json
```

Internal gates check profile identities, package integrity, no empirical
derivation inputs, and unchanged official predictions. External gates require
target data and are marked `NOT_EVALUATED_DATA_ABSENT` when such data are not
present.

## 12. Claim Boundaries

Allowed claim:

```text
internal boundary no-fit package complete; external empirical comparison layer separate/open
```

Not claimed:

- empirical validation;
- peer review;
- exact observed masses;
- external survey validation;
- replacement of the Standard Model;
- feedback from empirical target data into the BHSM derivation.

## 13. Discussion

The v1.0.0 package is best read as a frozen internal mathematical/computational
release. The boundary package is complete at the level described by the
artifacts, while external comparison is an open, separately implemented layer.
This separation is essential: if empirical target data later disagree, the
proper response is to report the disagreement rather than retune the internal
constants.

## 14. Conclusion

BHSM v1.0.0 exports a complete internal boundary no-fit prediction package and
a separate comparison-only empirical layer. The release is ready for repository
inspection, reproducibility testing, Zenodo archival, and future external
comparison work. It does not claim empirical validation.

## References

See `manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.bib`.

## Appendix A: Artifact Manifest

Core artifacts:

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

## Appendix B: Test and Audit Summary

PR #53 validation:

- Focused completion tests: 9 passed
- Adjacent stack tests: 112 passed
- Full suite: 1768 passed
- Forbidden-claims audit: passed
- BHSM status audit: passed
- Frozen prediction integrity audit: passed
- Safety scan: clean; only benign checklist/test wording and variable-name hits

This release sprint adds release-package tests and reruns the full suite.

## Appendix C: Release Checklist

Release checklist:

```text
docs/release_checklist_v1.0.0.md
```

Post-merge release commands are documented there but are not run by this
manuscript.

## v7.2 status addendum

The current repository supersedes the earlier physical-map status of this
historical v1.0.0 package. A finite-input common observable transport is now
defined in the Standard Model `overline_MS` scheme at
`mu_star=ell_star^-1`, with one-loop running on a fixed-active-content
interval, explicit electroweak and CKM maps, and one `G_F` calibration.

This establishes `BHSM_PHYSICAL_COMPLETE` as observable-map completion. It
does not promote the independent gauge, Yukawa, or scalar inputs to
predictions. The release audit finds no distinct action-derived falsifiable
physical prediction after historical screens and conditional extensions are
excluded. The manuscript is therefore not relabeled external-review ready.

Current exact verdict:
`BHSM_RELEASE_COMPLETION_BLOCKED_BY_ABSENCE_OF_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PREDICTION`.

## v7.3 prediction-construction addendum

The six independent construction routes have now been evaluated against the
authoritative action. The exact fermion operator is the localized Standard
Model Dirac-Yukawa operator; no Hopf connection acts on its bundle and no
self-adjoint boundary member is action-selected. The protected kernel and
positive BHSM fermion gap therefore do not exist as current action outputs.

The scalar/topographic Hessian separates into cap/KKT and localized Higgs
blocks at fixed metric. No orthogonal physical scalar projector is derived.
The Berger shape and generation projectors remain inputs. Input cancellation
leaves only structural invariants, and the fixed-h quartic coefficient has no
particle-observable map.

The common missing object is a non-universal action coupling transporting a
distinctive Berger/Hopf/topographic mode into a localized physical operator.
Adding such a term would extend rather than derive the current action. RB-15
and RB-16 therefore remain open.

Current exact verdict:
`BHSM_DISTINCT_PREDICTION_REQUIRES_NEW_BULK_BOUNDARY_COUPLING_NOT_PRESENT_IN_ACTION`.

## v8.0 mass--curvature response addendum

V8.0 explicitly extends the stratified action by coupling the cap-even trace
of the Einstein--GHY canonical momentum to the localized Yukawa operators.
The selected scalar is
\(\kappa_{\rm env}=-(3\kappa_1)^{-1}h_{ab}\pi_{\rm env}^{ab}\). Scalar
momentum is excluded by the retained scalar parity and zero seam trace; the
matcher reaction is the same metric canonical response and is not counted
twice.

The collar construction retains
\(J(Y,\rho)=\det(I+\rho S(Y))\), with
\(J_{\rm round}=\cos^3\rho\). The constrained action does not supply two
independent positive core and surface energies, so no normalized
energy-envelopment ratio or stationary radial localization family is
derived.

The curvature response is one real gauge-singlet channel. Conditional on
the supplied three-family localized spaces it acts as the identity, giving
exact singular-value ratios \(1:1:1\) and leaving CKM undefined under
degeneracy. This result was hashed before comparison and subsequently
invalidated by the nondegenerate historical and common-scale records. No
fit, new mediator, second scale, or post-comparison retuning was used.

RB-15 remains blocked by the absence of family-resolving action incidence;
RB-16 remains downstream.

Current exact verdict:
`BHSM_MASS_RESPONSE_BLOCKED_BY_UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION`.

## v8.1 mode-resolved curvature-incidence addendum

V8.1 retains the complete Brown--York tensor. On the round collar its
four-dimensional trace split uses one quarter, and the first cap-identified
normal response contains a nonzero traceless time/spatial tensor. The signed
intrinsic operator and measure are even and first change at second collar
order. The spatial response remains isotropic.

The exact Hopf reduction provides scalar associated bundles
\(\mathcal H_{(J,m)}=S^7\times_{\rho_J}V_J\) of rank \(2J+1\). It does not
provide an internal spinor parent, chirality, finite family projector, or a
bundle/action map attaching those modes to the localized fermion operator.
The latter remains the intrinsic Standard Model Dirac--Yukawa operator with
\(D_{\rm Hopf/twist}=0\). Triality likewise supplies representation
transport, not three independently responding localized fermion states.

Within each irreducible \(V_J\), the round response commutes with \(Sp(1)\)
and is central by Schur's lemma. Different blocks are not selected as
same-charge families. No physical response matrix, mass ratio, or CKM
observable is therefore defined. RB-15 remains blocked and RB-16 remains
downstream.

Current exact verdict:
`BHSM_FAMILY_RESOLUTION_REQUIRES_NEW_INTERNAL_FERMION_BUNDLE_EXTENSION`.

## v8.2 original generation-projector recovery addendum

The corrected campaign recovers the historical charged-sector triples as one
base mode plus two excitation modes and constructs their rank-three
orthogonal projectors. The exact triality projectors conditionally realize
the same three abstract slots; they are not multiplied by the Berger ladder.
The master-action classification remains a finite independent
generation-module input rather than an action-derived family theorem.

Solving the operational boundary equations completely gives infinitely many
lepton and up roots and four nonzero down roots. The implementation's
`n_modes=2` truncation is the structural input. No regularity, chirality,
anomaly, self-adjoint-domain, or action-gap result excludes the displayed
higher roots.

The full interface tensor cannot be projected into a physical family
response because the proxy mode stress is absent from the localized fermion
action. Mass ratios and CKM therefore remain undefined. The domain-wall
replacement is paused. RB-15 remains blocked and RB-16 remains downstream.

Current exact verdict:
`BHSM_ORIGINAL_GENERATION_PROJECTOR_BLOCKED_BY_UNEXCLUDED_HIGHER_MODES`.

