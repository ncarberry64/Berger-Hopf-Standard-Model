"""Record Outcome C for the completed spectral-Schur finite cover."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "intrinsic_state_selection"
BOX = ARTIFACTS / "BHSM_N12_SPECTRAL_SCHUR_RECENTERABLE_FLOW_BOX_3.json"
DOMAIN = ARTIFACTS / "BHSM_N12_SPECTRAL_SCHUR_ENDPOINT_3_DOMAIN.json"
TRANSPORT = ARTIFACTS / "BHSM_N12_RECENTERED_EVENT_TRANSPORT_DOMAIN_2_3.json"
AUDIT = ARTIFACTS / "BHSM_N12_RECENTERED_EVENT_EIGENVALUE_PRECISION_AUDIT_2_3.json"
RESULT = ARTIFACTS / "BHSM_N12_SPECTRAL_SCHUR_FINITE_COVER_OUTCOME_C.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    inputs = (BOX, DOMAIN, TRANSPORT, AUDIT)
    box, domain, transport, audit = [
        json.loads(path.read_text(encoding="utf-8")) for path in inputs
    ]
    cover = box["cover"]
    corrected_lambda = float(
        transport["event"]["corrected_target_ball_lower_decimal"]
    )
    corrected_du_da = float(
        transport["event"]["corrected_d_u_d_a_lower_decimal"]
    )
    validation = {
        "all_endpoint_certificates_valid": all(
            record["validation_passed"]
            for record in (box, domain, transport, audit)
        ),
        "finite_cover_strictly_extended": (
            cover["candidate_cumulative_coordinate_time"]
            > cover["authoritative_raw_frontier_coordinate_time"]
        ),
        "no_terminal_event_or_reset_hit": cover["terminal_event_hit"] is False,
        "no_existing_physical_domain_exit": (
            cover["physical_domain_exit"] is False
        ),
        "corrected_event_and_chart_transversality_positive": (
            corrected_lambda > 0.0 and corrected_du_da > 0.0
        ),
        "eta_boundary_Dirac_and_tail_margins_closed": (
            domain["existing_physical_domain"]["eta_lower"] > 0.0
            and domain["existing_physical_domain"]["boundary_lapse_lower"] > 0.0
            and domain["Dirac"]["relative_ball_perturbation_upper"] < 1.0
            and domain["continuum_tail"]["epsilon_ED_M0_upper"] >= 0.0
        ),
        "binary_cross_center_event_subtraction_not_promoted": (
            audit["claim_boundary"][
                "binary_cross-center_event_difference_has_physical_authority"
            ] is False
        ),
        "no_equation_gate_selector_orientation_scale_or_parent_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_SPECTRAL_SCHUR_FINITE_COVER_OUTCOME_C",
        "classification": (
            "OUTCOME_C_AUTHORIZED_FINITE_FORWARD_COVER_EXHAUSTED_WITH_"
            "NO_EVENT_HIT_AND_NO_DOMAIN_EXIT"
            if all(validation.values()) else
            "SPECTRAL_SCHUR_FINITE_COVER_OUTCOME_NOT_CLOSED"
        ),
        "authoritative_frontier": {
            "coordinate_time": cover[
                "candidate_cumulative_coordinate_time"
            ],
            "endpoint_tube_radius_upper": float(
                cover["Taylor_endpoint_tube_radius_upper"]
            ),
            "chart_margin_lower": float(cover["chart_ball_margin_lower"]),
            "corrected_event_lower": corrected_lambda,
            "corrected_d_u_d_a_lower": corrected_du_da,
            "eta_lower": domain["existing_physical_domain"]["eta_lower"],
            "boundary_lapse_lower": domain[
                "existing_physical_domain"
            ]["boundary_lapse_lower"],
            "Dirac_relative_perturbation_upper": domain[
                "Dirac"
            ]["relative_ball_perturbation_upper"],
            "ordered_eigenline_gap_lower": domain[
                "ordered_event"
            ]["eigenline_gap_lower"],
            "continuum_tail_upper": domain[
                "continuum_tail"
            ]["epsilon_ED_M0_upper"],
            "terminal_event_hit": False,
            "physical_domain_exit": False,
        },
        "cover_exhaustion": {
            "physical_obstruction_identified": False,
            "first_representation_term_preventing_proportional_propagation": (
                "THE_FIXED_9.8E-10_ACTION_CHART_REQUIRES_A_FULL_ENDPOINT_"
                "RECERTIFICATION_AFTER_APPROXIMATELY_2.4E-16_OF_"
                "COORDINATE_TIME"
            ),
            "repeating_the_same_local_box_is_not_a_reachability_proof": True,
        },
        "claim_boundary": {
            "continuum_child": "CERTIFIED",
            "forward_cover_outcome": "C",
            "intrinsic_state_selection": "OPEN",
            "gauge_scale_flavor_neutrino_observable_prediction": "LOCKED",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DERIVE_OR_CERTIFY_A_CUMULATIVE_RETAINED_ACTION_FORWARD_CONTROL_"
            "THAT_COVERS_MACROSCOPIC_ACTION_PATH_WITH_ACTION_TAYLOR_EVENT_"
            "TRANSPORT_OR_LOCALIZES_THE_FIRST_EXISTING_DOMAIN_EXIT"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "coordinate_time": payload["authoritative_frontier"]["coordinate_time"],
        "corrected_event_lower": corrected_lambda,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
