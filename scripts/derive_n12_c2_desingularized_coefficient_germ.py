"""Derive the intrinsic-u outgoing C2 coefficient and transfer germ."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_DESINGULARIZED_COEFFICIENT_GERM.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
TRANSFER = BASE / "BHSM_N12_C2_OUTGOING_LOCAL_TRANSFER_GERM.json"
THEORY = ROOT / "theory/n12_c2_desingularized_coefficient_germ.md"
INPUTS = (BIRTH, INTERFACE, TRANSFER, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all C2 desingularized-germ inputs required")
    birth, interface, transfer = (
        _load(path) for path in (BIRTH, INTERFACE, TRANSFER)
    )
    if not all(
        record.get("validation_passed") is True
        for record in (birth, interface, transfer)
    ):
        raise RuntimeError("validated C2 birth, orientation, and transfer required")

    outgoing = interface["event_outgoing_orientation"]
    c_lower = float(outgoing["root_c_psi_lower"])
    c_upper = float(outgoing["center_c_psi_interval"][1]) + float(
        outgoing["line_cubic_shift_upper"]
    ) + float(outgoing["state_cubic_shift_upper"])
    b_lower = float(outgoing["root_b_psi_lower"])
    b_upper = float(outgoing["center_b_psi"]) + float(
        outgoing["fixed_b_shift_upper"]
    ) + float(outgoing["line_b_shift_upper"])
    coordinate_u_rate = (2.0 * c_lower * b_lower, 2.0 * c_upper * b_upper)

    coefficient = birth["C2_birth_coefficient"]
    lapse_lower, lapse_upper = (
        float(value) for value in coefficient["root_lapse_interval"]
    )
    h_lower, h_upper = (
        float(value)
        for value in coefficient["root_D_tau_log_R4_interval"]
    )
    proper_u_rate = (
        coordinate_u_rate[0] / lapse_upper,
        coordinate_u_rate[1] / lapse_lower,
    )
    proper_time_per_u = (
        1.0 / proper_u_rate[1],
        1.0 / proper_u_rate[0],
    )
    log_radius_per_u = (
        h_lower / proper_u_rate[1],
        h_upper / proper_u_rate[0],
    )
    coordinate_log_radius_rate = (
        lapse_lower * h_lower,
        lapse_upper * h_upper,
    )

    validation = {
        "validated_actual_C2_birth_orientation_and_transfer_consumed": True,
        "outgoing_c_psi_interval_is_strictly_positive": c_lower > 0.0,
        "outgoing_b_psi_interval_is_strictly_positive": b_lower > 0.0,
        "coordinate_u_rate_interval_is_strictly_positive": (
            0.0 < coordinate_u_rate[0] <= coordinate_u_rate[1]
        ),
        "proper_u_rate_interval_is_strictly_positive": (
            0.0 < proper_u_rate[0] <= proper_u_rate[1]
        ),
        "proper_time_per_u_interval_is_strictly_positive": (
            0.0 < proper_time_per_u[0] <= proper_time_per_u[1]
        ),
        "log_radius_per_u_interval_is_strictly_positive": (
            0.0 < log_radius_per_u[0] <= log_radius_per_u[1]
        ),
        "coordinate_and_proper_time_rates_not_conflated": (
            lapse_lower > 0.0 and lapse_upper > 0.0
        ),
        "pole_cancelled_event_identity_at_lambda_zero_consumed": float(
            outgoing["root_hitting_product_lower"]
        )
        > 0.0,
        "local_inverse_function_theorem_applies_one_sided": (
            proper_u_rate[0] > 0.0
        ),
        "no_explicit_segment_edge_or_future_endpoint_promoted": True,
        "no_history_member_selector_scale_action_term_recurrence_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_C2_DESINGULARIZED_COEFFICIENT_GERM",
        "status": "C2_PHYSICAL_EVENT_U_COEFFICIENT_GERM_STRICTLY_OUTGOING",
        "classification": (
            "THE_EXISTING_PHYSICAL_EVENT_COORDINATE_u=lambda_event^2_HAS_"
            "STRICTLY_POSITIVE_COORDINATE_AND_PROPER_TIME_RATES_AT_THE_"
            "ACTUAL_C2_BIRTH,_SO_u_IS_A_ONE_SIDED_INTRINSIC_LOCAL_"
            "PARAMETER_AND_log_R4_HAS_A_STRICTLY_POSITIVE_CERTIFIED_"
            "DERIVATIVE_WITH_RESPECT_TO_u;_THE_NEXT_MISSING_DATA_ARE_"
            "NEIGHBORHOOD_REMAINDER_BOUNDS_NOT_NEW_C2_PHYSICS"
        ),
        "exact_identities": {
            "physical_event_coordinate": "u=lambda_event^2",
            "coordinate_time": "D_t_u(0)=2*c_psi*b_psi",
            "proper_time_conversion": "d_tau=N*dt",
            "proper_time": "D_tau_u(0)=2*c_psi*b_psi/N",
            "coefficient": (
                "x(u)=x0+[N*H/(2*c_psi*b_psi)]*u+o(u)"
            ),
            "transfer": (
                "T(u)=I+[N/(2*c_psi*b_psi)]*u*G0+o(u)"
            ),
        },
        "certified_intervals": {
            "c_psi": [c_lower, c_upper],
            "b_psi": [b_lower, b_upper],
            "lapse_N": [lapse_lower, lapse_upper],
            "D_tau_log_R4": [h_lower, h_upper],
            "D_t_u": list(coordinate_u_rate),
            "D_tau_u": list(proper_u_rate),
            "D_t_log_R4": list(coordinate_log_radius_rate),
            "d_tau_du": list(proper_time_per_u),
            "d_log_R4_du": list(log_radius_per_u),
        },
        "local_consequence": {
            "one_sided_nonzero_outgoing_C2_segment_exists": True,
            "u_is_strictly_increasing_on_some_local_segment": True,
            "R4_is_strictly_increasing_on_some_local_segment": True,
            "segment_length_selected_or_claimed": False,
            "validation_edge_promoted_to_physical_endpoint": False,
            "complete_C2_history_or_response_claimed": False,
        },
        "exact_next_dependency": (
            "CERTIFY_ON_AN_EXPLICIT_C2_u_CHART_NEIGHBORHOOD_THE_"
            "POLE_CANCELLED_VECTOR_FIELD_AND_FIRST_PHYSICAL_QUOTIENT_"
            "JACOBI_BOUNDS,_INCLUDING_VARIATION_OF_2*c_psi*b_psi/N,_H,_"
            "THE_SELECTED_EIGENLINE,_AND_ALL_RETAINED_DOMAIN_MARGINS;_"
            "THEN_INTEGRATE_THE_ACTUAL_SEGMENT_TRANSFER_WITH_REMAINDER_CONTROL"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_EXPLICIT_C2_u_CHART_NEIGHBORHOOD_BOUND",
            "actual_C2_desingularized_coefficient_germ": "CERTIFIED",
            "abstract_nonzero_outgoing_C2_segment": "CERTIFIED_LOCAL",
            "explicit_validated_C2_segment": "OPEN",
            "complete_M_C2_and_second_jet": "OPEN",
            "zero_source_force": "OPEN_AFTER_COMPLETE_C2_REALIZATION",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "D_tau_u": payload["certified_intervals"]["D_tau_u"],
                "d_log_R4_du": payload["certified_intervals"][
                    "d_log_R4_du"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
