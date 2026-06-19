# Claim Status Table

| Claim | Status | Where to inspect | What would break it |
| --- | --- | --- | --- |
| Standard Model gauge ledger is reproduced conditionally | `DERIVED_CONDITIONAL` | `theory/claims_ledger.json`, `tests/test_hypercharges.py`, `tests/test_anomalies.py` | Failure of admitted ledger consistency or anomaly tests |
| Hypercharge derivation within admitted chiral pattern | `VERIFIED_TEST` | `src/hypercharge.py`, `tests/test_hypercharges.py` | Hypercharges no longer satisfy invariance/anomaly checks |
| Anomaly cancellation | `VERIFIED_TEST` | `src/anomalies.py`, `tests/test_anomalies.py` | Nonzero anomaly residuals |
| Gauge/electroweak screens | `STRONG_SCREEN` | `src/gauge_couplings.py`, `src/higgs_scale.py`, `tests/test_couplings.py` | Screen values leave fixed tolerance bands |
| Charged-sector mode selection | `STRONG_SCREEN` | `src/mode_selection.py`, `theory/boundary_operator_scaffold.md` | Boundary operators fail to recover the frozen ledger |
| H_T gap / no-extra-light-state audit | `PROXY_AUDIT` | `src/ht_operator.py`, `src/spectral_gap.py`, prediction ledger | Full twisted Dirac spectrum produces extra light states |
| Scalar/topographic decoupling | `PROXY_AUDIT` | `src/scalar_decoupling.py`, scalar tests | Unscreened light scalar/topographic mode survives |
| Precision QCD/RG matching | `OPEN` | QCD/RG scaffold files | Scheme-consistent precision comparison fails fixed bands |
| Full structural architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, theorem-discharge chain | Does not imply numerical closure or Standard Model replacement |
| Numerical closure | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Must remain open until all symbolic numerical inputs are derived and locked before comparison |
| Finite algebra | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, theorem-discharge files | Finite closure spectrum or algebra blocks fail guardrail tests |
| SM-like charges | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, charge/anomaly bridge tests | Charge table or anomaly bridge fails |
| Gauge normalization scaffold | `DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md`, trace-normalization files | Trace weights or normalization factors fail |
| Charged hierarchy mechanism | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Required symbolic hierarchy inputs cannot be localized |
| CKM source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Up/down sector-relative source cannot be represented |
| CKM CP source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Phase loop cannot be represented sector-relatively |
| CKM numerical prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Requires pre-comparison lock of CKM finite-width, displacement, phase, and exponent inputs |
| CKM `1/16` exponent | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | `docs/open_blockers_backlog.md` | Must not be fit to CKM residuals |
| Neutral topographic suppression route | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral suppression operator cannot be represented |
| Neutral topographic suppression action `S_nu_topo` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_neutral_topographic_suppression_action.md` | Must not be claimed until `Delta y_nu`, `H_topo^(nu)`, `E_nu`, and `S_barrier` are derived before comparison |
| Neutral saddle displacement `Delta_y_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_neutral_saddle_displacement.md` | Must not be claimed until the stationary-point or centroid ingredients are derived before comparison |
| Neutral effective action `S_eff_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_neutral_effective_action.md` | Must not be claimed until the internal metric, projection/lapse map, neutral boundary tensors, neutral boundary condition, and neutral profile are derived before comparison |
| Subsurface neutral projection geometry `g_sub`, `ellapse_nu`, `Pi_sub_to_ext` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_subsurface_projection_geometry.md` | Must not be claimed until the scalar/topographic profile, coordinate-invariant projection convention, internal metric, positivity/causality proof, and neutral boundary tensors are derived before comparison |
| Scalar/topographic boundary variation | `DERIVED_CONDITIONAL` | `theory/theorem_discharge_scalar_topographic_boundary_variation.md` | Conditional symbolic boundary operator fails or is fit to neutrino data |
| Normal-coupling/collar convention `R_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_normal_coupling_collar_convention.md` | Must not be claimed until fixed-normal, collar, or Robin convention is derived without fitted neutrino data |
| Collar geometry package | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_collar_geometry_package.md` | Must not be claimed until collar measure, orientation, inner-edge condition, admissible variation data, and Robin coefficients are derived without fitted neutrino data |
| Complete scalar/topographic collar action | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_complete_scalar_topographic_collar_action.md` | Must not be claimed until `L_collar`, `J(Y,rho)`, `s_n`, edge data, admissible variations, and Robin coefficients are derived without fitted neutrino data |
| Collar measure / extrinsic geometry | `DERIVED_CONDITIONAL_WITH_OPEN_GEOMETRIC_INPUTS` | `theory/theorem_discharge_collar_measure_extrinsic_geometry.md` | The symbolic collar Jacobian is conditionally derived, but the BHSM embedding/profile values needed to evaluate `K(Y)` and `S` remain open and unfitted |
| Boundary embedding / shape operator | `DERIVED_CONDITIONAL_WITH_OPEN_EMBEDDING_INPUTS` | `theory/theorem_discharge_boundary_embedding_shape_operator.md` | The boundary embedding, induced metric, unit normal, second fundamental form, shape operator, and trace formulas are localized or conditionally derived; numerical/function values remain open unless a BHSM scalar/topographic boundary profile and embedding are derived |
| Scalar/topographic level-set boundary embedding | `DERIVED_CONDITIONAL_WITH_OPEN_LEVEL_SET_INPUTS` | `theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md` | Two candidate level-set routes are localized and regular-level-set geometry is conditional; thresholds, explicit profiles, metric values, orientation, `S_nu_topo`, and `epsilon_nu_topo` remain open |
| Scalar/topographic profile input classification | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_scalar_topographic_profile_input_classification.md` | Profile objects are classified; threshold selection, metric/profile evaluation, and neutral action evaluation remain open before any numerical comparison |
| Scalar/topographic profile EOM source audit | audit `COMPLETED`; source result `PARTIAL_EOM_SOURCE_FOUND`; profile EOM objects `OPEN_LOCALIZABLE` | `theory/theorem_discharge_scalar_topographic_profile_eom_source_audit.md` | Schematic scalar bulk variation and symbolic boundary variation exist, but complete spacetime/internal profile EOMs, thresholds, profile solutions, `S_nu_topo` value, and `epsilon_nu_topo` remain open |
| Scalar/topographic boundary-condition normal form | `DERIVED_CONDITIONAL` for form; coefficients and values `OPEN_LOCALIZABLE` | `theory/theorem_discharge_scalar_topographic_boundary_condition_normal_form.md` | Dirichlet, Neumann, Robin/mixed, and conditional source-coupled forms are recorded, but coefficients, thresholds, profile solutions, and neutral suppression values remain open |
| Boundary coefficient and threshold source audit | audit `COMPLETED`; coefficient families and dimensions `DERIVED_CONDITIONAL`; values `OPEN_LOCALIZABLE` | `theory/theorem_discharge_boundary_coefficient_threshold_source_audit.md` | Coefficient values, coefficient ratios, source terms, thresholds, profile solutions, and neutral suppression values remain open |
| Finite sector projector compression | `STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE` | `docs/bhsm_sector_projector_ledger_theorem.md`, `src/sector_projector_hessian_fork.py` | Reproduces sector operators and target amplitudes, but is not fully action-derived |
| Charged Hessian anisotropy `rho_ch` | `OPEN_LOCALIZABLE` | `docs/bhsm_charged_hessian_fork_audit.md` | Exact old costs are conditional on `rho_ch=1`; cyclic candidate costs are conditional on `rho_ch=3`; action must decide |
| Charged Hessian source audit | audit `COMPLETED`; `rho_ch` action value `OPEN_LOCALIZABLE`; `rho_ch=1` `MINIMAL_ACTION_CLOSURE_CANDIDATE`; `rho_ch=3` `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | `docs/bhsm_charged_hessian_source_audit.md`, `data/bhsm_charged_hessian_source_audit.json` | No charged action/Hessian source currently decides `rho_ch`; charged `qj` cross-terms remain forbidden unless action-derived; neutral/topographic mixing cannot leak into charged Hessian without explicit coupling |
| Eta projection/no-overfit route | `VALIDATED_CANDIDATE`; exact value `OPEN` | `docs/bhsm_eta_projection_no_overfit.md` | `8/9` route downgraded; measured alpha and fitted `Pi_l` are forbidden as derivations |
| `Z_virt^{u,2}` dimension-ratio path | `STRONG_DERIVATION_CANDIDATE` | `docs/bhsm_eta_projection_no_overfit.md` | Applicability to the relevant up-sector virtual correction remains to be proven |
| `Z_virt^{u,2}` virtual-door applicability | `OPEN_LOCALIZABLE`; two-door pair/rank-one ratio formalized | `docs/bhsm_up_sector_virtual_door_applicability.md`, `data/bhsm_up_sector_virtual_door_applicability.json`, `src/up_sector_virtual_door_applicability.py` | The ratio `1/2` is not fully derived unless the relevant up-sector virtual correction is proven to sample the two-door virtual pair |
| Robin coefficients `A_nu`, `B_nu` | `OPEN_LOCALIZABLE` | `theory/theorem_discharge_collar_geometry_package.md` | Must not be fit to neutrino, PMNS, or anomaly/FTL data |
| Neutral boundary tensors `chi_nu_AB`, `lambda_nu`, `neutral_boundary_condition` | `OPEN_LOCALIZABLE` for tensor values; symbolic boundary condition `DERIVED_CONDITIONAL` | `theory/theorem_discharge_neutral_boundary_tensors.md`, `theory/theorem_discharge_scalar_topographic_boundary_variation.md` | Must not be claimed until tensor values, normal-coupling convention, internal/subsurface metric, neutral profile, and positivity/stability proof are derived before comparison |
| Neutral topographic suppression action value | `OPEN` | `theory/theorem_discharge_neutral_topographic_suppression_action.md` | No numerical value is derived or fitted |
| Neutrino mass prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Requires derived `S_nu_topo` and locked neutral matrix inputs before comparison |
| PMNS source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral/charged-lepton diagonalization source fails |
| PMNS CP source | `STRUCTURALLY_DERIVED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Neutral phase loop cannot be represented |
| PMNS numerical prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Requires pre-comparison lock of neutral operator parameters and phase loop |
| Full fermion-sector architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Numerical fermion masses or mixing values are not claimed |
| Gauge-Higgs-fermion architecture | `INTEGRATED_CONDITIONAL` | `docs/bhsm_numerical_input_closure_map.md` | Full numerical SM prediction is not claimed |
| Full numerical SM prediction | `OPEN` | `docs/bhsm_numerical_input_closure_map.md` | Must not be claimed until all open numerical inputs are locked before comparison |
| Stability/coupling bounds | `OPEN` | `docs/open_blockers_backlog.md` | Must not be asserted from finite diagnostics alone |
| Higher-loop thresholds | `OPEN` | `docs/open_blockers_backlog.md` | Must not use mixed-scale masses as precision truth |
| Replacement readiness | `NOT_ACHIEVED` | `docs/bhsm_numerical_input_closure_map.md` | Must not be claimed until numerical and theorem blockers close |
| Full first-principles SM derivation | `FORBIDDEN` | `theory/forbidden_claims.md` | This claim is not made in this release |
| QCD confinement proof | `FORBIDDEN` | `theory/forbidden_claims.md` | This claim is not made in this release |
| Experimental confirmation/community acceptance | `FORBIDDEN` | this release package | This claim is not made in this release |

Status categories used in this release:

- `DERIVED_CONDITIONAL`
- `VERIFIED_TEST`
- `STRONG_SCREEN`
- `PROXY_AUDIT`
- `OPEN`
- `OPEN_LOCALIZABLE`
- `STRUCTURALLY_INTEGRATED`
- `STRUCTURALLY_DERIVED_CONDITIONAL`
- `INTEGRATED_CONDITIONAL`
- `NOT_ACHIEVED`
- `FORBIDDEN`
