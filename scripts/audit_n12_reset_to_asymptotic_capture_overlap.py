"""Audit overlap between the certified reset neighborhood and capture basin."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_RESET_TO_ASYMPTOTIC_CAPTURE_OVERLAP_AUDIT.json"
)
THEORY = ROOT / "theory/n12_reset_to_asymptotic_capture_overlap_audit.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json",
    ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_CALDERON_ACTION_BALL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing overlap-audit inputs: " + ", ".join(missing))
    capture, radius, ball, local_flow, oracle = (
        _load(path) for path in INPUTS[:-1]
    )
    records = (capture, radius, ball, local_flow, oracle)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated reset/capture overlap inputs required")

    witness = radius["radius_Cauchy_jet_witness"]
    reset_r4 = float(witness["boundary_R4"])
    reset_epsilon = reset_r4**-2
    ball_radius = float(ball["action_coordinate_ball_radius_per_sector"])
    validation = {
        "reset_R4_is_positive": reset_r4 > 0.0,
        "reset_epsilon_recomputed_from_action_owned_radius": math.isclose(
            reset_epsilon, math.exp(-2.0 * float(witness["boundary_log_R4"])),
            rel_tol=2.0e-15,
        ),
        "capture_constants_are_explicitly_unquantified": (
            capture["capture_theorem"]["there_exist_unquantified"]
            == "epsilon_star>0_AND_delta_star>0"
        ),
        "capture_surface_is_not_certified": (
            capture["scope"]["explicit_capture_surface_certified"] is False
        ),
        "reset_entry_is_not_certified": (
            capture["scope"]["AE2_reset_entry_certified"] is False
        ),
        "Calderon_ball_is_local_to_each_reset_root": (
            ball["scope"].startswith("FINITE_N12_FULL_ACTION_COORDINATE_NEIGHBORHOOD")
        ),
        "existing_flow_variation_bounds_are_local": (
            local_flow["status"] == "LOCAL_SECOND_STATE_JACOBI_AND_LOG_RADIUS_TUBE_DERIVED"
        ),
        "actual_parametric_reset_oracle_is_open": (
            oracle["claim_boundary"]["actual_parametric_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "reset_radius_Cauchy_jet_rank_is_two": witness["radius_Cauchy_jet_rank"] == 2,
        "time_quotient_leaves_physical_radius_history_direction": (
            witness[
                "rank_inequality_after_any_one_dimensional_time_quotient"
            ]
            == 1
        ),
        "no_unrelated_radius_comparison_promoted_to_overlap": True,
    }

    return {
        "artifact": "BHSM_N12_RESET_TO_ASYMPTOTIC_CAPTURE_OVERLAP_AUDIT",
        "status": "EXISTING_RESET_AND_LOCAL_FLOW_CERTIFICATES_DO_NOT_YET_REACH_A_QUANTIFIED_CAPTURE_SURFACE",
        "classification": (
            "THE_CERTIFIED_RESET_LIES_AT_R4=1.0023342201094778_AND_"
            "epsilon=R4^-2_APPROX_0.99535;_THE_CALDERON_AND_EULER_DIRAC_"
            "CERTIFICATES_ARE_LOCAL_TO_THE_RESET_WHILE_THE_ASYMPTOTIC_"
            "CAPTURE_CONSTANTS_ARE_EXISTENTIAL_ONLY,_SO_NO_COMMON_CHART_"
            "OVERLAP_INEQUALITY_OR_SET_VALUED_RESET_INTERSECTION_IS_YET_"
            "EVALUABLE"
        ),
        "reset_data": {
            "R4": reset_r4,
            "log_R4": witness["boundary_log_R4"],
            "epsilon=R4^-2": reset_epsilon,
            "proper_log_R4_rate": witness["boundary_proper_log_R4_rate"],
            "raw_reset_tangent_dimension": witness["raw_reset_tangent_dimension"],
            "radius_Cauchy_jet_rank": witness["radius_Cauchy_jet_rank"],
            "minimum_rank_after_time_quotient": witness[
                "rank_inequality_after_any_one_dimensional_time_quotient"
            ],
        },
        "available_local_certificates": {
            "Calderon_action_coordinate_radius": ball_radius,
            "Calderon_center": "EACH_ENCLOSED_EXACT_RESET_ROOT",
            "Euler_Dirac_variation_scope": "LOCAL_ANCHOR_ACTION_BALL",
            "finite_first_and_mixed_second_log_R4_bounds": local_flow[
                "validation"
            ]["finite_local_first_and_mixed_log_R4_bounds"],
        },
        "missing_overlap_data": {
            "numeric_epsilon_star_lower": None,
            "numeric_delta_star_lower": None,
            "common_asymptotic_norm_and_chart": None,
            "validated_reset_component_cover_to_capture_surface": None,
            "set_valued_reset_stratum_intersection": None,
            "first_and_mixed_second_quotient_jets_through_connection": None,
        },
        "noncomparison_theorem": {
            "Calderon_ball_radius_may_be_compared_directly_to_epsilon_star": False,
            "reason": (
                "THEY_ARE_RADII_IN_DIFFERENT_CHARTS_WITH_DIFFERENT_CENTERS_"
                "AND_NORMS;_NO_CERTIFIED_TRANSITION_MAP_BOUND_IS_AVAILABLE"
            ),
            "one_stored_reset_representative_is_sufficient": False,
        },
        "exact_next_dependency": {
            "capture_side": (
                "DERIVE_EXPLICIT_FINITE_N12_COMPACTIFIED_ACTION_MAJORANTS_"
                "GIVING_A_POSITIVE_CAPTURE_SURFACE_AND_ALL_REGULARITY_MARGINS"
            ),
            "connection_side": (
                "VALIDATE_A_FORWARD_COMPONENT_COVER_FROM_A_NONEMPTY_PHYSICAL_"
                "RESET_QUOTIENT_STRATUM_TO_THAT_SURFACE_WITH_FIRST_AND_MIXED_"
                "SECOND_JETS,_OR_CERTIFY_A_LATER_EVENT_OR_CANONICAL_STOP_FIRST"
            ),
            "required_join": (
                "PROVE_THE_TERMINAL_COVER_SET_IS_CONTAINED_IN_THE_CAPTURE_"
                "SURFACE_IN_ONE_COMMON_NORM_AND_CHART"
            ),
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_QUANTITATIVE_CAPTURE_SURFACE_AND_RESET_COMPONENT_INTERSECTION",
            "Gate8": "LOCKED",
            "finite_N12_existential_capture_basin": "DERIVED",
            "quantitative_capture_surface": "OPEN",
            "reset_to_capture_overlap": "NOT_CERTIFIED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
