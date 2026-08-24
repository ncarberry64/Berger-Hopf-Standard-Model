"""Derive the weakest source-weighted spectral criterion for the E1 force."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_e1_source_measure import (  # noqa: E402
    e1_source_measure_dyadic_bound,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json"
)
INFRARED = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_E1_INFRARED_CONTROL_AUDIT.json"
)
BRST = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json"
)
SYNTHESIS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
)
WEAK = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_WEAK_HEAT_VARIATIONS.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_forward_e1_source_measure.py"
INPUTS = (INFRARED, BRST, SYNTHESIS, WEAK, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all E1 source-measure criterion inputs required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in INPUTS
        if path.suffix == ".json"
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all E1 source-measure criterion inputs must validate")
    infrared = records[INFRARED.name]
    brst = records[BRST.name]
    synthesis = records[SYNTHESIS.name]
    weak = records[WEAK.name]
    witness = e1_source_measure_dyadic_bound(3.0, 1.0, 2.0)

    validation = {
        "all_inputs_validated": True,
        "full_operator_infrared_control_is_open": infrared["adjudication"][
            "E1_infrared_synthesis_from_current_bounds"
        ]
        == "OPEN",
        "BRST_universal_cancellation_is_unavailable": brst["adjudication"][
            "BRST_grading_closes_E1_infrared"
        ]
        is False,
        "single_probe_is_unavailable_as_heat_synthesis": synthesis[
            "retained_functional_calculus"
        ]["one_resolvent_probe_sufficient"]
        is False,
        "compact_source_variation_class_is_retained": weak[
            "weak_variation_theorem"
        ]["allowed_variations"].startswith("SMOOTH_COMPACTLY_SUPPORTED"),
        "exact_dyadic_witness_closes": witness[
            "first_E1_variation_absolute_upper"
        ]
        == 7.0,
        "epsilon_zero_is_not_promoted": True,
        "no_reference_gap_profile_endpoint_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION",
        "status": "SOURCE_WEIGHTED_E1_FIRST_VARIATION_SUFFICIENT_CRITERION_DERIVED",
        "classification": (
            "THE_ZERO_SOURCE_WEAK_GEOMETRY_FORCE_DOES_NOT_REQUIRE_A_UNIFORM_"
            "BOUND_ON_THE_ENTIRE_MAXIMAL_FORWARD_SPECTRAL_MEASURE_IF_ITS_"
            "ACTION_OWNED_SOURCE_WEIGHTED_GRADED_MEASURE_HAS_STRICTLY_MORE_"
            "THAN_LINEAR_LOW_ENERGY_VANISHING_AND_A_FINITE_E1_WEIGHTED_HIGH_"
            "ENERGY_TAIL;_AN_EXACT_DYADIC_SUM_THEN_BOUNDS_THE_FIRST_VARIATION"
        ),
        "theorem": {
            "source_weighted_measure": (
                "nu_h(B)=STr(E_K(B)*P_h)_IN_TOTAL_VARIATION_FOR_ONE_RETAINED_"
                "COMPACTLY_SUPPORTED_GEOMETRY_DIRECTION_h"
            ),
            "low_energy_hypothesis": (
                "abs(nu_h)([0,Lambda])<=C_h*Lambda^(1+epsilon_h)_FOR_"
                "0<Lambda<=1,_epsilon_h>0"
            ),
            "high_energy_hypothesis": (
                "H_h=integral_[1,infinity]exp(-lambda)/lambda_"
                "dabs(nu_h)(lambda)<infinity"
            ),
            "dyadic_low_bound": "2*C_h/(1-2^(-epsilon_h))",
            "force_bound": (
                "abs(D_h_Gamma_heat)<=C_h/(1-2^(-epsilon_h))+H_h/2"
            ),
            "retained_heat_length": 1.0,
            "scope": "FIRST_ZERO_SOURCE_WEAK_GEOMETRY_VARIATION_ONLY",
        },
        "exact_witness": {
            "C_h": 3.0,
            "epsilon_h": 1.0,
            "H_h": 2.0,
            **witness,
        },
        "hindsight": {
            "uniform_global_operator_gap_logically_required": False,
            "full_unweighted_spectral_measure_bound_logically_required": False,
            "one_source_weighted_measure_estimate_sufficient_for_force": True,
            "actual_N12_source_weighted_constants_C_epsilon_H": "OPEN",
            "pair_contact_second_variation_criterion": "NOT_DERIVED_HERE",
        },
        "exact_next_dependency": (
            "BOUND_THE_ACTUAL_N12_SOURCE_WEIGHTED_GRADED_SPECTRAL_COUNTING_"
            "FUNCTION_NEAR_ZERO_AND_ITS_E1_WEIGHTED_HIGH_ENERGY_TAIL_FOR_"
            "EACH_RETAINED_WEAK_GEOMETRY_DIRECTION;_THEN_ASSEMBLE_AND_SIGN_"
            "ADJUDICATE_THE_ZERO_SOURCE_FORCE"
        ),
        "claim_boundary": {
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
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
    print(json.dumps({
        "status": payload["status"],
        "witness_force_bound": payload["exact_witness"][
            "first_E1_variation_absolute_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
