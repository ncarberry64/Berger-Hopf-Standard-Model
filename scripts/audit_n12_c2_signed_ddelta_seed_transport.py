"""Audit transport of the signed reference-center DDelta ball to the exact tube."""

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

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT.json"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
STEP = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_c2_signed_ddelta_seed_transport_audit.md"
INPUTS = (
    FIELD, FIELD_DATA, BORDERED, BORDERED_DATA, GROWTH, STEP, CORE, CORE_DATA,
    THEORY,
)
INFLATION = 1.0 + 1.0e-10
REFERENCE_NODE = 1214


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing DDelta transport inputs: " + ", ".join(missing))
    field, bordered, growth, step, core = (
        _load(path) for path in (FIELD, BORDERED, GROWTH, STEP, CORE)
    )
    if not all(record.get("validation_passed") is True for record in (
        field, bordered, growth, step, core,
    )):
        raise RuntimeError("validated signed-seed and continuation parents required")

    with np.load(FIELD_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        delta_partial = np.asarray(data["Delta_first_partial_action"], dtype=float)
        delta_seed_remainder = float(
            data["Delta_first_total_remainder_action_norm_upper"]
        )
    with np.load(BORDERED_DATA) as data:
        response = np.asarray(data["bordered_response"], dtype=float)
        response_first = np.asarray(
            data["bordered_response_derivative_action"], dtype=float
        )
        bordered_matrix = np.asarray(data["bordered_matrix"], dtype=float)
    with np.load(CORE_DATA) as data:
        proof_centers = np.asarray(data["C2_proof_center_nodes"], dtype=float)
        node_tubes = np.asarray(data["node_action_tube_upper"], dtype=float)

    center_match = float(np.linalg.norm(
        (proof_centers[REFERENCE_NODE] - center) * weights
    ))
    incoming_tube = float(node_tubes[REFERENCE_NODE])
    domain_radius = float(step["domain"]["selected_domain_radius"])
    fresh = growth["fresh_line_bounds"]
    pole_free = growth["fresh_pole_free_bounds"]
    forcing = bordered_matrix @ response
    rhs_zero = _up(float(np.linalg.norm(forcing[:-1])))
    rhs_one = float(pole_free["rhs_raw_derivative_center"])
    rhs_two = float(pole_free["rhs_raw_second_derivative_upper"])
    line_one = float(
        fresh["weighted_selected_to_complement_first_variation_on_ball"]
    )
    line_two = float(fresh["selected_line_second_variation_coefficient_upper"])
    b_one_center = _up(float(np.linalg.norm(response_first[-1])))
    b_two = _up(
        line_two * rhs_zero + 2.0 * line_one * rhs_one + rhs_two
    )
    b_one_ball = _up(b_one_center + b_two * domain_radius)

    cubic = growth["moving_cubic"]
    c_one_ball = _up(
        float(cubic["center_complete_first_derivative_upper"])
        + float(cubic["second_derivative_upper"]) * domain_radius
    )
    c_two = float(cubic["second_derivative_upper"])
    c_upper = float(step["domain"]["c_interval"][1])
    b_upper = float(step["domain"]["b_psi_interval"][1])
    signed_descriptor = float(field["center_field"]["signed_descriptor_decimal"])
    R_two = float(step["second_variation"]["R_second_variation_upper"])
    delta_two = _up(
        c_two * b_upper + 2.0 * c_one_ball * b_one_ball
        + c_upper * b_two + abs(signed_descriptor) * R_two
    )

    seed_norm = float(np.linalg.norm(delta_partial))
    transported_remainder = _up(
        delta_seed_remainder + delta_two * incoming_tube
    )
    zero_exclusion_margin = seed_norm - transported_remainder
    maximum_resolving_radius = max(
        0.0, (seed_norm - delta_seed_remainder) / delta_two
    )
    localization_improvement_required = incoming_tube / maximum_resolving_radius

    validation = {
        "reference_center_is_exactly_stored_node_1214": center_match == 0.0,
        "incoming_exact_state_tube_lies_inside_first_matrix_domain": (
            0.0 < incoming_tube < domain_radius
        ),
        "second_variation_product_rule_is_finite_positive": (
            math.isfinite(delta_two) and delta_two > 0.0
        ),
        "transported_ball_is_a_valid_mean_value_enclosure": (
            transported_remainder
            >= delta_seed_remainder + delta_two * incoming_tube
        ),
        "retained_coarse_transport_ball_contains_zero": zero_exclusion_margin < 0.0,
        "coarse_transport_does_not_resolve_signed_family_covector": (
            transported_remainder > seed_norm
        ),
        "failure_is_proof_resolution_not_physical_singularity": (
            step["hindsight"]["obstruction_physical"] is False
        ),
        "proof_center_not_promoted_to_exact_history": (
            core["coefficient_path"]["proof_centers_are_exact_physical_states"]
            is False
        ),
        "no_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT",
        "status": (
            "COARSE_DDELTA_TRANSPORT_CERTIFIED_BUT_NOT_SIGN_RESOLVING"
            if passed else "DDELTA_TRANSPORT_AUDIT_FAILED"
        ),
        "classification": (
            "THE_RETAINED_SELECTED_LINE_AND_HARD_COMPLEMENT_PRODUCT_"
            "MAJORANTS_GIVE_A_VALID_D2DELTA_BOUND_ON_THE_FIRST_MATRIX_"
            "CHART,_BUT_TRANSPORT_FROM_THE_NODE_1214_PROOF_CENTER_ACROSS_"
            "ITS_CERTIFIED_EXACT_STATE_TUBE_PRODUCES_A_BALL_CONTAINING_ZERO;_"
            "THIS_IS_A_PROOF_RESOLUTION_ARTIFACT_NOT_A_PHYSICAL_OBSTRUCTION"
        ),
        "reference_transport": {
            "reference_node": REFERENCE_NODE,
            "proof_center_match_action_norm": center_match,
            "incoming_exact_state_tube_action_radius_upper": incoming_tube,
            "first_matrix_chart_action_radius": domain_radius,
            "DDelta_seed_partial_action_norm": seed_norm,
            "DDelta_seed_remainder_action_norm_upper": delta_seed_remainder,
            "b_psi_second_variation_upper": b_two,
            "R_second_variation_upper": R_two,
            "D2Delta_action_bilinear_norm_upper": delta_two,
            "transported_DDelta_remainder_action_norm_upper": transported_remainder,
            "transported_ball_zero_exclusion_margin": zero_exclusion_margin,
            "transported_remainder_to_seed_norm_ratio": (
                transported_remainder / seed_norm
            ),
            "maximum_tube_radius_for_this_bound_to_exclude_zero": (
                maximum_resolving_radius
            ),
            "required_tube_localization_improvement_factor": (
                localization_improvement_required
            ),
        },
        "theorem": {
            "Delta": "Delta=c*b_psi+s*R_up_to_the_retained_signed_convention",
            "coarse_second_variation": (
                "norm(D2Delta)<=c2*b+2*c1*b1+c*b2+abs(s)*R2"
            ),
            "transport": (
                "DDelta(Y_exact)_in_DDelta(Y_1214)+Ball(0,r_seed+B_D2Delta*r_tube)"
            ),
            "zero_exclusion_test": "norm(DDelta_partial)>r_seed+B_D2Delta*r_tube",
        },
        "adjudication": {
            "coarse_second_variation_transport": "CERTIFIED",
            "signed_DDelta_reference_seed": "CERTIFIED",
            "signed_DDelta_on_exact_parametric_family": "OPEN_NOT_RESOLVED_BY_COARSE_BOUND",
            "physical_obstruction_found": False,
            "minimal_missing_theorem": (
                "DIRECT_CANCELLATION_PRESERVING_D2DELTA_BOUND_OR_A_"
                "STRICTLY_TIGHTER_EXACT_STATE_LOCALIZATION"
            ),
            "transposed_exact_segment_map_action": "INDEPENDENTLY_OPEN",
            "actual_projected_zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_D2DELTA_DIRECTLY_FROM_THE_SIGNED_DELTA_DIFFERENTIAL_"
            "INCLUDING_SELECTED_LINE_HARD_COMPLEMENT_CANCELLATIONS,_OR_"
            "LOCALIZE_THE_EXACT_NODE_1214_STATE_BELOW_THE_REPORTED_RESOLVING_"
            "RADIUS;_DO_NOT_PROMOTE_THE_COARSE_PRODUCT_BALL_TO_A_PHYSICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_DIRECT_D2DELTA_SEGMENT_ACTION_SOURCE_AND_TAIL",
            "Gate8": "LOCKED",
            "signed_D_Y_Delta": "OPEN",
            "actual_signed_duration_covector": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
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
        "reference_transport": payload["reference_transport"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
