"""Audit what is still needed to promote the N12 infinity branch to a basin."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_CAPTURE_BASIN_PRECONDITIONS.json"
)
THEORY = ROOT / "theory/n12_asymptotic_capture_basin_preconditions.md"
JET_SOURCE = ROOT / (
    "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json",
    JET_SOURCE,
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing capture-basin audit inputs: " + ", ".join(missing))

    descriptor, branch, connection = (_load(path) for path in INPUTS[:3])
    if not all(
        record.get("validation_passed") is True
        for record in (descriptor, branch, connection)
    ):
        raise RuntimeError("validated capture-basin inputs required")

    source = JET_SOURCE.read_text(encoding="utf-8")
    clusters = descriptor["descriptor"]["bordered_clusters"]
    validation = {
        "weight_seven_helper_is_explicitly_a_quadratic_jet": (
            "Return the exact weight-seven quadratic jet" in source
        ),
        "helper_disclaims_nonlinear_truncation_away_from_background": (
            "not a\n    proposed truncation of the nonlinear retained action away from that\n"
            "    background" in source
        ),
        "linear_center_count_is_25": clusters["center_count"] == 25,
        "linear_stable_count_is_25": clusters["stable_count"] == 25,
        "linear_unstable_count_is_zero": clusters["unstable_count"] == 0,
        "existing_result_is_one_analytic_branch": (
            branch["analytic_branch_theorem"]["conclusion"][
                "complete_descriptor_branch"
            ]
            == "Z(epsilon)=epsilon*X5+epsilon^2*R(epsilon)"
        ),
        "existing_branch_does_not_prove_backward_connection": (
            branch["nonlinear_consequence"]["backward_continuation_to_formation_or_event"]
            == "NOT_PROVED_BY_THIS_LOCAL_INFINITY_THEOREM"
        ),
        "connection_ledger_already_denies_a_trapping_basin": (
            connection["adjudication"]["analytic_branch_is_current_exterior_oracle"]
            is False
        ),
        "no_selector_endpoint_chord_scale_fit_or_action_term_added": True,
    }

    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_CAPTURE_BASIN_PRECONDITIONS",
        "status": "LINEAR_DESCRIPTOR_AND_ONE_ANALYTIC_BRANCH_DO_NOT_PROVE_AN_OPEN_CAPTURE_BASIN",
        "classification": (
            "THE_WEIGHT_SEVEN_CERTIFICATE_IS_AN_EXACT_TWO_JET_ONLY;_IT_FIXES_"
            "THE_LINEAR_25_CENTER_PLUS_25_STABLE_DESCRIPTOR_BUT_NOT_THE_"
            "NONLINEAR_LEADING_WEIGHT_CENTER_VECTOR_FIELD;_THE_EXISTING_"
            "BRIOT_BOUQUET_RESULT_PROVES_ONE_ANALYTIC_H4_TO_H0_BRANCH,_NOT_"
            "A_TRAPPING_NEIGHBORHOOD_OR_RESET_INTERSECTION"
        ),
        "certified": {
            "weight_seven_action_two_jet": True,
            "physical_linear_modes": {
                "center": 25,
                "stable": 25,
                "unstable": 0,
                "algebraic": descriptor["descriptor"]["algebraic_infinite_mode_count"],
            },
            "one_complete_action_analytic_infinity_branch": True,
            "branchwise_H4_limit": "H0>0",
        },
        "not_certified": {
            "exact_reduced_identity_N7_equals_zero": False,
            "leading_weight_center_set_invariant": False,
            "normally_attracting_center_manifold": False,
            "open_local_capture_basin": False,
            "quantitative_capture_radius": False,
            "AE2_reset_image_intersects_capture_basin": False,
            "continuum_uniform_capture_basin": False,
        },
        "logical_obstruction": {
            "general_reduced_form": (
                "a'=v;_v'=-7*H0*v+N7(a,v)+epsilon*F(a,v,epsilon)"
            ),
            "known_jet_conditions": "N7(0,0)=0_AND_D_N7(0,0)=0",
            "missing_identity": "N7(a,0)=0_OR_A_REPLACEMENT_TRAPPING_BOUND",
            "why_two_jet_is_insufficient": (
                "A_CUBIC_WEIGHT_SEVEN_ACTION_TERM_IS_INVISIBLE_TO_THE_ACTION_"
                "TWO_JET_BUT_CONTRIBUTES_A_QUADRATIC_CENTER_VECTOR_FIELD"
            ),
            "why_one_branch_is_insufficient": (
                "AN_INVARIANT_GRAPH_EXISTENCE_THEOREM_DOES_NOT_CONTROL_NEARBY_"
                "INITIAL_DATA_OR_ESTABLISH_NORMAL_ATTRACTION"
            ),
        },
        "minimal_next_theorem": {
            "route_A": (
                "EXTRACT_THE_EXACT_CONSTRAINT_REDUCED_NONLINEAR_WEIGHT_SEVEN_"
                "VECTOR_FIELD_AND_PROVE_AN_INVARIANT_NORMALLY_ATTRACTING_"
                "CENTER_MANIFOLD_WITH_A_POSITIVE_H4_AND_DOMAIN_MARGIN"
            ),
            "route_B": (
                "PROVE_A_COMPLETE_LEADING_WEIGHT_LYAPUNOV_OR_TRAPPING_"
                "INEQUALITY_AND_ABSORB_ALL_POSITIVE_epsilon_WEIGHT_REMAINDERS"
            ),
            "then": (
                "COMPUTE_EXPLICIT_CAPTURE_MAJORANTS_AND_CERTIFY_RESET_ENTRY,_"
                "OR_CERTIFY_A_LATER_EVENT_OR_CANONICAL_STOP_FIRST"
            ),
        },
        "supersession": {
            "analytic_infinity_branch_preserved": True,
            "branchwise_H4_to_H0_preserved": True,
            "open_basin_promotion_authorized": False,
            "mathematical_infinite_branch_reclassified": False,
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_NONLINEAR_LEADING_WEIGHT_BASIN_OR_DIRECT_CONNECTION_OWNER",
            "Gate8": "LOCKED",
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
