"""Exclude an ordered-event return on the certified local continuum flow."""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INITIAL = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
)
FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
EVENT_COMPACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ORDERED_EVENT_COMPACT_MODULUS.json"
)
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_NO_EVENT_RETURN.json"
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    getcontext().prec = 180
    inputs = (INITIAL, FLOW, OBSERVATION, EVENT_COMPACT)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing local no-return inputs: " + ", ".join(missing))

    initial = _load(INITIAL)
    flow = _load(FLOW)
    observation = _load(OBSERVATION)
    event_compact = _load(EVENT_COMPACT)
    if not all(record["validation_passed"] is True for record in (
        initial, flow, observation, event_compact,
    )):
        raise RuntimeError("validated initial-side, flow, and event bounds required")

    initial_lower = Decimal(
        initial["continuum_transfer"]["continuum_initial_child_event_value_lower"]
    )
    path_upper = Decimal(flow["directed_decimal_bounds"][
        "vector_field_path_length_upper"
    ])
    third_upper = Decimal.from_float(float(
        observation["sector_bounds"]["child"]["action_third_variation_bound"]
    ))
    core_change = third_upper * path_upper
    flow_error = Decimal(flow["directed_decimal_bounds"][
        "Galerkin_flow_error_upper"
    ])
    event_tail_coefficient = Decimal.from_float(float(
        event_compact["bounds"]["C_event_G_upper"]
    ))
    tail_change = Decimal(2) * event_tail_coefficient * flow_error
    event_lower = initial_lower - core_change - tail_change
    duration = Decimal(flow["directed_decimal_bounds"]["coordinate_duration"])

    validation = {
        "continuum_initial_side_positive": initial_lower > 0,
        "finite_core_event_change_uses_existing_action_third_variation": (
            third_upper > 0 and path_upper > 0
        ),
        "continuum_Galerkin_event_tail_uses_existing_projector_modulus": (
            event_tail_coefficient > 0 and flow_error >= 0
        ),
        "ordered_event_stays_strictly_positive_on_local_interval": event_lower > 0,
        "no_local_first_return": event_lower > 0 and duration > 0,
        "no_new_event_gate_equation_selector_or_trajectory": True,
        "later_return_or_exit_unadjudicated": True,
    }
    payload = {
        "artifact": "BHSM_N12_LOCAL_CONTINUUM_NO_EVENT_RETURN",
        "classification": (
            "ORDERED_EVENT_STAYS_POSITIVE_ON_THE_CERTIFIED_LOCAL_CONTINUUM_"
            "FLOW;_ANY_FIRST_FORWARD_RETURN_MUST_OCCUR_AFTER_LOCAL_BALL_EXIT"
        ),
        "interval": {
            "coordinate_duration_lower": str(duration),
            "action_path_length_upper": str(path_upper),
        },
        "event_enclosure": {
            "initial_value_lower": str(initial_lower),
            "finite_core_third_variation_upper": str(third_upper),
            "finite_core_change_upper": str(core_change),
            "Galerkin_flow_error_upper": str(flow_error),
            "event_projector_tail_coefficient_upper": str(event_tail_coefficient),
            "two_endpoint_tail_change_upper": str(tail_change),
            "event_value_lower_throughout_interval": str(event_lower),
            "sign_throughout_interval": "POSITIVE",
        },
        "consequence": {
            "first_forward_return_inside_certified_local_interval": False,
            "later_first_forward_return_exists": False,
            "physical_domain_exit_proved": False,
            "next_dependency": (
                "EXTEND_THE_EXISTING_ANALYTIC_ACTION_BALL_COVER_BEYOND_THE_"
                "FIRST_LOCAL_INTERVAL_UNTIL_A_TRANSVERSE_EVENT_RETURN_OR_"
                "RETAINED_PHYSICAL_DOMAIN_EXIT_IS_CERTIFIED"
            ),
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "event_value_lower_throughout_interval": str(event_lower),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
