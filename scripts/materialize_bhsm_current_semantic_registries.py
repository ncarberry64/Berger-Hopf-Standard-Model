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
    "artifacts/flagship_integration/BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json",
    "artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
    "artifacts/flagship_integration/BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json",
    "artifacts/flagship_integration/BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH.json",
    "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json",
    "artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json",
    "artifacts/flagship_integration/BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
    "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json",
    "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json",
    "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json",
    "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json",
    "artifacts/flagship_integration/BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json",
    "artifacts/flagship_integration/BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json",
    "artifacts/flagship_integration/BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json",
    "artifacts/flagship_integration/BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json",
    "artifacts/flagship_integration/BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json",
    "artifacts/flagship_integration/BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json",
    "artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json",
    "artifacts/flagship_integration/BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json",
    "artifacts/flagship_integration/BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json",
    "artifacts/flagship_integration/BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER.json",
    "artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json",
    "artifacts/flagship_integration/BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json",
    "artifacts/flagship_integration/BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json",
    "artifacts/flagship_integration/BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json",
    "artifacts/flagship_integration/BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.json",
    "artifacts/flagship_integration/BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_SOLUTION_BALL.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json",
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
    seam_synthesis_no_go = loaded["artifacts/flagship_integration/BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json"]
    endpoint_load_reduction = loaded["artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"]
    moving_endpoint_jets = loaded["artifacts/flagship_integration/BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json"]
    force_first_jet = loaded["artifacts/flagship_integration/BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH.json"]
    force_adjoint = loaded["artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json"]
    forward_adjoint_kkt = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"]
    kkt_existence = loaded["artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json"]
    continuation = loaded["artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json"]
    direct_existence = loaded["artifacts/flagship_integration/BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json"]
    chronology = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json"]
    asymptotic_connection = loaded["artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json"]
    asymptotic_nhim = loaded["artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"]
    maximal_weyl = loaded["artifacts/flagship_integration/BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"]
    maximal_adjoint = loaded["artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json"]
    c2_maximal = loaded["artifacts/flagship_integration/BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"]
    projected_cauchy = loaded["artifacts/flagship_integration/BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"]
    heat_zeta = loaded["artifacts/flagship_integration/BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json"]
    exact_field = loaded["artifacts/flagship_integration/BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"]
    launch_chart = loaded["artifacts/flagship_integration/BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"]
    launch_adjoint = loaded["artifacts/flagship_integration/BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json"]
    fixed_seed_owner = loaded["artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"]
    parametric_base = loaded["artifacts/flagship_integration/BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"]
    signed_adjoint = loaded["artifacts/flagship_integration/BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"]
    duration_coverage = loaded["artifacts/flagship_integration/BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"]
    source_ontology = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"]
    joint_heat_seed = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"]
    core_diagram = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT.json"]
    graded_cotangent = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT.json"]
    duration_incidence = loaded["artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER.json"]
    ddelta_transport = loaded["artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT.json"]
    ddelta_row = loaded["artifacts/flagship_integration/BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"]
    reduced_row = loaded["artifacts/flagship_integration/BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"]
    suppressed_row = loaded["artifacts/flagship_integration/BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json"]
    core_audit = loaded["artifacts/flagship_integration/BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json"]
    nhim_angular_no_go = loaded["artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"]
    local_reset_terminal = loaded["artifacts/flagship_integration/BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json"]
    momentum_jacobian = loaded["artifacts/flagship_integration/BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.json"]
    full_reset_jacobian = loaded["artifacts/flagship_integration/BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"]
    terminal_candidate = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json"]
    terminal_center = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json"]
    terminal_radii = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"]
    terminal_margin = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"]
    terminal_orientation = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"]
    terminal_component = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY.json"]
    terminal_two_sided = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"]
    weight_seven_descriptor = loaded["artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json"]
    weight_five_modulation = loaded["artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json"]
    weight_five_mp_audit = loaded["artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION.json"]
    analytic_center_lift = loaded["artifacts/flagship_integration/BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json"]
    interval_center_lift = loaded["artifacts/flagship_integration/BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json"]
    full_asymptotic_branch = loaded["artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"]
    frontier = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"]
    if not (
        exact_field["claim_boundary"]["exact_fixed_s_field_oracle"] == "CERTIFIED"
        and exact_field["claim_boundary"]["actual_parametric_base_history"] == "OPEN"
        and launch_chart["claim_boundary"]["local_C2_launch_manifold"]
        == "CERTIFIED_73_DIMENSIONAL"
        and launch_chart["dimension_theorem"]["swapped_C2_seed_image"] == 72
        and launch_chart["dimension_theorem"]["fixed_C2_seed_lift_kernel"] == 67
        and launch_chart["dimension_theorem"]["C2_launch_manifold"] == 73
        and launch_chart["adjudication"]["reset_member_selected"] is False
        and launch_chart["claim_boundary"]["maximal_C2_response"] == "OPEN"
        and launch_adjoint["claim_boundary"]["launch_adjoint_interface"] == "DERIVED"
        and launch_adjoint["adjudication"]["67_kernel_downstream_C2_contribution"]
        == "IDENTICALLY_ZERO"
        and launch_adjoint["adjudication"]["67_kernel_directions_may_be_discarded_from_full_seam_saddle"]
        is False
        and launch_adjoint["claim_boundary"]["actual_zero_source_force"] == "OPEN"
        and fixed_seed_owner["claim_boundary"]["fixed_C2_kernel_identification"]
        == "DERIVED"
        and fixed_seed_owner["adjudication"][
            "67_kernel_is_the_raw_fixed_C2_preceding_E1_tangent"
        ]
        is True
        and fixed_seed_owner["adjudication"][
            "separate_arbitrary_direct_seam_covector_should_be_invented"
        ]
        is False
        and fixed_seed_owner["claim_boundary"]["actual_joint_base_history_and_adjoint"]
        == "OPEN_CURRENT_OWNER"
        and parametric_base["claim_boundary"][
            "parametric_base_history_existence_through_1222"
        ]
        == "DERIVED"
        and parametric_base["adjudication"][
            "proof_center_selected_as_a_physical_member"
        ]
        is False
        and parametric_base["claim_boundary"]["signed_joint_adjoint"]
        == "OPEN_NUMERICAL_CERTIFICATION"
        and signed_adjoint["claim_boundary"]["signed_finite_core_adjoint_assembly"]
        == "DERIVED"
        and signed_adjoint["adjudication"]["proof_center_used_as_physical_history"]
        is False
        and signed_adjoint["claim_boundary"]["actual_BHSM_signed_covector"]
        == "OPEN"
        and duration_incidence["claim_boundary"][
            "signed_radius_lapse_duration_incidence_formula"
        ]
        == "DERIVED"
        and duration_incidence["claim_boundary"][
            "signed_D_Y_Delta_reference_center_ball"
        ]
        == "CERTIFIED_LOCAL_SEED"
        and duration_incidence["claim_boundary"]["signed_D_Y_Delta"] == "OPEN"
        and duration_incidence["adjudication"]["proof_center_used_as_physical_history"]
        is False
        and ddelta_transport["status"]
        == "COARSE_DDELTA_TRANSPORT_CERTIFIED_BUT_NOT_SIGN_RESOLVING"
        and ddelta_transport["adjudication"]["physical_obstruction_found"]
        is False
        and ddelta_transport["adjudication"][
            "signed_DDelta_on_exact_parametric_family"
        ]
        == "OPEN_NOT_RESOLVED_BY_COARSE_BOUND"
        and ddelta_row["adjudication"]["direct_signed_Delta_recombination"]
        == "DERIVED"
        and ddelta_row["adjudication"]["selected_line_b_psi_inverse_free_identity"]
        == "DERIVED"
        and ddelta_row["adjudication"]["hard_response_evaluation"]
        == "SPECTRAL_COMPLEMENT_NOT_BORDERED_SOLVE"
        and ddelta_row["adjudication"]["full_98_by_98_D2Delta_norm_required"]
        is False
        and ddelta_row["adjudication"]["one_dominant_D2Delta_row_sufficient"]
        is True
        and ddelta_row["adjudication"]["mixed_second_eigenline_vector_required"]
        is False
        and ddelta_row["adjudication"]["mixed_second_eigenline_contraction"]
        == "REDUCED_TO_ONE_HARD_ADJOINT_AND_LOCAL_SOURCE"
        and ddelta_row["adjudication"][
            "moving_eigenline_derivative_matrix_required_for_cb_row"
        ]
        is False
        and ddelta_row["adjudication"][
            "nested_hard_adjoint_vectors_required_for_cb_row"
        ]
        is False
        and ddelta_row["adjudication"]["fully_reduced_interval_representation"]
        == "LOCAL_ACTION_AND_SOURCE_JETS_PLUS_Psi_Psi_h_Psi_i_z_Vhard"
        and ddelta_row["adjudication"]["complete_cb_row_assembly"]
        == "FINITE_LOCAL_ACTION_SOURCE_JETS_AND_ONE_FIRST_EIGENLINE_JACOBI_MATRIX_ONLY"
        and ddelta_row["adjudication"][
            "rigorous_dominant_row_enclosure_on_exact_tube"
        ]
        == "OPEN"
        and ddelta_row["adjudication"]["physical_event_stop_or_zero_force_found"]
        is False
        and reduced_row["adjudication"]["dominant_bc_row"]
        == "CERTIFIED_BELOW_RESOLVING_CEILING"
        and reduced_row["adjudication"]["nested_hard_adjoint_vectors_required"]
        is False
        and reduced_row["adjudication"]["s_suppressed_hard_response_row"]
        == "OPEN"
        and reduced_row["adjudication"]["signed_D_Y_Delta_on_exact_family"]
        == "OPEN_PENDING_s_HARD_ROW"
        and reduced_row["adjudication"]["Gate7"] == "OPEN"
        and suppressed_row["adjudication"]["s_suppressed_hard_response_row"]
        == "CERTIFIED"
        and suppressed_row["adjudication"]["complete_signed_D2Delta_dominant_row"]
        == "CERTIFIED_BELOW_RESOLVING_CEILING"
        and suppressed_row["adjudication"]["signed_D_Y_Delta_on_exact_node_1214_family"]
        == "ZERO_EXCLUDED"
        and suppressed_row["adjudication"]["transposed_exact_segment_map_action"]
        == "OPEN"
        and suppressed_row["adjudication"]["Gate7"] == "OPEN"
        and core_audit["claim_boundary"]["core_transmitted_physical_manifold"]
        == "OWNER_HYPOTHESIS_NOT_ACTION_DERIVED"
        and core_audit["claim_boundary"]["a_equals_1_over_118"]
        == "OWNER_CANDIDATE_NOT_DERIVED"
    ):
        raise RuntimeError("exact C2 launch/core-nonselection frontier is not current")
    if ae2.get("action_version") != "BHSM-AE-2.0.0":
        raise RuntimeError("AE2 action version mismatch")
    if not (
        duration_coverage["adjudication"][
            "all_1222_interval_transposed_duration_actions"
        ] == "CERTIFIED"
        and source_ontology["external_internal_partition"]["set_to_zero"]
        == ["J_ext"]
        and source_ontology["validation"][
            "zero_external_source_does_not_impose_zero_birth_trace"
        ] is True
        and source_ontology["adjudication"]["internal_response_zeroing"]
        == "FORBIDDEN"
        and joint_heat_seed["adjudication"]["joint_reverse_seed_formula"]
        == "CLOSED"
        and joint_heat_seed["adjudication"][
            "actual_joint_graded_coefficient_cotangent"
        ] == "OPEN_CURRENT_NUMERICAL_OWNER"
        and core_diagram["adjudication"][
            "all_1222_interval_transposed_duration_actions"
        ] == "CERTIFIED"
        and core_diagram["adjudication"]["joint_heat_cotangent_reverse_seed"]
        == "CLOSED"
        and core_diagram["adjudication"]["exact_joint_spectral_trace"]
        == "OPEN"
        and graded_cotangent["adjudication"]["new_grading_required"] is False
        and graded_cotangent["matching_audit"][
            "actual_per_level_joint_operator_family"
        ] == "ACTUALLY_MISSING"
    ):
        raise RuntimeError("joint Gate7 source/cotangent frontier is not current")
    if force_sign_no_go["claim_boundary"]["universal_force_sign_shortcut"] != "CLOSED_INVALID":
        raise RuntimeError("finite-endpoint force-sign shortcut was not closed invalid")
    if seam_synthesis_no_go["claim_boundary"]["broad_negative_axis_synthesis_route"] != "CLOSED_INVALID":
        raise RuntimeError("broad negative-axis synthesis route was not closed invalid")
    if not (
        endpoint_load_reduction["claim_boundary"]["endpoint_domain_ownership"]
        == "CLOSED"
        and endpoint_load_reduction["claim_boundary"]["actual_projected_force"]
        == "OPEN"
        and endpoint_load_reduction["minimal_maximal_history_theorem"][
            "universal_terminal_reachability_required"
        ] is False
    ):
        raise RuntimeError("action-owned endpoint-load reduction is not current")
    if not (
        moving_endpoint_jets["claim_boundary"][
            "moving_endpoint_two_jet_chain_rule"
        ] == "DERIVED"
        and moving_endpoint_jets["claim_boundary"]["actual_maximal_history"]
        == "OPEN"
        and moving_endpoint_jets["claim_boundary"]["actual_projected_force"]
        == "OPEN"
    ):
        raise RuntimeError("reset-stratum moving-endpoint jet frontier is not current")
    if not (
        force_first_jet["claim_boundary"]["G7_08_actual_projected_force"]
        == "OPEN_CURRENT_OWNER"
        and force_first_jet["action_derivative_critical_path"][
            "first_jet_highest_action_derivative"
        ] == "D3_L"
        and force_first_jet["action_derivative_critical_path"][
            "mixed_second_highest_action_derivative"
        ] == "D4_L"
    ):
        raise RuntimeError("force first-jet critical path is not current")
    if not (
        force_adjoint["claim_boundary"]["G7_08_force_adjoint_pullback"]
        == "DERIVED"
        and force_adjoint["computational_consequence"][
            "forward_Jacobi_columns_required"
        ] == 0
        and force_adjoint["claim_boundary"][
            "parametric_maximal_base_history_or_joint_KKT"
        ] == "OPEN"
    ):
        raise RuntimeError("force adjoint-pullback frontier is not current")
    if not (
        forward_adjoint_kkt["claim_boundary"]["G7_09_joint_system"]
        == "DERIVED_UNSOLVED"
        and forward_adjoint_kkt["claim_boundary"][
            "actual_finite_endpoint_stratum_solution"
        ] == "OPEN_CURRENT_OWNER"
        and forward_adjoint_kkt["claim_boundary"][
            "single_reset_representative_sufficient"
        ] is False
    ):
        raise RuntimeError("finite-endpoint forward-adjoint KKT frontier is not current")
    if not (
        kkt_existence["claim_boundary"]["finite_endpoint_KKT_root"]
        == "OPEN_CURRENT_OWNER"
        and kkt_existence["failure_classification"][
            "missing_existential_or_validated_global_temporal_control"
        ] is True
        and kkt_existence["failure_classification"][
            "retained_action_incompatibility_proved"
        ] is False
    ):
        raise RuntimeError("forward-adjoint KKT existence gate is not current")
    if not (
        continuation["adjudication"][
            "local_implicit_function_theorem_applicable_now"
        ] is False
        and continuation["adjudication"][
            "continuation_route_invalid_in_principle"
        ] is False
        and continuation["claim_boundary"]["synthetic_Hessian_promoted"]
        is False
        and continuation["claim_boundary"][
            "historical_constant_reset_Hessian_promoted"
        ] is False
    ):
        raise RuntimeError("same-action continuation precondition audit is not current")
    if not (
        direct_existence["claim_boundary"]["finite_endpoint_KKT_root"]
        == "OPEN_CURRENT_OWNER"
        and direct_existence["adjudication"][
            "heat_regulator_alone_closes_direct_method"
        ] is False
        and direct_existence["adjudication"][
            "local_principal_coercivity_closes_global_KKT_existence"
        ] is False
        and direct_existence["adjudication"][
            "direct_existence_route_invalid_in_principle"
        ] is False
        and direct_existence["adjudication"][
            "retained_action_incompatibility_proved"
        ] is False
    ):
        raise RuntimeError("direct KKT existence precondition audit is not current")
    if not (
        chronology["claim_boundary"]["maximal_child_exterior_oracle"]
        == "OPEN_CURRENT_OWNER"
        and chronology["claim_boundary"]["finite_endpoint_KKT_root"]
        == "OPTIONAL_SUFFICIENT_SUBROUTE_OPEN"
        and chronology["adjudication"][
            "post_event_finite_terminal_reachability_required"
        ] is False
        and chronology["adjudication"][
            "infinite_Friedrichs_child_exterior_allowed"
        ] is True
    ):
        raise RuntimeError("formation/decay chronology supersession is not current")
    if not (
        asymptotic_connection["claim_boundary"]["maximal_child_exterior_oracle"]
        == "OPEN_CURRENT_OWNER"
        and asymptotic_connection["adjudication"][
            "analytic_branch_is_current_exterior_oracle"
        ] is False
        and asymptotic_connection["adjudication"][
            "infinite_Friedrichs_route_invalid_in_principle"
        ] is False
        and asymptotic_connection["adjudication"][
            "chord_03_has_finite_proof_obligation"
        ] is False
    ):
        raise RuntimeError("asymptotic child-exterior connection audit is not current")
    if not (
        asymptotic_nhim["capture_theorem"]["H4_limit"] == "H0>0"
        and asymptotic_nhim["scope"]["AE2_reset_entry_certified"] is False
        and maximal_weyl["closed_here"][
            "Friedrichs_negative_z_Weyl_value_uniqueness"
        ] is True
        and maximal_adjoint["validation"]["fixed_channel_source_Dini_is_closed"]
        is True
        and maximal_adjoint["claim_boundary"]["actual_weighted_load"]
        == "OPEN_CURRENT_OWNER"
        and c2_maximal["adjudication"][
            "abstract_M_C2_value_definition_exists_and_is_unique"
        ] is True
        and projected_cauchy["claim_boundary"]["projected_Cauchy_criterion"]
        == "DERIVED"
        and projected_cauchy["claim_boundary"]["actual_projected_Cauchy_tail"]
        == "OPEN_CURRENT_OWNER"
        and projected_cauchy["validation"][
            "absolute_weighted_norm_is_only_sufficient"
        ] is True
        and heat_zeta["claim_boundary"]["finite_optical_infinite_route"]
        == "CLOSED_NO_GO"
        and heat_zeta["claim_boundary"][
            "infinite_optical_common_scale_zeta_criterion"
        ] == "DERIVED"
        and heat_zeta["claim_boundary"]["separate_common_scale_zeta_tail_required"]
        is False
        and heat_zeta["claim_boundary"]["actual_joint_replacement_Cauchy_tail"]
        == "OPEN_CURRENT_OWNER"
        and nhim_angular_no_go["claim_boundary"][
            "asymptotic_NHIM_absolute_graded_force_route"
        ] == "CLOSED_NO_GO"
        and nhim_angular_no_go["claim_boundary"]["actual_finite_stratum"]
        == "OPEN_CURRENT_OWNER"
        and nhim_angular_no_go["route_adjudication"]["new_canonical_stop_declared"]
        is False
        and local_reset_terminal["claim_boundary"][
            "local_reset_terminal_transversality_route"
        ] == "CLOSED_INSUFFICIENT"
        and local_reset_terminal["claim_boundary"]["actual_finite_stratum"]
        == "OPEN_CURRENT_OWNER"
        and local_reset_terminal["route_adjudication"][
            "global_reset_quotient_finite_stratum_disproved"
        ] is False
        and momentum_jacobian["continuation_consequence"][
            "intrinsic_reset_tangent_recenter_now_analytic"
        ] is True
        and full_reset_jacobian["dimensions"]["rank"] == 57
        and full_reset_jacobian["dimensions"]["physical_tangent_nullity"] == 139
        and terminal_candidate["terminal_normal_block"]["rank"] == 58
        and terminal_candidate["center"]["child"]["hitting_product"] < 0.0
        and terminal_candidate["proof_boundary"][
            "finite_terminal_stratum_certified"
        ] is False
        and terminal_candidate["claim_boundary"]["Gate7"]
        == "ACTIVE_TERMINAL_ROOT_BALL_CERTIFICATION"
        and terminal_center["directed_Y_upper"] < 1.0e-12
        and terminal_center["directed_Z0_upper"] < 1.0e-5
        and terminal_radii["radii_polynomial"]["root_ball_closed"] is True
        and terminal_radii["radii_polynomial"][
            "contraction_bound_Z0_plus_Z2_r"
        ] < 1.0
        and "SUPERSEDED" in terminal_margin["status"]
        and terminal_orientation["root_cubic_transfer"][
            "root_c_psi_upper"
        ] < 0.0
        and terminal_orientation["root_forcing_transfer"][
            "root_b_psi_lower"
        ] > 0.0
        and terminal_orientation["claim_boundary"]["Gate7"]
        == "ACTIVE_FINITE_ENDPOINT_ZERO_SOURCE_FORCE"
        and terminal_component["claim_boundary"]["finite_terminal_incidence"]
        == "CERTIFIED"
        and terminal_component["claim_boundary"]["finite_terminal_incoming_germ"]
        == "CERTIFIED"
        and terminal_component["claim_boundary"][
            "positive_duration_reset_to_later_endpoint_history"
        ] == "OPEN_CURRENT_OWNER"
        and terminal_component["claim_boundary"]["actual_projected_force"]
        == "OPEN_AFTER_OPERATOR"
        and terminal_two_sided["claim_boundary"][
            "positive_duration_forward_child_history"
        ] == "CERTIFIED_LOCAL_EXISTENCE"
        and terminal_two_sided["exact_local_theorem"]["physical_chronology"]
        == "E0_TO_C1_TO_[T>0]_E1_TO_C2"
        and terminal_two_sided["exact_local_theorem"][
            "same_event_recurrence_required"
        ] is False
        and terminal_two_sided["claim_boundary"][
            "compact_finite_endpoint_operator"
        ] == "OPEN_CURRENT_OWNER"
    ):
        raise RuntimeError(
            "maximal-adjoint/NHIM/certified-terminal frontier is not current"
        )
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
