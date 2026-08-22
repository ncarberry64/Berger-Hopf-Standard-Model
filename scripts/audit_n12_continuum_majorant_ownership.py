"""Audit ownership and effectiveness of the N12-to-infinity radii constants.

This consumes only canonical retained-action artifacts.  It does not estimate
missing constants by fitting finite probes and does not evaluate a radii
polynomial until every factor belongs to the same source-restricted,
positive-duration continuum map.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = Path(os.environ.get(
    "BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_RESULT",
    ".tmp_n12_continuum_majorant_ownership.json",
))


def _load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _maximum_sampled_n2_shell(
    payload: dict[str, Any], side: str,
) -> dict[str, float | int]:
    values = [
        (float(shell["mode_squared_weak_norm"]), int(row["N"]), int(shell["mode"]))
        for row in payload["evaluations"][side]
        for shell in row["omitted_shells"]
    ]
    value, order, mode = max(values)
    return {"value": value, "probe_order": order, "mode": mode}


def main() -> None:
    theorem = _load(
        "artifacts/n12_source_restricted_positive_duration/"
        "BHSM_N12_SOURCE_RESTRICTED_POSITIVE_DURATION_THEOREM.json"
    )
    n16 = _load(
        "artifacts/n16_coupled_momentum_response/"
        "BHSM_N16_COUPLED_MOMENTUM_RESPONSE_AUDIT.json"
    )
    source_n64 = _load(
        "artifacts/n12_dynamic_calderon_checkpoint/"
        "BHSM_N64_FULL_QVM_CONSTRAINT_TAIL_DIAGNOSTIC.json"
    )
    calderon_n12 = _load(
        "artifacts/n12_direct_checkpoint/"
        "BHSM_N12_EVENT_CHILD_CALDERON_N12_TO_N32_P96.json"
    )
    calderon_n48 = _load(
        "artifacts/n12_dynamic_calderon_checkpoint/"
        "BHSM_N48_SOURCE_CORRECTED_CALDERON_SYMBOL_AUDIT.json"
    )
    calderon_n64 = _load(
        "artifacts/n12_dynamic_calderon_checkpoint/"
        "BHSM_N64_SOURCE_CORRECTED_CALDERON_SYMBOL_AUDIT.json"
    )
    radii = _load(
        "artifacts/n12_direct_checkpoint/"
        "BHSM_N12_FULL_ACTION_RADII_CERTIFICATE.json"
    )
    neighborhood = _load(
        "artifacts/n12_direct_checkpoint/"
        "BHSM_N12_PHYSICAL_NEIGHBORHOOD_CERTIFICATE.json"
    )

    beta = float(theorem["action_owned_constants"]["principal_modulus_gap"])
    tail_inverse = float(
        theorem["action_owned_constants"]
        ["high_tail_inverse_bound_after_compact_cutoff"]
    )
    n12_gap = float(calderon_n12["N12_minimum_seven_by_seven_symbol_gap"])
    n48_gap = float(
        calderon_n48["evaluations"]["192"]["linear_candidate"]
        ["seven_by_seven_symbol_gap"]
    )
    n64_gap = float(
        calderon_n64["evaluations"]["96"]["linear_candidate"]
        ["seven_by_seven_symbol_gap"]
    )
    paired = n16["paired_exact_hard_momentum_response"]
    paired_soft = float(paired["paired_singular_values"][1])
    sampled_cr = {
        side: _maximum_sampled_n2_shell(source_n64, side)
        for side in ("event", "child")
    }

    constants = {
        "C_r": {
            "owned_law": "norm(r_n)_weak<=C_r*n^-2",
            "analytic_exponent_owned": True,
            "explicit_validated_upper_bound": None,
            "sampled_lower_bounds_on_any_valid_C_r": sampled_cr,
            "finite_samples_are_an_upper_bound": False,
            "status": "OPEN_NON_EFFECTIVE_CONSTANT",
        },
        "K": {
            "principal_high_tail_bound": tail_inverse,
            "principal_formula": "4/(sqrt(29)-5)",
            "principal_compact_cutoff_explicitly_enclosed": False,
            "finite_static_Calderon_inverse_diagnostics": {
                "N12": 1.0 / n12_gap,
                "N48_source_corrected_probe": 1.0 / n48_gap,
                "N64_source_corrected_probe": 1.0 / n64_gap,
            },
            "N16_instantaneous_paired_soft_response": paired_soft,
            "N16_instantaneous_paired_soft_reciprocal": 1.0 / paired_soft,
            "N16_map_is_the_positive_duration_continuum_observation_map": False,
            "finite_static_gaps_used_as_uniform_K": False,
            "explicit_positive_duration_continuum_inverse_bound": None,
            "status": "OPEN_NON_EFFECTIVE_COMPACTNESS_MODULUS",
        },
        "M2": {
            "finite_N12_local_Z2": float(
                radii["applied_Hessian_ball_bounds"]["total_Z2"]
            ),
            "finite_N12_ball_radius": float(radii["action_coordinate_ball_radius"]),
            "uniform_source_restricted_continuum_M2": None,
            "finite_N12_local_bound_promoted_as_continuum_bound": False,
            "status": "OPEN_CONTINUUM_MAJORANT",
        },
        "physical_neighborhood": {
            "finite_N12_action_radius": float(
                neighborhood["action_coordinate_ball_radius"]
            ),
            "finite_N12_eta_lower_bound": float(
                neighborhood["eta_neighborhood"]["ball_lower_bound"]
            ),
            "continuum_tail_transfer_radius": None,
            "finite_N12_root_ball_promoted_as_tail_neighborhood": False,
            "status": "OPEN_CONTINUUM_TRANSFER",
        },
    }

    effective_lemma = {
        "name": (
            "EFFECTIVE_SOURCE_RESTRICTED_POSITIVE_DURATION_"
            "COMPACTNESS_MODULUS"
        ),
        "required_construction": [
            "CHOOSE_A_FINITE_ACTION_OWNED_CUTOFF_M0",
            "ENCLOSE_THE_SOURCE_SELECTED_POSITIVE_DURATION_OBSERVATION_"
            "LOWER_BOUND_c_M0_ON_THE_EXISTING_NORMAL_QUOTIENT",
            "DERIVE_AN_EXPLICIT_ACTION_OWNED_TAIL_PERTURBATION_"
            "epsilon_obs(M0)_FROM_C_r_AND_THE_STRONG_GRAPH_PROPAGATOR_RATE",
            "PROVE_epsilon_obs(M0)<c_M0",
        ],
        "conclusion": (
            "c_infinity>=c_M0-epsilon_obs(M0)>0_AND_"
            "K<=1/(c_M0-epsilon_obs(M0))"
        ),
        "is_a_lemma_in_the_existing_closed_range_proof": True,
        "new_proxy_theorem": False,
        "missing_first_input": (
            "EXPLICIT_RATE_FROM_THE_INVERSE_SQUARE_SOURCE_RESTRICTED_"
            "S2_TAIL_TO_THE_POSITIVE_DURATION_OBSERVATION_OPERATOR"
        ),
    }

    radii_ready = all(
        constants[name][field] is not None
        for name, field in (
            ("C_r", "explicit_validated_upper_bound"),
            ("K", "explicit_positive_duration_continuum_inverse_bound"),
            ("M2", "uniform_source_restricted_continuum_M2"),
            ("physical_neighborhood", "continuum_tail_transfer_radius"),
        )
    )
    validation = {
        "principal_gap_reproduced": math.isclose(
            beta, math.sqrt(29.0) - 5.0, rel_tol=0.0, abs_tol=1.0e-15
        ),
        "conditional_high_tail_inverse_reproduced": math.isclose(
            tail_inverse, 4.0 / beta, rel_tol=0.0, abs_tol=1.0e-14
        ),
        "N16_hard_response_remains_closed": bool(
            paired["strict_exact_merit_reduction"]
        ),
        "N16_soft_channel_remains_category_2": bool(
            paired["soft_channel"]["classification"]
            == "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
            "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
        ),
        "no_finite_probe_fit_promoted": True,
        "incompatible_map_constants_not_multiplied": True,
        "nonlinear_continuum_radii_not_evaluated_with_missing_inputs": not radii_ready,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "N12_TO_INFINITY_RADII_CONSTANT_OWNERSHIP_AUDITED;_"
            "QUALITATIVE_CLOSED_RANGE_IS_NON_EFFECTIVE_AND_THE_FIRST_"
            "MISSING_OBJECT_IS_THE_POSITIVE_DURATION_OBSERVATION_"
            "COMPACTNESS_MODULUS"
        ),
        "constants": constants,
        "effective_compactness_lemma": effective_lemma,
        "radii_polynomial_rigorously_evaluable": radii_ready,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
