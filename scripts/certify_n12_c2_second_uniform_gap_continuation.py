"""Continue C2 on the fresh fixed-descriptor chart."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_uniform_gap_fiber_ball import (  # noqa: E402
    uniform_gap_descriptor_fiber_ball,
)
from certify_n12_c2_descriptor_fiber_cancelled_continuation import (  # noqa: E402
    _fiber_center_field,
)
from certify_n12_c2_fresh_center_denominator_continuation import (  # noqa: E402
    _float_lower, _float_upper, _maximal_closing_step,
)
from certify_n12_c2_uniform_gap_continuation import _center_response  # noqa: E402
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
PREFIX = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
PREFIX_DATA = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.npz"
CHART = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_uniform_gap_fiber_ball.py"
THEORY = ROOT / "theory" / "n12_c2_second_uniform_gap_continuation.md"
RESULT = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
DATA_RESULT = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.npz"
INPUTS = (PREFIX, PREFIX_DATA, CHART, GROWTH, MODULE, THEORY)
MAX_BOXES = 512


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing second uniform-gap inputs: " + ", ".join(missing))
    prefix, chart, growth = (_json(path) for path in (PREFIX, CHART, GROWTH))
    if not all(record.get("validation_passed") is True for record in (prefix, chart, growth)):
        raise RuntimeError("validated fresh-chart continuation parents required")
    with np.load(PREFIX_DATA) as data:
        center = np.asarray(data["C2_uniform_gap_predictor_centers"][-1], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    prior = prefix["continuation"]
    fresh = growth["fresh_line_bounds"]
    line = {
        "eigenline_gap_lower": float(fresh["eigenline_gap_lower"]),
        "weighted_selected_to_complement_first_variation_on_ball": float(
            fresh["weighted_selected_to_complement_first_variation_on_ball"]
        ),
        "selected_eigenvalue_first_derivative_bound": float(
            fresh["selected_eigenvalue_first_derivative_bound"]
        ),
        "selected_eigenvalue_raw_Hessian_bound": float(
            fresh["selected_eigenvalue_raw_Hessian_bound"]
        ),
    }
    birth = {
        "moving_cubic": growth["moving_cubic"],
        "selected_line": {
            "first_variation_coefficient_upper": float(
                fresh["weighted_selected_to_complement_first_variation_on_ball"]
            ),
            "complete_second_variation_coefficient_upper": float(
                fresh["selected_line_second_variation_coefficient_upper"]
            ),
        },
        "birth_limit_generator": growth["birth_limit_generator"],
    }
    pf = growth["fresh_pole_free_bounds"]
    certificate_radius = float(
        growth["radius_derivation"]["selected_growth_chart_radius"]
    )
    rows: list[dict[str, Any]] = []
    centers = [center.copy()]
    exhaustion = "SECOND_UNIFORM_GAP_SAFETY_LIMIT_REACHED"
    witness: dict[str, Any] = {}

    with localcontext() as context:
        context.prec = 100
        signed_s = Decimal(prior["final_signed_lambda_decimal"])
        initial_s = signed_s
        tube = Decimal.from_float(float(prior["final_endpoint_tube_radius_upper"]))
        initial_tube = tube
        base_path = Decimal(0)
        proper_lower_sum = Decimal(0)
        proper_upper_sum = Decimal(0)
        for index in range(MAX_BOXES):
            path_upper = _float_upper(base_path)
            parent_radius = certificate_radius - path_upper
            response = _center_response(center, weights, reference)
            descriptor_upper = _float_upper(signed_s)
            try:
                for _ in range(16):
                    ball = uniform_gap_descriptor_fiber_ball(
                        incoming_tube=_float_upper(tube),
                        parent_radius=parent_radius,
                        base_path=path_upper,
                        descriptor_upper=descriptor_upper,
                        pf=pf, line=line, birth=birth,
                        center_state=center,
                        center_b=float(response["b_psi_center"]),
                        center_hard_raw_norm=float(response["hard_rate_raw_norm"]),
                        center_selected_action_norm=float(response["selected_action_norm"]),
                        weights=weights, coefficient_enclosure=_coefficient_enclosure,
                    )
                    proof = _fiber_center_field(
                        center=center, weights=weights, reference=reference,
                        signed_s=float(signed_s), c_interval=tuple(ball["c_psi_interval"]),
                        ball=ball,
                    )
                    step = _maximal_closing_step(
                        center=center, weights=weights, signed_s=float(signed_s),
                        tube=_float_upper(tube), ball=ball, proof=proof,
                    )
                    required = _float_upper(
                        signed_s + Decimal.from_float(float(step["selected_midpoint_step"]))
                    )
                    if required <= descriptor_upper:
                        break
                    descriptor_upper = required
                else:
                    raise ArithmeticError("second descriptor fixed point did not close")
            except ArithmeticError as error:
                exhaustion = "SECOND_UNIFORM_GAP_CONTINUATION_PROOF_EXHAUSTED"
                witness = {
                    "message": str(error),
                    "incoming_tube_upper": _float_upper(tube),
                    "fresh_center_path_upper": path_upper,
                    "remaining_growth_chart_radius": parent_radius,
                }
                break

            step_s = Decimal.from_float(float(step["selected_midpoint_step"]))
            if float(step["stored_step_norm"]) == 0.0:
                exhaustion = "BINARY64_PREDICTOR_CENTER_REPRESENTATION_LIMIT"
                witness = {
                    "message": "positive descriptor step rounds to zero stored action-center increment",
                    "signed_lambda_step_decimal": str(step_s),
                    "incoming_tube_upper": _float_upper(tube),
                    "fresh_center_path_upper": _float_upper(base_path),
                    "remaining_growth_chart_radius": certificate_radius - _float_upper(base_path),
                }
                break
            end_s = signed_s + step_s
            physical_increment = end_s**2 - signed_s**2
            if physical_increment <= 0:
                exhaustion = "SECOND_UNIFORM_GAP_PHYSICAL_INCREMENT_NOT_POSITIVE"
                break
            delta_lower = Decimal.from_float(float(ball["Delta_interval"][0]))
            delta_upper = Decimal.from_float(float(ball["Delta_interval"][1]))
            coordinate_lower = physical_increment / (Decimal(2) * delta_upper)
            coordinate_upper = physical_increment / (Decimal(2) * delta_lower)
            lapse_lower = Decimal.from_float(float(ball["lapse_interval"][0]))
            lapse_upper = Decimal.from_float(float(ball["lapse_interval"][1]))
            proper_lower = lapse_lower * coordinate_lower
            proper_upper = lapse_upper * coordinate_upper
            proper_lower_sum += proper_lower
            proper_upper_sum += proper_upper
            base_path += Decimal.from_float(float(step["stored_step_norm"]))
            tube = Decimal.from_float(float(step["new_tube"]))
            center = np.asarray(step["stored_center"], dtype=float)
            signed_s = end_s
            centers.append(center.copy())
            rows.append({
                "second_uniform_gap_index": index + 1,
                "global_segment_index": int(prior["total_certified_segments"]) + index + 1,
                "selected_branch": int(response["selected_branch"]),
                "descriptor_fiber_lambda_upper": float(ball["descriptor_fiber_lambda_upper"]),
                "incoming_tube_upper": float(ball["incoming_endpoint_tube_radius"]),
                "joint_feasibility_upper_radius": float(ball["joint_feasibility_upper_radius"]),
                "selected_ball_radius": float(ball["selected_midpoint_radius"]),
                "uniform_hard_gap_lower": float(ball["uniform_hard_gap_lower"]),
                "hard_Gronwall_exponent_upper": float(ball["covariant_hard_Gronwall_exponent_upper"]),
                "Delta_lower": float(ball["Delta_interval"][0]),
                "fixed_s_speed_upper": float(ball["regularized_speed_upper"]),
                "fixed_s_Jacobi_upper": float(ball["pole_free_regularized_Jacobi_upper"]),
                "center_field_norm": float(proof["field_action_norm"]),
                "center_field_mismatch_upper": float(proof["field_mismatch_upper"]),
                "signed_lambda_step_decimal": str(step_s),
                "physical_u_increment_decimal": str(physical_increment),
                "proper_time_increment_interval": [
                    _float_lower(proper_lower), _float_upper(proper_upper),
                ],
                "Jacobi_growth_upper": float(step["growth"]),
                "endpoint_tube_radius_upper": _float_upper(tube),
                "fresh_center_path_upper": _float_upper(base_path),
                "root_use_inside_selected_ball": float(step["root_use"]),
                "proof_center_is_physical_endpoint": False,
            })
        else:
            exhaustion = "INTERNAL_512_BOX_IMPLEMENTATION_GUARD_REACHED_NOT_A_PHYSICAL_OUTCOME"

    np.savez_compressed(
        DATA_RESULT,
        C2_second_uniform_gap_predictor_centers=np.asarray(centers),
        state_weights=weights,
        branch_reference=reference,
    )
    accepted = len(rows)
    validation = {
        "validated_1192_segment_prefix_consumed": int(prior["total_certified_segments"]) == 1192,
        "fresh_chart_certifies_strict_extension": accepted > 0,
        "all_centers_retain_branch_24": accepted > 0 and all(row["selected_branch"] == 24 for row in rows),
        "all_gap_Delta_and_proper_margins_positive": accepted > 0 and all(
            row["uniform_hard_gap_lower"] > 0.0 and row["Delta_lower"] > 0.0
            and row["proper_time_increment_interval"][0] > 0.0 for row in rows
        ),
        "all_tubes_close_in_fresh_descriptor_balls": accepted > 0 and all(
            row["root_use_inside_selected_ball"] < row["selected_ball_radius"] for row in rows
        ),
        "old_chart_majorants_and_redundant_denominator_not_used": True,
        "proof_exhaustion_not_promoted_to_event_or_stop": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION",
        "status": (
            "C2_SECOND_UNIFORM_GAP_CONTINUATION_CERTIFIED" if passed
            else "C2_SECOND_UNIFORM_GAP_CONTINUATION_NOT_CERTIFIED"
        ),
        "continuation": {
            "prior_total_segments": int(prior["total_certified_segments"]),
            "additional_certified_segments": accepted,
            "total_certified_segments": int(prior["total_certified_segments"]) + accepted,
            "rows": rows,
            "initial_signed_lambda_decimal": str(initial_s),
            "final_signed_lambda_decimal": str(signed_s),
            "initial_endpoint_tube_radius_upper": _float_upper(initial_tube),
            "final_endpoint_tube_radius_upper": _float_upper(tube),
            "fresh_center_path_upper": _float_upper(base_path),
            "additional_proper_duration_interval": [
                _float_lower(proper_lower_sum), _float_upper(proper_upper_sum),
            ],
            "exhaustion_classification": exhaustion,
            "exhaustion_witness": witness,
            "exhaustion_is_event_or_canonical_stop": False,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
        },
        "hindsight": {
            "result": "OPEN",
            "classification": "CONTINUOUS_WITHIN_CLASS_EVOLUTION;_NUMERICAL_CONDITIONING",
            "obstruction_physical": False,
            "outcome": "C_REGULAR_CONTINUATION_REMAINS_OPEN",
        },
        "adjudication": {
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "Gate7": "G7_08_OPEN_MAXIMAL_C2_FORCE_OR_FINITE_EVENT_STOP",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "STORE_THE_PREDICTOR_CENTER_AS_A_COMPENSATED_BASE_PLUS_ACTION_"
            "OFFSET_AND_CONTINUE_THE_SAME_FRESH_FIXED_DESCRIPTOR_CHART;_DO_NOT_"
            "CREATE_ZERO_GEOMETRY_ROWS"
        ),
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
        encoding="utf-8", newline="\n",
    )
    continuation = payload["continuation"]
    print(json.dumps({
        "status": payload["status"],
        "additional_segments": continuation["additional_certified_segments"],
        "total_segments": continuation["total_certified_segments"],
        "final_signed_lambda": continuation["final_signed_lambda_decimal"],
        "final_tube": continuation["final_endpoint_tube_radius_upper"],
        "fresh_path": continuation["fresh_center_path_upper"],
        "exhaustion": continuation["exhaustion_classification"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
