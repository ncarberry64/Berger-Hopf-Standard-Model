# BHSM Status

This file is the current area-level status source. Detailed sprint records are
evidence, not competing public status pages.

BHSM is an artifact-backed computational framework for Berger-Hopf boundary-mode physics. Current public status: structural architecture integrated conditional; frozen predictions unchanged; physical eV/GeV neutrino mass closure remains open; external HEP runtime integration remains gated.

BHSM has conditional dimensionless neutrino propagation closure, a conditional neutral spectral-mass theorem, and conditional measurement-supported admissible neutral positivity. Physical eV/GeV neutrino mass closure remains open pending a numeric neutral stiffness length sqrt(A_nu/Z_nu), a physical K_neutral,eff map in m^-2, and complete-action derivation of the admissible response cone.

Status taxonomy: `ESTABLISHED`, `ARTIFACT_BACKED`, `CANDIDATE`, `CONDITIONAL`,
`OPEN`, `BLOCKED`, `RUNTIME_GATED`, `REFERENCE_ONLY`, `RETIRED`.

| Area | Status | What is established | What remains open | Command/artifact |
| --- | --- | --- | --- | --- |
| Frozen internal predictions | `ESTABLISHED` | Frozen Markdown and JSON prediction records with integrity tests | External comparison is separate | `docs/frozen_predictions.md` |
| Python computational interface | `ESTABLISHED` | Offline geometry, prediction, comparison, and report interfaces | New physics formulas require their own evidence | `python -m bhsm.interface --help` |
| CERN ROOT adapter | `CI_COMPILED_RUNTIME_GATED` | Header-only utility, PyROOT expression wrapper, and pinned ROOT-container C++ smoke test | Documented file-schema, detector-stack, and institutional HEP validation | `integrations/cern-root/README.md` |
| Prediction registry | `ESTABLISHED` | Calibration, prediction, comparison, theorem, and runtime statuses | Registry expansion is evidence-driven | `python -m bhsm.interface registry` |
| CLI reports | `ESTABLISHED` | Deterministic text, Markdown, and JSON reports | None for current offline commands | `python -m bhsm.interface report --format json` |
| Prediction gallery | `ARTIFACT_BACKED` | Registry-backed review table and optional plots | External comparisons remain separate | `python -m bhsm.interface gallery --format markdown` |
| Artifact-backed adapters | `ARTIFACT_BACKED` | Source discovery, provenance, formula registry, and five adapters | Open theorems are not inferred from artifacts | `python -m bhsm.interface artifact-sources` |
| CKM matrix | `ARTIFACT_BACKED` | Frozen matrix artifact and provenance adapter | Empirical evaluation is separate | `artifacts/CKM_no_fit_operator_output_v1.json` |
| PMNS matrix | `ARTIFACT_BACKED` | Frozen matrix artifact and provenance adapter | Physical neutrino basis and scale remain open | `artifacts/PMNS_no_fit_operator_output_v1.json` |
| CP phase / Z6 holonomy | `ARTIFACT_BACKED` | Local CP holonomy phase artifact and CKM/PMNS attachment evidence | Numerical external comparison remains separate | `artifacts/CP_no_fit_holonomy_output_v1.json` |
| Boundary constants | `ARTIFACT_BACKED` | No-fit boundary package and adapter | No automatic promotion of downstream theorems | `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json` |
| Mass ratios | `ARTIFACT_BACKED` | Frozen charged-sector ratio artifact and adapter | Precision external comparisons are scheme-sensitive | `theory/bhsm_v1_frozen_prediction_set.json` |
| W calibration policy | `REFERENCE_ONLY` | W may set the geometric-to-physical unit scale | It is not independent in the same calibrated run | `python -m bhsm.interface status W_boson` |
| Electron-neutrino comparison policy | `REFERENCE_ONLY` | Default comparison is upper-limit based | A vetted central mass reference is not supplied by default | `python -m bhsm.interface status electron_neutrino` |
| Standalone CP O_int | `RETIRED_TARGET` | CP is represented by the artifact-backed Z6 holonomy constraint | No standalone production vertex is required or claimed | `python -m bhsm.interface close-minimal-action cp_o_int` |
| X_ch boundary response | `CONDITIONAL_ACTION_THEOREM` | Author ontology plus local boundary sources define field -> `P_ch` -> `X_ch` -> response | Numerical normalization and any 4D production identification remain open | `python -m bhsm.interface close-minimal-action X_ch` |
| Neutrino propagation mass | `CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE` | `K_nu`, `g_nu`, `kappa_nu`, and dimensionless `tau` produce deterministic threshold-response rows | Artifact-backed dimensionful neutral scale and physical flavor-observable map | `python -m bhsm.interface neutrino-propagation-report --format markdown` |
| Canonical neutrino closure status | `CONDITIONAL_DIMENSIONLESS_PROPAGATION_CLOSURE` | Dimensionless propagation, conditional spectral theorem, and conditional cone positivity are reported separately | Numeric stiffness length, physical curvature map, and complete-action cone derivation | `python -m bhsm.interface neutrino-closure-status --format markdown` |
| Neutral dimensionful scale | `OPEN_MISSING_NEUTRAL_SCALE` | Offline candidate, measure, and threshold-map audits distinguish the dimensionless response from physical units | Physical boundary-measure normalization, neutral background energy density, transport normalization, and threshold-to-energy map | `python -m bhsm.interface neutrino-scale-report --format markdown` |
| Legacy curvature mass bridge | `ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL` | Bundled author papers support `m=(c^2/(2G))r^2 k_loc` as a documented matching functional plus scalar-EFT and S3 action context | A BHSM neutral `r_prop`, physical `k_neutral,eff` map, and derivation of the matching functional from the BHSM action | `python -m bhsm.interface legacy-neutral-scale-report --format markdown` |
| Neutral propagation radius | `CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE` | The physical neutral-field domain defines symbolic `r_prop` with length dimension and no empirical input | Numerical metre value and neutral-mode support theorem | `python -m bhsm.interface neutral-propagation-radius --format json` |
| Neutral physical curvature | `CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE` | Dimensionless `R_nu` and symbolic `k_neutral,eff=kappa_curv R_nu` are separated cleanly | Action-derived `kappa_curv` in `m^-2`, boundary stiffness, and physical transport normalization | `python -m bhsm.interface neutral-physical-curvature --format json` |
| Dimensionful neutrino mass | `DIMENSIONFUL_MASS_NOT_AVAILABLE` | Radius, curvature, and mass-dimension gates are executable and fail closed | Numeric radius, physical curvature normalization, and corrected/action-derived mass functional; current legacy formula evaluates dimensionally to mass/length | `python -m bhsm.interface neutral-radius-curvature-report --format markdown` |
| Neutral mass-gap action | `ARTIFACT_BACKED_MASS_GAP_ACTION` | Bundled scalar action and spectral-gap analogue load offline | Neutral coefficients remain conditional | `python -m bhsm.interface neutrino-mass-gap-action --format json` |
| Neutral stiffness ratio | `OPEN_MISSING_NUMERIC_STIFFNESS_RATIO` | `sqrt(A_nu/Z_nu)` is defined symbolically | Numeric action-derived value in metres | `python -m bhsm.interface neutral-stiffness-ratio --format json` |
| Neutral spectral mass | `CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE` | Dimensionally correct theorem shape and conditional response-cone positivity are executable | Numeric stiffness length and physical `K_neutral,eff`; complete-action cone derivation remains a limitation | `python -m bhsm.interface neutral-spectral-report --format markdown` |
| Admissible neutral positivity | `CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE` | Exact copositivity on an explicit nonnegative response cone; no clipping used | Complete-action derivation of the measurement-supported response cone | `python -m bhsm.interface neutral-positivity-report --format markdown` |
| Neutral action normalization | `OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION` | Partial propagation, boundary variation, and collar-measure source chain is explicit | `chi_nu`, `lambda_nu`, normalized support measure, profile/embedding, orientation/edge data | `python -m bhsm.interface neutral-action-source-search --format json` |
| Neutral stiffness length | `OPEN_MISSING_NUMERIC_STIFFNESS_LENGTH` | `sqrt(A_nu_gap/Z_nu)` is dimensionally specified | Numeric action-derived ratio with dimension `L^2` | `python -m bhsm.interface neutral-action-stiffness --format json` |
| Action-supported response cone | `CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE` | Partial variational and interaction-support sources identified | Complete normalized action derivation of response coordinates and constraints | `python -m bhsm.interface neutral-action-response-cone --format json` |
| Physical neutral mass closure | `DIMENSIONFUL_MASS_NOT_AVAILABLE` | Unit-safe closure command fails closed | Numeric stiffness length in metres and physical curvature in `m^-2` | `python -m bhsm.interface neutral-action-closure-report --format markdown` |
| Full-completion ledger | `INTEGRATED_CONDITIONAL_ARCHITECTURE_WITH_OPEN_BLOCKERS` | Sixteen categories, explicit priorities, and a partial boundary-measure/identity-transport closure | Physical measure normalization, action theorems, unit maps, and runtime gates remain open | `python -m bhsm.interface full-completion-status --format markdown` |
| Charged action/stiffness/mixing | `CONDITIONAL_CHARGED_SOURCES_WITH_OPEN_ACTION_NORMALIZATION_AND_CKM_EXPONENT_DERIVATION` | Projectors, charged coefficients, frozen CKM formulas, and conditional eta/mixing sources are inventoried | Charged action normalization, unique rho_ch, eta_l action source, CKM 1/16 theorem, and cross-scale transport | `python -m bhsm.interface charged-closure-report --format markdown` |
| Common-16 closure | `CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE` | Exact incidence, bridge/beta, and reciprocal fraction identities | Action-derived `Omega_f`, selected `rho_ch=3`, charged overlap source, and CKM reciprocal transport theorem | `python -m bhsm.interface final-completion-status --format markdown` |
| FeynRules minimal model | `RUNTIME_GATED` | Disabled handoff assets and validation contracts exist | Complete eligible interaction set and live FeynRules validation | `python -m bhsm.interface status feynrules_minimal_model` |
| UFO export | `RUNTIME_GATED` | Export contract and runner scaffolds exist | Real export and loadability validation | `python -m bhsm.interface status ufo_export` |
| MadGraph smoke test | `RUNTIME_GATED` | Smoke-test plan and runner scaffolds exist | Validated UFO plus live MadGraph execution | `python -m bhsm.interface status madgraph_smoke_test` |

The detailed claim boundary is centralized in [CLAIMS.md](CLAIMS.md).

## v1.9 Engine/Physics Separation

- Engine: deterministic coordinate transforms, synthetic and CMS-derived
  four-vector validation, precision gates, ROOT compile/runtime smoke, and
  environment-specific performance diagnostics.
- Physics: integrated conditional architecture with open action, transport,
  normalization, unit-map, gauge/scalar, and runtime gates.
- `Omega_f`: `STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED`.
- `rho_ch=3`: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.
- charged overlap `4/3`: `OPEN_MISSING_CHARGED_OVERLAP_4_OVER_3_ACTION_SOURCE`.
- Engine results are not empirical validation of BHSM Physics and do not cover
  detector reconstruction.

## v2.0 Primitive Charged Incidence

- Exact conditional algebra: `Omega_ch=(3,6,12)`, `T_ch=21`, `rho_ch=3`,
  `s_ch=(1,2,4)`, `Pi_ch=(1,2,4)/7`, `O_ch=4/3`, `N_16=16`,
  `g_bridge=16/189`, and `beta_ch=(16,32,64)/1323`.
- `rho_ch`: `CONDITIONAL_RHO_CH_PRIMITIVE_LATTICE_CANDIDATE`; its action
  normalization rule remains open.
- CKM transport: `CONDITIONAL_CKM_LOG_TRANSPORT_CANDIDATE`; the averaging
  theorem remains open.
- Physical normalization is open; external reproduction is prepared but not completed.

## v2.1 Action Lemmas

- Abstract quadratic log averaging: `ARTIFACT_BACKED_MATHEMATICAL_LEMMA`.
- Primitive lattice action rule: `OPEN_MISSING_ACTION_PRIMITIVE_LATTICE_NORMALIZATION_RULE`.
- Maximal-overlap action rule: `OPEN_MISSING_ACTION_RULE_THAT_BRIDGE_USES_MAX_PRIMITIVE_OVERLAP`.
- CKM application: `OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM`.
- The mathematical lemma proves equal log sharing, not the physical identity or equivalence of sixteen CKM channels.

## v2.2 CKM Channel Equivalence

- Exact candidate dimensions: `N_ud=8`, `N_total_end=49`, `N_sum_self=21`, and `N_max_self=16`.
- Channel-count status: `MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS`.
- Maximal-sector selection: `OPEN_MISSING_MAXIMAL_SECTOR_CKM_SELECTION_RULE`.
- CKM application: `OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM`.
- The abstract lemma is reused; no action-backed rule currently selects `End(V_d)` over the three competing spaces.

## v2.3 Hermitian Bidirectional CKM Channel

- One-way dimensions: `dim Hom(V_u,V_d)=8` and `dim Hom(V_d,V_u)=8`.
- Bidirectional candidate: `N_CKM=16` from the direct sum of the two directions.
- Source status: `CONDITIONAL_HERMITIAN_BIDIRECTIONAL_CKM_CHANNEL_CANDIDATE`.
- Adjoint-pair selection: `OPEN_MISSING_CKM_ADJOINT_PAIR_SELECTION_RULE`.
- The CKM target contains `+ h.c.`, but that structure remains a standard target convention rather than an action-derived transport theorem.
- Maximal self-response is retired as the primary CKM source; its equal dimension is not physical source selection.
