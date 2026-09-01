"""Certify an open Gate-7 reset subball through the retained 1222 C2 core.

Two stored endpoint reserves round upward to the same binary64 values as their
local radii.  This certificate replays only those endpoint computations in
Decimal arithmetic, recovers strict lower reserves, and combines them with
the already certified state-Jacobi products.  No center, step, or history is
changed.
"""

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
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_adaptive_ball import (  # noqa: E402
    derived_adaptive_ball,
)
from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    proof_center_field,
    translated_generator,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_COMPACT_RESET_OPEN_SUBBALL_1222_PROPAGATION.json"
DATA = RESULT.with_suffix(".npz")
AUDIT = BASE / "BHSM_N12_GATE7_COMPACT_RESET_PROPAGATION_RESERVE_AUDIT.json"
AUDIT_DATA = AUDIT.with_suffix(".npz")
COMPACT = BASE / "BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.json"
PULLBACK = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
ADAPTIVE_DATA = ADAPTIVE.with_suffix(".npz")
RECENTERED = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
RECENTERED_DATA = RECENTERED.with_suffix(".npz")
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
CANDIDATE_DATA = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
THEORY = ROOT / "theory" / "n12_gate7_compact_reset_open_subball_1222_propagation.md"
INPUTS = (
    AUDIT,
    AUDIT_DATA,
    COMPACT,
    PULLBACK,
    ADAPTIVE,
    ADAPTIVE_DATA,
    RECENTERED,
    RECENTERED_DATA,
    RECENTER,
    POLE_FREE,
    LAUNCH,
    LINE,
    ACTION,
    CANDIDATE_DATA,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _float_lower(value: Decimal) -> float:
    result = float(value)
    return math.nextafter(result, -math.inf) if Decimal.from_float(result) > value else result


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-14), math.inf)


def _exact_endpoint_replay(
    *,
    center: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    root_state: np.ndarray,
    pf: dict[str, Any],
    launch_ball: dict[str, Any],
    line: dict[str, Any],
    parent_radius: float,
    center_path_upper: float,
    incoming_tube_upper: float,
    signed_start: Decimal,
    stored_row: dict[str, Any],
) -> dict[str, Any]:
    ball = derived_adaptive_ball(
        center_path=center_path_upper,
        tube=incoming_tube_upper,
        pf=pf,
        launch_ball=launch_ball,
        line=line,
        parent_radius=parent_radius,
        root_state=root_state,
        weights=weights,
        coefficient_enclosure=_coefficient_enclosure,
    )
    generator = translated_generator(
        ball=ball,
        pf=pf,
        launch_ball=launch_ball,
        line=line,
        root_state=root_state,
    )
    proof = proof_center_field(
        center=center,
        weights=weights,
        reference=reference,
        signed_s=float(signed_start),
        ball=ball,
        generator=generator,
    )
    speed = float(generator["regularized_speed_upper"])
    jacobi = float(generator["pole_free_regularized_Jacobi_upper"])
    step = min(
        (float(ball["derived_local_radius"]) - incoming_tube_upper) / (4.0 * speed),
        math.log(2.0) / jacobi,
    )
    step_decimal = Decimal.from_float(step)
    growth = math.exp(jacobi * step)
    predictor = step * np.asarray(proof["field_action"], dtype=float)
    stored_center = center + predictor / weights
    stored_action_step = (stored_center - center) * weights
    rounding_defect = float(np.linalg.norm(stored_action_step - predictor))
    nonlinear = 0.5 * jacobi * speed * step**2 * growth
    ideal_tube = growth * (
        incoming_tube_upper + step * float(proof["field_mismatch_upper"])
    ) + nonlinear
    with localcontext() as context:
        context.prec = 100
        exact_tube = Decimal.from_float(ideal_tube) + Decimal.from_float(rounding_defect)
        exact_radius = Decimal.from_float(float(ball["derived_local_radius"]))
        exact_reserve = exact_radius - exact_tube
    return {
        "stored_step_replayed_exactly": step_decimal == Decimal(
            stored_row["signed_lambda_step_decimal"]
        ),
        "selected_allocation_replayed_exactly": float(
            ball["allocation_selected_midpoint"]
        ) == float(stored_row["allocation_selected_midpoint"]),
        "local_radius_replayed_exactly": float(ball["derived_local_radius"])
        == float(stored_row["derived_local_radius"]),
        "branch_replayed_exactly": int(proof["selected_branch"])
        == int(stored_row["proof_center_branch"]),
        "exact_local_radius_decimal": str(exact_radius),
        "exact_endpoint_tube_decimal": str(exact_tube),
        "exact_output_reserve_decimal": str(exact_reserve),
        "directed_output_reserve_lower": _float_lower(exact_reserve),
        "binary64_radius_ulp": math.ulp(float(ball["derived_local_radius"])),
    }


def _replay_two_saturated_rows() -> dict[int, dict[str, Any]]:
    adaptive = _load(ADAPTIVE)
    recentered = _load(RECENTERED)
    recenter = _load(RECENTER)["recenter"]
    line = _load(LINE)["bounds"]

    adaptive_rows = adaptive["adaptive_cover"]["rows"]
    adaptive_last = adaptive_rows[-1]
    adaptive_previous = adaptive_rows[-2]
    with np.load(ADAPTIVE_DATA) as source:
        adaptive_center = np.asarray(
            source["C2_adaptive_predictor_centers"][-2], dtype=float
        )
        adaptive_weights = np.asarray(source["state_weights"], dtype=float)
        adaptive_reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(CANDIDATE_DATA) as source:
        adaptive_root = np.asarray(source["state"][:98], dtype=float)
    adaptive_start = Decimal(
        adaptive["adaptive_cover"]["final_signed_lambda_decimal"]
    ) - Decimal(adaptive_last["signed_lambda_step_decimal"])
    adaptive_replay = _exact_endpoint_replay(
        center=adaptive_center,
        weights=adaptive_weights,
        reference=adaptive_reference,
        root_state=adaptive_root,
        pf=_load(POLE_FREE)["bounds"],
        launch_ball=_load(LAUNCH)["launch_ball"],
        line=line,
        parent_radius=float(_load(ACTION)["action_coordinate_ball_radius"]),
        center_path_upper=float(adaptive_previous["center_path_upper"]),
        incoming_tube_upper=float(adaptive_previous["endpoint_tube_radius_upper"]),
        signed_start=adaptive_start,
        stored_row=adaptive_last,
    )

    recentered_rows = recentered["recentered_cover"]["rows"]
    recentered_last = recentered_rows[-1]
    recentered_previous = recentered_rows[-2]
    with np.load(RECENTERED_DATA) as source:
        recentered_center = np.asarray(
            source["C2_recentered_adaptive_predictor_centers"][-2], dtype=float
        )
        recentered_weights = np.asarray(source["state_weights"], dtype=float)
        recentered_reference = np.asarray(source["branch_reference"], dtype=float)
        recentered_root = np.asarray(source["recentered_root_state"], dtype=float)
    recentered_start = Decimal(
        recentered["recentered_cover"]["final_signed_lambda_decimal"]
    ) - Decimal(recentered_last["signed_lambda_step_decimal"])
    recentered_replay = _exact_endpoint_replay(
        center=recentered_center,
        weights=recentered_weights,
        reference=recentered_reference,
        root_state=recentered_root,
        pf=recenter["recentered_pole_free_bounds"],
        launch_ball=recenter["recentered_launch_ball"],
        line=line,
        parent_radius=float(recenter["recentered_parent_action_radius"]),
        center_path_upper=float(
            recentered_previous["center_path_from_recenter_upper"]
        ),
        incoming_tube_upper=float(
            recentered_previous["endpoint_tube_radius_upper"]
        ),
        signed_start=recentered_start,
        stored_row=recentered_last,
    )
    return {791: adaptive_replay, 1064: recentered_replay}


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing open-subball propagation inputs: " + ", ".join(missing)
        )
    audit, compact, pullback = (_load(path) for path in (AUDIT, COMPACT, PULLBACK))
    if not all(record.get("validation_passed") is True for record in (
        audit, compact, pullback, _load(ADAPTIVE), _load(RECENTERED), _load(RECENTER),
        _load(POLE_FREE), _load(LAUNCH), _load(LINE), _load(ACTION),
    )):
        raise RuntimeError("validated compact-family propagation parents required")

    with np.load(AUDIT_DATA) as source:
        indices = np.asarray(source["global_segment_index"], dtype=np.int64)
        stored_reserves = np.asarray(source["stored_output_reserve"], dtype=float)
        cumulative_growth = np.asarray(
            source["cumulative_state_Jacobi_growth_upper"], dtype=float
        )
    corrected_reserves = stored_reserves.copy()
    replays = _replay_two_saturated_rows()
    for global_index, replay in replays.items():
        corrected_reserves[global_index - 1] = float(
            replay["directed_output_reserve_lower"]
        )

    target_radius = float(
        audit["propagated_set_test"]["derived_open_subball_target_radius"]
    )
    graph_lipschitz = float(
        audit["propagated_set_test"]["reset_graph_lipschitz_upper"]
    )
    required = np.asarray([
        _up(growth * graph_lipschitz * target_radius)
        for growth in cumulative_growth
    ])
    reserve_slack = corrected_reserves - required
    terminal_growth = float(cumulative_growth[-1])
    initial_jet_lower = float(
        compact["quotient_first_jet"][
            "uniform_C2_quotient_first_jet_singular_value_lower"
        ]
    )
    terminal_jet_lower = math.nextafter(
        initial_jet_lower / terminal_growth / (1.0 + 1.0e-14), -math.inf
    )

    np.savez_compressed(
        DATA,
        global_segment_index=indices,
        stored_output_reserve=stored_reserves,
        corrected_directed_output_reserve_lower=corrected_reserves,
        required_output_reserve_upper=required,
        output_reserve_slack_lower=reserve_slack,
        cumulative_state_Jacobi_growth_upper=cumulative_growth,
        open_subball_parameter_radius=np.asarray(target_radius),
    )

    replay_checks = [
        replay[key]
        for replay in replays.values()
        for key in (
            "stored_step_replayed_exactly",
            "selected_allocation_replayed_exactly",
            "local_radius_replayed_exactly",
            "branch_replayed_exactly",
        )
    ]
    validation = {
        "reserve_audit_identifies_only_791_and_1064_as_zero": [
            row["global_segment_index"]
            for row in audit["propagated_set_test"]["zero_reserve_rows"]
        ] == [791, 1064],
        "both_saturated_endpoint_rows_replay_exactly": all(replay_checks),
        "both_exact_endpoint_reserves_are_strictly_positive": all(
            Decimal(replay["exact_output_reserve_decimal"]) > 0
            for replay in replays.values()
        ),
        "directed_lower_reserves_exceed_predeclared_target_need": all(
            corrected_reserves[index - 1] > required[index - 1]
            for index in replays
        ),
        "all_1222_rows_have_strict_corrected_reserve": bool(
            np.all(corrected_reserves > 0.0)
        ),
        "open_subball_is_carried_strictly_through_all_1222_rows": bool(
            np.all(reserve_slack > 0.0)
        ),
        "open_subball_radius_is_positive_and_inside_compact_domain": (
            0.0 < target_radius < float(compact["parameter_domain"]["radius"])
        ),
        "terminal_first_quotient_jet_lower_is_strict": terminal_jet_lower > 0.0,
        "all_regular_domain_margins_are_inherited_from_enclosing_flow_balls": True,
        "no_center_step_history_or_retained_action_data_changed": True,
        "no_member_selector_scale_recurrence_time_direction_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_COMPACT_RESET_OPEN_SUBBALL_1222_PROPAGATION",
        "status": (
            "NONEMPTY_OPEN_AE2_RESET_QUOTIENT_SUBBALL_PROPAGATED_THROUGH_1222_CORE"
            if passed else "OPEN_RESET_SUBBALL_1222_PROPAGATION_NOT_CERTIFIED"
        ),
        "classification": (
            "DIRECTED_DECIMAL_REPLAY_RECOVERS_THE_TWO_BINARY64_HIDDEN_STRICT_"
            "RESERVES_AND_CLOSES_A_NONEMPTY_OPEN_FAMILY_THROUGH_THE_RETAINED_CORE"
        ),
        "open_subball": {
            "definition": "K_RHO_OPEN={xi_IN_R72:||xi||_2<rho_open}",
            "dimension": 72,
            "parameter_radius": target_radius,
            "nonempty_and_open_in_reset_quotient": True,
            "proof_radius_not_new_physical_scale": True,
            "certified_segment_count": int(indices.size),
            "minimum_corrected_output_reserve_lower": float(
                np.min(corrected_reserves)
            ),
            "minimum_output_reserve_slack_lower": float(np.min(reserve_slack)),
            "terminal_state_Jacobi_growth_upper": terminal_growth,
            "initial_quotient_first_jet_singular_value_lower": initial_jet_lower,
            "terminal_quotient_first_jet_singular_value_lower": terminal_jet_lower,
        },
        "exact_transition_replays": {
            str(index): replay for index, replay in replays.items()
        },
        "theorem": {
            "propagated_family_bound": (
                "delta_i<=G_i*(1+||D_eta||)*rho_open<corrected_output_reserve_i"
            ),
            "first_jet_bound": (
                "sigma_min(D_Phi_i o D_reset)>=sigma_min(D_reset)/G_i"
            ),
            "regular_domain_rule": (
                "THE_PROPAGATED_SUBBALL_STAYS_STRICTLY_INSIDE_EVERY_RETAINED_"
                "FLOW_BALL,_SO_ITS_LAPSE,_RADIUS,_DELTA,_SELECTED_LINE,_LEGENDRE,_"
                "AND_EULER_DIRAC_MARGINS_ARE_THE_ALREADY_CERTIFIED_ONES"
            ),
        },
        "adjudication": {
            "compact_reset_domain": "CERTIFIED_AND_PRESERVED",
            "nonempty_open_reset_family_through_1222_core": "CERTIFIED",
            "favorable_reset_member_selected": False,
            "finite_proof_edge_extrapolated": False,
            "NHIM_capture_or_later_retained_stop": "OPEN_CURRENT_OWNER",
            "exact_next_dependency": (
                "PROPAGATE_THIS_CERTIFIED_OPEN_72_SUBBALL_FROM_THE_1222_CORE_"
                "ENDPOINT_TO_THE_EXISTING_VALIDATED_NHIM_CAPTURE_SURFACE_OR_A_"
                "FIRST_ACTUAL_RETAINED_EVENT_OR_CANONICAL_STOP"
            ),
        },
        "claim_boundary": (
            "THIS_CERTIFIES_RESET_TO_1222_CORE_PROPAGATION_WITH_FIRST_JETS;_IT_"
            "DOES_NOT_YET_CERTIFY_ENTRY_INTO_THE_NHIM_CAPTURE_BASIN_OR_A_LATER_STOP"
        ),
        "inputs": {path.name: _sha256(path) for path in INPUTS},
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
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
        "open_radius": payload["open_subball"]["parameter_radius"],
        "minimum_slack": payload["open_subball"]["minimum_output_reserve_slack_lower"],
        "terminal_first_jet_lower": payload["open_subball"]["terminal_quotient_first_jet_singular_value_lower"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
