"""Audit whether the analytic infinite branch is reset-connected child data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json"
)
THEOREM = ROOT / "theory/n12_asymptotic_child_exterior_connection_preconditions.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    THEOREM,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing asymptotic-connection inputs: " + ", ".join(missing))
    chronology, branch, descriptor, reset, maximal, parametric = (
        _load(path) for path in INPUTS[:-1]
    )
    records = (chronology, branch, descriptor, reset, maximal, parametric)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated asymptotic-connection inputs required")

    validation = {
        "infinite_Friedrichs_child_exterior_is_action_allowed": (
            chronology["adjudication"]["infinite_Friedrichs_child_exterior_allowed"]
            is True
            and maximal["endpoint_rule"]["if_Tmax_is_infinite"]
            == "CLOSE_THE_NONNEGATIVE_MINIMAL_FORM_BY_ITS_FRIEDRICHS_CLOSURE"
        ),
        "analytic_infinite_branch_exists": (
            branch["analytic_branch_theorem"]["conclusion"]["exists_epsilon_star"]
            is True
        ),
        "branch_has_positive_expansion_limit": (
            branch["nonlinear_consequence"]["a_preserves_H4_to_H_inf_positive"]
            is True
        ),
        "backward_connection_is_not_proved": (
            branch["nonlinear_consequence"]["backward_continuation_to_formation_or_event"]
            == "NOT_PROVED_BY_THIS_LOCAL_INFINITY_THEOREM"
        ),
        "descriptor_has_center_modes": (
            descriptor["descriptor"]["center_root"] == 0.0
            and descriptor["descriptor"]["bordered_clusters"]["center_count"] == 25
        ),
        "descriptor_has_no_unstable_finite_mode": (
            descriptor["descriptor"]["bordered_clusters"]["unstable_count"] == 0
        ),
        "reset_family_has_physical_coefficient_jet_variation": (
            reset["fiber_invariance_adjudication"]["actual_parametric_exterior_oracle_still_required"]
            is True
            and reset["radius_Cauchy_jet_witness"][
                "rank_inequality_after_any_one_dimensional_time_quotient"
            ]
            == 1
        ),
        "single_reset_representative_not_promoted": (
            reset["fiber_invariance_adjudication"]["single_reset_representative_promoted"]
            is False
        ),
        "actual_parametric_oracle_is_open": (
            parametric["adjudication"]["actual_parametric_N12_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "no_chord_selector_endpoint_action_term_scale_fit_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS",
        "status": "ANALYTIC_INFINITY_BRANCH_NOT_YET_RESET_CONNECTED_CHILD_EXTERIOR",
        "classification": (
            "THE_COMPLETE_ACTION_ANALYTIC_R4_TO_INFINITY_BRANCH_IS_A_VALID_"
            "CANDIDATE_INFINITE_FRIEDRICHS_EXTERIOR,_BUT_ITS_25_CENTER_MODES_"
            "AND_LOCAL_BRIOT_BOUQUET_EXISTENCE_DO_NOT_PROVE_A_TRAPPING_BASIN_"
            "OR_INTERSECTION_WITH_THE_SET_VALUED_AE2_RESET_IMAGE;_A_RESET_TO_"
            "ASYMPTOTIC_CONNECTION_OR_FINITE_CANONICAL_STOP_THEOREM_IS_STILL_"
            "REQUIRED"
        ),
        "available_asymptotic_data": {
            "complete_action_branch": "Z(epsilon)=epsilon*X5+epsilon^2*R(epsilon)",
            "epsilon": "R4^-2",
            "H4_limit": "H0=sqrt(kappa0/42)>0",
            "finite_mode_counts": {
                "stable": descriptor["descriptor"]["bordered_clusters"]["stable_count"],
                "center": descriptor["descriptor"]["bordered_clusters"]["center_count"],
                "unstable": descriptor["descriptor"]["bordered_clusters"]["unstable_count"],
            },
            "event_or_stop_inside_local_asymptotic_neighborhood": False,
        },
        "nonpromotion": {
            "no_unstable_linear_root_implies_open_nonlinear_basin": False,
            "one_Briot_Bouquet_branch_is_a_center_stable_manifold": False,
            "dimension_count_proves_reset_intersection": False,
            "one_stored_reset_state_is_on_asymptotic_branch": False,
            "common_scale_center_is_gauge": False,
        },
        "sufficient_connection_routes": {
            "validated_connection": (
                "CERTIFY_A_NONEMPTY_RESET_QUOTIENT_STRATUM_FORWARD_INTO_A_"
                "TRAPPING_ASYMPTOTIC_NEIGHBORHOOD_WITH_FIRST_GEOMETRY_JACOBI_"
                "FAMILY_AND_ALL_DOMAIN_MARGINS"
            ),
            "intersection_or_degree": (
                "PROVE_A_TRANSVERSE_INTERSECTION_OR_NONZERO_DEGREE_BETWEEN_"
                "THE_AE2_RESET_IMAGE_AND_THE_CONTROLLED_CENTER_STABLE_"
                "ASYMPTOTIC_MANIFOLD"
            ),
            "finite_alternative": (
                "CERTIFY_A_LATER_EVENT_OR_CANONICAL_EXIT_AND_USE_ITS_RETAINED_"
                "FINITE_ENDPOINT_RULE"
            ),
        },
        "adjudication": {
            "analytic_branch_is_current_exterior_oracle": False,
            "infinite_Friedrichs_route_invalid_in_principle": False,
            "finite_endpoint_route_invalid_in_principle": False,
            "retained_action_incompatibility_proved": False,
            "chord_03_has_finite_proof_obligation": False,
        },
        "exact_next_dependency": (
            "PROVE_OR_CERTIFY_A_NONEMPTY_EVENT_GENERATED_RESET_QUOTIENT_"
            "FAMILY_CONNECTS_TO_THE_ANALYTIC_ASYMPTOTIC_FRIEDRICHS_EXTERIOR_"
            "WITH_THE_REQUIRED_GEOMETRY_JETS_AND_DOMAIN_MARGINS,_OR_CERTIFY_"
            "THE_FIRST_LATER_EVENT_OR_CANONICAL_EXIT;_DO_NOT_PROMOTE_THE_LOCAL_"
            "INFINITY_BRANCH_BY_DIMENSION_COUNT_OR_NO_UNSTABLE_LINEAR_ROOTS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RESET_TO_MAXIMAL_EXTERIOR_CONNECTION_CURRENT_OWNER",
            "Gate8": "LOCKED",
            "asymptotic_branch": "DERIVED_LOCAL_NOT_RESET_CONNECTED",
            "maximal_child_exterior_oracle": "OPEN_CURRENT_OWNER",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
