# BHSM Artifact Index

## B8 geometry–energy parent action v6.0.2

| Package | Contents | Primary artifact | Status | CLI |
| --- | --- | --- | --- | --- |
| Parent-action matrix, Lovelock/minimality audit, confinement and sigma sectors, bulk/boundary/collar equations, Hopf reduction, stationarity/Hessian, thresholds, reduction, and hidden inputs | Sixteen deterministic v6.0.2 artifacts | `artifacts/BHSM_b8_geometry_energy_parent_action_report_v6_0_2.json` | `BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED` / `BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED` | `python -m bhsm.interface b8-parent-action-status --format markdown` |

The package classifies a finite action family but does not select a physical
domain, coefficient normalization, confinement invariant, or stable phase.

## B8/S7 physical domain and action-source closure v6.0.1

| Package | Contents | Primary artifact | Status | CLI |
| --- | --- | --- | --- | --- |
| Domain/time/action matrix, B8/S7 embedding, metric/stationarity, measures, bundle pushforward, collar, physical-boundary map, S3 reclassification, scalar readiness, and hidden-input audit | Fourteen deterministic v6.0.1 artifacts | `artifacts/BHSM_b8_s7_physical_domain_action_source_closure_report_v6_0_1.json` | `BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING` | `python -m bhsm.interface b8-s7-physical-domain-status --format markdown` |

The package preserves the exact v6.0 topology while proving that no stored
v5.4-v6.0 action selects it as the physical dynamical domain.

## S7 fiber integration and physical localization v6.0

| Package | Contents | Primary artifact | Status | CLI |
| --- | --- | --- | --- | --- |
| S7 source inventory, exact fibration/nested diagram, metric-measure ledger, pushforward theorem, physical-domain fork, and action/collar localization | Eight deterministic v6.0 artifacts | `artifacts/BHSM_s7_fiber_integration_physical_localization_report_v6_0.json` | `BHSM_S7_ARCHITECTURE_AMBIGUOUS` | `python -m bhsm.interface s7-fiber-integration-status --format markdown` |

The topology and conditional pushforward theorem are derived; the physical S7/B8 action domain, metric, signature, orientation, fiber scale, and collar attachment remain open.

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

<!-- BHSM_UNIFIED_DYNAMICAL_ACTION_CONSTRUCTION_V5_4 -->
## Unified dynamical action construction v5.4

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_unified_dynamical_action_configuration_space_v5_4.json` | `UNIFIED_BHSM_CONFIGURATION_SPACE_DEFINED` | Defines the boundary/collar domain, measure, fields, sector/projector spaces, dynamical variables, fixed data, and admissible boundary conditions. |
| `artifacts/BHSM_unified_dynamical_action_candidate_v5_4.json` | `UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY` | Gives the explicit symbolic unified action candidate and term inventory. |
| `artifacts/BHSM_unified_action_coefficient_dimension_table_v5_4.json` | `UNIFIED_ACTION_COEFFICIENT_DIMENSION_TABLE_COMPLETE_SYMBOLIC` | Records every coefficient, sign convention, dependency, derivation status, and dimension check. |
| `artifacts/BHSM_unified_action_variational_equations_v5_4.json` | `UNIFIED_ACTION_VARIATIONAL_EQUATIONS_DERIVED_SYMBOLICALLY` | Stores symbolic operator equations and boundary terms for each active variable. |
| `artifacts/BHSM_unified_action_quadratic_operators_v5_4.json` | `UNIFIED_ACTION_QUADRATIC_OPERATORS_EXTRACTED_CONDITIONALLY` | Extracts the Hessian/quadratic operator blocks and their domain, adjoint, zero-mode, and response caveats. |
| `artifacts/BHSM_unified_action_interaction_source_map_v5_4.json` | `UNIFIED_ACTION_INTERACTION_SOURCE_MAP_CONSTRUCTED_CONDITIONALLY` | Maps interactions to source terms and variations while preserving open normalization and rare-B blockers. |
| `artifacts/BHSM_unified_action_dimensionful_scale_analysis_v5_4.json` | `UNIFIED_ACTION_DIMENSIONFUL_SCALE_ANALYSIS_SYMBOLIC_OPEN` | Separates dimensionless geometric normalization from the explicit open physical scale `Lambda_BH`. |
| `artifacts/BHSM_unified_action_reduced_model_v5_4.json` | `UNIFIED_ACTION_REDUCED_MODEL_DETERMINISTIC_STABLE` | Provides a deterministic coupled two-mode reduced model with equations, spectrum, stability check, and zero residual. |
| `artifacts/BHSM_unified_dynamical_action_construction_report_v5_4.json` | `UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY` | Final construction report with derived, symbolic, open, and preserved-claim statuses. |

Doctrine: `docs/bhsm_unified_dynamical_action_construction_v5_4.md`.

<!-- BHSM_PHYSICAL_SCALE_GENERATION_V5_5 -->
## Physical-scale generation v5.5

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_physical_scale_object_inventory_v5_5.json` | `SCALE_OBJECT_INVENTORY_COMPLETE` | Inventories boundary radius, collar, metric, curvature, volume, scalar/topographic amplitude, potential coefficients, spectra, Hessians, and running objects with dimension and absolute-scale status. |
| `artifacts/BHSM_physical_scale_candidate_comparison_v5_5.json` | `PHYSICAL_SCALE_CANDIDATES_COMPARED` | Compares geometric-radius, scalar/topographic vacuum, spectral, and transmutation candidates under action support, dimensional consistency, stability, uniqueness, inputs, and computability. |
| `artifacts/BHSM_selected_physical_scale_mechanism_v5_5.json` | `SCALAR_TOPOGRAPHIC_SCALE_VACUUM_SELECTED_CONDITIONALLY` | Selects the nonzero scalar/topographic scale-vacuum branch as the strongest conditional mechanism. |
| `artifacts/BHSM_physical_scale_equation_v5_5.json` | `PHYSICAL_SCALE_EQUATION_DERIVED_CONDITIONALLY` | Stores the scale equation `beta_scale sigma^3 - alpha_scale sigma = 0` and the nonzero branch `sqrt(alpha_scale/beta_scale)`. |
| `artifacts/BHSM_physical_scale_stability_analysis_v5_5.json` | `NONZERO_SCALE_BRANCH_STABLE_CONDITIONALLY` | Records the zero branch, nonzero Hessian `2 alpha_scale`, runaway condition, and sign degeneracy. |
| `artifacts/BHSM_physical_scale_dimension_unit_map_v5_5.json` | `DIMENSION_AND_UNIT_MAP_CONDITIONAL` | Maps dimensionless scale, length, inverse length, and mass/energy conversion while preserving the open unit anchor. |
| `artifacts/BHSM_physical_scale_operator_propagation_v5_5.json` | `PHYSICAL_SCALE_PROPAGATION_MAP_CONDITIONAL` | Shows how `M_BH` would enter fermion, gauge, scalar, boundary-mode, charged-current, neutral-response, and propagator structures. |
| `artifacts/BHSM_physical_scale_reduced_model_v5_5.json` | `REDUCED_SCALE_SETTING_MODEL_DETERMINISTIC_STABLE` | Provides a deterministic symbolic-unit reduced solution and stability check. |
| `artifacts/BHSM_physical_scale_generation_report_v5_5.json` | `BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY` | Final v5.5 report with derived, conditional, open, and preserved-claim statuses. |

Doctrine: `docs/bhsm_physical_scale_generation_v5_5.md`.

<!-- BHSM_SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVATION_V5_6 -->
## Scalar/topographic vacuum action derivation v5.6

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_scalar_topographic_order_parameter_v5_6.json` | `SCALE_ORDER_PARAMETER_DEFINED_CONDITIONALLY` | Defines `sigma_scale` as a normalized scalar/topographic mode coefficient and separates it from `sigma_profile`. |
| `artifacts/BHSM_scalar_topographic_action_source_v5_6.json` | `SCALAR_TOPOGRAPHIC_ACTION_SOURCE_ASSEMBLED_CONDITIONALLY` | Assembles `S_ST=S_T_bulk+S_Phi_internal+S_threshold+S_boundary+S_collar` from existing source conventions. |
| `artifacts/BHSM_scalar_topographic_variable_dictionary_v5_6.json` | `SCALAR_TOPOGRAPHIC_VARIABLE_DICTIONARY_COMPLETE` | Reconciles `T`, `Phi`, thresholds, profile width, `sigma_scale`, collar, curvature, coefficients, and unit anchors. |
| `artifacts/BHSM_scalar_topographic_reduced_vacuum_functional_v5_6.json` | `REDUCED_VACUUM_FUNCTIONAL_DERIVED_CONDITIONALLY` | Derives `V_eff` and expresses `alpha_scale`/`beta_scale` as reduced action functionals. |
| `artifacts/BHSM_scalar_topographic_vacuum_solution_v5_6.json` | `NONZERO_VACUUM_BRANCH_DERIVED_CONDITIONALLY` | Stores the branch equation, Hessian, stability, boundedness, and vacuum-energy result. |
| `artifacts/BHSM_curvature_threshold_expansion_audit_v5_6.json` | `CURVATURE_THRESHOLD_MASS_GAP_INVALIDATED_FOR_THIS_ACTION` | Expands the old curvature-threshold candidate and records that no mass term survives. |
| `artifacts/BHSM_scalar_topographic_unit_anchor_v5_6.json` | `UNIT_ANCHOR_REMAINS_OPEN` | Records that the vacuum fixes `M_BH/M_star` but not `M_star` or `ell_star`. |
| `artifacts/BHSM_physical_scale_v5_5_update_from_v5_6.json` | `V5_5_SCALE_BRANCH_UPDATED_BY_V5_6` | Updates v5.5 by replacing free scale coefficients with conditional action functionals. |
| `artifacts/BHSM_scalar_topographic_vacuum_reduced_model_v5_6.json` | `SCALAR_TOPOGRAPHIC_REDUCED_MODEL_STABLE` | Provides a deterministic reduced action solution and field-equation residual check. |
| `artifacts/BHSM_scalar_topographic_vacuum_action_derivation_report_v5_6.json` | `SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVED_CONDITIONALLY` | Final v5.6 construction report. |

Doctrine: `docs/bhsm_scalar_topographic_vacuum_action_derivation_v5_6.md`.

<!-- BHSM_SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSURE_V5_7 -->
## Scalar/topographic profile boundary closure v5.7

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_scalar_topographic_solved_profile_v5_7.json` | `SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY` | Stores the normalized homogeneous Berger-boundary profile solution, variable dictionary, boundary data, mode normalization, and reduced residuals. |
| `artifacts/BHSM_scalar_topographic_evaluated_vacuum_functional_v5_7.json` | `VACUUM_FUNCTIONAL_EVALUATED_CONDITIONALLY` | Evaluates `A_ST=-2`, `C_ST=0`, `G_ST=8`, `alpha_scale=2`, `beta_scale=8`, branch data, finite-difference checks, and component contributions. |
| `artifacts/BHSM_scalar_topographic_hessian_response_v5_7.json` | `HESSIAN_RESPONSE_CONSTRUCTED_ON_REDUCED_DOMAIN` | Records the reduced Hessian, eigenvalues, Green/response eigenvalues, zero/negative-mode status, and old mass-gap invalidation guard. |
| `artifacts/BHSM_scalar_topographic_profile_boundary_closure_report_v5_7.json` | `SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY` | Final v5.7 report, including v5.5/v5.6 updates and preserved open gates. |

Doctrine: `docs/bhsm_scalar_topographic_profile_boundary_closure_v5_7.md`.

<!-- BHSM_ABSOLUTE_UNIT_ANCHOR_GENERATION_V5_8 -->
## Absolute unit-anchor generation v5.8

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_primordial_compact_state_v5_8.json` | `PRIMORDIAL_COMPACT_STATE_DEFINED_AS_CANDIDATE` | Defines the normalized primordial compact Berger-Hopf state, candidate invariants, and primordial-to-late-time doctrine. |
| `artifacts/BHSM_absolute_unit_scale_modulus_audit_v5_8.json` | `ABSOLUTE_UNIT_SCALE_MODULUS_NOT_FIXED` | Audits `g=L^2 g_hat`, action scaling terms, spectral/topological candidates, and the flat global size modulus. |
| `artifacts/BHSM_absolute_unit_propagation_v5_8.json` | `UNIT_PROPAGATION_BLOCKED_PENDING_ABSOLUTE_ANCHOR` | Records which physical-unit operator maps remain blocked until `ell_star` or `M_star` exists. |
| `artifacts/BHSM_absolute_unit_anchor_generation_report_v5_8.json` | `BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED` | Final v5.8 report with derived, conditional, open, and claim-boundary statuses. |

Doctrine: `docs/bhsm_absolute_unit_anchor_generation_v5_8.md`.

<!-- BHSM_PILOT_WAVE_SCALE_MODULUS_DYNAMICS_V5_9 -->
## Pilot-wave scale-modulus dynamics v5.9

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_pilot_wave_canonical_hamiltonian_v5_9.json` | `REDUCED_CANONICAL_DYNAMICS_DERIVED_CONDITIONALLY` | Stores the reduced action, Hamiltonian, constraint, Hamilton equations, and v5.8 flat-L preservation check. |
| `artifacts/BHSM_pilot_wave_configuration_metric_v5_9.json` | `CONFIGURATION_SPACE_METRIC_AND_MEASURE_DEFINED` | Defines the reduced scale-covariant configuration metric, measure, and rescaling behavior. |
| `artifacts/BHSM_pilot_wave_wave_equation_v5_9.json` | `BHSM_REDUCED_WAVE_EQUATION_DERIVED_CONDITIONALLY` | Records the timeless pilot-wave equation, Laplace-Beltrami operator, ontology separation, and boundary-state caveat. |
| `artifacts/BHSM_pilot_wave_bohmian_guidance_v5_9.json` | `BOHMIAN_DECOMPOSITION_AND_GUIDANCE_DERIVED_CONDITIONALLY` | Stores the quantum Hamilton-Jacobi equation, continuity equation, quantum potential, guidance law, and current residual. |
| `artifacts/BHSM_pilot_wave_quantum_potential_scaling_audit_v5_9.json` | `PILOT_WAVE_QUANTUM_DYNAMICS_SCALE_COVARIANT` | Audits global scale covariance and records that the quantum force does not select finite `L0`. |
| `artifacts/BHSM_pilot_wave_primordial_boundary_state_v5_9.json` | `PRIMORDIAL_QUANTUM_BOUNDARY_STATE_NOT_UNIQUELY_DERIVED` | Records the outgoing-branch option and the open boundary-state source for width, turning point, and absolute `L`. |
| `artifacts/BHSM_pilot_wave_deterministic_trajectory_v5_9.json` | `GUIDED_COMPACT_TO_EXPANDING_TRAJECTORY_CONSTRUCTED_CONDITIONALLY` | Gives the analytic guidance trajectory `L(tau)=L_initial exp(k tau)` with `sigma_scale=1/2`. |
| `artifacts/BHSM_pilot_wave_hidden_scale_audit_v5_9.json` | `NO_HIDDEN_SCALE_PROMOTED` | Audits hidden scale sources such as width, box, regulator, chart, endpoint, factor ordering, and initial coordinate. |
| `artifacts/BHSM_pilot_wave_scale_modulus_dynamics_report_v5_9.json` | `BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS` | Final v5.9 report with derived, conditional, open, invalidated, and preserved-claim statuses. |

Doctrine: `docs/bhsm_pilot_wave_scale_modulus_dynamics_v5_9.md`.

<!-- BHSM_QUANTUM_EFFECTIVE_ACTION_CASIMIR_BACKREACTION_V5_10 -->
## Quantum effective action and Casimir backreaction v5.10

Primary result: `BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL`.

| Artifact | Status | Purpose |
|---|---|---|
| `artifacts/BHSM_quantum_mode_ownership_v5_10.json` | `QUANTUM_MODE_OWNERSHIP_LEDGER_PARTIAL_EXPLICIT` | Separates retained collective variables from integrated and excluded fluctuations to prevent one-loop/pilot-wave double counting. |
| `artifacts/BHSM_quantum_euclidean_operator_domain_ledger_v5_10.json` | `EUCLIDEAN_OPERATOR_LEDGER_PARTIAL_FULL_DETERMINANT_BLOCKED` | Audits Euclidean continuation, domains, adjoints, ellipticity, zero modes, negative modes, and determinant eligibility. |
| `artifacts/BHSM_quantum_gauge_fixing_ghost_audit_v5_10.json` | `GAUGE_AND_GHOST_DETERMINANT_BLOCKED` | Records that no final gauge-fixing functional, ghost operator, boundary condition, or zero-mode quotient is derived. |
| `artifacts/BHSM_quantum_berger_hopf_spectral_ledger_v5_10.json` | `BERGER_HOPF_SPECTRAL_LEDGER_CONTROLLED_REDUCED_SUBSET` | Gives the exact two-mode homogeneous v5.7 ledger while integrating only the mode orthogonal to retained `sigma_scale`. |
| `artifacts/BHSM_quantum_heat_kernel_divergence_v5_10.json` | `FINITE_REDUCED_HEAT_TRACE_EXACT_FIELD_THEORY_DIVERGENCES_OPEN` | Separates the exact finite heat trace from unavailable full Seeley-DeWitt and ultraviolet data. |
| `artifacts/BHSM_quantum_renormalization_counterterm_v5_10.json` | `RENORMALIZATION_NOT_CLOSED_MU_EXPLICIT` | Keeps `mu` explicit and records missing counterterms, running coefficients, scheme closure, and RG invariance. |
| `artifacts/BHSM_quantum_zeta_determinant_v5_10.json` | `EXACT_FINITE_REDUCED_ZETA_DETERMINANT_COMPUTED` | Computes the one included bosonic determinant and direct/zeta equality without a cutoff. |
| `artifacts/BHSM_quantum_casimir_trace_anomaly_v5_10.json` | `CASIMIR_AND_TOTAL_ANOMALY_NOT_DERIVED_REDUCED_SCALE_RESPONSE_ONLY` | Leaves physical Casimir/anomaly outputs null and records only the reduced one-mode scale response. |
| `artifacts/BHSM_quantum_backreaction_equations_v5_10.json` | `REDUCED_PARTIAL_BACKREACTION_EQUATIONS_DERIVED` | Derives the partial `(L,a_Berger,sigma_scale,rho_star)` force equations and unresolved stress components. |
| `artifacts/BHSM_quantum_effective_modulus_solution_v5_10.json` | `NO_FINITE_STABLE_EFFECTIVE_MODULUS_SOLUTION_IN_PARTIAL_SYSTEM` | Shows the partial `-1/L` force has no finite positive stationary point and no positive coupled Hessian. |
| `artifacts/BHSM_quantum_pilot_wave_no_double_counting_update_v5_10.json` | `PILOT_WAVE_UPDATE_DEFERRED_PARTIAL_EFFECTIVE_ACTION_NO_DOUBLE_COUNTING_EXPLICIT` | Preserves v5.9 while defining the future effective-action-to-pilot-wave hierarchy. |
| `artifacts/BHSM_quantum_uploaded_source_audit_v5_10.json` | `UPLOADED_SOURCE_CANDIDATES_AUDITED_NOT_USED_AS_SCALE_INPUTS` | Prevents manuscript descriptions, legacy mass ansatzes, or cosmology coefficients from becoming hidden inputs. |
| `artifacts/BHSM_quantum_effective_action_casimir_backreaction_report_v5_10.json` | `BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL` | Final report with derived, conditional, invalidated, open, and claim-boundary statuses. |

Doctrine: `docs/bhsm_quantum_effective_action_casimir_backreaction_v5_10.md`.

<!-- BHSM_FULL_GEOMETRIC_GAUGE_FIXED_HESSIAN_V5_11 -->
## Full geometric and gauge-fixed Hessian v5.11

Primary result: `BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL`.

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_full_hessian_field_gauge_symmetry_ledger_v5_11.json` | Complete field and symmetry inventory. |
| `artifacts/BHSM_full_hessian_background_stationarity_v5_11.json` | Background, tadpole, and stationarity ledger. |
| `artifacts/BHSM_full_hessian_second_variation_block_map_v5_11.json` | Source-qualified map of all 36 Hessian blocks. |
| `artifacts/BHSM_full_hessian_geometric_gauge_ghost_v5_11.json` | Geometric gauge/ghost and conformal-mode audit. |
| `artifacts/BHSM_full_hessian_primordial_boundary_tension_surface_mode_v5_11.json` | Candidate vacuum boundary tension, stress, normal shape equation, surface Hessian, release threshold, and scale classification. |
| `artifacts/BHSM_full_hessian_internal_gauge_ghost_v5_11.json` | Internal gauge/ghost architecture. |
| `artifacts/BHSM_full_hessian_fermion_dirac_domain_eta_v5_11.json` | Dirac, domain, current, index, and eta ledger. |
| `artifacts/BHSM_full_hessian_scalar_topographic_v5_11.json` | Formal full scalar matrix and exact homogeneous reduction. |
| `artifacts/BHSM_full_hessian_charged_neutral_classification_v5_11.json` | Charged/neutral determinant ownership. |
| `artifacts/BHSM_full_hessian_boundary_self_adjointness_v5_11.json` | Boundary forms and adjoint-domain audit. |
| `artifacts/BHSM_full_hessian_principal_symbol_ellipticity_v5_11.json` | Principal symbols and strong ellipticity status. |
| `artifacts/BHSM_full_hessian_zero_negative_modes_v5_11.json` | Zero, collective, and negative-mode accounting. |
| `artifacts/BHSM_full_hessian_heat_kernel_readiness_v5_11.json` | Laplace-form input readiness. |
| `artifacts/BHSM_full_hessian_reduced_operator_complex_v5_11.json` | Finite gauge/ghost consistency model. |
| `artifacts/BHSM_full_geometric_gauge_fixed_hessian_report_v5_11.json` | Focused construction report and next sprint. |

Doctrine: `docs/bhsm_full_geometric_gauge_fixed_hessian_v5_11.md`.

<!-- BHSM_PRIMORDIAL_BOUNDARY_TENSION_ACTION_SOURCE_CLOSURE_V5_12 -->
## Primordial boundary-tension action source closure v5.12

Primary result: `BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED`.

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_primordial_boundary_collar_action_source_v5_12.json` | Exact stored term/source and coefficient ledger. |
| `artifacts/BHSM_primordial_boundary_dimension_localization_v5_12.json` | Physical-domain, coefficient-dimension, and `V_red` localization audit. |
| `artifacts/BHSM_primordial_boundary_stress_tensor_v5_12.json` | Variational stress definition and source-separated contributions. |
| `artifacts/BHSM_primordial_normal_displacement_variations_v5_12.json` | Convention-controlled normal geometry identities. |
| `artifacts/BHSM_primordial_inside_outside_pressure_v5_12.json` | Static, threshold, and post-release pressure separation. |
| `artifacts/BHSM_primordial_curvature_bending_coefficients_v5_12.json` | `c_K`, `c_K2`, `c_S`, GHY, counterterm, and source audit. |
| `artifacts/BHSM_primordial_collar_jacobian_stress_v5_12.json` | Active Jacobian, collar stress, and normalized `rho_star` status. |
| `artifacts/BHSM_primordial_normal_shape_equation_v5_12.json` | Fully source-statused normal shape architecture. |
| `artifacts/BHSM_primordial_surface_hessian_eigenproblem_v5_12.json` | Surface operator, spectrum, domain, and scaling architecture. |
| `artifacts/BHSM_primordial_release_threshold_crossing_v5_12.json` | Release requirements and competing-scaling theorem. |
| `artifacts/BHSM_primordial_absolute_unit_one_scale_v5_12.json` | Absolute-unit and minimal-one-scale classification. |
| `artifacts/BHSM_primordial_release_energy_conversion_v5_12.json` | Pilot-wave and primordial conversion ledger. |
| `artifacts/BHSM_primordial_reduced_threshold_model_v5_12.json` | Exact reduced roots, crossing classes, and scale covariance. |
| `artifacts/BHSM_primordial_boundary_tension_action_source_closure_report_v5_12.json` | Final derived, conditional, invalidated, and open result. |
| `artifacts/BHSM_spacetime_recycling_candidate_action_v5_12.json` | Candidate top-form action, field equation, normalization, boundary ensemble, and source search. |
| `artifacts/BHSM_spacetime_recycling_top_form_dimension_degree_v5_12.json` | Symbolic bulk dimension, form degree, source-worldvolume, and physical-dimension audit. |
| `artifacts/BHSM_spacetime_recycling_core_source_flux_jump_v5_12.json` | Core-source support, current conservation, conditional flux jump, and information doctrine. |
| `artifacts/BHSM_spacetime_recycling_stress_energy_pressure_v5_12.json` | Candidate metric stress, normal projection, and fixed-flux versus fixed-charge pressure. |
| `artifacts/BHSM_spacetime_recycling_causal_constraint_audit_v5_12.json` | Canonical constraints, local/global degrees of freedom, and no-signal boundary. |
| `artifacts/BHSM_spacetime_recycling_zero_point_flux_energy_v5_12.json` | Vacuum-floor, excited flux-sector, and local-interference separation. |
| `artifacts/BHSM_spacetime_recycling_primordial_late_time_map_v5_12.json` | Primordial and late-time source regimes with prohibited cosmological promotions. |

Doctrine: `docs/bhsm_primordial_boundary_tension_action_source_closure_v5_12.md`.

<!-- BHSM_ENERGY_GEOMETRY_CONFINEMENT_INVARIANT_V6_0_3 -->
## Energy--geometry confinement invariant v6.0.3

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_sigma_domain_candidate_audit_v6_0_3.json` | Separates bulk, boundary, collar, localized-mode, and bundle sigma domains. |
| `artifacts/BHSM_action_native_sigma_coupling_ledger_v6_0_3.json` | Records every audited action term, Hessian source, parity, and source status. |
| `artifacts/BHSM_confinement_invariant_admissibility_matrix_v6_0_3.json` | Applies covariance, dimension, conservation, signature, and representation gates. |
| `artifacts/BHSM_confinement_local_quasilocal_global_classification_v6_0_3.json` | Prevents local, interface, quasilocal, and global source mixing. |
| `artifacts/BHSM_complete_sigma_quadratic_operator_v6_0_3.json` | Gives the complete conditional Hessian, symbol, domain, and boundary form. |
| `artifacts/BHSM_physicality_spectral_threshold_problem_v6_0_3.json` | Defines the lowest physical mode and harmonic-coherence selection test. |
| `artifacts/BHSM_physicality_finite_enclosure_correction_v6_0_3.json` | Separates gradient, bulk, boundary, and collar finite-size terms. |
| `artifacts/BHSM_physicality_nonlinear_formed_phase_v6_0_3.json` | Gives the conditional stabilized one-mode branch. |
| `artifacts/BHSM_physicality_domain_wall_envelope_v6_0_3.json` | Records the planar wall formula and why the full envelope remains open. |
| `artifacts/BHSM_physicality_emergent_boundary_test_v6_0_3.json` | Lists regular-level-set, geometry, stress, and junction gates. |
| `artifacts/BHSM_coupled_geometry_sigma_hessian_v6_0_3.json` | Defines the full coupled collective-coordinate Hessian architecture. |
| `artifacts/BHSM_parent_matter_dependency_audit_v6_0_3.json` | Identifies the exact parent matter data needed by each candidate. |
| `artifacts/BHSM_parent_to_v5_sigma_reduction_map_v6_0_3.json` | Blocks reverse engineering of the v5 normalized coefficients. |
| `artifacts/BHSM_three_threshold_dependency_ledger_v6_0_3.json` | Separates formation, release, and black-hole de-enveloping. |
| `artifacts/BHSM_physicality_scale_hidden_input_audit_v6_0_3.json` | Exposes every primitive normalization and scale. |
| `artifacts/BHSM_energy_geometry_confinement_invariant_report_v6_0_3.json` | Final claim-safe result and next-branch routing. |

Doctrine: `docs/bhsm_energy_geometry_confinement_invariant_v6_0_3.md`.

<!-- BHSM_HARMONIC_PHYSICALITY_COUPLING_SELECTION_V6_0_4 -->
## Harmonic physicality coupling selection v6.0.4

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_harmonic_linear_no_selection_theorem_v6_0_4.json` | Proves free orthogonal modes have no invariant relative-phase energy. |
| `artifacts/BHSM_harmonic_interfering_parent_field_ledger_v6_0_4.json` | Audits sigma, matter, gauge, geometry, connection, flux, and spinor candidates. |
| `artifacts/BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json` | Records the exact round-S7 scalar subspectrum and open parent spectrum. |
| `artifacts/BHSM_harmonic_cubic_quartic_interaction_tensors_v6_0_4.json` | Separates the parity-zero cubic tensor from the conditional quartic tensor. |
| `artifacts/BHSM_harmonic_geometric_selection_rule_matrix_v6_0_4.json` | Applies representation, charge, parity, topology, collar, and boundary gates. |
| `artifacts/BHSM_harmonic_octave_discrete_scale_audit_v6_0_4.json` | Derives the unique round-S7 octave pair and rejects scale promotion. |
| `artifacts/BHSM_harmonic_resonance_condition_registry_v6_0_4.json` | Separates frequency commensurability from nonzero interaction. |
| `artifacts/BHSM_harmonic_resonant_normal_form_v6_0_4.json` | Records conservative normal-form requirements and missing channel. |
| `artifacts/BHSM_harmonic_phase_locked_solution_v6_0_4.json` | Prevents prescribed phases without amplitude equations and stability. |
| `artifacts/BHSM_harmonic_basis_invariant_coherence_v6_0_4.json` | Defines spectral-projector coherence and its phase-blind limit. |
| `artifacts/BHSM_harmonic_constrained_variational_selection_v6_0_4.json` | Requires actual conserved constraints and a second constrained variation. |
| `artifacts/BHSM_harmonic_coherent_incoherent_stress_v6_0_4.json` | Defines the equal-invariant comparison and records unavailable shifts. |
| `artifacts/BHSM_harmonic_sigma_hessian_shift_v6_0_4.json` | Audits independent-field and sigma-self shifts without assuming a sign. |
| `artifacts/BHSM_harmonic_physicality_threshold_v6_0_4.json` | Leaves control, critical value, and crossing open. |
| `artifacts/BHSM_harmonic_coupled_coherent_sigma_hessian_v6_0_4.json` | Defines the complete coupled sector ledger. |
| `artifacts/BHSM_harmonic_geometric_modulus_selection_v6_0_4.json` | Prevents resonance-only metric selection. |
| `artifacts/BHSM_harmonic_emergent_enclosure_test_v6_0_4.json` | Keeps an imposed round container distinct from emergence. |
| `artifacts/BHSM_harmonic_parent_to_v5_compatibility_v6_0_4.json` | Preserves the v5 and generation firewall. |
| `artifacts/BHSM_harmonic_absolute_scale_hidden_input_audit_v6_0_4.json` | Exposes all unsourced coefficients, geometry, and base-scale inputs. |
| `artifacts/BHSM_harmonic_physicality_coupling_selection_report_v6_0_4.json` | Final negative/blocked result and next-branch routing. |

Doctrine: `docs/bhsm_harmonic_physicality_coupling_selection_v6_0_4.md`.

<!-- BHSM_MINIMAL_PARENT_THEORY_KILL_TEST_V6_0_5 -->
## Minimal parent theory freeze and kill test v6.0.5

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json` | Immutable domain, signature, action, field, coupling, boundary, and primitive freeze. |
| `artifacts/BHSM_minimal_parent_action_equations_stress_v6_0_5.json` | Equations, stress, conservation, and geometric-source test. |
| `artifacts/BHSM_minimal_parent_linear_spectrum_v6_0_5.json` | Exact free carrier spectrum at sigma zero. |
| `artifacts/BHSM_minimal_parent_nonlinear_resonance_kill_v6_0_5.json` | Shows the carrier has no nonlinear resonant self-channel. |
| `artifacts/BHSM_minimal_parent_coherent_sigma_shift_kill_v6_0_5.json` | Audits the Lorentzian-sign-indefinite unsourced sigma shift. |
| `artifacts/BHSM_minimal_parent_nonlinear_sigma_branch_v6_0_5.json` | Records the conditional branch and failed trigger. |
| `artifacts/BHSM_minimal_parent_coupled_hessian_kill_v6_0_5.json` | Records missing gauge quotient, Floquet problem, and spectrum. |
| `artifacts/BHSM_minimal_parent_to_v5_kill_v6_0_5.json` | Blocks reverse-engineered v5 recovery. |
| `artifacts/BHSM_minimal_parent_primitive_count_v6_0_5.json` | Counts seven raw and five normalized unsourced primitives. |
| `artifacts/BHSM_minimal_parent_theory_kill_test_report_v6_0_5.json` | Ten-test verdict and foundational-axiom stop. |

Doctrine: `docs/bhsm_minimal_parent_theory_kill_test_v6_0_5.md`.

The v6.0.5 trigger failure is scoped to the frozen autonomous coherent
nonzero-sigma transition. General action-supported energy--geometry
envelopment and transient free-scalar localization remain open.

<!-- BHSM_CORRESPONDENCE_NOVELTY_FIREWALL_V6_0_6 -->
## Correspondence, ontology, and novelty firewall v6.0.6

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_physicality_ontology_v6_0_6.json` | Freezes the minimal interpretive physicality/envelopment dictionary. |
| `artifacts/BHSM_established_physics_correspondence_registry_v6_0_6.json` | Separates standard correspondence from BHSM novelty. |
| `artifacts/BHSM_geometric_reinterpretation_registry_v6_0_6.json` | Records ontology as reinterpretation rather than theorem. |
| `artifacts/BHSM_native_derivation_registry_v6_0_6.json` | Inventories BHSM-specific exact and conditional results. |
| `artifacts/BHSM_novelty_prediction_firewall_v6_0_6.json` | Classifies all major claims and defines the frozen-prediction gate. |
| `artifacts/BHSM_harmonic_role_reclassification_v6_0_6.json` | Retains the exact octave without a universal trigger claim. |
| `artifacts/BHSM_sigma_role_reclassification_v6_0_6.json` | Reclassifies sigma as a candidate reduced/persistent variable. |
| `artifacts/BHSM_b8_s7_berger_s3_candidate_role_matrix_v6_0_6.json` | Audits nine possible roles for legacy Berger S3. |
| `artifacts/BHSM_b8_s7_berger_s3_required_maps_v6_0_6.json` | Separates exact Hopf maps from missing reduction maps. |
| `artifacts/BHSM_b8_s7_berger_s3_metric_measure_compatibility_v6_0_6.json` | Separates the round fiber from a generic Berger metric. |
| `artifacts/BHSM_parent_to_v5_action_sector_map_v6_0_6.json` | Audits eight v5 action sectors without reverse engineering. |
| `artifacts/BHSM_s7_to_berger_s3_mode_branching_readiness_v6_0_6.json` | Defines representation, measure, domain, and operator gates. |
| `artifacts/BHSM_b8_s7_berger_s3_reduction_blockers_v6_0_6.json` | Lists the exact blockers for the reduction theorem. |
| `artifacts/BHSM_full_bhsm_roadmap_v6_0_6.json` | Redirects the full program through the parent-to-v5 bridge. |
| `artifacts/BHSM_correspondence_hidden_input_claim_audit_v6_0_6.json` | Confirms no measured input or observable rewrite. |
| `artifacts/BHSM_correspondence_novelty_firewall_report_v6_0_6.json` | Final result, stop condition, and next-branch routing. |

Doctrine: `docs/bhsm_correspondence_novelty_firewall_v6_0_6.md`.

<!-- BHSM_B8_S7_BERGER_S3_REDUCTION_THEOREM_V6_0_7 -->
## B8/S7-to-Berger-S3 reduction theorem v6.0.7

Constructive interpretation: the exact fixed-axis obstruction selects
`BHSM_TWISTOR_MEDIATED_BERGER_ROUTE_SELECTED` and
`BHSM_BERGER_ASSOCIATED_BUNDLE_FORMULATION_REQUIRED`. The artifacts exclude a
direct scalar reduction over `S4`; they do not exclude the nested
`S1 -> S7 -> CP3`, `S2 -> CP3 -> S4` program.

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_quaternionic_hopf_bundle_convention_ledger_v6_0_7.json` | Fixes bundle, connection, curvature, transition, and orientation conventions. |
| `artifacts/BHSM_global_4_2_1_metric_audit_v6_0_7.json` | Separates a total-space anisotropic tensor from an Sp(1)-natural reduction. |
| `artifacts/BHSM_sp1_to_u1_reduction_theorem_v6_0_7.json` | Proves the nonzero-c2 U(1)-reduction obstruction. |
| `artifacts/BHSM_fiber_restriction_berger_metric_v6_0_7.json` | Derives the intrinsic Berger metric, curvature, volume, and round limit. |
| `artifacts/BHSM_local_global_berger_fiber_classification_v6_0_7.json` | Classifies nonround fibers as an associated/gauge-fixed family. |
| `artifacts/BHSM_berger_measure_orientation_reduction_v6_0_7.json` | Separates physical integration, averaging, restriction, and pushforward. |
| `artifacts/BHSM_berger_hodge_star_decomposition_v6_0_7.json` | Gives exact pointwise sign and scale factors. |
| `artifacts/BHSM_berger_differential_operator_decomposition_v6_0_7.json` | Records connection and O'Neill mixing omitted by a naive sum. |
| `artifacts/BHSM_berger_fiber_mode_globalization_theorem_v6_0_7.json` | Derives the associated-bundle transformation law. |
| `artifacts/BHSM_berger_consistent_truncation_test_v6_0_7.json` | Applies all twelve exact reduction kill tests. |
| `artifacts/BHSM_so8_hopf_berger_representation_branching_v6_0_7.json` | Closes low-level branching checks and leaves the general intertwiner open. |
| `artifacts/BHSM_existing_berger_mode_ledger_parent_map_v6_0_7.json` | Audits frozen sector labels without parent promotion. |
| `artifacts/BHSM_berger_scalar_action_reduction_v6_0_7.json` | Derives the associated scalar structure while blocking v5 coefficient recovery. |
| `artifacts/BHSM_berger_gauge_reduction_readiness_v6_0_7.json` | Identifies connection architecture without gauge-coupling claims. |
| `artifacts/BHSM_berger_dirac_reduction_readiness_v6_0_7.json` | Identifies twisted Dirac architecture without a fermion spectrum. |
| `artifacts/BHSM_berger_boundary_collar_role_firewall_v6_0_7.json` | Separates fiber, B8-boundary, spacetime-normal, and collar objects. |
| `artifacts/BHSM_lovelock_berger_action_reduction_map_v6_0_7.json` | Audits P1, P2, and P3 structures without family selection. |
| `artifacts/BHSM_parent_to_v5_coefficient_map_v6_0_7.json` | Keeps every reduced coefficient and missing source explicit. |
| `artifacts/BHSM_berger_reduction_scale_hidden_input_audit_v6_0_7.json` | Separates ratios from the open common scale modulus. |
| `artifacts/BHSM_b8_s7_to_berger_s3_reduction_report_v6_0_7.json` | Final obstruction verdict, stop condition, and next branch. |

Doctrine: `docs/bhsm_b8_s7_to_berger_s3_reduction_theorem_v6_0_7.md`.

<!-- BHSM_TWISTOR_BERGER_ASSOCIATED_BUNDLE_V6_0_8 -->
## Twistor-mediated Berger associated-bundle construction v6.0.8

| Artifact | Purpose |
|---|---|
| `artifacts/BHSM_nested_global_distribution_theorem_v6_0_8.json` | Derives the global orthogonal `4+2+1` splitting, transitions, integrability, curvature, and orientation. |
| `artifacts/BHSM_twistor_mediated_s3_reconstruction_v6_0_8.json` | Proves the nested preimage identity and reconstructs the complete `S1->S3->S2` fiber. |
| `artifacts/BHSM_global_nested_twistor_berger_metric_v6_0_8.json` | Constructs the global nested metric and classifies its generic and enhanced symmetries. |
| `artifacts/BHSM_twistor_berger_fiber_metric_recovery_v6_0_8.json` | Recovers the repository Berger metric and exact scalar spectral splitting. |
| `artifacts/BHSM_berger_fiberwise_hilbert_bundle_v6_0_8.json` | Constructs finite-rank fiberwise eigenspace bundles and reality pairing. |
| `artifacts/BHSM_associated_bundle_transition_connection_ledger_v6_0_8.json` | Fixes transition, connection, curvature, inner-product, and weight-transport laws. |
| `artifacts/BHSM_berger_covariant_reduced_operator_v6_0_8.json` | Derives the minimally coupled scalar multiplet operator and scopes other endomorphisms. |
| `artifacts/BHSM_berger_finite_multiplet_closure_test_v6_0_8.json` | Separates exact linear closure from generic nonlinear tower generation. |
| `artifacts/BHSM_so8_sp2_sp1_u1_branching_extension_v6_0_8.json` | Gives the general round-S7 scalar branching formula and U(1) weights. |
| `artifacts/BHSM_twistor_berger_multiplet_action_reduction_v6_0_8.json` | Reduces the provisional P1 scalar/action structure in covariant multiplet language. |
| `artifacts/BHSM_v5_berger_engine_global_reinterpretation_v6_0_8.json` | Reinterprets exact fiberwise calculations globally without promoting effective ledgers. |
| `artifacts/BHSM_twistor_berger_gauge_forward_link_v6_0_8.json` | Records the geometric connection precursor and its open normalization. |
| `artifacts/BHSM_twistor_berger_scalar_topographic_forward_link_v6_0_8.json` | Separates the singlet, moduli, boundary, and topographic possibilities. |
| `artifacts/BHSM_twistor_berger_coefficient_scale_ledger_v6_0_8.json` | Tracks coefficient sources, convention bridges, ratios, and the open common scale. |
| `artifacts/BHSM_twistor_berger_associated_bundle_report_v6_0_8.json` | Final constructive result, exact constraints, and next action-normalization dependency. |

Doctrine: `docs/bhsm_twistor_berger_associated_bundle_v6_0_8.md`.

<!-- BHSM_TWISTOR_BERGER_ACTION_NORMALIZATION_V6_0_9 -->
## Twistor--Berger action normalization v6.0.9

The 23 deterministic JSON artifacts are enumerated by
`src/bhsm/interface/twistor_berger_action_normalization.py`. They cover the
convention and measure; P1 curvature, connection, moduli, and canonical
multiplets; cubic/quartic overlaps and selection rules; the spectral gap and
tower bounds; the normalized action and separate P2/P3 ledger; parent-to-v5,
sigma/gauge/fermion readiness; scale, stability, hidden inputs, and report.

Doctrine: `docs/bhsm_twistor_berger_action_normalization_v6_0_9.md`.

<!-- BHSM_P1_LORENTZIAN_BACKGROUND_CONSTRAINT_V6_0_10 -->
## P1 Lorentzian background constraint closure v6.0.10

The 22 deterministic artifacts enumerated by
`src/bhsm/interface/p1_lorentzian_background_constraint.py` cover the ADM
ledger and action; Hamiltonian/momentum constraints; scale/shape equations;
static round/Jensen tests; required support; exact dynamic branches; the
anisotropic system and reduced stability; sigma/connection audits; dynamic
tower control; background connection/multiplet operators; scale,
parent-to-v5, P2/P3, hidden-input, and final-report ledgers.

Doctrine: `docs/bhsm_p1_lorentzian_background_constraint_v6_0_10.md`.

<!-- BHSM_ROUND_BACKGROUND_GAUGE_SCALAR_V6_1 -->
## Round-background gauge and scalar sector v6.1

The 22 deterministic artifacts enumerated by
`src/bhsm/interface/round_background_gauge_scalar_sector.py` cover the exact
control-window test and its one-third floor; the M8/M5/M4 firewall; Sp1 and
nested U1 normalizations and their convention ratio; charge operators and
gauge vertices; scalar candidates, sigma selection, kinetic normalization,
potential sources, tower terms, and constraint-reduced Hessian; gauge-scalar
couplings; aperture readiness; M5/M4 dimensions; the parent-to-v5 map;
spectrum and spinorial boundary-operator forward link (with the historical
artifact filename retained); scale, hidden inputs, and the final report. The
payloads also freeze the permanent fermionic/Clifford and no-monopole
firewall.

Doctrine: `docs/bhsm_round_background_gauge_scalar_v6_1.md`.

<!-- BHSM_PARENT_M5_M4_BOUNDARY_REDUCTION_V6_1_1 -->
## Parent M5 to equatorial-M4 boundary reduction v6.1.1

The 26 deterministic artifacts enumerated by
`src/bhsm/interface/m5_m4_boundary_reduction.py` cover the permanent
fermionic/Clifford and no-monopole firewall; exact M5 hyperspherical and
equatorial geometry; equator roles and selection; boundary/control-surface
separation; Gauss--Codazzi and GHY variation; the normal Sturm--Liouville
problem and zero-mode audit; gravitational, Sp1, nested-U1, and scalar
normalizations; localization sources and self-adjoint domains; currents,
aperture, potential, parent-to-v5/v4, Clifford readiness, scale, hidden inputs,
and final doctrine report.

Doctrine: `docs/bhsm_parent_m5_to_m4_boundary_reduction_v6_1_1.md`.

<!-- BHSM_M4_LORENTZ_SELECTED_LOCALIZATION_V6_1_2 -->
## M4 Lorentz-selected boundary localization v6.1.2

The 25 deterministic artifacts enumerated by
`src/bhsm/interface/m4_lorentz_localization.py` cover the scalar, connection,
and principal tensor Lorentz-normalization theorems; mismatch functionals and
great-S3 orbit selection; P1/GHY, Z2, exact collar, sigma, P2/P3, and
tree-induction source audits; localized Sturm--Liouville and finite-width
profile diagnostics; the minimum unsourced intrinsic boundary-action family;
common action, currents, aperture, fermionic readiness, scale,
parent-to-v5/v4, hidden-input, and final-report ledgers.

Doctrine: `docs/bhsm_m4_lorentz_selected_localization_v6_1_2.md`.

<!-- BHSM_MINIMAL_EQUATORIAL_BOUNDARY_ACTION_V6_1_3 -->
## Minimal equatorial boundary action freeze v6.1.3

The 23 deterministic artifacts enumerated by
`src/bhsm/interface/minimal_equatorial_boundary_action.py` cover Boundary
Axiom B1; the trace-versus-intrinsic theorem; the frozen action and exact
metric matching; coefficient-lock and primitive-count tests; intrinsic
gravity, connection, nested-U1, and scalar sectors; potential sourcing;
combined variation and round-background backreaction; Lorentz hyperbolicity
and constraint-reduced stability; physical-boundary status; current and
aperture readiness; parent and fermionic maps; scale and hidden-input audits;
and the final report.

Doctrine: `docs/bhsm_minimal_equatorial_boundary_action_v6_1_3.md`.

<!-- BHSM_INTRINSIC_M4_JUNCTION_BACKGROUND_V6_1_4 -->
## Intrinsic M4 junction-supported background closure v6.1.4

The 25 deterministic artifacts enumerated by
`src/bhsm/interface/intrinsic_m4_junction_background.py` cover the frozen
total action; exact variation and matching elimination; smooth-equator
residual; Gaussian-normal equations; one-sided junction factors;
constant-curvature roots and regular Z2 double caps; boundary FRW and branch
classification; coefficient and primitive ledgers; connection and sigma
vacua; the missing-term gate; conservation; reduced-stability and tensor
audits; Lorentz structure; coefficient-source, parent-map, fermionic, scale,
hidden-input, and final-report records.

Doctrine: `docs/bhsm_intrinsic_m4_junction_background_v6_1_4.md`.
