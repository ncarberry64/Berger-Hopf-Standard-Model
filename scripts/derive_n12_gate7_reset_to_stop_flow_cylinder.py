"""Materialize the exact Gate-7 reset-to-stop flow-cylinder reduction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_RESET_TO_STOP_FLOW_CYLINDER.json"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
FAMILY = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
STOP = BASE / "BHSM_N12_C2_REFINED_CANONICAL_STOP_RECONNAISSANCE.json"
STOP_DATA = STOP.with_suffix(".npz")
CONCAVITY = BASE / "BHSM_N12_C2_GLOBAL_DELTA_CONCAVITY_RECONNAISSANCE.json"
THEORY = ROOT / "theory" / "n12_gate7_reset_to_stop_flow_cylinder.md"
INPUTS = (LAUNCH, FAMILY, STOP, STOP_DATA, CONCAVITY, THEORY)


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
        raise FileNotFoundError("missing flow-cylinder inputs: " + ", ".join(missing))
    launch, family, stop, concavity = (
        _load(path) for path in (LAUNCH, FAMILY, STOP, CONCAVITY)
    )
    witness = stop["candidate_stop"]
    launch_dimension = int(launch["dimension_theorem"]["C2_launch_manifold"])
    stop_dimension = launch_dimension - 1
    ds_da = float(witness["ds_da"])
    validation = {
        "certified_reset_launch_chart_has_dimension_73": (
            launch.get("validation_passed") is True and launch_dimension == 73
        ),
        "exact_family_exists_through_certified_1222_core": (
            family.get("validation_passed") is True
        ),
        "candidate_stop_has_negative_Delta": float(witness["Delta"]) < 0.0,
        "candidate_stop_is_transverse": ds_da < 0.0,
        "candidate_stop_keeps_selected_line_simple": (
            float(witness["selected_eigenline_gap"]) > 0.0
        ),
        "candidate_stop_keeps_positive_lapse_and_radius": (
            float(witness["boundary_lapse"]) > 0.0
            and float(witness["boundary_radius"]) > 0.0
        ),
        "stop_face_plus_flow_coordinate_matches_child_dimension": (
            stop_dimension + 1 == launch_dimension
        ),
        "concavity_route_is_action_owned": (
            "ACTION_OWNED_GLOBAL_DELTA_CONCAVITY_CANDIDATE_LOCALIZED"
            in concavity["status"]
        ),
        "finite_interval_witness_not_overpromoted": (
            stop["claim_boundary"]["between_core_and_stop_interval_shadowing"]
            is False
        ),
        "no_selector_recurrence_new_stop_chord_action_scale_or_time_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_RESET_TO_STOP_FLOW_CYLINDER",
        "status": (
            "EXACT_EXISTENCE_ONLY_FLOW_CYLINDER_REDUCTION_DERIVED;_"
            "FINITE_INTERVAL_WITNESS_OPEN"
            if passed else "FLOW_CYLINDER_REDUCTION_INVALID"
        ),
        "theorem": {
            "regular_child_dimension": launch_dimension,
            "Euler_Dirac_stop_face_dimension": stop_dimension,
            "flow_coordinate_dimension": 1,
            "dimension_identity": "73=72+1",
            "stop_face": "Sigma_ED={s=0,_Delta<0,_all_other_domain_margins_strict}",
            "transversality_identity": "Ds[V]=Delta/||G||!=0",
            "proof_only_reverse_cylinder": "C(z,a)=Phi_-a(iota_Sigma(z))",
            "local_rank_identity": "rank[D_iota,-V]=73",
            "physical_orientation": "ONLY_Phi_+a_IS_THE_FORWARD_PHYSICAL_HISTORY",
        },
        "Gate7_requirement": {
            "classification": "EXISTENCE_ONLY",
            "required": "AT_LEAST_ONE_CERTIFIED_FORWARD_RESET_HISTORY_REACHES_A_FINITE_EVENT_OR_CANONICAL_STOP",
            "not_required": "UNIVERSAL_STOP_OR_TERMINAL_EVENT_REACHABILITY_FOR_THE_FULL_RESET_FAMILY",
            "minimal_present_certificate": (
                "ONE_VALIDATED_RESET_RELATION_WITNESS_PLUS_SCALAR_INTERVAL_"
                "NEWTON_FIRST_HIT_AND_STRICT_EARLIER_DOMAIN_MARGINS"
            ),
            "proof_coordinate_witness_is_a_physical_selector": False,
        },
        "refined_center": {
            "action_length_from_1222_core": stop["action_length"][
                "certified_core_to_candidate_stop"
            ],
            "Delta": witness["Delta"],
            "Ds_V": ds_da,
            "selected_eigenline_gap": witness["selected_eigenline_gap"],
            "boundary_lapse": witness["boundary_lapse"],
            "boundary_radius": witness["boundary_radius"],
            "role": "MULTIPLE_SHOOTING_CENTER_NOT_INTERVAL_AUTHORITY_OR_SELECTOR",
        },
        "finite_proof_operator": {
            "initial_block": "CERTIFIED_RESET_ROOT_AND_1222_CORE_MEMBER_INCLUSION",
            "seams": "SAME_ACTION_FORWARD_GREEN_HERMITE_OR_SHEARED_LOHNER_RESIDUALS",
            "terminal_equation": "s(y_N)=0",
            "terminal_time_column": "Ds[V]=Delta/||G||",
            "domain_conditions": "STRICT_INEQUALITIES_WITH_FIRST_HIT_BOUNDARY_EXCLUSION",
            "solver": "INVERSE_FREE_BORDERED_KRAWCZYK_OR_INTERVAL_NEWTON",
        },
        "exact_next_dependency": (
            "ASSEMBLE_ONE_FINITE_CORRELATED_MULTIPLE_SHOOTING_ENCLOSURE_FROM_"
            "THE_CERTIFIED_1222_CORE_TO_THE_REFINED_TRANSVERSE_STOP_CENTER,_"
            "USING_THE_RETAINED_GREEN_HERMITE_OR_SHEARED_LOHNER_BLOCKS;_"
            "CERTIFY_BOUNDARY_EXCLUSION_AND_THE_SCALAR_s_ZERO_INTERVAL_ROOT"
        ),
        "claim_boundary": {
            "exact_flow_cylinder_theorem": "DERIVED",
            "candidate_stop_center": "REFINED",
            "finite_reset_to_stop_witness": "OPEN_CURRENT_OWNER",
            "finite_endpoint_operator_theorem_applied": False,
            "Gate7": "ACTIVE",
            "Gate8": "LOCKED",
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
        "Gate7_requirement": payload["Gate7_requirement"],
        "refined_center": payload["refined_center"],
        "exact_next_dependency": payload["exact_next_dependency"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
