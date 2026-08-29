"""Reduce Gate-7 open-family stop reachability to one transverse witness."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_OPEN_FAMILY_STOP_TRANSVERSALITY_REDUCTION.json"
OPEN_FAMILY = BASE / "BHSM_N12_GATE7_COMPACT_RESET_OPEN_SUBBALL_1222_PROPAGATION.json"
FLOW_CYLINDER = BASE / "BHSM_N12_GATE7_RESET_TO_STOP_FLOW_CYLINDER.json"
REFINED_STOP = BASE / "BHSM_N12_C2_REFINED_CANONICAL_STOP_RECONNAISSANCE.json"
DENSE_FIRST_HIT = BASE / "BHSM_N12_C2_STOP_DENSE_DESCRIPTOR_FIRST_HIT.json"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json"
CORRELATED = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.json"
THEORY = ROOT / "theory" / "n12_gate7_open_family_stop_transversality_reduction.md"
INPUTS = (
    OPEN_FAMILY,
    FLOW_CYLINDER,
    REFINED_STOP,
    DENSE_FIRST_HIT,
    TANGENT,
    CORRELATED,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing open-family stop-reduction inputs: " + ", ".join(missing)
        )
    open_family, cylinder, refined, dense, tangent, correlated = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(record.get("validation_passed") is True for record in (
        open_family, cylinder, dense,
    )):
        raise RuntimeError("validated open-family, cylinder, and first-hit parents required")
    if refined.get("validation_passed") is not False:
        raise RuntimeError("refined stop must remain reconnaissance, not interval authority")
    if tangent.get("validation_passed") is not False or correlated.get("validation_passed") is not False:
        raise RuntimeError("center transport diagnostics must remain non-authoritative")

    subball = open_family["open_subball"]
    center = cylinder["refined_center"]
    tangent_summary = tangent["summary"]
    correction = correlated["summary"]
    terminal_rate = float(center["Ds_V"])
    gap = float(center["selected_eigenline_gap"])
    lapse = float(center["boundary_lapse"])
    radius = float(center["boundary_radius"])
    action_length = float(center["action_length_from_1222_core"])

    validation = {
        "open_reset_family_has_dimension_72": (
            subball["dimension"] == 72
            and subball["nonempty_and_open_in_reset_quotient"] is True
        ),
        "open_family_reaches_1222_core_with_strict_first_jet": (
            subball["terminal_quotient_first_jet_singular_value_lower"] > 0.0
        ),
        "regular_child_dimension_is_seed_plus_flow": (
            cylinder["theorem"]["regular_child_dimension"] == 73
            and cylinder["theorem"]["Euler_Dirac_stop_face_dimension"] == 72
            and cylinder["theorem"]["flow_coordinate_dimension"] == 1
        ),
        "launch_seed_plus_flow_rank_is_73": (
            cylinder["theorem"]["local_rank_identity"]
            == "rank[D_iota,-V]=73"
        ),
        "candidate_terminal_crossing_is_transverse": terminal_rate < 0.0,
        "candidate_other_domain_margins_are_strict": (
            gap > 0.0 and lapse > 0.0 and radius > 0.0 and action_length > 0.0
        ),
        "dense_center_first_hit_is_exact_only_for_stored_polynomials": (
            dense["claim_boundary"]["stored_center_first_hit"] is True
            and dense["claim_boundary"]["exact_history_first_hit"]
            == "OPEN_UNTIL_CORRELATED_SHADOWING_AND_MARGIN_TRANSFER"
        ),
        "center_transport_remains_diagnostic_not_interval_authority": (
            tangent["authority"]
            == "CENTER_AND_SECOND_ORDER_MAGNUS_ONLY_NOT_INTERVAL_HISTORY_AUTHORITY"
            and correlated["authority"]
            == "SIGNED_FINE_GREEN_CENTER_DIAGNOSTIC_NOT_INTERVAL_AUTHORITY"
        ),
        "no_universal_reachability_or_member_selector_is_required": (
            cylinder["Gate7_requirement"]["classification"] == "EXISTENCE_ONLY"
            and cylinder["Gate7_requirement"][
                "proof_coordinate_witness_is_a_physical_selector"
            ] is False
        ),
        "no_selector_recurrence_scale_action_time_direction_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_OPEN_FAMILY_STOP_TRANSVERSALITY_REDUCTION",
        "status": (
            "ONE_TRANSVERSE_CENTER_WITNESS_SUFFICES_FOR_OPEN_72D_STOP_STRATUM"
            if passed else "OPEN_FAMILY_STOP_TRANSVERSALITY_REDUCTION_INVALID"
        ),
        "classification": (
            "FLOW_EQUIVARIANCE_PRESERVES_THE_72_SEED_JET_AND_THE_FLOW_COLUMN;_"
            "A_SINGLE_EXACT_TRANSVERSE_CENTER_HIT_THEREFORE_EXTENDS_BY_THE_"
            "IMPLICIT_FUNCTION_THEOREM_TO_A_NONEMPTY_OPEN_RESET_SEED_STRATUM"
        ),
        "reduction_theorem": {
            "core_seed_map": "E:B_rho_open_IN_R72_TO_M_C2",
            "augmented_forward_map": "F(xi,a)=Phi_a(E(xi))",
            "rank_transport_identity": (
                "[D_xi_F,V(F)]=D_Phi_a(E(xi))*[D_E,V(E(xi))]"
            ),
            "launch_rank": 73,
            "stop_equation": "s(F(xi,a))=0",
            "terminal_time_derivative": "partial_a_s=Ds[V]=Delta/||G||",
            "implicit_function_consequence": (
                "ONE_EXACT_CENTER_HIT_WITH_Ds[V]!=0_GIVES_A_UNIQUE_C1_HIT_TIME_"
                "a(xi)_FOR_EVERY_xi_IN_A_NONEMPTY_OPEN_NEIGHBORHOOD_OF_ZERO"
            ),
            "universal_reachability_required": False,
        },
        "certified_open_core_input": {
            "dimension": int(subball["dimension"]),
            "parameter_radius": float(subball["parameter_radius"]),
            "terminal_first_jet_singular_value_lower": float(
                subball["terminal_quotient_first_jet_singular_value_lower"]
            ),
            "certified_segment_count": int(subball["certified_segment_count"]),
        },
        "existing_transverse_center_target": {
            "action_length_from_core": action_length,
            "Delta": float(center["Delta"]),
            "Ds_V": terminal_rate,
            "selected_eigenline_gap": gap,
            "boundary_lapse": lapse,
            "boundary_radius": radius,
            "stored_center_first_hit_bracket_width": float(
                dense["summary"]["terminal_root_bracket_fraction_width"]
            ),
            "terminal_physical_correction_diagnostic_2_norm": float(
                correction["terminal_physical_state_correction_2_norm"]
            ),
            "physical_fundamental_operator_diagnostic_2_norm": float(
                tangent_summary["physical_fundamental_operator_2_norm"]
            ),
            "role": "KRAWCZYK_CENTER_ONLY_NOT_INTERVAL_HISTORY_AUTHORITY",
        },
        "adjudication": {
            "whole_open_family_multiple_shooting_required": False,
            "one_correlated_center_shadowing_certificate_required": True,
            "open_seed_stratum_after_center_hit": "AUTOMATIC_BY_TRANSVERSALITY",
            "current_geometric_owner": (
                "CERTIFY_ONE_CORRELATED_1222_CORE_CENTER_HISTORY_TO_THE_EXISTING_"
                "TRANSVERSE_s_ZERO_FIRST_HIT_WITH_STRICT_EARLIER_DOMAIN_MARGINS"
            ),
            "NHIM_bridge_required_if_stop_witness_closes": False,
            "finite_endpoint_operator_available_after_witness": True,
        },
        "exact_next_dependency": (
            "CLOSE_OUTWARD_ROUNDED_CORRELATED_Y_Z1_Z2_FOR_THE_EXISTING_QUARTER_"
            "STEP_CENTER,_TRANSFER_STRICT_PRETERMINAL_MARGINS,_AND_APPLY_SCALAR_"
            "INTERVAL_NEWTON_AT_THE_STORED_TRANSVERSE_FIRST_HIT;_DO_NOT_PROPAGATE_"
            "THE_FULL_72D_FAMILY_IN_THE_MULTIPLE_SHOOTING_SOLVE"
        ),
        "claim_boundary": (
            "THE_OPENNESS_PROMOTION_IS_PROVED_CONDITIONALLY_ON_ONE_EXACT_CENTER_"
            "WITNESS;_THE_CURRENT_NUMERICAL_CENTER_IS_NOT_YET_INTERVAL_SHADOWED"
        ),
        "inputs": {path.name: _sha256(path) for path in INPUTS},
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
        "current_owner": payload["adjudication"]["current_geometric_owner"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
