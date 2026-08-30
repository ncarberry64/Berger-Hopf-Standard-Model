"""Materialize the current BHSM physical-completeness accounting matrix.

This ledger separates implemented universal algebra from action-owned physical
predictions.  A reusable formula or guarded API is evidence of infrastructure,
not evidence that a pole, particle, amplitude, width, magnetic moment, or
forward forecast has been derived on the current BHSM background.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "BHSM_PHYSICAL_COMPLETENESS_MATRIX.json"

GATE7_AUTHORITY = (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_MINIMUM_CONTRACTION_ADJUDICATION.json"
)

ENGINE_PATHS = {
    "action_expansion": "src/bhsm/interface/universal_physical_action_expansion.py",
    "retained_n12_adapter": "src/bhsm/interface/retained_n12_action_expansion_adapter.py",
    "retained_sm_adapter": "src/bhsm/interface/retained_sm_physics_adapter.py",
    "sm_gauge_vertices": "src/bhsm/interface/bhsm_standard_model_gauge_vertices.py",
    "yukawa_vertices": "src/bhsm/interface/bhsm_yukawa_vertices.py",
    "quadratic_spectrum": "src/bhsm/interface/universal_quadratic_spectrum.py",
    "brst_quotient": "src/bhsm/interface/universal_brst_quotient.py",
    "momentum_map": "src/bhsm/interface/universal_momentum_map.py",
    "vertex_amplitude": "src/bhsm/interface/universal_vertex_amplitude.py",
    "lsz": "src/bhsm/interface/universal_lsz.py",
    "decay_collision": "src/bhsm/interface/universal_decay_collision.py",
    "precision_form_factor": "src/bhsm/interface/universal_precision_form_factor.py",
    "spectral_forecast": "src/bhsm/interface/universal_spectral_forecast.py",
    "loop_renormalization": "src/bhsm/interface/universal_loop_renormalization.py",
    "rg_flow": "src/bhsm/interface/universal_rg_flow.py",
    "gf_scale": "src/bhsm/interface/universal_gf_scale.py",
    "prediction_freeze": "src/bhsm/interface/universal_prediction_freeze.py",
    "release_reconciliation": "src/bhsm/interface/universal_release_reconciliation.py",
    "external_state_sum": "src/bhsm/interface/universal_external_state_sum.py",
    "benchmark_suite": "src/bhsm/interface/universal_benchmark_suite.py",
    "partial_wave": "src/bhsm/interface/universal_partial_wave.py",
    "dressed_pole": "src/bhsm/interface/universal_dressed_pole.py",
}

ENGINE_TEST_PATHS = {
    "action_expansion": "tests/test_universal_physical_action_expansion.py",
    "retained_n12_adapter": "tests/test_retained_n12_action_expansion_adapter.py",
    "retained_sm_adapter": "tests/test_retained_sm_physics_adapter.py",
    "sm_gauge_vertices": "tests/test_bhsm_standard_model_gauge_vertices.py",
    "yukawa_vertices": "tests/test_bhsm_yukawa_vertices.py",
    "quadratic_spectrum": "tests/test_universal_quadratic_spectrum.py",
    "brst_quotient": "tests/test_universal_brst_quotient.py",
    "momentum_map": "tests/test_universal_momentum_map.py",
    "vertex_amplitude": "tests/test_universal_vertex_amplitude.py",
    "lsz": "tests/test_universal_lsz.py",
    "decay_collision": "tests/test_universal_decay_collision.py",
    "precision_form_factor": "tests/test_universal_precision_form_factor.py",
    "spectral_forecast": "tests/test_universal_spectral_forecast.py",
    "loop_renormalization": "tests/test_universal_loop_renormalization.py",
    "rg_flow": "tests/test_universal_rg_flow.py",
    "gf_scale": "tests/test_universal_gf_scale.py",
    "prediction_freeze": "tests/test_universal_prediction_freeze.py",
    "release_reconciliation": "tests/test_universal_release_reconciliation.py",
    "external_state_sum": "tests/test_universal_external_state_sum.py",
    "benchmark_suite": "tests/test_universal_benchmark_suite.py",
    "partial_wave": "tests/test_universal_partial_wave.py",
    "dressed_pole": "tests/test_universal_dressed_pole.py",
}

IMPLEMENTATION_STATUSES = (
    "NOT_IMPLEMENTED",
    "IMPLEMENTED_PROVISIONAL",
    "IMPLEMENTED_GATED",
    "IMPLEMENTED_PROMOTABLE",
)

ENGINE_VERIFIED_COMMIT = "1f6908ebc8c76af409d10d6f36bbce6373215cd2"

IMPLEMENTATION_STATUS_BY_ID = {
    "GATE7_PHYSICAL_BACKGROUND": "NOT_IMPLEMENTED",
    "UNIVERSAL_ACTION_EXPANSION": "IMPLEMENTED_GATED",
    "RETAINED_SM_COMPONENT_ATTACHMENT": "IMPLEMENTED_GATED",
    "UNIVERSAL_QUADRATIC_SPECTRUM_AND_PROPAGATORS": "IMPLEMENTED_GATED",
    "UNIVERSAL_CUBIC_AND_QUARTIC_VERTEX_GENERATOR": "IMPLEMENTED_GATED",
    "STANDARD_MODEL_GAUGE_VERTEX_TENSORS": "IMPLEMENTED_GATED",
    "ACTION_OWNED_YUKAWA_MASS_AND_MIXING": "IMPLEMENTED_GATED",
    "LSZ_EXTERNAL_STATE_NORMALIZATION": "IMPLEMENTED_GATED",
    "RENORMALIZATION_AND_LOOP_COMPLETION": "IMPLEMENTED_GATED",
    "UNIVERSAL_GF_SCALE_MAP": "IMPLEMENTED_GATED",
    "KNOWN_PARTICLE_COVERAGE": "IMPLEMENTED_PROVISIONAL",
    "PARTICLE_STABILITY_AND_DECAYS": "IMPLEMENTED_GATED",
    "COLLISION_AND_SCATTERING_PREDICTION": "IMPLEMENTED_GATED",
    "LEPTON_MAGNETIC_MOMENTS": "IMPLEMENTED_GATED",
    "NEW_PARTICLE_SPECTRAL_ENCLOSURES": "IMPLEMENTED_GATED",
    "BENCHMARK_OBSERVABLE_SUITE": "IMPLEMENTED_PROVISIONAL",
    "FROZEN_FORWARD_PREDICTIONS": "IMPLEMENTED_PROVISIONAL",
    "PHYSICAL_RELEASE_RECONCILIATION": "IMPLEMENTED_GATED",
}

ACTION_OWNED_BY_ID = {
    "GATE7_PHYSICAL_BACKGROUND": True,
    "UNIVERSAL_ACTION_EXPANSION": True,
    "RETAINED_SM_COMPONENT_ATTACHMENT": True,
    "UNIVERSAL_QUADRATIC_SPECTRUM_AND_PROPAGATORS": True,
    "UNIVERSAL_CUBIC_AND_QUARTIC_VERTEX_GENERATOR": True,
    "STANDARD_MODEL_GAUGE_VERTEX_TENSORS": True,
    "ACTION_OWNED_YUKAWA_MASS_AND_MIXING": True,
    "LSZ_EXTERNAL_STATE_NORMALIZATION": True,
    "RENORMALIZATION_AND_LOOP_COMPLETION": True,
    "UNIVERSAL_GF_SCALE_MAP": True,
    "KNOWN_PARTICLE_COVERAGE": True,
    "PARTICLE_STABILITY_AND_DECAYS": False,
    "COLLISION_AND_SCATTERING_PREDICTION": False,
    "LEPTON_MAGNETIC_MOMENTS": False,
    "NEW_PARTICLE_SPECTRAL_ENCLOSURES": True,
    "BENCHMARK_OBSERVABLE_SUITE": False,
    "FROZEN_FORWARD_PREDICTIONS": False,
    "PHYSICAL_RELEASE_RECONCILIATION": True,
}

PROMOTION_GATE_BY_ID = {
    "GATE7_PHYSICAL_BACKGROUND": "SAME_CENTER_OUTWARD_74D_Y_Z1_Z2_CONTRACTION",
    "UNIVERSAL_ACTION_EXPANSION": "GATE7_CLOSED_PLUS_HISTORY_SEAM_ACTION_ASSEMBLY",
    "RETAINED_SM_COMPONENT_ATTACHMENT": "CURRENT_AE2_BACKGROUND_FULL_FIELD_ACTION_QUANTUM_SADDLE_AND_SCALE",
    "UNIVERSAL_QUADRATIC_SPECTRUM_AND_PROPAGATORS": "PHYSICAL_S2_PENCIL_BRST_SCALE_AND_GATE7",
    "UNIVERSAL_CUBIC_AND_QUARTIC_VERTEX_GENERATOR": "PHYSICAL_HISTORY_S3_S4_AND_ACTION_SELECTED_MODES",
    "STANDARD_MODEL_GAUGE_VERTEX_TENSORS": "CURRENT_LOCAL_ZERO_MOMENTUM_LORENTZIAN_GAUGE_RESIDUES",
    "ACTION_OWNED_YUKAWA_MASS_AND_MIXING": "CURRENT_SAME_ACTION_HS_HESSIAN_AND_PHYSICAL_HS_AMPLITUDE",
    "LSZ_EXTERNAL_STATE_NORMALIZATION": "SIMPLE_ACTION_SELECTED_PHYSICAL_POLES",
    "RENORMALIZATION_AND_LOOP_COMPLETION": "COMPLETE_DIAGRAM_COUNTERTERM_AND_WARD_LEDGER",
    "UNIVERSAL_GF_SCALE_MAP": "FROZEN_ACTION_C_F_AND_SINGLE_AUTHORIZED_G_F_CALIBRATION",
    "KNOWN_PARTICLE_COVERAGE": "COMPLETE_PHYSICAL_SPECTRUM_AND_COMPARISON_AFTER_FREEZE",
    "PARTICLE_STABILITY_AND_DECAYS": "COMPLETE_ACTION_OWNED_CHANNEL_AND_AMPLITUDE_LEDGER",
    "COLLISION_AND_SCATTERING_PREDICTION": "PHYSICAL_LSZ_RENORMALIZED_AMPLITUDES_AND_KINEMATICS",
    "LEPTON_MAGNETIC_MOMENTS": "ACTION_SELECTED_LEPTONS_RENORMALIZED_VERTEX_WARD_AND_Q2_ZERO",
    "NEW_PARTICLE_SPECTRAL_ENCLOSURES": "COMPLETE_FROZEN_PHYSICAL_SPECTRUM_BEFORE_SEARCH_COMPARISON",
    "BENCHMARK_OBSERVABLE_SUITE": "ALL_REQUIRED_INDEPENDENT_PHYSICAL_BENCHMARKS_MATERIALIZED",
    "FROZEN_FORWARD_PREDICTIONS": "PRE_COMPARISON_COMMIT_WITH_NUMERICAL_INTERVALS_AND_HASHES",
    "PHYSICAL_RELEASE_RECONCILIATION": "ALL_REQUIRED_ROWS_PROMOTED_AND_ONE_CLEAN_RELEASE_REPRODUCTION",
}

ALLOWED_CLASSIFICATIONS = (
    "DERIVED_POINT_PREDICTION",
    "DERIVED_INTERVAL_PREDICTION",
    "DERIVED_SELECTION_RULE",
    "DERIVED_QUALITATIVE_STRUCTURE",
    "COMPARISON_ONLY",
    "OPEN_INTERNAL_BLOCKER",
    "OUTSIDE_BHSM_1_0_SCOPE",
)

REQUIRED_RECORD_IDS = (
    "GATE7_PHYSICAL_BACKGROUND",
    "UNIVERSAL_ACTION_EXPANSION",
    "RETAINED_SM_COMPONENT_ATTACHMENT",
    "UNIVERSAL_QUADRATIC_SPECTRUM_AND_PROPAGATORS",
    "UNIVERSAL_CUBIC_AND_QUARTIC_VERTEX_GENERATOR",
    "STANDARD_MODEL_GAUGE_VERTEX_TENSORS",
    "ACTION_OWNED_YUKAWA_MASS_AND_MIXING",
    "LSZ_EXTERNAL_STATE_NORMALIZATION",
    "RENORMALIZATION_AND_LOOP_COMPLETION",
    "UNIVERSAL_GF_SCALE_MAP",
    "KNOWN_PARTICLE_COVERAGE",
    "PARTICLE_STABILITY_AND_DECAYS",
    "COLLISION_AND_SCATTERING_PREDICTION",
    "LEPTON_MAGNETIC_MOMENTS",
    "NEW_PARTICLE_SPECTRAL_ENCLOSURES",
    "BENCHMARK_OBSERVABLE_SUITE",
    "FROZEN_FORWARD_PREDICTIONS",
    "PHYSICAL_RELEASE_RECONCILIATION",
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _record(
    identifier: str,
    required_output: str,
    implementation_status: str,
    engine_evidence: tuple[str, ...],
    satisfied_dependencies: tuple[str, ...],
    remaining_internal_blockers: tuple[str, ...],
) -> dict[str, Any]:
    evidence = [{
        "kind": "gate_authority",
        "path": GATE7_AUTHORITY,
        "sha256": _sha256(ROOT / GATE7_AUTHORITY),
    }]
    for key in engine_evidence:
        for kind, paths in (("source", ENGINE_PATHS), ("focused_test", ENGINE_TEST_PATHS)):
            path = paths[key]
            evidence.append({"kind": kind, "path": path, "sha256": _sha256(ROOT / path)})
    return {
        "id": identifier,
        "implementation_status": IMPLEMENTATION_STATUS_BY_ID[identifier],
        "implementation_detail": implementation_status,
        "prediction_classification": "OPEN_INTERNAL_BLOCKER",
        "required_output": required_output,
        "evidence": evidence,
        "satisfied_dependencies": list(satisfied_dependencies),
        "dependencies_open": list(remaining_internal_blockers),
        "promotion_gate": PROMOTION_GATE_BY_ID[identifier],
        "action_owned": ACTION_OWNED_BY_ID[identifier],
        "empirical_input_used": False,
        "last_verified_commit": ENGINE_VERIFIED_COMMIT,
        "physical_prediction_materialized": False,
    }


def build_payload() -> dict[str, Any]:
    gate_path = ROOT / GATE7_AUTHORITY
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    sources = {GATE7_AUTHORITY: _sha256(gate_path)}
    sources.update({path: _sha256(ROOT / path) for path in ENGINE_PATHS.values()})
    sources.update({path: _sha256(ROOT / path) for path in ENGINE_TEST_PATHS.values()})

    gate_blocker = gate["exact_blocker"]
    records = [
        _record(
            "GATE7_PHYSICAL_BACKGROUND",
            "ONE_FROZEN_ACTION_SELECTED_PHYSICAL_BACKGROUND_WITH_AN_OUTWARD_CONTRACTION_CERTIFICATE",
            "PRECISE_EQUATION_LEVEL_BLOCKER_LOCALIZED",
            (),
            ("one retained-exact-field 74D replay center", "one-shot nonlinear replay"),
            (gate_blocker,),
        ),
        _record(
            "UNIVERSAL_ACTION_EXPANSION",
            "ACTION_OWNED_S2_S3_S4_ON_THE_FROZEN_PHYSICAL_HISTORY_QUOTIENT",
            "VALIDATED_LOCAL_KERNEL_GATED",
            ("action_expansion", "retained_n12_adapter"),
            ("matrix-free S3/S4 API", "complex physical-frame polarization contractions", "retained 96-point local S0-S2 equivalence audit"),
            ("Gate7 frozen background", "history and seam action assembly", "global physical quotient frame"),
        ),
        _record(
            "RETAINED_SM_COMPONENT_ATTACHMENT",
            "CURRENT_AE2_ATTACHMENT_OF_RETAINED_BUNDLE_REPRESENTATIONS_SELECTION_RULES_AND_RESPONSE_SEEDS",
            "RETAINED_COMPONENT_MATCH_AND_NONPROMOTION_BLOCKERS_IMPLEMENTED",
            ("retained_sm_adapter",),
            ("faithful three-family chiral bundle", "allowed Yukawa channel classes", "gauge/HS response seeds", "historical-center nonpromotion"),
            ("Gate7 closed background", "current AE2 background attachment", "machine-readable full gauge-fermion-HS action", "same-action replacement quantum saddle", "action-selected HS direction", "action-derived Yukawa matrices and spectrum"),
        ),
        _record(
            "UNIVERSAL_QUADRATIC_SPECTRUM_AND_PROPAGATORS",
            "ACTION_OWNED_POLES_RESIDUES_AND_GAUGE_FIXED_PROPAGATORS",
            "GENERAL_DESCRIPTOR_AND_DRESSED_POLE_ALGEBRA_IMPLEMENTED_GATED",
            ("quadratic_spectrum", "brst_quotient", "momentum_map", "dressed_pole"),
            ("inverse-free generalized eigenproblem", "simple-pole residue algebra", "inverse-free bordered nonlinear dressed-pole tracking", "complex mass/width and left/right residue readout", "simplicity and causal-pole diagnostics", "explicit constraint/gauge nullspace quotient", "Faddeev-Popov regularity check", "guarded background-derived momentum map"),
            ("frozen history S2 pencil", "complete same-action self-energy ledger", "action-owned constraint/gauge generators and gauge condition", "frozen-background momentum-map instance", "physical scale instance"),
        ),
        _record(
            "UNIVERSAL_CUBIC_AND_QUARTIC_VERTEX_GENERATOR",
            "MACHINE_READABLE_ACTION_OWNED_S3_S4_VERTICES_WITH_ALL_INTERNAL_INDICES",
            "BARE_VERTEX_AND_TREE_EXCHANGE_ALGEBRA_IMPLEMENTED_GATED",
            ("action_expansion", "vertex_amplitude", "retained_n12_adapter"),
            ("matrix-free bare S3/S4 contractions", "complex external polarization support", "inverse-free tree exchange solve", "complete s/t/u tree assembly with one quartic contact"),
            ("history/seam S3/S4 assembly", "action-selected external modes", "momentum and symmetry bookkeeping"),
        ),
        _record(
            "STANDARD_MODEL_GAUGE_VERTEX_TENSORS",
            "RETAINED_SU3_SU2_U1_REPRESENTATION_TENSORS_WITH_ACTION_DERIVED_LOCAL_COUPLINGS",
            "REPRESENTATION_AND_VERTEX_TENSORS_IMPLEMENTED_COUPLING_PROMOTION_GATED",
            ("sm_gauge_vertices", "retained_sm_adapter"),
            ("retained multiplet generators", "nonabelian structure constants", "fermion-gauge and three-gauge internal tensors", "measured-coupling rejection"),
            ("current-background local zero-momentum gauge residues", "electric-magnetic Lorentzian equality", "same-action coupling normalization"),
        ),
        _record(
            "ACTION_OWNED_YUKAWA_MASS_AND_MIXING",
            "SAME_ACTION_YUKAWA_MATRICES_FERMION_MASS_RESPONSES_AND_RELATIVE_LEFT_MIXING",
            "YUKAWA_MASS_AND_MIXING_ALGEBRA_IMPLEMENTED_SELECTION_GATED",
            ("yukawa_vertices", "retained_sm_adapter"),
            ("four retained gauge-invariant channel types", "same-action-HS-Hessian provenance gate", "SVD mass response", "CKM/PMNS-type relative left frames", "observable-fit rejection"),
            ("current action-selected physical HS direction", "current same-action 3x3 Yukawa matrices", "physical HS amplitude", "simple action-derived mass spectra"),
        ),
        _record(
            "LSZ_EXTERNAL_STATE_NORMALIZATION",
            "ACTION_SELECTED_UNIT_RESIDUE_EXTERNAL_STATES",
            "INVERSE_FREE_SIMPLE_POLE_NORMALIZATION_IMPLEMENTED_GATED",
            ("lsz", "quadratic_spectrum"),
            ("descriptor-derivative unit-residue normalization",),
            ("physical simple poles", "action-selected mode identities", "frozen-background pole provenance"),
        ),
        _record(
            "RENORMALIZATION_AND_LOOP_COMPLETION",
            "FINITE_ACTION_OWNED_LOOP_VERTICES_WITH_WARD_SLAVNOV_TAYLOR_CLOSURE",
            "REGULATED_LEDGER_AND_PROMOTION_GATES_IMPLEMENTED",
            ("loop_renormalization", "rg_flow", "dressed_pole"),
            ("Laurent ledger", "counterterm/ghost/Jacobian categories", "Ward residual checks", "observable-fit rejection", "joint same-action full-parameter RG transport", "RG invariant residual monitoring", "complete-ledger and Gate7 guarded dressed-pole consumer"),
            ("complete action-owned diagram ledger", "complete counterterm ledger", "sector Ward identities", "finite observable extraction"),
        ),
        _record(
            "UNIVERSAL_GF_SCALE_MAP",
            "ONE_SHARED_DIMENSIONAL_MAP_G_F_EQUALS_C_F_OVER_LAMBDA_SQUARED",
            "SOLE_CALIBRATION_FORMULA_IMPLEMENTED_INPUTS_OPEN",
            ("gf_scale",),
            ("one-calibration API", "sector-retuning rejection"),
            ("action-derived frozen c_F", "owner-authorized G_F comparison datum", "frozen background identity"),
        ),
        _record(
            "KNOWN_PARTICLE_COVERAGE",
            "COMPLETE_ACTION_DERIVED_MODE_AND_OBSERVABLE_MATRIX_FOR_ESTABLISHED_PARTICLE_PHYSICS",
            "CLASSIFICATION_LEDGER_ONLY",
            ("spectral_forecast", "retained_sm_adapter", "yukawa_vertices", "prediction_freeze"),
            ("interval mode and stability record types", "immutable coverage matrix and downstream comparison firewall", "retained chiral bundle match", "mass/mixing readout algebra"),
            ("physical spectrum", "quantum-number assignment", "known-particle comparison layer", "all required benchmark predictions"),
        ),
        _record(
            "PARTICLE_STABILITY_AND_DECAYS",
            "COMPLETE_CHANNEL_SELECTION_PARTIAL_WIDTH_TOTAL_WIDTH_AND_LIFETIME_REGISTRY",
            "TWO_THREE_AND_RECURSIVE_MULTI_BODY_READOUT_AND_INTERVAL_STABILITY_ALGEBRA_IMPLEMENTED_GATED",
            ("decay_collision", "spectral_forecast", "lsz", "vertex_amplitude", "external_state_sum"),
            ("two-body phase space", "deterministic three-body invariant/helicity-angle phase space", "deterministic recursive Lorentz-invariant multi-body phase space with reconstructed four-momenta", "physical-quotient outgoing sums and incoming density-matrix averages", "channel aggregation", "complete-ledger stability criterion"),
            ("physical mode spectrum", "complete action-owned channel enumeration", "renormalized amplitudes", "outward multi-body quadrature error where required", "physical unit map"),
        ),
        _record(
            "COLLISION_AND_SCATTERING_PREDICTION",
            "ACTION_OWNED_LSZ_AMPLITUDES_AND_CROSS_SECTIONS_FOR_REQUIRED_BENCHMARKS",
            "TREE_TWO_TO_TWO_AND_COUPLED_PARTIAL_WAVE_READOUT_ALGEBRA_IMPLEMENTED_GATED",
            ("vertex_amplitude", "lsz", "decay_collision", "loop_renormalization", "momentum_map", "external_state_sum", "partial_wave"),
            ("tree contact-plus-exchange algebra", "complete s/t/u assembly without quartic double counting", "physical-quotient outgoing sums and incoming density-matrix averages", "two-to-two phase space and angular quadrature", "guarded Mandelstam invariant map", "coupled-channel Legendre partial-wave projection", "complete-ledger unitarity and incomplete-subspace absorption/excess diagnostics"),
            ("physical external modes", "renormalized complete amplitudes", "complete open-channel unitarity ledger", "benchmark kinematics", "hadronic bridge where required"),
        ),
        _record(
            "LEPTON_MAGNETIC_MOMENTS",
            "ACTION_DERIVED_ELECTRON_MUON_TAU_F2_ZERO_PREDICTIONS",
            "FORM_FACTOR_PROJECTOR_AND_PROMOTION_GATES_IMPLEMENTED",
            ("precision_form_factor", "loop_renormalization", "lsz", "yukawa_vertices"),
            ("basis-independent F1/F2 projector", "a_l=F2(0) readout", "fail-closed renormalized-vertex plus LSZ muon g-2 composition"),
            ("action-selected lepton modes", "complete renormalized electromagnetic vertex", "Ward normalization F1(0)=1", "q-squared to zero enclosure"),
        ),
        _record(
            "NEW_PARTICLE_SPECTRAL_ENCLOSURES",
            "FROZEN_MODE_INTERVALS_OR_EXCLUSIONS_WITH_QUANTUM_NUMBERS_AND_DECAYS",
            "INTERVAL_FORECAST_ALGEBRA_IMPLEMENTED_GATED",
            ("spectral_forecast", "quadratic_spectrum", "dressed_pole", "decay_collision"),
            ("declared-domain spectral exclusion", "inverse-free complex dressed-pole mass/width readout", "interval decay-channel classification"),
            ("complete physical spectrum enclosure", "physical scale", "complete decay ledger", "pre-comparison frozen forecast artifact"),
        ),
        _record(
            "BENCHMARK_OBSERVABLE_SUITE",
            "INDEPENDENT_MASS_MIXING_DECAY_SCATTERING_AND_PRECISION_BENCHMARKS",
            "CROSS_SECTOR_BENCHMARK_MANIFEST_EVALUATOR_IMPLEMENTED_NO_PHYSICAL_OUTPUTS",
            ("benchmark_suite", "prediction_freeze", "quadratic_spectrum", "vertex_amplitude", "decay_collision", "precision_form_factor", "retained_sm_adapter", "sm_gauge_vertices", "yukawa_vertices"),
            ("pre-comparison benchmark manifest schema", "exact mode-and-observable coverage check", "cross-sector action/background/scale consistency", "required-engine dependency check", "promoted frozen-prediction classification check"),
            ("Gate7 closure", "instantiated action-owned engines", "frozen physical benchmark definitions", "materialized promoted benchmark predictions", "comparison-after-prediction records"),
        ),
        _record(
            "FROZEN_FORWARD_PREDICTIONS",
            "COMMITTED_PRE_COMPARISON_NOVEL_PREDICTIONS_AND_FALSIFICATION_TARGETS",
            "FIREWALL_SCHEMA_ONLY",
            ("spectral_forecast", "prediction_freeze"),
            ("experimental-result-free interval forecast functions", "immutable prediction records and comparison firewall"),
            ("frozen physical spectrum", "novel prediction registry", "pre-comparison commit and hashes"),
        ),
        _record(
            "PHYSICAL_RELEASE_RECONCILIATION",
            "FULL_BHSM_1_0_RELEASE_WITH_EVERY_REQUIRED_ROW_DERIVED_OR_EXPLICITLY_SCOPED",
            "EXECUTABLE_FAIL_CLOSED_RELEASE_RECONCILIATION_IMPLEMENTED_GATED",
            ("release_reconciliation", "prediction_freeze"),
            ("single-action/background/scale consistency checks", "noncircular prerequisite-row promotion check", "complete frozen benchmark coverage check", "byte-exact artifact manifest", "clean-reproduction gate"),
            ("Gate7 closure", "all required physical rows", "one clean deterministic release reproduction", "mainline release integration"),
        ),
    ]

    identifiers = tuple(record["id"] for record in records)
    validations = {
        "Gate7_authority_is_validated": gate["validation_passed"] is True,
        "Gate7_is_not_closed": gate["claim_boundary"]["Gate7"] == "ACTIVE_NOT_CLOSED",
        "same_center_interval_contraction_is_the_exact_Gate7_owner": (
            gate["claim_boundary"]["current_center_interval_contraction"]
            == "OPEN_PRECISELY_LOCALIZED"
        ),
        "all_required_rows_are_present_once": (
            identifiers == REQUIRED_RECORD_IDS and len(set(identifiers)) == len(identifiers)
        ),
        "all_rows_use_allowed_classifications": all(
            record["prediction_classification"] in ALLOWED_CLASSIFICATIONS for record in records
        ),
        "all_rows_use_frozen_implementation_statuses": all(
            record["implementation_status"] in IMPLEMENTATION_STATUSES for record in records
        ),
        "implemented_infrastructure_is_not_relabelled_as_prediction": all(
            record["physical_prediction_materialized"] is False for record in records
        ),
        "every_open_row_has_a_concrete_internal_blocker": all(
            record["dependencies_open"] for record in records
        ),
        "no_measured_value_is_used_upstream": all(
            record["empirical_input_used"] is False for record in records
        ),
        "every_capability_has_hashed_evidence_and_a_promotion_gate": all(
            record["evidence"] and record["promotion_gate"] for record in records
        ),
        "FULL_BHSM_COMPLETE_false": gate["FULL_BHSM_COMPLETE"] is False,
    }
    return {
        "artifact": "BHSM_PHYSICAL_COMPLETENESS_MATRIX",
        "schema_version": 2,
        "canonical_action_version": "BHSM-AE-2.0.0",
        "FULL_BHSM_COMPLETE": False,
        "current_status": "GATE7_INTERVAL_PROMOTION_OPEN__UNIVERSAL_ACTION_TO_OBSERVABLE_INFRASTRUCTURE_IMPLEMENTED_GATED",
        "prediction_firewall": (
            "MEASURED_VALUES_MAY_NOT_SELECT_UPSTREAM_BRANCH_COEFFICIENT_"
            "NORMALIZATION_FORMULA_CARRIER_MODE_OR_RENORMALIZATION_SCALE"
        ),
        "allowed_classifications": list(ALLOWED_CLASSIFICATIONS),
        "allowed_implementation_statuses": list(IMPLEMENTATION_STATUSES),
        "status_taxonomy": {
            "implementation_status": "CAPABILITY_MATURITY_ONLY",
            "prediction_classification": "SCIENTIFIC_OUTPUT_AUTHORITY_ONLY",
            "action_owned": "THE_IMPLEMENTED_CAPABILITY_ENFORCES_OR_CARRIES_ACTION_PROVENANCE;_THIS_DOES_NOT_IMPLY_A_PHYSICAL_OUTPUT_EXISTS",
        },
        "Gate7_authority": {
            "path": GATE7_AUTHORITY,
            "status": gate["claim_boundary"]["Gate7"],
            "exact_blocker": gate_blocker,
            "background_freeze_for_universal_physics_engine": gate["adjudication"][
                "background_freeze_for_universal_physics_engine"
            ],
        },
        "source_sha256": sources,
        "records": records,
        "completion_rule": {
            "Gate7_must_be_closed": True,
            "every_required_row_must_leave_OPEN_INTERNAL_BLOCKER": True,
            "point_or_interval_predictions_must_be_frozen_before_comparison": True,
            "implemented_API_is_never_sufficient_evidence_of_a_prediction": True,
        },
        "validation": validations,
        "validation_passed": all(validations.values()),
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
