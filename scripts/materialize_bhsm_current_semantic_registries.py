"""Materialize the nine authoritative AE2/Gate-7 normalization registries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.current_semantic_normalization import build_registries  # noqa: E402


TARGET = ROOT / "artifacts/current_semantics"
SOURCES = (
    "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json",
    "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    "artifacts/flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json",
    "artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json",
    "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    "artifacts/flagship_integration/BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE.json",
    "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    "artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO.json",
    "artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json",
    "artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json",
    "artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION.json",
    "artifacts/flagship_integration/BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json",
    "artifacts/flagship_integration/BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json",
    "artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json",
    "artifacts/intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json",
    "artifacts/BHSM_alpha_i_update_v4_2.json",
    "theory/bhsm_prediction_ledger.json",
    "artifacts/frozen_constants_v2.json",
    "artifacts/BHSM_rho_ch_action_audit_v1_9.json",
    "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
    "theory/norman_owner_ontology_recovered.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def verify_current_lineage() -> None:
    """Verify the rebuilt DAG statuses against the newest stored theorems."""

    loaded = {
        item: json.loads((ROOT / item).read_text(encoding="utf-8"))
        for item in SOURCES
        if item.endswith(".json")
    }
    theorem_sources = [item for item in SOURCES if item.startswith("artifacts/flagship_integration/")]
    if not all(loaded[item].get("validation_passed") is True for item in theorem_sources):
        raise RuntimeError("every current Gate7 theorem input must be validated")
    ae2 = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"]
    nonfermion = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"]
    factorized = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json"]
    reduction = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json"]
    radius_route = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json"]
    linear_tail = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json"]
    power_tail = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json"]
    compact_dini = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"]
    angular_dini = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"]
    finite_domain = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"]
    finite_force = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"]
    force_domain = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"]
    event_weyl = loaded["artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"]
    seam_correction = loaded["artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"]
    seam_enclosure = loaded["artifacts/flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"]
    seam_family = loaded["artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"]
    projected_saddle = loaded["artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"]
    time_quotient = loaded["artifacts/flagship_integration/BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json"]
    operator_data_gate = loaded["artifacts/flagship_integration/BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE.json"]
    parametric_oracle = loaded["artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json"]
    radius_jet = loaded["artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"]
    executable_oracle = loaded["artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json"]
    force_sign_no_go = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO.json"]
    weight_seven_descriptor = loaded["artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json"]
    weight_five_modulation = loaded["artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json"]
    weight_five_mp_audit = loaded["artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION.json"]
    analytic_center_lift = loaded["artifacts/flagship_integration/BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json"]
    interval_center_lift = loaded["artifacts/flagship_integration/BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json"]
    full_asymptotic_branch = loaded["artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"]
    frontier = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"]
    if ae2.get("action_version") != "BHSM-AE-2.0.0":
        raise RuntimeError("AE2 action version mismatch")
    if force_sign_no_go["claim_boundary"]["universal_force_sign_shortcut"] != "CLOSED_INVALID":
        raise RuntimeError("finite-endpoint force-sign shortcut was not closed invalid")
    if nonfermion["claim_boundary"]["nonfermion_critical_zero_graph_excluded"] is not True:
        raise RuntimeError("disk does not close the nonfermion threshold obstruction")
    if factorized["claim_boundary"]["factorized_N12_low_energy_source_measure"] != "OPEN":
        raise RuntimeError("disk no longer identifies factorized source measure as open")
    if factorized["claim_boundary"]["strict_product_Dirac_Wronskian_required_in_advance"] is not False:
        raise RuntimeError("disk still requires the superseded strict Wronskian premise")
    if frontier["preserved_open_objects"]["realized_factorized_source_weighted_limiting_absorption"] != "OPEN":
        raise RuntimeError("disk frontier does not identify the current live owner")
    if reduction["claim_boundary"]["abstract_factorized_transfer_to_source_measure_theorem"] != "CLOSED":
        raise RuntimeError("factorized source-measure reduction is not closed")
    if reduction["claim_boundary"]["actual_N12_infinite_end_threshold_normalization"] != "OPEN":
        raise RuntimeError("realized infinite-end normalization is not the current live owner")
    if radius_route["claim_boundary"]["conditional_integrable_radius_threshold_theorem"] != "CLOSED":
        raise RuntimeError("integrable reciprocal-radius threshold route is not closed")
    if not (
        radius_route["claim_boundary"]["actual_N12_reciprocal_radius_integrability"] == "OPEN"
        and radius_route["claim_boundary"]["direct_nonintegrable_tail_theorem"] == "OPEN"
    ):
        raise RuntimeError("realized infinite-tail dichotomy is not the current live owner")
    if linear_tail["claim_boundary"]["exact_linear_radius_tail_theorem"] != "CLOSED":
        raise RuntimeError("exact linear-radius tail theorem is not closed")
    if not (
        linear_tail["claim_boundary"]["actual_N12_radius_asymptotic_class"] == "OPEN"
        and linear_tail["claim_boundary"]["general_sublinear_or_nonasymptotic_tail"] == "OPEN"
    ):
        raise RuntimeError("remaining radius-tail class is not the current live owner")
    if power_tail["claim_boundary"]["all_exact_nonnegative_power_radius_tails"] != "CLOSED":
        raise RuntimeError("exact power-radius tail family is not closed")
    if not (
        power_tail["claim_boundary"]["actual_N12_radius_asymptotic_class"] == "OPEN"
        and power_tail["claim_boundary"]["general_nonasymptotic_tail"] == "OPEN"
    ):
        raise RuntimeError("power-tail predecessor does not preserve its pre-closure frontier")
    if compact_dini["factorization_only_test"]["answer"] != "YES_WITHIN_THE_RETAINED_ADMISSIBLE_CLASS":
        raise RuntimeError("compact-source factorization theorem is not closed")
    if compact_dini["claim_boundary"]["angular_sum"] != "OPEN_CURRENT_OWNER":
        raise RuntimeError("angular channel sum is not the current live owner")
    if angular_dini["adjudication"]["fixed_channel_source_Dini"] != "CLOSED_DO_NOT_REOPEN":
        raise RuntimeError("angular audit reopened the fixed-channel theorem")
    if angular_dini["adjudication"]["arbitrary_positive_tail_angular_sum"] != "FALSE":
        raise RuntimeError("angular audit did not retain its exact counterexample")
    if angular_dini["conditional_at_most_linear_sufficient_class"]["status"] != "CLOSED_CONDITIONAL_THEOREM":
        raise RuntimeError("at-most-linear angular barrier theorem is not closed conditionally")
    if not (
        angular_dini["adjudication"]["eventual_two_sided_Lipschitz_radius_sufficient"] is True
        and angular_dini["adjudication"]["eventual_logarithmic_speed_Osgood_radius_sufficient"] is True
        and angular_dini["adjudication"]["radius_monotonicity_required"] is False
        and angular_dini["adjudication"]["eventual_two_sided_Lipschitz_radius_proved_by_action"] is False
        and angular_dini["adjudication"]["eventual_logarithmic_speed_Osgood_radius_proved_by_action"] is False
    ):
        raise RuntimeError("current angular owner is not the action-to-radius bound")
    if angular_dini["retained_action_uniform_scale_ownership_audit"]["status"] != "EXACT_SCALE_WEIGHTS_DERIVED_NO_OSGOOD_DECAY_THEOREM":
        raise RuntimeError("uniform-scale Osgood ownership audit is not current")
    if finite_domain["claim_boundary"]["finite_encapsulation_existence"] != "CLOSED_LOCAL_ACTION_THEOREM":
        raise RuntimeError("finite-encapsulation existence is not closed locally")
    if finite_domain["claim_boundary"]["zero_source_force"] != "NEXT_CURRENT_OWNER":
        raise RuntimeError("zero-source force is not the current Gate7 owner")
    if not (
        finite_force["claim_boundary"]["zero_source_force_functional"] == "DERIVED"
        and finite_force["claim_boundary"]["zero_source_force_value"] == "OPEN"
    ):
        raise RuntimeError("finite-endpoint force frontier is not current")
    if force_domain["domain_adjudication"]["arbitrary_regular_free_cutoff_allowed"] is not False:
        raise RuntimeError("an arbitrary force-domain cutoff was restored")
    if not (
        event_weyl["claim_boundary"]["event_normal_Weyl_initial_condition"] == "DERIVED"
        and seam_correction["supersession"]["superseded_claim"]
        == "M(0,z)=W_phys_AS_THE_PHYSICAL_AE2_EVENT_INITIAL_VALUE"
        and seam_correction["claim_boundary"]["physical_AE2_event_initial_value"]
        == "OPEN"
        and seam_correction["claim_boundary"][
            "child_arm_Calderon_value_and_geometry_jets"
        ]
        == "OPEN"
        and seam_enclosure["claim_boundary"]["two_sided_child_load_at_z_minus_1"]
        == "ENCLOSED_BROADLY"
        and seam_enclosure["claim_boundary"]["complete_heat_spectral_family"]
        == "OPEN"
        and seam_family["claim_boundary"][
            "complete_spectral_parameter_coverage"
        ]
        == "CLOSED_ON_NEGATIVE_REAL_AXIS"
        and seam_family["claim_boundary"]["actual_spectral_trace_value"]
        == "OPEN"
    ):
        raise RuntimeError("two-sided AE2 force value frontier is not current")
    if not (
        projected_saddle["claim_boundary"][
            "constraint_tangent_force_criterion"
        ] == "DERIVED"
        and projected_saddle["claim_boundary"][
            "ambient_force_zero_required"
        ] is False
        and projected_saddle["claim_boundary"][
            "actual_projected_force_value"
        ] == "OPEN"
        and projected_saddle["claim_boundary"][
            "same_action_saddle"
        ] == "OPEN_COUPLED_TO_FORCE"
    ):
        raise RuntimeError("constraint-projected replacement saddle frontier is not current")
    if not (
        time_quotient["claim_boundary"]["raw_reset_tangent_dimension"]
        == "DERIVED_67"
        and time_quotient["claim_boundary"][
            "post_time_quotient_dimension_count"
        ] == "RETAINED_66"
        and time_quotient["claim_boundary"]["explicit_time_generator"]
        == "OPEN"
        and time_quotient["force_and_saddle_consequence"][
            "raw_boundary_log_R4_projection_promoted_to_physical_quotient"
        ] is False
    ):
        raise RuntimeError("reset time-quotient generator frontier is not current")
    if not (
        operator_data_gate["claim_boundary"][
            "complete_action_owned_exterior_oracle"
        ] == "OPEN_CURRENT_OWNER"
        and operator_data_gate["claim_boundary"][
            "projected_KKT_solver"
        ] == "DERIVED"
        and operator_data_gate["logical_boundary"][
            "persistence_validation_endpoint_may_be_promoted"
        ] is False
        and operator_data_gate["logical_boundary"][
            "infinite_nonencapsulating_formation_tail_reopened"
        ] is False
    ):
        raise RuntimeError("joint finite-history operator data frontier is not current")
    if not (
        parametric_oracle["claim_boundary"][
            "finite_endpoint_oracle_regularity_theorem"
        ] == "DERIVED_CONDITIONAL"
        and parametric_oracle["claim_boundary"][
            "actual_parametric_exterior_oracle"
        ] == "OPEN_CURRENT_OWNER"
        and parametric_oracle["adjudication"][
            "single_hand_selected_reset_history_sufficient"
        ] is False
        and parametric_oracle["adjudication"][
            "global_smoothness_across_endpoint_switches_claimed"
        ] is False
        and parametric_oracle["adjudication"][
            "infinite_tail_analysis_reopened"
        ] is False
    ):
        raise RuntimeError("parametric reset-fiber exterior frontier is not current")
    if not (
        radius_jet["claim_boundary"][
            "radius_Cauchy_jet_variation_after_time_quotient"
        ] == "NONZERO"
        and radius_jet["claim_boundary"]["common_scale_full_action_gauge"]
        is False
        and radius_jet["claim_boundary"]["common_scale_physical_modulation"]
        == "RETAIN"
        and radius_jet["fiber_invariance_adjudication"][
            "actual_parametric_exterior_oracle_still_required"
        ] is True
    ):
        raise RuntimeError("reset-fiber radius-jet and scale-center frontier is not current")
    if not (
        executable_oracle["claim_boundary"][
            "stable_Weyl_value_first_second_jet_solver"
        ] == "DERIVED"
        and executable_oracle["claim_boundary"][
            "actual_parametric_exterior_oracle"
        ] == "OPEN_CURRENT_OWNER"
        and executable_oracle["claim_boundary"][
            "two_chord_core_as_complete_force_domain"
        ] is False
        and executable_oracle["solver_contract"][
            "ill_conditioned_Euler_Dirac_kinetic_block_inverted"
        ] is False
    ):
        raise RuntimeError("executable parametric exterior interface is not current")
    if not (
        weight_seven_descriptor["claim_boundary"][
            "weight_seven_quadratic_action"
        ] == "DERIVED"
        and weight_seven_descriptor["claim_boundary"][
            "physical_descriptor_pencil"
        ] == "DERIVED"
        and weight_seven_descriptor["descriptor"][
            "bordered_clusters"
        ]["center_count"] == 25
        and weight_seven_descriptor["descriptor"][
            "bordered_clusters"
        ]["stable_count"] == 25
        and weight_seven_descriptor["descriptor"][
            "bordered_clusters"
        ]["unstable_count"] == 0
        and weight_seven_descriptor["claim_boundary"][
            "full_remainder_outcome"
        ] == "OPEN"
    ):
        raise RuntimeError("weight-seven transverse descriptor frontier is not current")
    if not (
        weight_five_modulation["claim_boundary"][
            "exact_weight_five_action"
        ] == "DERIVED"
        and weight_five_modulation["claim_boundary"][
            "constraint_reduced_center_force_operator"
        ] == "DERIVED"
        and weight_five_modulation["center_force"][
            "coefficient_solution_evaluated"
        ] is False
        and weight_five_modulation["claim_boundary"][
            "uniform_full_remainder_outcome"
        ] == "OPEN"
    ):
        raise RuntimeError("weight-five center modulation frontier is not current")
    if not (
        weight_five_mp_audit["claim_boundary"][
            "multiprecision_bordered_solve"
        ] == "DERIVED_HISTORICAL"
        and weight_five_mp_audit["claim_boundary"][
            "weight_five_coefficient"
        ] == "OPEN_NOT_PROMOTED"
        and weight_five_mp_audit["tail_diagnostics"][
            "tight_coefficient_enclosure_certified"
        ] is False
        and weight_five_mp_audit["adjudication"][
            "full_remainder_outcome_promoted"
        ] is False
    ):
        raise RuntimeError("weight-five multiprecision nonpromotion frontier is not current")
    if not (
        analytic_center_lift["claim_boundary"][
            "analytic_preconditioned_local_block_lift"
        ] == "DERIVED"
        and analytic_center_lift["converged_tail"][
            "directed_interval_certified"
        ] is False
        and analytic_center_lift["adjudication"][
            "sign_promoted_as_rigorous_action_theorem"
        ] is False
        and analytic_center_lift["claim_boundary"][
            "uniform_full_remainder_outcome"
        ] == "OPEN"
    ):
        raise RuntimeError("analytic local-block center-lift frontier is not current")
    if not (
        interval_center_lift["claim_boundary"][
            "directed_weight_five_center_lift"
        ] == "CERTIFIED"
        and interval_center_lift["common_scale_interval"][
            "strictly_positive"
        ] is True
        and interval_center_lift["common_scale_rate_interval"][
            "strictly_negative"
        ] is True
        and interval_center_lift["claim_boundary"][
            "uniform_full_remainder_outcome"
        ] == "OPEN"
        and interval_center_lift["claim_boundary"][
            "physical_finite_history_zero_source_force"
        ] == "OPEN"
    ):
        raise RuntimeError("directed interval center-lift frontier is not current")
    if not (
        full_asymptotic_branch["claim_boundary"][
            "mathematical_transverse_nonlinear_modulation_consequence"
        ] == "CLOSED_OUTCOME_A"
        and full_asymptotic_branch["nonlinear_consequence"][
            "a_preserves_H4_to_H_inf_positive"
        ] is True
        and full_asymptotic_branch["nonlinear_consequence"][
            "physical_particle_statement"
        ] is False
        and full_asymptotic_branch["claim_boundary"][
            "physical_finite_history_zero_source_force"
        ] == "OPEN"
    ):
        raise RuntimeError("full retained asymptotic-branch frontier is not current")


def materialize() -> list[Path]:
    source_paths = [ROOT / item for item in SOURCES]
    missing = [path for path in source_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"normalization inputs missing: {missing}")
    verify_current_lineage()
    hashes = {item: sha256(ROOT / item) for item in SOURCES}
    registries = build_registries(hashes)
    TARGET.mkdir(parents=True, exist_ok=True)
    output = []
    for name, payload in sorted(registries.items()):
        path = TARGET / name
        path.write_bytes(deterministic_bytes(payload))
        output.append(path)
    return output


if __name__ == "__main__":
    for result in materialize():
        print(result)
