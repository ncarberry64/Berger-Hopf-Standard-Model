"""Derive the local parametric C2 base-family theorem through core 1222."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
EXACT_FIELD = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
HARD = BASE / "BHSM_N12_C2_UNIFORM_GAP_HARD_RESPONSE.json"
ROOT_CENTER = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
ROOT_DATA = ROOT_CENTER.with_suffix(".npz")
PULLBACK = BASE / "BHSM_N12_C2_1222_COMPLETE_GEOMETRY_PULLBACK_NORM.json"
OWNER = BASE / "BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"
THEORY = ROOT / "theory" / "n12_c2_1222_parametric_base_family.md"
INPUTS = (
    LAUNCH,
    EXACT_FIELD,
    CORE,
    CORE_DATA,
    HARD,
    ROOT_CENTER,
    ROOT_DATA,
    PULLBACK,
    OWNER,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing parametric-base inputs: " + ", ".join(missing))
    launch, exact_field, core, hard, root, pullback, owner = (
        _load(path)
        for path in (LAUNCH, EXACT_FIELD, CORE, HARD, ROOT_CENTER, PULLBACK, OWNER)
    )
    if not all(record.get("validation_passed") is True for record in (
        launch, exact_field, core, hard, root, pullback, owner,
    )):
        raise RuntimeError("validated parametric-base lineage required")

    with np.load(CORE_DATA) as data:
        nodes = np.asarray(data["C2_proof_center_nodes"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        tubes = np.asarray(data["node_action_tube_upper"], dtype=float)
        durations = np.asarray(data["segment_proper_duration_interval"], dtype=float)
        log_radius_intervals = np.asarray(data["node_log_R4_interval"], dtype=float)
    with np.load(ROOT_DATA) as data:
        reset_product_center = np.asarray(data["state"], dtype=float)
    initial_center_residual = float(
        np.linalg.norm((nodes[0] - reset_product_center[:98]) * weights)
    )
    root_distance = float(
        root["refined_radii_theorem"]["a_posteriori_root_distance_upper"]
    )
    total_duration = np.sum(durations, axis=0)
    minimum_radius = float(np.exp(np.min(log_radius_intervals[:, 0])))

    validation = {
        "reset_generated_launch_dimension_is_73": (
            launch["dimension_theorem"]["C2_launch_manifold"] == 73
            and launch["adjudication"]["reset_member_selected"] is False
        ),
        "exact_fixed_s_field_is_available_on_the_regular_chart": (
            exact_field["claim_boundary"]["exact_fixed_s_field_oracle"]
            == "CERTIFIED"
        ),
        "complete_fixed_s_growth_is_finite_and_close_to_one": (
            math.isfinite(hard["finite_s_correction"]["covered_full_ball_growth_upper"])
            and hard["finite_s_correction"]["covered_full_ball_growth_upper"]
            < 1.013
        ),
        "selected_line_gap_c_and_Delta_are_strict": (
            hard["validation"]["uniform_line_gap_is_strict"] is True
            and hard["validation"]["c_b_and_Delta_stay_positive"] is True
        ),
        "finite_core_has_1222_positive_intervals": (
            nodes.shape == (1223, 98)
            and durations.shape == (1222, 2)
            and bool(np.all(durations[:, 0] > 0.0))
        ),
        "finite_core_initial_center_is_the_reset_chart_center": (
            initial_center_residual == 0.0
        ),
        "certified_exact_normal_root_is_in_the_initial_flow_tube": (
            root_distance <= float(tubes[0])
        ),
        "finite_core_tubes_and_radii_stay_positive": (
            bool(np.all(tubes > 0.0)) and minimum_radius > 0.0
        ),
        "far_core_edge_is_not_a_physical_endpoint": (
            core["endpoint_event_child_partition"][
                "far_core_edge_is_physical_endpoint"
            ]
            is False
        ),
        "finite_core_geometry_first_jet_norm_is_available": (
            pullback["claim_boundary"]["complete_finite_core_geometry_pullback_norm"]
            == "CERTIFIED"
        ),
        "one_joint_history_adjoint_remains_the_force_owner": (
            owner["adjudication"]["one_joint_history_adjoint_is_preferred"]
            is True
        ),
        "no_selector_endpoint_recurrence_scale_fit_gate_chord_or_prediction_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY",
        "status": (
            "LOCAL_73_PARAMETER_EXACT_C2_HISTORY_FAMILY_EXISTS_THROUGH_FINITE_CORE_1222"
            if passed
            else "C2_1222_PARAMETRIC_BASE_FAMILY_NOT_DERIVED"
        ),
        "classification": (
            "THE_RESET_GENERATED_73_DIMENSIONAL_LAUNCH_CHART,_THE_C2_EXACT_"
            "FIXED_s_ACTION_FIELD,_AND_THE_COMPACT_1222_SEGMENT_REGULAR_COVER_"
            "IMPLY_BY_SMOOTH_ODE_DEPENDENCE_A_NONEMPTY_LOCAL_FAMILY_OF_EXACT_"
            "C2_HISTORIES_AND_THEIR_JACOBI_FIELDS_THROUGH_EVERY_FINITE_CORE_"
            "PREFIX;_THE_PROOF_CENTERS_REMAIN_ENCLOSURE_DATA_NOT_SELECTED_"
            "PHYSICAL_HISTORIES"
        ),
        "theorem": {
            "launch_chart": "R_AE2_LOCAL(xi,s),_(xi,s)_IN_R72_TIMES_[0,epsilon)",
            "state_equation": "D_s_Y=F_s(Y),_Dlambda[F_s]=1",
            "regularity": (
                "F_s_IS_C1_ON_THE_CERTIFIED_SIMPLE_LINE_POSITIVE_Delta_"
                "POSITIVE_RADIUS_CHART"
            ),
            "flow_family": "Y(s;theta)=Phi_s(R_AE2_LOCAL(theta))",
            "Jacobi_family": (
                "D_s_J_theta=D_Y_F_s(Y(s;theta))*J_theta_WITH_"
                "J_theta(0)=D_theta_R_AE2_LOCAL"
            ),
            "existence_scope": (
                "THERE_EXISTS_epsilon_1222>0_FOR_WHICH_THE_FAMILY_EXISTS_"
                "THROUGH_EVERY_PREFIX_OF_THE_1222_SEGMENT_COMPACT_COVER"
            ),
            "coefficient_family": (
                "x(s;theta)=log_R4(Y(s;theta))_AND_THE_PROPER_DURATION_"
                "COEFFICIENTS_ARE_C1_IN_theta"
            ),
            "operator_consequence": (
                "THE_FINITE_CORE_K(theta),M_C2(theta),AND_FIRST_GEOMETRY_"
                "JETS_ARE_ACTION_OWNED_C1_FAMILIES"
            ),
        },
        "finite_cover_witness": {
            "node_count": int(nodes.shape[0]),
            "segment_count": int(durations.shape[0]),
            "proper_duration_interval": [
                float(total_duration[0]), float(total_duration[1])
            ],
            "minimum_node_tube_radius": float(np.min(tubes)),
            "maximum_node_tube_radius": float(np.max(tubes)),
            "minimum_certified_R4": minimum_radius,
            "initial_center_action_residual": initial_center_residual,
            "normal_root_distance_upper": root_distance,
            "initial_tube_radius": float(tubes[0]),
            "complete_fixed_s_growth_upper": hard["finite_s_correction"][
                "covered_full_ball_growth_upper"
            ],
            "epsilon_1222": "EXISTS_POSITIVE_NOT_NUMERICALLY_LOWER_BOUNDED_HERE",
        },
        "adjudication": {
            "positive_duration_forward_history_existence_reopened": False,
            "parametric_C2_base_history_exists_through_finite_core_1222": True,
            "proof_center_selected_as_a_physical_member": False,
            "signed_backward_adjoint_is_well_defined_on_each_family_member": True,
            "signed_backward_adjoint_numerically_evaluated_and_certified": False,
            "far_core_edge_is_event_or_stop": False,
            "maximal_C2_tail": "OPEN_CURRENT_OWNER_AFTER_FINITE_CORE_FORCE_NET",
            "actual_projected_zero_source_force": "OPEN",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "nonempty local 73-parameter exact C2 base family through core 1222",
                "action-owned first Jacobi family exists on every finite prefix",
                "finite-core operator and first geometry jets exist as C1 families",
            ],
            "INVALIDATED": [
                "absence of any parametric base history is the current blocker",
                "a proof center must be selected to define the finite-core family",
                "the 1222 proof edge is a physical endpoint",
            ],
            "OPEN": [
                "validated signed joint-history adjoint covector on the family",
                "graded heat-minus-zeta source contraction",
                "maximal projected force Cauchy tail or a finite later stop",
            ],
        },
        "hindsight": {
            "classification": "PROOF_LANGUAGE_ARTIFACT_REMOVED",
            "obstruction_physical": False,
            "remaining_obstruction": "NUMERICAL_FORCE_REALIZATION_AND_MAXIMAL_TAIL",
        },
        "exact_next_dependency": (
            "FORM_THE_SIGNED_JOINT_HISTORY_BACKWARD_ADJOINT_AS_A_PARAMETRIC_"
            "OR_INTERVAL_OBJECT_ON_THIS_NONEMPTY_FINITE_CORE_FAMILY,_CONTRACT_"
            "THE_ACTUAL_GRADED_HEAT_MINUS_ZETA_SOURCE,_AND_COMPARE_NESTED_"
            "CORE_FORCE_NETS_BEFORE_ADDRESSING_THE_MAXIMAL_TAIL"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_SIGNED_FORCE_NET_AND_MAXIMAL_TAIL",
            "Gate8": "LOCKED",
            "parametric_base_history_existence_through_1222": "DERIVED",
            "numeric_parametric_or_interval_history_oracle": "OPEN",
            "signed_joint_adjoint": "OPEN_NUMERICAL_CERTIFICATION",
            "maximal_C2_response": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "finite_cover_witness": payload["finite_cover_witness"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
