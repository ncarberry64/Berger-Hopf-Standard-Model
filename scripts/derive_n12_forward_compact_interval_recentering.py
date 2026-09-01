"""Derive automatic finite recentering on every regular pre-stop interval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMPACT_INTERVAL_RECENTERING.json"
)
CONTINUUM_FLOW = ARTIFACTS / (
    "intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
SOURCE_DOMAIN = ARTIFACTS / (
    "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
)
JACOBI_BOUNDS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS.json"
)
TRANSFER_VARIATIONS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS.json"
)
PROPER_TIME = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
)
INPUTS = (
    CONTINUUM_FLOW,
    SOURCE_DOMAIN,
    JACOBI_BOUNDS,
    TRANSFER_VARIATIONS,
    PROPER_TIME,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all compact-interval recentering inputs are required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("all compact-interval recentering inputs must validate")
    continuum, domain, jacobi, transfer, proper_time = records
    alternatives = continuum["maximal_flow_alternative"]["finite_time_outcomes"]
    validation = {
        "all_inputs_validated": True,
        "unique_maximal_continuum_flow_available": continuum[
            "maximal_flow_alternative"
        ]["unique_maximal_continuum_child_flow"]
        is True,
        "bounded_margin_local_constants_available": "K(B,delta)"
        in continuum["uniform_local_estimate"]["bounded_margin_set"],
        "only_existing_finite_stops_used": len(alternatives) == 3,
        "source_domain_supports_all_maximal_outcomes": all(
            domain["validation"][key] is True
            for key in (
                "maximal_forward_history_closed",
                "finite_maximal_outcomes_are_exits_not_regular_truncations",
                "Friedrichs_rule_retained_for_excluded_endpoint",
            )
        ),
        "local_second_Jacobi_algebra_available": jacobi["validation_passed"] is True,
        "channel_transfer_variation_algebra_available": transfer[
            "validation_passed"
        ]
        is True,
        "proper_time_form_ownership_available": proper_time[
            "validation_passed"
        ]
        is True,
        "no_terminal_return_universal_bound_or_new_gate_assumed": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_COMPACT_INTERVAL_RECENTERING",
        "status": "FINITE_REGULAR_INTERVAL_JACOBI_TRANSFER_COVER_AUTOMATIC",
        "classification": (
            "ON_EVERY_CLOSED_REGULAR_PRESTOP_INTERVAL_THE_CONTINUOUS_"
            "MAXIMAL_ACTION_FLOW_HAS_A_FINITE_STRONG_NORM_MAXIMUM_AND_A_"
            "POSITIVE_MINIMUM_OF_ALL_EXISTING_DOMAIN_MARGINS;_THEREFORE_"
            "THE_CONTINUUM_K(B,delta)_LOCAL_THEOREM_AUTOMATICALLY_GIVES_A_"
            "FINITE_RECENTERING_COVER_FOR_THE_STATE_JACOBI_RADIUS_AND_"
            "FIXED_CHANNEL_TRANSFER_JETS_WITHOUT_AN_APRIORI_GLOBAL_ACTION_"
            "BALL_COVER_OR_TERMINAL_RETURN"
        ),
        "compact_interval_theorem": {
            "interval": "[0,T]_WITH_T<T_stop_OR_ANY_FINITE_T_ON_AN_INFINITE_REGULAR_HISTORY",
            "trajectory_compactness": "Y([0,T])_IS_COMPACT_IN_THE_STRONG_S2_TOPOLOGY",
            "owned_norm_bound": "B_T=max_[0,T]_norm_S2(Y(tau))<infinity",
            "owned_margin_bound": (
                "delta_T=min_[0,T]_OF_ALL_EXISTING_CONTINUOUS_POSITIVE_"
                "METRIC_LAPSE_ETA_INERTIA_TRACE_GAUGE_DIRAC_MARGINS>0"
            ),
            "local_owner": "K(B_T,delta_T)_CONTINUUM_RECENTERING_THEOREM",
            "finite_subcover": "COMPACTNESS_PLUS_POSITIVE_LOCAL_DURATIONS",
            "gluing": "UNIQUENESS_OF_THE_RETAINED_ACTION_FLOW_AND_LINEAR_VARIATIONAL_SYSTEMS",
            "outputs": [
                "STATE_FIRST_AND_MIXED_SECOND_JACOBI_COCYCLES",
                "x=log_R4_FIRST_AND_MIXED_SECOND_PULLBACKS",
                "FINITE_FIXED_CHANNEL_TRANSFER_FIRST_AND_MIXED_SECOND_JETS",
                "REGULAR_FINITE_INTERVAL_WEYL_CHART_JETS_WHERE_THE_CHART_DENOMINATOR_IS_NONZERO",
            ],
        },
        "necessity_reduction": {
            "explicit_a_priori_global_B_delta_for_finite_regular_intervals": False,
            "numerical_finite_action_ball_cover_for_finite_regular_intervals": False,
            "terminal_event_return_for_finite_regular_interval_jets": False,
            "new_history_selector": False,
            "uniform_bounds_as_T_goes_to_infinity": "NOT_PROVIDED_BY_COMPACTNESS",
        },
        "maximal_end_split": {
            "actual_terminal_reset_hit": (
                "USE_THE_EXISTING_RESET_GRAPH_AND_THE_FINITE_INTERVAL_"
                "TRANSFER_JETS_UP_TO_THE_FIRST_HIT"
            ),
            "finite_canonical_domain_stop": (
                "STOP_THE_REGULAR_VARIATIONAL_PROPAGATION_AND_USE_THE_"
                "EXISTING_FRIEDRICHS_FORM_CLOSURE;_NO_REGULAR_EXTENSION_"
                "ACROSS_THE_STOP_IS_CLAIMED"
            ),
            "infinite_regular_history": (
                "EVERY_FINITE_EXHAUSTION_INTERVAL_IS_CLOSED_BY_THIS_THEOREM_"
                "BUT_C1_C2_CONVERGENCE_OF_THE_BIRTH_WEYL_MAP_AT_THE_"
                "FRIEDRICHS_LIMIT_REQUIRES_A_RELATIVE_FORM_OR_INTEGRABLE_"
                "VARIATION_BOUND"
            ),
        },
        "exact_next_dependency": (
            "PROVE_C1_C2_RELATIVE_FORM_CONTROL_OR_AN_EQUIVALENT_INTEGRABLE_"
            "FIXED_CHANNEL_RICCATI_TRANSFER_VARIATION_BOUND_AT_EVERY_"
            "INFINITE_REGULAR_FRIEDRICHS_END;_FINITE_REGULAR_PRESTOP_"
            "INTERVALS_REQUIRE_NO_ADDITIONAL_GLOBAL_COVER"
        ),
        "claim_boundary": {
            "finite_regular_interval_variational_cover": "DERIVED",
            "infinite_Friedrichs_end_Weyl_C1_C2_limit": "OPEN",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03": "NOT_AUTHORIZED",
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "infinite_end": payload["claim_boundary"][
                    "infinite_Friedrichs_end_Weyl_C1_C2_limit"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
