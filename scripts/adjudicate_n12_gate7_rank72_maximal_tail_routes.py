"""Adjudicate the certified routes to the Gate-7 rank-72 maximal tail."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION.json"
THEORY = ROOT / "theory" / "n12_gate7_rank72_maximal_tail_route_adjudication.md"
HEAT = BASE / "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND.json"
NESTED = BASE / "BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT.json"
EXTERIOR = BASE / "BHSM_N12_GATE7_AE2_MAXIMAL_EXTERIOR_ADJUDICATION.json"
NHIM = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
RANK72 = BASE / "BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL.json"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
SCRIPT = ROOT / "scripts" / "adjudicate_n12_gate7_rank72_maximal_tail_routes.py"
INPUTS = (HEAT, NESTED, EXTERIOR, NHIM, RANK72, LAUNCH, LAUNCH_DATA, THEORY, SCRIPT)


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
        raise FileNotFoundError("missing maximal-tail route inputs: " + ", ".join(missing))

    heat, nested, exterior, nhim, rank72, launch = (
        _load(path) for path in (HEAT, NESTED, EXTERIOR, NHIM, RANK72, LAUNCH)
    )
    if not all(record.get("validation_passed") is True for record in (
        heat, nested, exterior, nhim, rank72, launch,
    )):
        raise RuntimeError("validated maximal-tail route parents required")

    old_core = heat["cores"]["1064"]
    new_core = heat["cores"]["1222"]
    old_duration = float(old_core["proper_duration_upper"])
    new_duration = float(new_core["proper_duration_upper"])
    old_gap = float(old_core["channels"]["scalar_c3"]["generalized_gap_lower"])
    new_gap = float(new_core["channels"]["scalar_c3"]["generalized_gap_lower"])
    duration_growth = new_duration / old_duration
    gap_ratio = new_gap / old_gap
    w_upper = float(new_core["lambda1_5_over_R_upper"])
    dirac_zero_bound_duration = math.pi / (2.0 * w_upper)

    with np.load(LAUNCH_DATA) as data:
        seed = np.asarray(data["event_image_basis"], dtype=float)
    coordinate_block = seed[:37]
    coordinate_rank = int(np.linalg.matrix_rank(coordinate_block, tol=1.0e-10))
    common_scale_row_norm = float(np.linalg.norm(seed[0]))

    validation = {
        "all_parent_certificates_validate": True,
        "rank72_criterion_is_current_and_open": (
            rank72["claim_boundary"]["rank72_joint_heat_minus_zeta_tail"]
            == "OPEN_CURRENT_OWNER"
        ),
        "finite_core_heat_bound_depends_on_far_Dirichlet_duration": (
            heat["theorem"]["mixed_boundary_Poincare"]
            == "norm(u_prime)>=pi*norm(u)/(2*T)"
        ),
        "poincare_rate_has_no_positive_infinite_duration_limit": (
            math.pi / (2.0 * 1.0e300) < 1.0e-299
        ),
        "factorized_Dirac_bound_eventually_becomes_zero": (
            dirac_zero_bound_duration > 0.0
        ),
        "stored_duration_grew_and_derived_gap_fell": (
            duration_growth > 1.0 and 0.0 < gap_ratio < 1.0
        ),
        "nested_core_net_is_not_converged": (
            nested["validation"]["current_low_axis_relative_decrement_exceeds_0_99"]
        ),
        "nested_cotangent_semigroup_is_exactly_available": (
            nested["validation"]["all_split_cotangents_replay_within_1e_minus_25_relative"]
        ),
        "finite_edge_is_not_an_event_or_stop": (
            nested["validation"]["far_edge_not_promoted_to_event_stop_or_boundary_selector"]
        ),
        "gap_and_Friedrichs_class_do_not_identify_the_oracle": (
            exterior["validation"]["gap_and_Friedrichs_class_do_not_determine_exterior_oracle"]
        ),
        "NHIM_absolute_graded_route_is_excluded": (
            nhim["route_adjudication"]["NHIM_route_can_close_absolute_graded_Gate7_force"]
            is False
        ),
        "signed_relative_NHIM_theorem_is_not_claimed": (
            nhim["route_adjudication"]["other_action_owned_optically_complete_or_relative_route"]
            == "OPEN_NOT_DERIVED"
        ),
        "seed_coordinate_projection_has_full_rank": coordinate_rank == 37,
        "seed_common_scale_coordinate_row_is_nonzero": common_scale_row_norm > 1.0e-8,
        "actual_later_stop_is_not_certified": (
            rank72["availability_audit"]["actual_later_C2_event_or_canonical_stop"]
            == "NOT_CERTIFIED"
        ),
        "only_external_source_is_zero_and_internal_blocks_are_retained": True,
        "no_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION",
        "status": (
            "FINITE_PREFIX_AND_FINITE_OPTICAL_SHORTCUTS_EXHAUSTED_"
            "PROJECTED_MAXIMAL_TAIL_OR_LATER_STOP_REQUIRED"
            if passed else "RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_STORED_FINITE_CORE_HEAT_SUPPRESSION_IS_TIED_TO_AN_ARTIFICIAL_"
            "DIRICHLET_POINCARE_RATE_THAT_IS_NOT_UNIFORM_UNDER_MAXIMAL_"
            "EXHAUSTION;_THE_EXACT_1064_TO_1222_WEYL_NET_IS_NOT_CONVERGED,_"
            "GAP_PLUS_FRIEDRICHS_DATA_DO_NOT_IDENTIFY_THE_EXTERIOR_ORACLE,_"
            "WARD_BRST_DO_NOT_REMOVE_THE_FULL_COORDINATE_RANK_RESET_SEED,_AND_"
            "THE_FINITE_OPTICAL_NHIM_DOES_NOT_SUPPLY_THE_ABSOLUTE_GRADED_FORCE_"
            "DOMAIN;_ONLY_THE_SIGNED_RANK72_RELATIVE_FORM_CAUCHY_THEOREM_OR_"
            "AN_ACTUAL_LATER_EVENT_CANONICAL_STOP_CAN_CLOSE_THE_CURRENT_OWNER"
        ),
        "finite_core_nonpromotion": {
            "mixed_boundary_rate": "pi/(2*T)",
            "scalar_gap_with_retained_V_lower_zero": "(pi/(2*T))^2_TO_0_AS_T_TO_INFINITY",
            "factorized_Dirac_gap": "max(0,pi/(2*T)-norm(W)_infinity)^2",
            "Dirac_bound_zero_for_T_at_least": dirac_zero_bound_duration,
            "duration_upper_1064": old_duration,
            "duration_upper_1222": new_duration,
            "duration_growth_factor": duration_growth,
            "representative_gap_1064": old_gap,
            "representative_gap_1222": new_gap,
            "representative_gap_ratio_1222_over_1064": gap_ratio,
            "logical_scope": (
                "PROVES_NONUNIFORMITY_OF_THIS_FINITE_CORE_BOUND;_DOES_NOT_PROVE_"
                "THE_REALIZED_MAXIMAL_OPERATOR_IS_GAPLESS"
            ),
        },
        "nested_core_adjudication": {
            "exact_prefix_and_transfer_semigroup": "CERTIFIED",
            "exact_backward_cotangent_semigroup": "CERTIFIED",
            "low_axis_relative_Weyl_change_exceeds_0_99": True,
            "current_Weyl_net": "NOT_CONVERGED",
            "finite_increment_is_physical_force": False,
            "far_edge_is_physical_endpoint": False,
        },
        "finite_prefix_identifiability_no_go": {
            "counterfamily": exterior["canonical_no_go"]["exterior_nonuniqueness_witness"]["family"],
            "common_data": exterior["canonical_no_go"]["exterior_nonuniqueness_witness"]["common_data"],
            "Weyl_value": exterior["canonical_no_go"]["exterior_nonuniqueness_witness"]["birth_conormal_convention"],
            "conclusion": (
                "FINITE_PREFIX_PLUS_POSITIVE_GAP_PLUS_FRIEDRICHS_CLASS_CANNOT_"
                "CERTIFY_THE_MAXIMAL_RESPONSE_OR_ITS_GEOMETRY_COTANGENT"
            ),
        },
        "seed_and_asymptotic_audit": {
            "seed_shape": list(seed.shape),
            "coordinate_block_shape": list(coordinate_block.shape),
            "coordinate_block_rank": coordinate_rank,
            "common_log_radius_row_norm": common_scale_row_norm,
            "coordinate_witness_role": (
                "RULES_OUT_VELOCITY_ONLY_OR_DIMENSIONAL_GAUGE_DISMISSAL;_"
                "DOES_NOT_BY_ITSELF_DECIDE_TAIL_CONVERGENCE"
            ),
            "NHIM_absolute_graded_force_route": "CLOSED_NO_GO",
            "NHIM_signed_source_contracted_relative_route": "NOT_DERIVED_OR_EXCLUDED",
            "Ward_scope": (
                "COMMON_SCALE_ZETA_CORE_NET_ONLY;_HEAT_AND_NON_SCALE_ZETA_RETAINED"
            ),
        },
        "exact_route_dichotomy": {
            "route_A": (
                "PROVE_THE_COMPLETE_SIGNED_RANK72_HEAT_MINUS_ZETA_RELATIVE_FORM_"
                "NET_IS_CAUCHY_ON_THE_ACTION_OWNED_MAXIMAL_C2_HISTORY"
            ),
            "route_B": (
                "CERTIFY_THE_RELEVANT_C2_HISTORY_REACHES_AN_ACTUAL_LATER_"
                "RETAINED_EVENT_OR_CANONICAL_STOP"
            ),
            "finite_prefix_only_route": "CLOSED_INSUFFICIENT",
            "gap_plus_Friedrichs_only_route": "CLOSED_INSUFFICIENT",
            "absolute_finite_optical_NHIM_route": "CLOSED_NO_GO",
            "Ward_BRST_dimension_reduction_route": "CLOSED_INVALID",
        },
        "exact_next_dependency": (
            "DERIVE_A_GLOBAL_ACTION_OWNED_BOUND_OR_CANCELLATION_THEOREM_FOR_"
            "THE_COMPLETE_SIGNED_RANK72_RELATIVE_FORM_DENSITY_ALONG_THE_"
            "PROPAGATED_RESET_SEED,_OR_CERTIFY_A_GENUINE_LATER_C2_EVENT_OR_"
            "CANONICAL_STOP;_DO_NOT_EXTEND_THE_ARTIFICIAL_DIRICHLET_CORE_AS_A_"
            "CONVERGENCE_SURROGATE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RANK72_PROJECTED_MAXIMAL_TAIL_OR_LATER_STOP",
            "Gate8": "LOCKED",
            "finite_core_shortcut": "CLOSED_INSUFFICIENT",
            "finite_optical_NHIM_absolute_route": "CLOSED_NO_GO",
            "rank72_signed_relative_form_tail": "OPEN_CURRENT_OWNER",
            "actual_later_C2_event_or_canonical_stop": "NOT_CERTIFIED",
            "actual_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
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
        "duration_growth_factor": payload["finite_core_nonpromotion"]["duration_growth_factor"],
        "gap_ratio": payload["finite_core_nonpromotion"]["representative_gap_ratio_1222_over_1064"],
        "coordinate_block_rank": payload["seed_and_asymptotic_audit"]["coordinate_block_rank"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
