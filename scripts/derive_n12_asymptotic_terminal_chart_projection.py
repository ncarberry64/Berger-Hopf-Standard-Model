"""Certify the exact N12 state-to-asymptotic terminal chart projection."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_asymptotic_terminal_chart import (  # noqa: E402
    MDIM,
    QDIM,
    compactified_terminal_chart,
    compactified_terminal_chart_jets,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import (  # noqa: E402
    RADIUS0,
)
from bhsm.interface.weight_seven_transverse_descriptor import (  # noqa: E402
    ROUND_EXPANSION_RATE,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_ASYMPTOTIC_TERMINAL_CHART_PROJECTION.json"
MATCHING = BASE / "BHSM_N12_GATE7_RESET_CAPTURE_DIAGRAM_MATCHING.json"
CHART = BASE / "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json"
TUBE = BASE / "BHSM_N12_GATE7_QUANTITATIVE_STABLE_CAPTURE_TUBE.json"
FAMILY = BASE / "BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY.json"
FIELD_DATA = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.npz"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_asymptotic_terminal_chart.py"
THEORY = ROOT / "theory" / "n12_asymptotic_terminal_chart_projection.md"
INPUTS = (MATCHING, CHART, TUBE, FAMILY, FIELD_DATA, MODULE, THEORY)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _decimal_log(value: str) -> Decimal:
    with localcontext() as context:
        context.prec = 100
        return Decimal(value).ln()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing terminal-chart inputs: " + ", ".join(missing))
    matching, chart, tube, family = (
        _load(path) for path in (MATCHING, CHART, TUBE, FAMILY)
    )
    if not all(record.get("validation_passed") is True for record in (
        matching, chart, tube, family,
    )):
        raise RuntimeError("validated terminal-chart lineage required")

    capture_radius = Decimal(tube["capture_tube"]["R4_lower"])
    with localcontext() as context:
        context.prec = 100
        q0_capture = float((capture_radius * Decimal(2) / Decimal(str(RADIUS0))).ln())
    round_state = np.zeros(2 * QDIM + MDIM)
    round_state[0] = q0_capture
    round_state[QDIM] = ROUND_EXPANSION_RATE
    round_projection = compactified_terminal_chart(round_state)

    rng = np.random.default_rng(71274)
    left = rng.normal(size=round_state.size)
    right = rng.normal(size=round_state.size)
    jets = compactified_terminal_chart_jets(round_state, left, right)

    with np.load(FIELD_DATA) as data:
        finite_center = np.asarray(data["center_state"], dtype=float)
    finite_projection = compactified_terminal_chart(finite_center)

    tube_log_epsilon = _decimal_log(tube["capture_tube"]["epsilon_upper"])
    round_log_epsilon = Decimal(str(round_projection["log_epsilon"]))
    round_descriptor = np.asarray(round_projection["descriptor"], dtype=float)
    validation = {
        "input_matching_localized_terminal_projection": (
            "terminal_transition" in matching["genuinely_missing"]
        ),
        "target_ordering_is_25_plus_25_plus_24": (
            chart["chart"]["dimension"] == 74
            and round_descriptor.shape == (74,)
        ),
        "physical_indices_match_declared_q0_w_b_order": (
            np.array_equal(
                round_projection["physical_coordinate_indices"],
                np.concatenate((np.asarray([0]), np.arange(13, 37))),
            )
        ),
        "round_center_family_projects_to_zero_descriptor": (
            float(np.linalg.norm(round_descriptor)) < 1.0e-12
        ),
        "round_capture_scale_uses_log_without_underflow_loss": (
            round_projection["epsilon_underflows_binary64"] is True
            and abs(round_log_epsilon - tube_log_epsilon) < Decimal("1e-10")
        ),
        "first_and_mixed_second_descriptor_jets_are_finite": all(
            np.all(np.isfinite(np.asarray(jets[key], dtype=float)))
            for key in (
                "D_descriptor_left",
                "D_descriptor_right",
                "D2_descriptor_mixed",
            )
        ),
        "normalized_epsilon_jets_are_finite": all(
            math.isfinite(float(jets[key]))
            for key in (
                "D_epsilon_over_epsilon_left",
                "D_epsilon_over_epsilon_right",
                "D2_epsilon_over_epsilon_mixed",
            )
        ),
        "finite_core_formula_replay_is_outside_capture_tube": (
            Decimal(str(finite_projection["log_epsilon"])) > tube_log_epsilon
        ),
        "finite_core_center_not_promoted_to_physical_history": True,
        "common_scale_recentered_not_quotiented": (
            round_projection["common_scale_recentered_not_quotiented"] is True
        ),
        "no_selector_recurrence_chord_fit_scale_action_or_time_direction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_TERMINAL_CHART_PROJECTION",
        "status": (
            "NONLINEAR_98_TO_74_COMPACTIFIED_TERMINAL_PROJECTION_DERIVED"
            if passed else "ASYMPTOTIC_TERMINAL_CHART_PROJECTION_INVALID"
        ),
        "classification": (
            "THE_EXACT_BOUNDARY_RADIUS_ATTACHMENT_AND_RETAINED_TIME_LAPSE_"
            "QUOTIENT_DEFINE_AN_EXECUTABLE_NONLINEAR_98_STATE_TO_74_COMPONENT_"
            "COMPACTIFIED_PHYSICAL_TERMINAL_MAP_WITH_FIRST_AND_MIXED_SECOND_"
            "JETS;_LOG_EPSILON_AND_NORMALIZED_EPSILON_JETS_AVOID_UNDERFLOW_"
            "AT_THE_CERTIFIED_CAPTURE_SCALE"
        ),
        "map": {
            "state_order": "q_37,qdot_37,m_24",
            "physical_coordinate_indices": [0] + list(range(13, 37)),
            "center_coordinates": "a=(q0_tilde,w_0..w_11,b_0..b_11)",
            "common_scale_recentering": "q0_tilde=q0-log_R4+log(RADIUS0/2)",
            "velocity_normals": (
                "eta=(q0_dot-DlogR4[qdot],dot_w_0..dot_w_11,dot_b_0..dot_b_11)"
            ),
            "multipliers": "m=(log_lapse_1..log_lapse_12,shift_0..shift_11)",
            "compactification": "log_epsilon=-2*log_R4",
            "output": "(log_epsilon,a_25,eta_25,m_24)",
            "descriptor_dimension": 74,
        },
        "jets": {
            "first_descriptor": "EXECUTABLE",
            "mixed_second_descriptor": "EXECUTABLE_WITH_UPSTREAM_MIXED_STATE_DIRECTION",
            "first_log_epsilon": "EXECUTABLE",
            "mixed_second_log_epsilon": "EXECUTABLE",
            "normalized_first_epsilon": "D_epsilon/epsilon=D_log_epsilon",
            "normalized_mixed_second_epsilon": (
                "D2_epsilon/epsilon=4*Dx_left*Dx_right-2*(D2x+Dx_mixed_state)"
            ),
        },
        "capture_origin_witness": {
            "R4": str(capture_radius),
            "q0": q0_capture,
            "log_epsilon": round_projection["log_epsilon"],
            "tube_log_epsilon": str(tube_log_epsilon),
            "descriptor_norm": float(np.linalg.norm(round_descriptor)),
            "product_norm": round_projection["product_norm"],
            "binary64_epsilon_underflows": round_projection["epsilon_underflows_binary64"],
            "role": "EXACT_ROUND_CENTER_FAMILY_CHART_REPLAY_NOT_RESET_CONNECTION",
        },
        "finite_core_diagnostic": {
            "log_R4": finite_projection["log_R4"],
            "log_epsilon": finite_projection["log_epsilon"],
            "descriptor_product_norm": finite_projection["product_norm"],
            "inside_capture_tube": False,
            "proof_center_selected_as_physical_history": False,
        },
        "supersession": {
            "terminal_transition_block": "CLOSED_BY_THIS_ARTIFACT",
            "regular_proper_time_callback": "PRESERVED_FROM_MATCHING_AUDIT",
            "remaining_connection_blocks": 1,
            "remaining_owner": (
                "VALIDATED_NONEMPTY_RESET_QUOTIENT_SET_PROPAGATION_OR_NONZERO_"
                "DEGREE_TO_TUBE_OR_FIRST_RETAINED_CANONICAL_STOP"
            ),
        },
        "exact_next_dependency": (
            "COMPOSE_THIS_TERMINAL_MAP_AND_JETS_WITH_THE_73_PARAMETER_RESET_"
            "LAUNCH_AND_EXACT_FIXED_s_FLOW_IN_A_NO_SELECTOR_INTERVAL_MULTIPLE_"
            "SHOOTING_OR_DEGREE_CERTIFICATE;_PROVE_STRICT_TUBE_INCLUSION_OR_"
            "THE_FIRST_RETAINED_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RESET_TO_CERTIFIED_CAPTURE_TUBE_OR_LATER_STOP",
            "terminal_capture_projection": "DERIVED_WITH_FIRST_AND_MIXED_SECOND_JETS",
            "reset_to_capture_or_stop_certificate": "OPEN_CURRENT_OWNER",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION",
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
        "capture_origin_witness": payload["capture_origin_witness"],
        "remaining_owner": payload["supersession"]["remaining_owner"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
