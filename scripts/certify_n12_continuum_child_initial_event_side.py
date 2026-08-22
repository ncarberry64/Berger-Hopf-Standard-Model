"""Certify the continuum child's initial ordered-event side.

This transfers the tracked child eigenvalue through the already-certified
N12 root ball and continuum action-graph correction.  It adds no event sign
condition and does not assert that a later forward return exists.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHILD_BALL = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CHILD_EVENT_EIGENLINE_BALL.json"
)
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
COMPACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FIRST_SUFFICIENT_COMPACT_CUTOFF.json"
)
ENDPOINTS = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
)
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    getcontext().prec = 180
    inputs = (CHILD_BALL, CONTINUUM, COMPACT, ENDPOINTS)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing initial-side inputs: " + ", ".join(missing))

    child = _load(CHILD_BALL)
    continuum = _load(CONTINUUM)
    compact = _load(COMPACT)
    endpoints = _load(ENDPOINTS)
    if not (
        child["validation_passed"] is True
        and child["sector"] == "child"
        and continuum["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
        and continuum["validation_passed"] is True
        and compact["validation_passed"] is True
        and endpoints["validation_passed"] is True
    ):
        raise RuntimeError("validated child, continuum, compact, and endpoint inputs required")

    center = Decimal.from_float(float(child["center_selected_eigenvalue_binary64"]))
    root_shift = Decimal.from_float(float(child["bounds"]["selected_eigenvalue_shift"]))
    finite_root_lower = center - root_shift
    continuum_radius = Decimal(
        continuum["nonlinear_continuum_radius"]["small_radii_root_upper"]
    )
    compact_coefficient = Decimal(
        compact["directed_decimal_bounds"]["C_compact_sum_upper"]
    )
    continuum_transfer = compact_coefficient * continuum_radius
    continuum_lower = finite_root_lower - continuum_transfer

    diagnostic_values = {
        points: Decimal.from_float(float(record["initial_child"]["raw_eigenvalue"]))
        for points, record in endpoints["endpoint_cross_quadrature"].items()
    }
    diagnostic_minimum = min(diagnostic_values.values())
    validation = {
        "tracked_child_eigenline_simple_on_certified_root_ball": (
            child["validation"]["selected_line_remains_simple"] is True
        ),
        "finite_exact_root_child_side_strictly_positive": finite_root_lower > 0,
        "continuum_transfer_uses_existing_complete_compact_coefficient": (
            compact["quantitative_normal_right_inverse_closed"] is True
        ),
        "continuum_child_side_strictly_positive": continuum_lower > 0,
        "cross_quadrature_values_positive_diagnostic_only": diagnostic_minimum > 0,
        "no_new_event_sign_gate_selector_equation_or_trajectory": True,
        "first_forward_return_still_unproved": True,
    }
    payload = {
        "artifact": "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE",
        "classification": (
            "CONTINUUM_CHILD_INITIAL_ORDERED_EVENT_SIDE_CERTIFIED_POSITIVE;_"
            "FINITE_FORWARD_RETURN_REMAINS_OPEN"
        ),
        "finite_N12_root_ball": {
            "tracked_index": child["transported_N12_eigenline_index"],
            "center_value": str(center),
            "eigenvalue_shift_upper": str(root_shift),
            "exact_root_value_lower": str(finite_root_lower),
            "eigenline_gap_lower": child["bounds"]["eigenline_gap_lower"],
        },
        "continuum_transfer": {
            "eigenvalue_transport_inequality": (
                "ABS(D_E_ORD(Y)[H])=ABS(<PSI,D_HESSIAN(Y)[H]PSI>)"
                "<=C_COMPACT*||H||_G_ON_THE_EXISTING_SOURCE_RESTRICTED_BALL"
            ),
            "action_graph_correction_radius_upper": str(continuum_radius),
            "complete_compact_observation_coefficient_upper": str(compact_coefficient),
            "event_value_transfer_upper": str(continuum_transfer),
            "continuum_initial_child_event_value_lower": str(continuum_lower),
            "sign": "POSITIVE",
        },
        "cross_quadrature_diagnostic": {
            "values": {key: str(value) for key, value in diagnostic_values.items()},
            "minimum": str(diagnostic_minimum),
            "promoted_as_analytic_bound": False,
        },
        "consequence": {
            "future_singular_hit_orientation_not_implied_by_initial_side": True,
            "reason": (
                "THE_EVENT_VECTOR_FIELD_IS_SINGULAR_AND_THE_ONE_SIDED_HITTING_"
                "ORIENTATION_IS_SIGN(C_PSI*B_PSI),_NOT_SIGN(D_T_E_ORD)"
            ),
            "return_exists": False,
            "return_domain_nonempty": False,
            "new_acceptance_condition": False,
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
        "continuum_initial_child_event_value_lower": str(continuum_lower),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
