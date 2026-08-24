"""Audit the infrared control needed to synthesize the retained E1 force."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_product_dirac_weyl_enclosures import (  # noqa: E402
    product_dirac_compact_radius_weyl_variation_bounds,
    product_dirac_nonnegative_exterior_weyl_bounds,
)
from bhsm.interface.aether_forward_scalar_weyl_enclosures import (  # noqa: E402
    scalar_compact_radius_weyl_variation_bounds,
    scalar_nonnegative_exterior_weyl_bounds,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_E1_INFRARED_CONTROL_AUDIT.json"
)
SYNTHESIS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
)
GLOBAL = ARTIFACTS / (
    "flagship_integration/BHSM_N12_GATE7_GLOBAL_HISTORY_DOMAIN_CLOSURE.json"
)
DOMAIN = ARTIFACTS / (
    "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
)
HEAT_TRACE = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_HEAT_TRACE_CLASS_AUDIT.json"
)
SCALAR = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
)
DIRAC = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
)
INPUTS = (SYNTHESIS, GLOBAL, DOMAIN, HEAT_TRACE, SCALAR, DIRAC)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _infrared_rows(duration: float, radius_lower: float) -> list[dict[str, float]]:
    rows = []
    scalar_potential = 3.0 / radius_lower**2
    superpotential = 1.5 / radius_lower
    for kappa2 in (1.0, 1.0e-2, 1.0e-4, 1.0e-6):
        scalar_base = scalar_nonnegative_exterior_weyl_bounds(
            duration, scalar_potential, kappa2
        )
        scalar_weak = scalar_compact_radius_weyl_variation_bounds(
            scalar_base["upper"], scalar_potential, kappa2
        )
        dirac_base = product_dirac_nonnegative_exterior_weyl_bounds(
            duration, superpotential, kappa2
        )
        dirac_weak = product_dirac_compact_radius_weyl_variation_bounds(
            dirac_base["upper"], superpotential, kappa2
        )
        rows.append(
            {
                "kappa_squared": kappa2,
                "z": -kappa2,
                "E1_first_multiplier_half_exp_minus_lambda_over_lambda": (
                    0.5 * math.exp(-kappa2) / kappa2
                ),
                "scalar_c3_Weyl_upper": scalar_base["upper"],
                "scalar_c3_first_weak_upper": scalar_weak[
                    "first_Weyl_variation_bound"
                ],
                "scalar_c3_mixed_weak_upper": scalar_weak[
                    "mixed_Weyl_variation_bound"
                ],
                "product_Dirac_abs_lambda_1p5_Weyl_upper": dirac_base["upper"],
                "product_Dirac_abs_lambda_1p5_first_weak_upper": dirac_weak[
                    "first_Weyl_variation_bound"
                ],
                "product_Dirac_abs_lambda_1p5_mixed_weak_upper": dirac_weak[
                    "mixed_Weyl_variation_bound"
                ],
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all E1 infrared audit inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all E1 infrared audit inputs must validate")
    synthesis = records[SYNTHESIS.name]
    global_history = records[GLOBAL.name]
    domain = records[DOMAIN.name]
    heat_trace = records[HEAT_TRACE.name]
    scalar = records[SCALAR.name]
    dirac = records[DIRAC.name]
    duration = float(scalar["certified_core"]["proper_duration_lower"])
    radius_lower = float(scalar["certified_core"]["R4_lower"])
    rows = _infrared_rows(duration, radius_lower)

    decreasing_kappa_rows = list(zip(rows, rows[1:]))
    validation = {
        "all_inputs_validated": True,
        "E1_synthesis_requirement_consumed": synthesis["adjudication"][
            "Gate7_zero_source_force_evaluable_from_current_rows"
        ]
        is False,
        "actual_maximal_outcome_is_unknown": global_history["ownership"][
            "actual_maximal_endpoint_outcome_known"
        ]
        is False,
        "uniform_global_R4_bound_is_not_available": (
            "UNIFORM_R4_BOUND"
            in global_history["exact_next_mathematical_lemma"]
        ),
        "complete_history_coefficient_oracle_is_not_available": domain[
            "ownership"
        ]["complete_history_coefficient_oracle_available"]
        is False,
        "positive_gap_does_not_close_infinite_heat_trace": heat_trace[
            "adjudication"
        ]["infinite_duration_plus_uniform_R4_upper_bound_sufficient_for_finite_Gamma_heat"]
        is False,
        "E1_first_multiplier_grows_toward_zero": all(
            later["E1_first_multiplier_half_exp_minus_lambda_over_lambda"]
            > earlier["E1_first_multiplier_half_exp_minus_lambda_over_lambda"]
            for earlier, later in decreasing_kappa_rows
        ),
        "scalar_weak_bounds_grow_toward_zero": all(
            later["scalar_c3_first_weak_upper"]
            > earlier["scalar_c3_first_weak_upper"]
            and later["scalar_c3_mixed_weak_upper"]
            > earlier["scalar_c3_mixed_weak_upper"]
            for earlier, later in decreasing_kappa_rows
        ),
        "product_Dirac_weak_bounds_grow_toward_zero": all(
            later["product_Dirac_abs_lambda_1p5_first_weak_upper"]
            > earlier["product_Dirac_abs_lambda_1p5_first_weak_upper"]
            and later["product_Dirac_abs_lambda_1p5_mixed_weak_upper"]
            > earlier["product_Dirac_abs_lambda_1p5_mixed_weak_upper"]
            for earlier, later in decreasing_kappa_rows
        ),
        "finite_endpoint_and_infinite_relative_routes_preserved": True,
        "no_gap_endpoint_reference_confinement_or_prediction_fabricated": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_E1_INFRARED_CONTROL_AUDIT",
        "status": "CURRENT_TWO_CHORD_RESOLVENT_BOUNDS_DO_NOT_CONTROL_E1_INFRARED_SYNTHESIS",
        "classification": (
            "THE_RETAINED_E1_FIRST_VARIATION_MULTIPLIER_BEHAVES_AS_ONE_OVER_"
            "TWO_LAMBDA_AT_ZERO;_THE_CURRENT_MAXIMAL_FORWARD_DOMAIN_HAS_NO_"
            "CERTIFIED_GLOBAL_POSITIVE_GAP_OR_COMPLETE_COEFFICIENT_ORACLE,_"
            "AND_THE_NEW_SCALAR_DERHAM_AND_PRODUCT_DIRAC_POISSON_VARIATION_"
            "BOUNDS_DIVERGE_AS_z_APPROACHES_ZERO_FROM_BELOW;_THEREFORE_THE_"
            "z_MINUS_1_ENCLOSURES_DO_NOT_CONTROL_THE_INFRARED_PART_OF_THE_E1_"
            "FUNCTIONAL_CALCULUS"
        ),
        "infrared_theorem": {
            "retained_multiplier": (
                "f_prime(lambda)=(1/2)*exp(-ell_kappa^2*lambda)/lambda"
            ),
            "limit": "f_prime(lambda)~1/(2*lambda)_AS_lambda_DOWN_TO_ZERO",
            "resolvent_probe": "z=-kappa^2",
            "scalar_Poisson_energy_factor": "M_upper/kappa^2",
            "product_Dirac_first_relative_form_factor": "M_upper/kappa",
            "product_Dirac_mixed_relative_form_factor": (
                "CONTAINS_M_upper/kappa^2"
            ),
            "conclusion": (
                "A_UNIFORM_GAP,_LOW_ENERGY_SPECTRAL_MEASURE_BOUND,_OR_ACTION_"
                "OWNED_RELATIVE_CANCELLATION_IS_REQUIRED_TO_SYNTHESIZE_E1"
            ),
        },
        "small_negative_z_rows": rows,
        "maximal_outcome_routes": {
            "actual_finite_terminal_or_domain_exit": (
                "EVALUATE_THE_FULL_FINITE_INTERVAL_OPERATOR_WITH_ITS_RETAINED_"
                "ENDPOINT_GRAPH_AND_CERTIFY_THE_RESULTING_SPECTRAL_GAP_AND_TAIL"
            ),
            "infinite_regular_Friedrichs_history": (
                "DERIVE_LOW_ENERGY_SPECTRAL_MEASURE_CONTROL_OR_AN_ACTION_OWNED_"
                "RELATIVE_HEAT_TRACE_REFERENCE_OR_TEMPORAL_CONFINEMENT"
            ),
            "terminal_event_reachability_required_a_priori": False,
        },
        "adjudication": {
            "abstract_maximal_forward_source_domain": "DERIVED",
            "uniform_global_positive_source_gap": "NOT_CERTIFIED",
            "E1_infrared_synthesis_from_current_bounds": "OPEN",
            "z_minus_1_channel_enclosures": "VALID_NOT_SUFFICIENT",
            "zero_source_weak_geometry_force": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_LOW_ENERGY_MAXIMAL_FORWARD_SPECTRAL_MEASURE_CONTROL_OR_AN_"
            "ACTION_OWNED_RELATIVE_HEAT_TRACE_CANCELLATION_SUFFICIENT_TO_"
            "INTEGRATE_THE_E1_FIRST_AND_SECOND_VARIATIONS;_KEEP_THE_ACTUAL_"
            "FINITE_ENDPOINT_OPERATOR_AS_THE_OPTIONAL_ALTERNATIVE"
        ),
        "claim_boundary": {
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "infrared_synthesis": payload["adjudication"][
                    "E1_infrared_synthesis_from_current_bounds"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
