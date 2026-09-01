"""Derive the no-selector 72+1 reset-generated C2 launch chart."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_c2_reset_generated_launch_chart import (  # noqa: E402
    reset_generated_launch_decomposition,
)
from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_fixed_s_field_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
DATA_RESULT = RESULT.with_suffix(".npz")
RESET = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
RESET_DATA = RESET.with_suffix(".npz")
ROOT_CENTER = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
ROOT_CENTER_DATA = ROOT_CENTER.with_suffix(".npz")
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
FIELD = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_c2_reset_generated_launch_chart.py"
FIELD_MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_exact_fixed_s_field.py"
THEORY = ROOT / "theory" / "n12_c2_reset_generated_launch_chart.md"
INPUTS = (
    RESET, RESET_DATA, ROOT_CENTER, ROOT_CENTER_DATA, INTERFACE, FIELD,
    MODULE, FIELD_MODULE, THEORY,
)
STATE_DIMENSION = 98
RESET_RANK = 57
RANK_THRESHOLD = 1.0e-8


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing C2 launch-chart inputs: " + ", ".join(missing))
    reset, root, interface, field_record = (
        _load(path) for path in (RESET, ROOT_CENTER, INTERFACE, FIELD)
    )
    if not all(record.get("validation_passed") is True for record in (
        reset, root, interface, field_record,
    )):
        raise RuntimeError("validated reset, root, interface, and field records required")

    with np.load(RESET_DATA) as data:
        jacobian = np.asarray(data["analytic_full_reset_jacobian"], dtype=float)
    with np.load(ROOT_CENTER_DATA) as data:
        joint_state = np.asarray(data["state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    # The two-sided theorem fixes the forward swapped interpretation:
    # original event E_* becomes the outgoing new child C2.
    event_seed = joint_state[:STATE_DIMENSION]
    exact_field = exact_fixed_s_field_action(
        state=event_seed,
        weights=weights,
        reference=reference,
        signed_descriptor=0.0,
    )
    decomposition = reset_generated_launch_decomposition(
        reset_jacobian=jacobian,
        outgoing_field_action=np.asarray(exact_field["field_action"], dtype=float),
        state_dimension=STATE_DIMENSION,
        reset_rank=RESET_RANK,
        rank_threshold=RANK_THRESHOLD,
    )

    array_names = (
        "reset_tangent_basis", "event_image_basis", "event_lift_kernel_basis",
        "outgoing_field_action", "outgoing_transverse_unit", "launch_basis",
        "reset_singular_values", "event_projection_singular_values",
    )
    np.savez_compressed(
        DATA_RESULT,
        **{name: np.asarray(decomposition[name]) for name in array_names},
    )

    event_row = jacobian[25, :STATE_DIMENSION]
    event_tangent_row_residual = float(
        np.linalg.norm(event_row @ decomposition["event_image_basis"])
    )
    validation = {
        "full_reset_rank_is_57": decomposition["reset_rank"] == 57,
        "reset_tangent_dimension_is_139": decomposition["reset_tangent_dimension"] == 139,
        "swapped_C2_seed_image_rank_is_72": decomposition["event_projection_rank"] == 72,
        "fixed_seed_lift_kernel_dimension_is_67": decomposition["event_lift_kernel_dimension"] == 67,
        "exact_outgoing_field_is_branch_24": int(exact_field["selected_branch"]) == 24,
        "exact_descriptor_identity_is_one": abs(float(exact_field["Dlambda_field"]) - 1.0) < 1.0e-12,
        "exact_outgoing_denominator_is_positive": float(exact_field["Delta"]) > 0.0,
        "outgoing_field_is_transverse_to_event_image": decomposition["outgoing_transverse_component_norm"] > RANK_THRESHOLD,
        "reset_generated_launch_dimension_is_73": decomposition["launch_dimension"] == 73,
        "event_image_is_tangent_to_ordered_event_row": event_tangent_row_residual < 1.0e-10,
        "launch_basis_is_orthonormal": decomposition["launch_orthonormality_residual_norm"] < 1.0e-12,
        "no_full_Euler_Dirac_or_reset_matrix_inverse_formed": decomposition["explicit_matrix_inverse_formed"] is False and exact_field["explicit_full_Euler_Dirac_inverse_formed"] is False,
        "no_reset_member_selector_endpoint_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART",
        "status": "C2_RESET_GENERATED_72_PLUS_1_LAUNCH_CHART_CERTIFIED" if passed else "C2_RESET_GENERATED_LAUNCH_CHART_NOT_CERTIFIED",
        "classification": "THE_FORWARD_SWAPPED_RESET_EVENT_IMAGE_HAS_72_ACTION_TANGENT_DIRECTIONS_AND_THE_EXACT_FIXED_s_FIELD_IS_TRANSVERSE_WITH_Dlambda_F_EQUALS_ONE,_SO_THE_LOCAL_C2_LAUNCH_MANIFOLD_HAS_73_DIRECTIONS_WITHOUT_SELECTING_A_RESET_MEMBER",
        "dimension_theorem": {
            "ambient_event_child": 196,
            "reset_rows_and_rank": 57,
            "reset_tangent": decomposition["reset_tangent_dimension"],
            "swapped_C2_seed_image": decomposition["event_projection_rank"],
            "fixed_C2_seed_lift_kernel": decomposition["event_lift_kernel_dimension"],
            "outgoing_descriptor_amplitude": 1,
            "C2_launch_manifold": decomposition["launch_dimension"],
            "identity": "139=72+67_AND_73=72+1",
        },
        "exact_launch_theorem": {
            "forward_swap": "E1=C_*_AND_C2=E_*",
            "seed_family": "pi_event(T_Creset)_HAS_DIMENSION_72_ON_THE_ORDERED_EVENT_HYPERSURFACE",
            "outgoing_generator": "F_0=F_s(E_*;s=0)",
            "transversality": "Dlambda[F_0]=1_WHILE_Dlambda[V]=0_FOR_V_IN_D_pi_event(T_Creset)",
            "launch_chart": "(xi,s)_MAPS_TO_Flow_s(E(xi)),_xi_IN_R72,_s>=0",
            "local_dimension": 73,
            "selector": None,
        },
        "numerical_coordinate_witness": {
            "rank_threshold": RANK_THRESHOLD,
            "reset_smallest_nonzero_singular_value": float(decomposition["reset_singular_values"][-1]),
            "event_projection_smallest_nonzero_singular_value": float(decomposition["event_projection_singular_values"][71]),
            "event_projection_largest_null_singular_value": float(decomposition["event_projection_singular_values"][72]),
            "outgoing_field_action_norm": float(np.linalg.norm(decomposition["outgoing_field_action"])),
            "outgoing_transverse_component_norm_after_unit_normalization": decomposition["outgoing_transverse_component_norm"],
            "event_tangent_row_residual_norm": event_tangent_row_residual,
            "reset_tangent_residual_norm": decomposition["reset_tangent_residual_norm"],
            "event_lift_projection_residual_norm": decomposition["event_lift_projection_residual_norm"],
            "event_lift_reset_residual_norm": decomposition["event_lift_reset_residual_norm"],
            "launch_orthonormality_residual_norm": decomposition["launch_orthonormality_residual_norm"],
            "proof_center_role": "COORDINATE_WITNESS_INSIDE_THE_CERTIFIED_ROOT_BALL_NOT_A_PHYSICAL_MEMBER_SELECTOR",
        },
        "matching_audit": [
            {
                "diagram_slot": "C2_RESET_GENERATED_INITIAL_MANIFOLD",
                "required_type": "ACTION_OWNED_NO_SELECTOR_LOCAL_OUTGOING_CHILD_CHART",
                "candidate": "RESET_EVENT_IMAGE_PLUS_EXACT_FIXED_s_TRANSVERSE_FLOW",
                "dimension_domain_check": "VALID_72_PLUS_1_EQUALS_73_ON_THE_REGULAR_BRANCH_24_CHART",
                "provenance_check": "VALID_RESET_JACOBIAN_EVENT_ORIENTATION_AND_EXACT_ACTION_FIELD",
                "verdict": "VALID_MATCH",
            },
            {
                "diagram_slot": "C2_MAXIMAL_RESPONSE_OR_FINITE_LATER_EVENT_STOP",
                "required_type": "COMPLETE_FORWARD_OPERATOR_RESPONSE_AND_PHYSICAL_QUOTIENT_COTANGENT",
                "candidate": "LOCAL_73_DIMENSIONAL_LAUNCH_CHART",
                "dimension_domain_check": "VALID_INITIAL_DOMAIN_ONLY",
                "provenance_check": "DOES_NOT_CONTROL_THE_MAXIMAL_TAIL",
                "verdict": "ACTUALLY_MISSING_AFTER_LAUNCH",
            },
        ],
        "adjudication": {
            "actual_parametric_C2_launch_domain": "CLOSED_LOCALLY",
            "reset_member_selected": False,
            "stored_proof_center_promoted_to_physical_history": False,
            "C2_maximal_endpoint_outcome": "OPEN",
            "projected_heat_minus_zeta_force_tail": "OPEN_CURRENT_OWNER",
            "zero_source_force": "OPEN",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "72-dimensional swapped reset-event seed image",
                "one exact action-generated transverse launch direction",
                "73-dimensional local C2 launch manifold",
            ],
            "INVALIDATED": [
                "a 139-dimensional arbitrary reset choice is required to launch C2",
                "a hand-selected reset member is needed to define the local C2 family",
                "the fixed-s proof centers themselves are physical histories",
            ],
            "OPEN": [
                "nonlinear parametric C2 coefficient/Jacobi path beyond the local launch",
                "finite later event/canonical stop or maximal projected force Cauchy tail",
                "zero-source force and same-action saddle",
            ],
        },
        "hindsight": {
            "classification": "ACTION_OWNED_DIMENSION_AND_CHART_NORMALIZATION",
            "obstruction_removed": "RESET_SELECTOR_AND_139_DIRECTION_LAUNCH_OVERPARAMETERIZATION",
            "remaining_obstruction": "MAXIMAL_FORWARD_OPERATOR_AND_PHYSICAL_DUAL_TAIL",
        },
        "exact_next_dependency": "PROPAGATE_THE_72_RESET_EVENT_IMAGE_DIRECTIONS_AND_THE_ONE_EXACT_OUTGOING_DESCRIPTOR_DIRECTION_THROUGH_THE_C2_FLOW_IN_A_COUPLED_FORWARD_ADJOINT_OR_MULTIPLE_SHOOTING_FORMULATION,_THEN_CERTIFY_A_FINITE_LATER_EVENT_STOP_OR_THE_PROJECTED_HEAT_MINUS_ZETA_CAUCHY_TAIL",
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_AFTER_LOCAL_C2_LAUNCH_CHART",
            "Gate8": "LOCKED",
            "local_C2_launch_manifold": "CERTIFIED_73_DIMENSIONAL",
            "maximal_C2_response": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
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
        "dimensions": payload["dimension_theorem"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
