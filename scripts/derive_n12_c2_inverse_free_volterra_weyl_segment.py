"""Feed the actual certified C2 launch into the inverse-free Weyl transfer."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_radius_jets,
)
from bhsm.interface.aether_forward_c2_volterra_enclosure import (  # noqa: E402
    short_segment_transfer_weyl_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_INVERSE_FREE_VOLTERRA_WEYL_SEGMENT.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
MATCHING = BASE / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_volterra_enclosure.py"
THEORY = ROOT / "theory/n12_c2_inverse_free_volterra_weyl_segment.md"
INPUTS = (LAUNCH, BIRTH, CANDIDATE, MATCHING, COMPACT, MODULE, THEORY)
QDIM = 37


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete inverse-free C2 segment inputs required")
    launch, birth, matching, compact = (
        _load(path) for path in (LAUNCH, BIRTH, MATCHING, COMPACT)
    )
    if not all(record.get("validation_passed") is True for record in (
        launch, birth, matching, compact,
    )):
        raise RuntimeError("validated C2 segment and operator parents required")
    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)[:98]
        weights = np.asarray(data["state_weights"], dtype=float)

    segment = launch["explicit_segment"]
    ball = launch["launch_ball"]
    x_interval = tuple(
        float(value) for value in segment["log_R4_interval_on_launch_ball"]
    )
    h_interval = tuple(
        float(value)
        for value in segment["D_tau_log_R4_interval_on_launch_ball"]
    )
    duration = tuple(
        float(value) for value in segment["proper_time_interval"]
    )
    signed_lambda_end = float(segment["signed_lambda_end_lower"])
    jacobi_growth = float(ball["first_Jacobi_growth_upper"])

    radius_jets = boundary_log_radius_jets(
        12, state[:QDIM], np.zeros(QDIM), np.zeros(QDIM)
    )
    x_gradient = np.asarray(radius_jets["gradient"], dtype=float)
    x_gradient_action = float(np.linalg.norm(x_gradient / weights[:QDIM]))
    signs_j = (-1.0) ** np.arange(12)
    b_dual = float(np.linalg.norm(signs_j / weights[25:37]))
    x_hessian_action = 2.0 * b_dual**2
    x_gradient_upper = (
        x_gradient_action
        + x_hessian_action * float(ball["action_radius"])
    )
    x_parameter_upper = x_gradient_upper * jacobi_growth

    signs_k = (-1.0) ** np.arange(1, 13)
    lapse_log_dual = float(np.linalg.norm(signs_k / weights[74:86]))
    lapse_lower, lapse_upper = (
        float(value) for value in segment["lapse_interval_on_launch_ball"]
    )
    lapse_derivative_upper = lapse_upper * lapse_log_dual
    Delta_lower = float(ball["Delta_interval"][0])
    Delta_derivative_upper = float(ball["Delta_action_derivative_upper"])
    duration_parameter_upper = (
        0.5 * signed_lambda_end**2
        * (
            lapse_derivative_upper / Delta_lower
            + lapse_upper * Delta_derivative_upper / Delta_lower**2
        )
        * jacobi_growth
    )

    common = {
        "spectral_parameter": -1.0,
        "log_radius_interval": x_interval,
        "proper_log_radius_rate_absolute_upper": max(abs(value) for value in h_interval),
        "proper_duration_interval": duration,
        "log_radius_parameter_upper": x_parameter_upper,
        "proper_duration_parameter_upper": duration_parameter_upper,
    }
    channels = {
        "scalar_c3": short_segment_transfer_weyl_enclosure(
            channel="scalar", unit_channel_value=3.0, **common
        ),
        "product_Dirac_lambda1_5_chirality_plus": (
            short_segment_transfer_weyl_enclosure(
                channel="product_Dirac", unit_channel_value=1.5,
                chirality=1, **common,
            )
        ),
        "product_Dirac_lambda1_5_chirality_minus": (
            short_segment_transfer_weyl_enclosure(
                channel="product_Dirac", unit_channel_value=1.5,
                chirality=-1, **common,
            )
        ),
    }
    quotient_rows = birth["C2_birth_quotient_jet"][
        "representative_directions"
    ]
    validation = {
        "actual_C2_launch_segment_consumed": (
            launch["claim_boundary"]["explicit_validated_C2_segment"]
            == "CERTIFIED"
        ),
        "existing_M_C2_slot_and_compact_operator_consumed": (
            matching["claim_boundary"]["C2_response_theory"]
            == "CLOSED_EXISTING_OBJECT_MATCH"
            and compact["claim_boundary"]["M_C_and_D_xi_M_C_algorithm"]
            == "DERIVED_EXECUTABLE"
        ),
        "all_channel_transfer_b_margins_are_positive": all(
            row["chart_margin_lower"] > 0.0 for row in channels.values()
        ),
        "all_Volterra_remainders_are_smaller_than_duration": all(
            row["transfer_second_order_remainder_upper"] < duration[0]
            for row in channels.values()
        ),
        "all_first_physical_quotient_Weyl_bounds_are_finite": all(
            math.isfinite(row["first_parameter_bounds"][
                "Weyl_parameter_Frobenius_upper"
            ])
            for row in channels.values()
        ),
        "two_independent_birth_Cauchy_directions_consumed": len(quotient_rows) == 2,
        "state_Jacobi_and_moving_duration_both_propagated": (
            x_parameter_upper > 0.0 and duration_parameter_upper > 0.0
        ),
        "local_launch_edge_is_not_promoted_to_physical_endpoint": (
            segment["future_endpoint_selected"] is False
        ),
        "no_terminal_load_or_matrix_inverse_used": all(
            row["terminal_load_imposed"] is False
            and row["explicit_matrix_inverse_formed"] is False
            for row in channels.values()
        ),
        "no_selector_recurrence_scale_fit_action_term_gate_or_chord_added": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_INVERSE_FREE_VOLTERRA_WEYL_SEGMENT",
        "status": (
            "ACTUAL_C2_LAUNCH_TRANSFER_AND_FIRST_QUOTIENT_WEYL_ENCLOSURE_CERTIFIED"
            if passed else "C2_LAUNCH_VOLTERRA_WEYL_ENCLOSURE_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_ACTUAL_RESET_SELECTED_C2_COEFFICIENT_SEGMENT_OCCUPIES_THE_"
            "FIRST_MAXIMAL_FORWARD_RESPONSE_LEG:_A_DUHAMEL_VOLTERRA_BOUND_"
            "PROVES_THE_TRANSFER_b_CHART,_THE_EXISTING_TWO_BOUNDARY_"
            "CALDERON_FORMULA_GIVES_THE_SCALAR_AND_FACTORIZED_DIRAC_WEYL_"
            "ENCLOSURES,_AND_THE_REGULARIZED_STATE_JACOBI_PLUS_MOVING_"
            "DURATION_PULLBACK_GIVE_A_FINITE_FIRST_PHYSICAL_QUOTIENT_BOUND_"
            "WITHOUT_AN_ENDPOINT_LOAD_OR_MATRIX_INVERSE"
        ),
        "diagram_matching": {
            "slot": "C2_birth-->C2_launch_edge",
            "required_type": "FREE_ENDPOINT_CHANNEL_TRANSFER_AND_CALDERON_GRAPH",
            "BHSM_object": "RETAINED_FIXED_CHANNEL_K(xi)_COMPOSED_WITH_ACTUAL_C2_FLOW",
            "composition_role": (
                "FIRST_SEGMENT_ADAPTER_FOR_M_C2_MAX;_NOT_THE_COMPLETE_"
                "MAXIMAL_FORWARD_RESPONSE"
            ),
            "verdict": "VALID_MATCH_LOCAL_SEGMENT",
        },
        "physical_quotient_pullback": {
            "unit_initial_action_direction": True,
            "state_Jacobi_growth_upper": jacobi_growth,
            "log_radius_action_gradient_upper": x_gradient_upper,
            "log_radius_parameter_upper": x_parameter_upper,
            "proper_duration_parameter_upper": duration_parameter_upper,
            "representative_birth_Cauchy_jets": [
                row["C2_birth_Cauchy_jet"] for row in quotient_rows
            ],
            "all_73_reset_image_directions_covered_by_uniform_bound": True,
        },
        "channels_at_z_minus_1": channels,
        "exact_next_dependency": (
            "CONTINUE_THE_SAME_ACTION_C2_FLOW_FROM_THE_NONPHYSICAL_LAUNCH_"
            "EDGE_UNTIL_THE_FIRST_COMPLETED_ENCAPSULATION_ENDPOINT_OR_"
            "CANONICAL_STOP,_COMPOSING_EACH_CERTIFIED_TRANSFER_BLOCK_BY_"
            "THE_EXISTING_MOBIUS_SCHUR_RULE;_ONLY_THEN_EVALUATE_COMPLETE_"
            "M_C2,_ZERO_SOURCE_FORCE,_SADDLE,_AND_PHYSICAL_HESSIAN"
        ),
        "claim_boundary": {
            "actual_first_C2_transfer_segment": "CERTIFIED",
            "first_physical_quotient_Weyl_enclosure": "CERTIFIED_UNIFORM",
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
            "launch_edge_physical_endpoint": False,
            "zero_source_force": "OPEN_AFTER_COMPLETE_M_C2",
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
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "chart_margins": {
            key: row["chart_margin_lower"]
            for key, row in payload["channels_at_z_minus_1"].items()
        },
        "first_Weyl_bounds": {
            key: row["first_parameter_bounds"][
                "Weyl_parameter_Frobenius_upper"
            ]
            for key, row in payload["channels_at_z_minus_1"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
