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
| Neutrino bedrock/dynamic doctrine | Dimensionless BHSM geometry separated from deferred QFT/SM physical realization | `artifacts/neutrino_bedrock_dynamic_layer_v1.json` | `STRUCTURAL_DOCTRINE_LOCKED` | `python -m bhsm.interface neutrino-bedrock-status --format markdown` |
| Full-completion v1.6 | Sixteen-category ledger, priority map, selected target, and partial closure | `artifacts/BHSM_full_completion_manifest_v1_6.json` | `INTEGRATED_CONDITIONAL_ARCHITECTURE_WITH_OPEN_BLOCKERS` | `python -m bhsm.interface full-completion-status --format markdown` |
| Charged closure v1.7 | Charged source, stiffness, eta_l, CKM exponent, mixing, and dimensional audits | `artifacts/BHSM_charged_closure_report_v1_7.json` | `CONDITIONAL_CHARGED_SOURCES` | `python -m bhsm.interface charged-closure-report --format markdown` |
| Final completion v1.8 | Common-16 identities, provenance gates, target scores, and updated blocker ledger | `artifacts/BHSM_final_completion_closure_report_v1_8.json` | `CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE` | `python -m bhsm.interface final-completion-status --format markdown` |
| Synthetic coordinate benchmark | Ten-million-event scalar, vectorized-control, and BHSM-inspired coordinate microbenchmark | `artifacts/coordinate_benchmark/coordinate_benchmark_results.json` | `SYNTHETIC_MICROBENCHMARK_NOT_PRODUCTION_HEP_VALIDATION` | `python -m bhsm.interface.benchmarks.coordinate_benchmark --events 10000000 --boundary-fraction 0.35 --repeats 3` |
| CERN Open Data coordinate benchmark | Published 2010 CMS dimuon four-vector transformation benchmark with DOI and checksums | `artifacts/cern_open_data_benchmark/results.json` | `CERN_OPEN_DATA_FOUR_VECTOR_BENCHMARK_NOT_TRACK_RECONSTRUCTION` | `python -m bhsm.interface.benchmarks.cern_open_data_benchmark --download --summary` |
| PR #98 CMS Open Data animation | Compact deterministic display sample, provenance manifest, offline GIF, and SVG fallback | `docs/assets/pr98_cms_open_data_animation/pr98_cms_sample_manifest.json` | `ENGINE_VALIDATION_VISUAL_NOT_PHYSICS_VALIDATION` | `python docs/assets/pr98_cms_open_data_animation/generate_pr98_cms_animation.py` |
| Native microarchitecture profile | C++ angular/direct harness and Linux perf counter protocol | `artifacts/native_microarchitecture_profile/profile_status.json` | `PROFILING_HARNESS_READY_COUNTERS_NOT_COLLECTED` | `./scripts/run_native_perf_profile.sh` |
| ROOT IMT scaling | Process-isolated `EnableImplicitMT(N)` throughput and checksum protocol | `artifacts/root_imt_scaling/scaling_status.json` | `ROOT_IMT_SCALING_MEASURED_ENVIRONMENT_SPECIFIC` | `python tools/run_root_imt_scaling.py --help` |
| Engine/Physics separation v1.9 | Validated and excluded engine capabilities separated from conditional physics status | `artifacts/BHSM_engine_physics_status_separation_v1_9.json` | `CLAIM_BOUNDARY_ESTABLISHED` | `python -m bhsm.interface engine-status --format markdown` |
| Engine invariants v1.9 | Offline Lorentz, round-trip, near-null, and scale-aware checks | `artifacts/BHSM_engine_invariant_preservation_v1_9.json` | `ENGINE_INVARIANTS_DETERMINISTIC_OFFLINE_PASS` | `python -m bhsm.interface engine-invariants --format json` |
| Minimal theorem core v1.9 | Reviewer-facing evidence and blocker map | `artifacts/BHSM_minimal_theorem_core_v1_9.json` | `INTEGRATED_CONDITIONAL_WITH_OPEN_GATES` | `python -m bhsm.interface minimal-theorem-core --format markdown` |
| Action derivation gates v1.9 | Omega_f, rho_ch, and charged-overlap provenance audits | `artifacts/BHSM_action_derivation_gates_report_v1_9.json` | `ACTION_DERIVATION_GATES_OPEN` | `python -m bhsm.interface omega-f-action-audit --format json` |
| Falsification table v1.9 | Explicit engine and physics falsifiers | `artifacts/BHSM_brutal_falsification_table_v1_9.json` | `REVIEWER_FALSIFICATION_MAP` | `python -m bhsm.interface falsification-table --format markdown` |
| External reproduction packet v1.9 | Narrow unsent engine reproduction protocol | `artifacts/BHSM_external_reproduction_packet_v1_9.json` | `PREPARED_NOT_SENT` | `python -m bhsm.interface external-reproduction-packet --format markdown` |
| Primitive charged incidence v2.0 | Exact gcd, projector, overlap, bridge/beta, and CKM reciprocal identities with open action gates | `artifacts/BHSM_primitive_charged_incidence_closure_report_v2_0.json` | `EXACT_CONDITIONAL_ALGEBRA_WITH_OPEN_ACTION_GATES` | `python -m bhsm.interface primitive-charged-incidence-report --format markdown` |
| Action lemmas v2.1 | Exact log-averaging proof separated from open BHSM action and CKM application gates | `artifacts/BHSM_action_lemma_closure_report_v2_1.json` | `ABSTRACT_LOG_LEMMA_PROVEN_ACTION_APPLICATIONS_OPEN` | `python -m bhsm.interface action-lemma-closure-report --format markdown` |
| CKM channel equivalence v2.2 | Exact competing channel counts and action-selection/application gates | `artifacts/BHSM_ckm_channel_equivalence_report_v2_2.json` | `OPEN_MISSING_CKM_CHANNEL_EQUIVALENCE_THEOREM` | `python -m bhsm.interface ckm-channel-equivalence-report --format markdown` |
| Hermitian bidirectional CKM channel v2.3 | Exact adjoint-pair count, source audit, alternatives, and CKM application gate | `artifacts/BHSM_ckm_bidirectional_channel_report_v2_3.json` | `CONDITIONAL_HERMITIAN_BIDIRECTIONAL_CKM_CHANNEL_CANDIDATE` | `python -m bhsm.interface ckm-bidirectional-channel-report --format markdown` |
| Normalized action CKM adjoint-pair v2.5 | Source search, Hermitian rule audit, normalized-action selection gate, transport-space gate, and alternative blockers | `artifacts/BHSM_normalized_action_adjoint_pair_selection_v2_5.json` | `OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION` | `python -m bhsm.interface normalized-action-adjoint-pair-report --format markdown` |
| Charged-current action transport-space v2.6 | Normalized charged-current action search, candidate term audit, competing transport spaces, Hermitian adjoint-pair gate, and CKM application gate | `artifacts/BHSM_charged_current_transport_space_audit_v2_6.json` | `OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE` | `python -m bhsm.interface charged-current-action-report --format markdown` |
| CERN ROOT integration status | Header-only mapper, PyROOT wrapper, and pinned-container C++ smoke gate | `integrations/cern-root/integration_status.json` | `ROOT_ADAPTER_LIVE_COMPILED_IN_CI_NOT_PRODUCTION_VALIDATED` | See `integrations/cern-root/README.md` |
| Theorem closure | Strict proof-gate report | `artifacts/BHSM_theorem_closure_report_v0_4.json` | `OPEN` | `python -m bhsm.interface theorem-closure-report` |
| CP O_int Sprint B | Staged interaction-attachment audit | `artifacts/BHSM_cp_o_int_attachment_report_v0_5.json` | `OPEN` | `python -m bhsm.interface cp-o-int-report` |
| CP O_int Sprint C | Callable symbolic field/action candidate | `artifacts/BHSM_cp_o_int_field_action_report_v0_6.json` | `CANDIDATE / OPEN` | `python -m bhsm.interface cp-o-int-field-action` |
| Minimal action report | Three-theorem action audit | `artifacts/BHSM_minimal_action_report_v0_8.json` | `OPEN` | `python -m bhsm.interface minimal-action-report` |
| Minimal action decisions | CP, `X_ch`, and neutrino first-missing-object records | `artifacts/BHSM_minimal_action_closure_manifest_v0_8.json` | `OPEN` | `python -m bhsm.interface minimal-action-status` |
| Claim policy | Consolidated allowed and unsupported claims | `artifacts/BHSM_clean_claims_index_v0_7.json` | `ESTABLISHED` | See `CLAIMS.md` |
| CKM bounded-interface normalization v2.7 | Bounded term, projector sandwich, paired normalization, CKM identification, and transport selection gates | `artifacts/BHSM_ckm_transport_space_selection_v2_7.json` | `OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION` | `python -m bhsm.interface ckm-bounded-interface-report --format markdown` |
| CKM boundary-measure normalization v2.8 | Symbolic measure, coefficient, same-term pairing, projector, and transport blockers | `artifacts/BHSM_normalized_ckm_action_candidate_v2_8.json` | `OPEN_MISSING_NORMALIZED_CKM_ACTION_CANDIDATE` | `python -m bhsm.interface ckm-boundary-measure-normalization-report --format markdown` |
| CKM coefficient form/value v2.9 | Weak coefficient form, runtime/registered sources, convention, and attachment blocker | `artifacts/BHSM_ckm_coefficient_form_v2_9.json` | `ARTIFACT_BACKED_CKM_COEFFICIENT_FORM` | `python -m bhsm.interface ckm-coefficient-form-report --format markdown` |
| Normalized weak gauge action source v3.0 | Conditional algebra, action skeleton, trace normalization, runtime/registered coupling provenance, and open overall coefficient | `artifacts/BHSM_weak_gauge_action_source_report_v3_0.json` | `OPEN_MISSING_NORMALIZED_WEAK_GAUGE_ACTION_COEFFICIENT` | `python -m bhsm.interface weak-gauge-action-source-report --format markdown` |
| Gauge-coupling quantum v3.1 | Registered `1:2:7` pattern, candidate weight source, volume denominator, action attachment, and downstream value gates | `artifacts/BHSM_gauge_coupling_quantum_report_v3_1.json` | `OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM` | `python -m bhsm.interface gauge-coupling-quantum-report --format markdown` |

<!-- BHSM_FULL_ACTION_CLOSURE_V4_0 -->
### v4.0 artifact package

The canonical package consists of `artifacts/BHSM_full_action_status_snapshot_v4_0.json`,
`artifacts/BHSM_full_theorem_blocker_dag_v4_0.json`, and the twelve sector gate artifacts
named `artifacts/BHSM_*_v4_0.json`. The materializer is
`scripts/materialize_full_action_closure_v4_0.py`.

## Full action closure v4.0

Status: `FULL_BHSM_NOT_COMPLETE`.

The deterministic blocker DAG is in [docs/full_theorem_blocker_dag.md](docs/full_theorem_blocker_dag.md) and
`artifacts/BHSM_full_theorem_blocker_dag_v4_0.json`.

- BHSM is not complete until the full action-normalization and scale gates close.
- The 1:2:7 gauge-coupling registry pattern is artifact-backed but not action-derived.
- The candidate denominator 6π² = 3 Vol(S³) is not a coupling derivation unless attached to the normalized gauge action.
- Sector weights do not derive gauge couplings without action attachment.
- The overall gauge-action coefficient k remains open unless fixed by the action.
- The CKM coefficient form is artifact-backed, but the CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived unless all CKM action, transport, identification, and log-averaging gates close.
- Dimensionless neutral/PMNS structure does not imply physical neutrino masses.
- Physical Delta m², matter effects, radiative corrections, stiffness length, curvature, and unit normalization remain open unless separately derived.
- Full BHSM completion is not claimed by this repository unless every completion gate passes.

<!-- BHSM_BOUNDARY_COLLAR_MEASURE_V4_1 -->
### v4.1 artifact package

The twelve canonical artifacts are named `artifacts/BHSM_*_v4_1.json` and are generated
deterministically by `scripts/materialize_boundary_collar_measure_v4_1.py` from
`bhsm.interface.boundary_collar_measure`.

## Boundary/collar measure v4.1

Measure status: `CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE`. Three coframe directions:
`ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS`. Unit-S3 normalization, frame averaging,
gauge trace attachment, and the gauge denominator remain open.

- The mathematical identity Vol(S³_unit)=2π² is not by itself a gauge-coupling derivation.
- The candidate denominator 6π² = 3 Vol(S³_unit) is not action-derived unless BHSM supplies an action-selected three-frame boundary average.
- A three-frame decomposition does not by itself imply a frame average.
- A frame average does not derive gauge couplings unless attached to gauge trace densities in the normalized action.
- The gauge coupling quantum λ_gauge = 1/(6π²) remains open unless the denominator is action-attached.
- The α_i values remain open unless the gauge quantum, sector weights, and action coefficient are attached by the normalized action.
- g2_BH remains open unless α2_BH is action-derived and the weak convention applies.
- The CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived.
- Full BHSM remains not complete unless all action-normalization and scale gates close.

<!-- BHSM_BERGER_FRAME_WEIGHTING_V4_2 -->
### v4.2 artifact package

The eleven canonical artifacts are named `artifacts/BHSM_*_v4_2.json` and are generated by
`scripts/materialize_berger_frame_weighting_v4_2.py` from `bhsm.interface.berger_frame_weighting`.

## Berger frame weighting v4.2

Equal weighting and frame-average normalization remain open. Berger anisotropy compatibility is
conditional on an action-selected orthonormal gauge coframe. Gauge attachment and all downstream
coupling gates remain open.

- Three artifact-backed Berger frame directions do not by themselves imply equal weighting.
- Equal weighting does not by itself imply average normalization by 1/3.
- Average normalization does not by itself attach to gauge trace densities.
- Berger anisotropy must be checked before equal frame averaging can be promoted.
- The denominator 1/[3 Vol(S³)] remains open unless equal frame averaging, unit-volume normalization, and gauge-trace attachment are supported.
- The gauge coupling quantum remains open unless the denominator is action-attached.
- α_i, g2_BH, CKM coefficient value, and CKM exponent remain open unless downstream action gates close.
- Full BHSM remains not complete.

<!-- BHSM_GAUGE_COFRAME_HODGE_V4_3 -->
### v4.3 artifact package

Nine canonical `artifacts/BHSM_*_v4_3.json` files are generated by
`scripts/materialize_gauge_coframe_hodge_v4_3.py`.

## Gauge coframe/Hodge v4.3

Gauge coframe basis remains open; Hodge-star metric dependence is conditional. Equal coefficients, frame averaging, gauge attachment, denominator, and downstream couplings remain open.

- Equal frame coefficients in an orthonormal coframe are distinct from equal coefficients in the raw Berger coframe.
- Hodge-star metric factors may absorb Berger anisotropy, but this does not by itself imply frame averaging by 1/3.
- Equal orthonormal coefficients do not imply average normalization.
- Average normalization does not imply gauge trace attachment.
- Gauge couplings, CKM coefficient value, and full BHSM completion remain open unless downstream gates close.

<!-- BHSM_BERGER_HODGE_COMPONENT_V4_4 -->
## Berger Hodge component map v4.4

The explicit component map is conditionally derived from the Berger metric and chosen orientation. Gauge-action coframe selection, equal action coefficients, frame averaging, attachment, denominator, and downstream couplings remain open.

- An explicit Berger Hodge-star component map is distinct from selecting the gauge-action coframe basis.
- The orthonormal coframe e^a absorbs Berger metric scale factors, while raw sigma_a components retain anisotropic Hodge factors.
- A component Hodge map does not by itself imply equal gauge-frame coefficients.
- Equal coefficients do not by themselves imply average normalization by 1/3.
- Gauge trace Hodge expansion does not by itself derive gauge couplings.
- The denominator 1/[3 Vol(S^3)] remains open unless frame averaging, unit volume normalization, and gauge-action attachment are all supported.
- alpha_i, g2_BH, CKM coefficient value, CKM exponent, and full BHSM completion remain open unless downstream gates close.

<!-- BHSM_CASIMIR_SHELL_SPECTRAL_RESIDUE_V4_5 -->
## Casimir-shell spectral residue v4.5

BHSM should not interpret w=(1,2,7) as gauge-boson counts. Gauge algebra dimensions remain (1,3,8). The candidate interpretation is that w=(1,2,7) are active Casimir-shell spectral residues: U(1) retains its sole abelian amplitude channel, while SU(2) and SU(3) separate one radial quadratic Casimir coordinate into the relative-boundary scale layer, leaving tangent residues 2 and 7. The universal factor 1/(6π²) is a candidate 3D boundary Weyl-density coefficient. The resulting λ_i=w_i/(6π²) is a candidate whitened boundary fluctuation covariance density. The action must still derive inverse-covariance placement and coupling identification before α_i is claimed as derived.

Statuses: `CASIMIR_SHELL_RESIDUE_STRONG_CANDIDATE`, `SPECTRAL_DENSITY_GAUGE_QUANTUM_CONDITIONAL`, `WHITENED_BOUNDARY_FLUCTUATION_CONDITIONAL`, and `INVERSE_COVARIANCE_PLACEMENT_CONDITIONAL`. All action and downstream gates remain open.

### Artifacts

- `artifacts/BHSM_casimir_shell_residue_v4_5.json`
- `artifacts/BHSM_spectral_density_gauge_quantum_v4_5.json`
- `artifacts/BHSM_whitened_boundary_operator_v4_5.json`
- `artifacts/BHSM_inverse_covariance_placement_v4_5.json`
- `artifacts/BHSM_open_gates_v4_5.json`

### Invalidations

1. Direct classical Yang-Mills density alone does not derive w=(1,2,7); it sees the radial norm R_i^2, not the angular dimension dim(g_i)-1.
2. Raw Green covariance of A_i does not scale as Weyl mode counting; the density belongs to whitened modes B_i=L_i^(1/2)A_i.
3. A fixed rank-7 SU(3) subalgebra or projector is not the primitive object; the candidate is the field-dependent tangent residue of the adjoint Casimir shell.
4. Leading Weyl density alone does not produce physical running; Z_i, lower spectral corrections, and an action-selected rho_i(mu) remain open.

### Open gates

- `OPEN_MISSING_CASIMIR_SHELL_ACTION_ATTACHMENT`
- `OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_L_i`

- `OPEN_MISSING_WHITENED_BOUNDARY_OPERATOR_ACTION_SOURCE`
- `OPEN_MISSING_SPECTRAL_COVARIANCE_SOURCE`
- `OPEN_MISSING_INVERSE_COVARIANCE_ACTION_ATTACHMENT`
- `OPEN_MISSING_SPECTRAL_CORRECTION_Z_i`
- `OPEN_MISSING_ACTION_SELECTED_RHO_i_OF_MU`
- `OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION`
- `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`
- `OPEN_MISSING_ALPHA_I_ACTION_DERIVATION`
- `OPEN_MISSING_G2_BH_ACTION_SOURCE`
- `OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE`
- `CKM_EXPONENT_NOT_DERIVED`
- `FULL_BHSM_NOT_COMPLETE`


<!-- BHSM_SECTOR_BOUNDARY_OPERATOR_V4_6 -->
## Sector boundary operator / whitened gauge action v4.6

BHSM v4.6 treats the sector boundary kinetic operator L_i(ρ) as a conditional Laplace-type candidate on active adjoint-valued boundary one-form fluctuations over the relative Berger boundary Σ_ρ. The operator is used only to define a whitened boundary fluctuation B_i=L_i(ρ)^{1/2}A_i and a candidate inverse-covariance quadratic action S_i=(1/2λ_i)<A_i,L_i(ρ)A_i>. The three boundary coframe channels are evaluated through the normalized primitive frame state τ_frame=1/3, so the raw one-form factor of three does not overcount the active residue. The v4.5 residue λ_i=w_i/(6π²) remains a conditional whitened fluctuation covariance density, not yet a derived physical gauge coupling. The action source for L_i(ρ), the gauge-fixed boundary domain, lower-order curvature/collar terms, Z_i(μ,ρ), ρ_i(μ), α_i identification, g2_BH, CKM value/exponent, and full BHSM completion remain open.

Statuses: `SECTOR_BOUNDARY_OPERATOR_CONDITIONAL_CANDIDATE`, `LAPLACE_TYPE_PRINCIPAL_SYMBOL_CONDITIONAL`, `FRAME_NORMALIZED_PRINCIPAL_RESIDUE_CONDITIONAL`, and `WHITENED_GAUGE_ACTION_CONDITIONAL`.

### Artifacts

- `artifacts/BHSM_sector_boundary_operator_v4_6.json`
- `artifacts/BHSM_whitened_gauge_action_v4_6.json`
- `artifacts/BHSM_boundary_operator_principal_symbol_v4_6.json`
- `artifacts/BHSM_frame_normalized_principal_residue_v4_6.json`
- `artifacts/BHSM_gauge_fixed_domain_gate_v4_6.json`
- `artifacts/BHSM_lower_order_operator_terms_gate_v4_6.json`
- `artifacts/BHSM_v4_6_open_gates.json`

### Invalidations

1. A raw unrestricted one-form Weyl count introduces a factor of three; the conditional primitive frame state tau_frame=1/3 prevents this overcount.
2. A Laplace-type principal symbol does not determine the full physical boundary operator; lower-order terms and the action source remain open.
3. L_i(rho) is not final on unrestricted gauge potentials without a gauge-fixed, transverse/coexact, quotient, or admissible boundary domain.
4. Whitened boundary-action coherence does not prove lambda_i=alpha_i; physical coupling identification remains action-gated.
5. Leading Weyl density plus candidate L_i does not produce running without Z_i, lower heat-kernel/collar corrections, and action-selected rho_i(mu).
6. This sprint does not derive gauge couplings, CKM values or exponent, or full BHSM completion.

### Open gates

- `OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_ACTION_SOURCE`
- `OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN`
- `OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS`
- `OPEN_MISSING_WHITENED_BOUNDARY_OPERATOR_ACTION_SOURCE`
- `OPEN_MISSING_SPECTRAL_COVARIANCE_SOURCE`
- `OPEN_MISSING_INVERSE_COVARIANCE_ACTION_ATTACHMENT`
- `OPEN_MISSING_SPECTRAL_CORRECTION_Z_i`
- `OPEN_MISSING_ACTION_SELECTED_RHO_i_OF_MU`
- `OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION`
- `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`
- `OPEN_MISSING_ALPHA_I_ACTION_DERIVATION`
- `OPEN_MISSING_G2_BH_ACTION_SOURCE`
- `OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE`
- `CKM_EXPONENT_NOT_DERIVED`
- `FULL_BHSM_NOT_COMPLETE`
- `OPEN_MISSING_CASIMIR_SHELL_ACTION_ATTACHMENT`
- `OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_L_i`

<!-- BHSM_GAUGE_COUPLING_ACTION_ATTACHMENT_KILLSCREEN_V4_7 -->
## Gauge-coupling action-attachment kill screen v4.7

| Artifact | Verdict | Purpose |
|---|---|---|
| `artifacts/BHSM_gauge_coupling_action_attachment_killscreen_v4_7.json` | `ACTION_ATTACHMENT_BLOCKED` | Tests all action-attachment escape routes and stops the spectral candidate from being promoted to physical `alpha_i`. |

Doctrine: `docs/bhsm_gauge_coupling_action_attachment_killscreen_v4_7.md`.

<!-- BHSM_CKM_RELATIVE_CURRENT_NORMALIZATION_KILLSCREEN_V4_8 -->
## CKM-relative current normalization kill screen v4.8

| Artifact | Verdict | Purpose |
|---|---|---|
| `artifacts/BHSM_ckm_relative_current_normalization_killscreen_v4_8.json` | `CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED` | Audits whether CKM-relative geometry derives `c_rel^2=4*pi` and preserves the v4.7 block when it does not. |

Doctrine: `docs/bhsm_ckm_relative_current_normalization_killscreen_v4_8.md`.

<!-- BHSM_COUPLING_BRIDGE_BLOCKER_CONSOLIDATION_V4_9 -->
## Coupling-bridge blocker consolidation v4.9

| Artifact | Verdict | Purpose |
|---|---|---|
| `artifacts/BHSM_coupling_bridge_blocker_consolidation_v4_9.json` | `COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE` | Consolidates v4.5–v4.8, freezes both blocked bridges, and records the CKM transport pivot. |

Doctrine: `docs/bhsm_coupling_bridge_blocker_consolidation_v4_9.md`.

<!-- BHSM_RARE_B_AFB_ZERO_FORWARD_PREDICTION_V5_0 -->
## Rare-B A_FB zero forward-prediction kill screen v5.0

| Artifact | Verdict | Purpose |
|---|---|---|
| `artifacts/BHSM_rare_b_afb_zero_forward_prediction_v5_0.json` | `RARE_B_AFB_ZERO_PREDICTION_BLOCKED` / `RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED` | Tests whether existing BHSM artifacts produce a no-fit rare-B `A_FB(q^2)` zero prediction or exact micro-plateau node coordinates; records the missing observable map when they do not. |

Doctrine: `docs/bhsm_rare_b_afb_zero_forward_prediction_v5_0.md`.

<!-- BHSM_RARE_B_OBSERVABLE_MAP_SCAFFOLD_V5_1 -->
## Rare-B observable map scaffold v5.1

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_rare_b_observable_convention_v5_1.json` | `RARE_B_OBSERVABLE_INTERFACE_ARTIFACTED` | Defines `q^2`, `A_FB`, numerator/denominator semantics, `dGamma/dq^2`, and optional optimized-observable placeholders. |
| `artifacts/BHSM_rare_b_transition_operator_interface_v5_1.json` | `RARE_B_TRANSITION_OPERATOR_INTERFACE_ARTIFACTED` | Defines `b -> s mu+ mu-` operator-basis and Wilson-coefficient slots without deriving them. |
| `artifacts/BHSM_rare_b_hadronic_interface_v5_1.json` | `RARE_B_HADRONIC_FORM_FACTOR_INTERFACE_ARTIFACTED` | Defines exclusive-channel form-factor inputs and preserves open BHSM hadronic derivation. |
| `artifacts/BHSM_rare_b_afb_null_balance_v5_1.json` | `RARE_B_AFB_NULL_BALANCE_INTERFACE_ARTIFACTED` | Separates `A_FB=N_FB/D_FB` from the numerator zero condition and nonzero-denominator domain gate. |
| `artifacts/BHSM_rare_b_bhsm_matching_map_v5_1.json` | `RARE_B_BHSM_MATCHING_MAP_OPEN_DEPENDENCY_GRAPH_ARTIFACTED` | Lists required BHSM-to-effective-rare-B matching dependencies and blockers. |
| `artifacts/BHSM_rare_b_observable_map_audit_v5_1.json` | `RARE_B_OBSERVABLE_MAP_AUDIT_ARTIFACTED` | Records the repository audit and independent yes/no closure answers. |
| `artifacts/BHSM_rare_b_observable_map_scaffold_verdict_v5_1.json` | `RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE` | Final interface verdict with prediction kill screen and preserved blocked statuses. |

Doctrine: `docs/bhsm_rare_b_observable_map_scaffold_v5_1.md`.

<!-- BHSM_B_TO_S_MUMU_OPERATOR_MATCHING_KILLSCREEN_V5_2 -->
## b -> s mu+ mu- operator-matching kill screen v5.2

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_rare_b_bhsm_operator_source_inventory_v5_2.json` | `RARE_B_OPERATOR_SOURCE_INVENTORY_ARTIFACTED` | Inventories candidate BHSM charged-current, neutral-response, CKM, action, current, and rare-B interface sources and records why none closes the physical transition operator. |
| `artifacts/BHSM_b_to_s_mumu_transition_dependency_graph_v5_2.json` | `B_TO_S_MUMU_TRANSITION_DEPENDENCY_GRAPH_ARTIFACTED` | Encodes the operator-matching chain and marks the first open edge at the FCNC generation mechanism. |
| `artifacts/BHSM_b_to_s_mumu_operator_matching_candidate_v5_2.json` | `B_TO_S_MUMU_OPERATOR_MATCHING_CANDIDATE_EMPTY_BLOCKED` | Records that no coherent BHSM-derived candidate survives the kill screen while preserving external `O7/O9/O10` convention slots. |
| `artifacts/BHSM_b_to_s_mumu_operator_matching_audit_v5_2.json` | `B_TO_S_MUMU_OPERATOR_MATCHING_AUDIT_ARTIFACTED` | Answers the FCNC, current, chirality, action, loop, dimension, scale, Wilson, and prediction kill-screen questions independently. |
| `artifacts/BHSM_b_to_s_mumu_operator_matching_verdict_v5_2.json` | `B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED` | Final v5.2 verdict, preserved statuses, new blockers, null Wilson outputs, and prediction kill screen. |

Doctrine: `docs/bhsm_b_to_s_mumu_operator_matching_killscreen_v5_2.md`.

<!-- BHSM_RARE_B_FCNC_GENERATION_MECHANISM_V5_3 -->
## Rare-B FCNC generation-mechanism kill screen v5.3

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_rare_b_neutral_current_flavor_structure_audit_v5_3.json` | `RARE_B_NEUTRAL_CURRENT_FLAVOR_STRUCTURE_AUDIT_ARTIFACTED` | Audits neutral-current flavor structure and records that no tree-level action-backed `b-s` neutral current is derived. |
| `artifacts/BHSM_rare_b_charged_current_pair_composition_v5_3.json` | `RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION_BLOCKED` | Records the missing two-insertion charged-current composition needed upstream of an induced FCNC kernel. |
| `artifacts/BHSM_rare_b_intermediate_response_inventory_v5_3.json` | `RARE_B_INTERMEDIATE_RESPONSE_KERNEL_ABSENT` | Inventories possible response/kernel objects and records why none supplies rare-B intermediate propagation. |
| `artifacts/BHSM_rare_b_fcnc_generation_candidate_v5_3.json` | `RARE_B_FCNC_GENERATION_CANDIDATE_EMPTY_BLOCKED` | Records the empty FCNC-generation candidate with explicit open gates and null prediction state. |
| `artifacts/BHSM_rare_b_gim_like_cancellation_audit_v5_3.json` | `RARE_B_GIM_LIKE_CANCELLATION_THEOREM_ABSENT` | Audits degeneracy-cancellation requirements and rejects CKM unitarity alone as a full weighted-response theorem. |
| `artifacts/BHSM_rare_b_fcnc_generation_dependency_graph_v5_3.json` | `RARE_B_FCNC_GENERATION_DEPENDENCY_GRAPH_ARTIFACTED` | Extends the v5.2 graph upstream with explicit FCNC-generation mechanism nodes and the first open edge. |
| `artifacts/BHSM_rare_b_fcnc_generation_mechanism_verdict_v5_3.json` | `RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED` | Final v5.3 verdict, preserved statuses, refined blockers, null Wilson outputs, and prediction kill screen. |

Doctrine: `docs/bhsm_rare_b_fcnc_generation_mechanism_v5_3.md`.
