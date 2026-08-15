"""Audit whether direct repetition can credibly close the N=3 SBP saddle."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

VERSION = "v17.40"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_DIRECT_REPETITION_CONTRACTION_ADEQUACY_AUDIT"
FULL_BHSM_COMPLETE = False
CLOSURE_TOLERANCE = 1e-6

STATE_SPECS = (
    (
        "v17.31",
        "BHSM_aether_n3_fresh_sbp_third_v0_priority_v17_31.json",
        "fresh_sbp_third_v0_priority",
        "selected_v0_priority_maximin",
    ),
    (
        "v17.33",
        "BHSM_aether_n3_fresh_sbp_second_period_priority_v17_33.json",
        "fresh_sbp_second_period_priority",
        "selected_period_priority_maximin",
    ),
    (
        "v17.34",
        "BHSM_aether_n3_fresh_sbp_fourth_v0_priority_v17_34.json",
        "fresh_sbp_fourth_v0_priority",
        "selected_v0_priority_maximin",
    ),
    (
        "v17.36",
        "BHSM_aether_n3_fresh_sbp_fifth_v0_priority_v17_36.json",
        "fresh_sbp_fifth_v0_priority",
        "selected_v0_priority_maximin",
    ),
    (
        "v17.37",
        "BHSM_aether_n3_fresh_sbp_third_period_priority_v17_37.json",
        "fresh_sbp_third_period_priority",
        "selected_period_priority_maximin",
    ),
    (
        "v17.38",
        "BHSM_aether_n3_fresh_sbp_sixth_v0_priority_v17_38.json",
        "fresh_sbp_sixth_v0_priority",
        "selected_v0_priority_maximin",
    ),
    (
        "v17.39",
        "BHSM_aether_n3_fresh_sbp_seventh_v0_priority_v17_39.json",
        "fresh_sbp_seventh_v0_priority",
        "selected_v0_priority_maximin",
    ),
)


def _load_states() -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    for version, filename, section, selection in STATE_SPECS:
        payload = json.loads((Path("artifacts") / filename).read_text(encoding="utf-8"))
        selected = payload[section][selection]
        states.append(
            {
                "version": version,
                "validation_passed": bool(payload["validation_passed"]),
                "metrics": selected["metrics"],
                "minimum_fractional_progress": selected[
                    "minimum_fractional_progress"
                ],
                "limiting_owner": selected["limiting_owner"],
            }
        )
    return states


def contraction_adequacy_audit() -> dict[str, Any]:
    states = _load_states()
    owners = tuple(states[0]["metrics"])
    promoted_passes = len(states) - 1
    contraction: dict[str, Any] = {}
    for owner in owners:
        initial = float(states[0]["metrics"][owner])
        final = float(states[-1]["metrics"][owner])
        per_pass = (final / initial) ** (1.0 / promoted_passes)
        projected = math.inf
        if 0 < per_pass < 1 and final > CLOSURE_TOLERANCE:
            projected = math.ceil(
                math.log(CLOSURE_TOLERANCE / final) / math.log(per_pass)
            )
        contraction[owner] = {
            "initial": initial,
            "final": final,
            "cumulative_fractional_reduction": 1.0 - final / initial,
            "observed_geometric_ratio_per_promoted_pass": per_pass,
            "constant_rate_extrapolated_additional_passes_to_1e-6": projected,
        }
    stepwise_strict = all(
        all(
            float(states[index + 1]["metrics"][owner])
            < float(states[index]["metrics"][owner])
            for owner in owners
        )
        for index in range(promoted_passes)
    )
    bottleneck_owner = max(
        contraction,
        key=lambda owner: contraction[owner][
            "constant_rate_extrapolated_additional_passes_to_1e-6"
        ],
    )
    return {
        "states": states,
        "promoted_passes": promoted_passes,
        "closure_tolerance": CLOSURE_TOLERANCE,
        "all_six_metrics_strictly_decrease_at_every_pass": stepwise_strict,
        "contraction_by_owner": contraction,
        "constant_rate_extrapolation_bottleneck": bottleneck_owner,
        "constant_rate_extrapolated_additional_passes": contraction[
            bottleneck_owner
        ]["constant_rate_extrapolated_additional_passes_to_1e-6"],
        "classification_scope": (
            "EMPIRICAL_ADEQUACY_OF_DIRECT_REPETITION_NOT_A_MATHEMATICAL_NO_GO"
        ),
        "interpretation": (
            "DIRECT_REPETITION_IS_STRICTLY_DESCENDING_BUT_NOT_A_CREDIBLE_"
            "COMPLETION_PATH_AT_THE_OBSERVED_CONTRACTION_RATE"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = contraction_adequacy_audit()
    validation = {
        "validated_state_chain_loaded": all(
            state["validation_passed"] for state in result["states"]
        ),
        "seven_authoritative_states_compared": len(result["states"]) == 7,
        "six_promoted_passes_measured": result["promoted_passes"] == 6,
        "all_six_metrics_strictly_descend": result[
            "all_six_metrics_strictly_decrease_at_every_pass"
        ],
        "final_residual_reproduced": math.isclose(
            result["contraction_by_owner"]["complete"]["final"],
            0.95790800098592,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "period_is_extrapolation_bottleneck": (
            result["constant_rate_extrapolation_bottleneck"] == "period"
        ),
        "direct_repetition_exceeds_one_thousand_projected_passes": (
            result["constant_rate_extrapolated_additional_passes"] > 1000
        ),
        "no_mathematical_no_go_claimed": (
            result["classification_scope"]
            == "EMPIRICAL_ADEQUACY_OF_DIRECT_REPETITION_NOT_A_MATHEMATICAL_NO_GO"
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_fresh_sbp_contraction_adequacy_audit_v17_40",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_contraction_adequacy_audit": result,
        "status": "RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained": (
            "OBSERVED_CONTRACTION_OF_THE_UNCHANGED_SIX_OWNER_N3_PHYSICAL_SYSTEM"
        ),
        "dependency_advanced": (
            "REASSESS_THE_N3_CORRECTION_BEFORE_FURTHER_DIRECT_REPETITION"
        ),
        "active_calculation": (
            "DERIVE_A_SAME_ACTION_COUPLED_PERIOD_V0_CORRECTION_WITH_ORIGINAL_"
            "SIX_OWNER_ACCEPTANCE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fresh_sbp_contraction_adequacy_audit_v17_40.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "contraction_adequacy_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
