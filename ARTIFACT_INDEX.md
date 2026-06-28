# BHSM Artifact Index

This index names the principal reviewer artifacts. Historical sprint artifacts
remain available under `artifacts/` and are discoverable with
`python -m bhsm.interface artifact-sources`.

The controlling minimal-action ontology is
`artifacts/BHSM_author_ontology_v0_8.json`; its bounded results are exported in
the `BHSM_*_minimal_action_closure_v0_8.json` artifacts.

| Artifact | Purpose | Source | Status | Related command |
| --- | --- | --- | --- | --- |
| Frozen predictions | Immutable internal prediction record | `docs/frozen_predictions.json` | `ESTABLISHED` | `python -m pytest -q` |
| Prediction registry | Prediction and policy entries | `artifacts/BHSM_prediction_registry_v0_1.json` | `ESTABLISHED` | `python -m bhsm.interface registry` |
| Python interface results | Deterministic interface examples | `artifacts/BHSM_python_interface_example_results_v0_1.json` | `ESTABLISHED` | `python -m bhsm.interface report` |
| Prediction gallery | Claim-aware registry view | `artifacts/BHSM_prediction_gallery_table_v0_2.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface gallery` |
| Notebook pack | Parse-only review notebooks | `artifacts/BHSM_notebook_pack_manifest_v0_2.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface notebook-pack --check` |
| CKM matrix | Frozen CKM magnitudes | `artifacts/CKM_no_fit_operator_output_v1.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface compute-artifact CKM_matrix_BHSM` |
| PMNS matrix | Frozen PMNS magnitudes | `artifacts/PMNS_no_fit_operator_output_v1.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface compute-artifact PMNS_matrix_BHSM` |
| CP phase | Holonomy phase seed | `artifacts/CP_no_fit_holonomy_output_v1.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface compute-artifact cp_holonomy_phase_attachment` |
| Boundary constants | No-fit boundary package | `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface compute-artifact boundary_constants` |
| Mass ratios | Frozen charged-sector ratios | `theory/bhsm_v1_frozen_prediction_set.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface compute-artifact mass_ratios` |
| Formula registry | Callable and blocker index | `artifacts/BHSM_formula_registry_v0_3.json` | `ARTIFACT_BACKED` | `python -m bhsm.interface formula-registry` |
| Author ontology | Controlling physical-boundary-field and response dictionary | `artifacts/BHSM_author_ontology_v0_8.json` | `AUTHOR_SUPPLIED` | `python -m bhsm.interface minimal-action-status` |
| Neutrino propagation closure | Dimensionless threshold-response candidate | `artifacts/BHSM_neutrino_numerical_closure_report_v0_9.json` | `CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE` | `python -m bhsm.interface neutrino-propagation-report --format markdown` |
| Neutral dimensionful scale closure | Unit-source, measure, and threshold-map audit | `artifacts/BHSM_neutral_scale_closure_report_v1_0.json` | `OPEN_MISSING_NEUTRAL_SCALE` | `python -m bhsm.interface neutrino-scale-report --format markdown` |
| Legacy curvature-threshold scale audit | Author theory corpus, curvature mass functional, radius search, and curvature map | `artifacts/BHSM_legacy_neutral_scale_report_v1_1.json` | `OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS` | `python -m bhsm.interface legacy-neutral-scale-report --format markdown` |
| Neutral radius/curvature closure | Symbolic radius and curvature candidates plus dimensional-consistency gate | `artifacts/BHSM_neutral_radius_curvature_report_v1_2.json` | `DIMENSIONFUL_MASS_NOT_AVAILABLE` | `python -m bhsm.interface neutral-radius-curvature-report --format markdown` |
| Neutral spectral stiffness | Scalar mass-gap analogue, legacy dimensional gate, neutral stiffness/gap, and positivity audit | `artifacts/BHSM_neutral_spectral_report_v1_3.json` | `CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE` | `python -m bhsm.interface neutral-spectral-report --format markdown` |
| Admissible neutral positivity | Exact raw audit, response-cone domain, copositivity proof, and counterexample search | `artifacts/BHSM_neutral_positivity_report_v1_4.json` | `CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE` | `python -m bhsm.interface neutral-positivity-report --format markdown` |
| Neutral action closure | Action-source inventory, stiffness extraction, curvature unit map, partial-action cone, and mass gate | `artifacts/BHSM_neutral_action_closure_report_v1_5.json` | `DIMENSIONFUL_MASS_NOT_AVAILABLE` | `python -m bhsm.interface neutral-action-closure-report --format markdown` |
| v1.5 status stabilization | Canonical five-part neutral closure split and public review boundary | `artifacts/BHSM_v1_5_status_stabilization_report.json` | `REVIEW_READY_WITH_OPEN_PHYSICAL_MASS_CLOSURE` | `python -m bhsm.interface neutrino-closure-status --format markdown` |
| Full-completion v1.6 | Sixteen-category ledger, priority map, selected target, and partial closure | `artifacts/BHSM_full_completion_manifest_v1_6.json` | `INTEGRATED_CONDITIONAL_ARCHITECTURE_WITH_OPEN_BLOCKERS` | `python -m bhsm.interface full-completion-status --format markdown` |
| Charged closure v1.7 | Charged source, stiffness, eta_l, CKM exponent, mixing, and dimensional audits | `artifacts/BHSM_charged_closure_report_v1_7.json` | `CONDITIONAL_CHARGED_SOURCES` | `python -m bhsm.interface charged-closure-report --format markdown` |
| Final completion v1.8 | Common-16 identities, provenance gates, target scores, and updated blocker ledger | `artifacts/BHSM_final_completion_closure_report_v1_8.json` | `CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE` | `python -m bhsm.interface final-completion-status --format markdown` |
| Theorem closure | Strict proof-gate report | `artifacts/BHSM_theorem_closure_report_v0_4.json` | `OPEN` | `python -m bhsm.interface theorem-closure-report` |
| CP O_int Sprint B | Staged interaction-attachment audit | `artifacts/BHSM_cp_o_int_attachment_report_v0_5.json` | `OPEN` | `python -m bhsm.interface cp-o-int-report` |
| CP O_int Sprint C | Callable symbolic field/action candidate | `artifacts/BHSM_cp_o_int_field_action_report_v0_6.json` | `CANDIDATE / OPEN` | `python -m bhsm.interface cp-o-int-field-action` |
| Minimal action report | Three-theorem action audit | `artifacts/BHSM_minimal_action_report_v0_8.json` | `OPEN` | `python -m bhsm.interface minimal-action-report` |
| Minimal action decisions | CP, `X_ch`, and neutrino first-missing-object records | `artifacts/BHSM_minimal_action_closure_manifest_v0_8.json` | `OPEN` | `python -m bhsm.interface minimal-action-status` |
| Claim policy | Consolidated allowed and unsupported claims | `artifacts/BHSM_clean_claims_index_v0_7.json` | `ESTABLISHED` | See `CLAIMS.md` |
