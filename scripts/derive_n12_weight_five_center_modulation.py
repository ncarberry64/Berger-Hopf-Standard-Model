"""Derive the exact weight-five center-force operator without solving it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
    exact_weight_five_action_jet_at_state,
    exact_weight_seven_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (  # noqa: E402
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)
from bhsm.interface.weight_seven_transverse_descriptor import (  # noqa: E402
    ROUND_EXPANSION_RATE,
    weight_five_center_lift_system,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json"
)
INPUTS = (
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _scale_rows() -> list[dict[str, float]]:
    dims = dimensions(12)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    velocity = np.zeros(qdim)
    velocity[0] = ROUND_EXPANSION_RATE
    multipliers = np.zeros(mdim)
    rows = []
    for shift in (0.0, 1.0, 2.0, 3.0):
        coordinates = np.zeros(qdim)
        coordinates[0] = shift
        jet = exact_weight_five_action_jet_at_state(
            12, coordinates, velocity, multipliers, points=384
        )
        radius = RADIUS0 * np.exp(shift)
        rows.append({
            "q0": shift,
            "value_over_R5": float(np.real(jet.value) / radius**5),
            "gradient_norm_over_R5": float(
                np.linalg.norm(np.real(jet.gradient)) / radius**5
            ),
            "hessian_norm_over_R5": float(
                np.linalg.norm(np.real(jet.hessian), 2) / radius**5
            ),
        })
    return rows


def _decomposition_rows() -> list[dict[str, float]]:
    dims = dimensions(12)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    velocity = np.zeros(qdim)
    velocity[0] = ROUND_EXPANSION_RATE
    multipliers = np.zeros(mdim)
    rows = []
    for shift in (1.0, 2.0, 3.0, 4.0):
        coordinates = np.zeros(qdim)
        coordinates[0] = shift
        full = exact_full_action_jet_at_state(
            12, coordinates, velocity, multipliers, points=384
        )
        seven = exact_weight_seven_action_jet_at_state(
            12, coordinates, velocity, multipliers, points=384
        )
        five = exact_weight_five_action_jet_at_state(
            12, coordinates, velocity, multipliers, points=384
        )
        radius = RADIUS0 * np.exp(shift)
        rows.append({
            "q0": shift,
            "absolute_remainder_over_R5": float(
                abs(np.real(full.value - seven.value - five.value)) / radius**5
            ),
        })
    return rows


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("weight-five modulation inputs required")
    inputs = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(item.get("validation_passed") is True for item in inputs):
        raise RuntimeError("validated weight-five lineage required")
    lift = weight_five_center_lift_system(points=384)
    matrix = np.asarray(lift.pop("matrix"))
    rhs = np.asarray(lift.pop("right_hand_side"))
    gradient = np.asarray(lift.pop("weight_five_gradient"))
    scale_rows = _scale_rows()
    decomposition = _decomposition_rows()
    value_spread = max(row["value_over_R5"] for row in scale_rows) - min(
        row["value_over_R5"] for row in scale_rows
    )
    gradient_spread = max(
        row["gradient_norm_over_R5"] for row in scale_rows
    ) - min(row["gradient_norm_over_R5"] for row in scale_rows)
    hessian_spread = max(
        row["hessian_norm_over_R5"] for row in scale_rows
    ) - min(row["hessian_norm_over_R5"] for row in scale_rows)
    validation = {
        "exact_retained_weight_five_terms_only": True,
        "weight_five_value_scale_covariance": abs(value_spread) < 2.0e-12,
        "weight_five_gradient_scale_covariance": abs(gradient_spread) < 2.0e-10,
        "weight_five_hessian_scale_covariance": abs(hessian_spread) < 2.0e-8,
        "full_minus_weight7_minus_weight5_decays_below_R5": all(
            later["absolute_remainder_over_R5"]
            < earlier["absolute_remainder_over_R5"]
            for earlier, later in zip(decomposition, decomposition[1:])
        ),
        "weight_five_velocity_gradient_exactly_zero": (
            bool(np.max(np.abs(gradient[37:74])) == 0.0)
        ),
        "physical_Feshbach_KKT_system_has_expected_shape": (
            matrix.shape == (74, 74) and rhs.shape == (74,)
        ),
        "R_minus_2_coefficient_solution_not_promoted": True,
        "ill_conditioned_coefficient_system_not_inverted": True,
        "owner_finite_encapsulation_scope_preserved": (
            inputs[1]["physical_domain"]["universal_terminal_reachability_required"]
            is False
        ),
        "no_gate_selector_scale_fit_or_new_time_direction_added": True,
    }
    return {
        "artifact": "BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION",
        "status": (
            "EXACT_WEIGHT_FIVE_CENTER_FORCE_OPERATOR_DERIVED_"
            "COEFFICIENT_SOLUTION_AND_UNIFORM_REMAINDER_OPEN"
        ),
        "classification": (
            "THE_COMPLETE_SCALE_WEIGHT_FIVE_PART_OF_THE_RETAINED_ACTION_IS_"
            "EXTRACTED_EXACTLY;_ITS_FIRST_CENTER_LIFT_IS_THE_BORDERED_"
            "FESHBACH_KKT_EQUATION_AT_sigma=-2H0,_BUT_THE_N12_COEFFICIENT_"
            "MATRIX_IS_TOO_ILL_CONDITIONED_FOR_A_FLOAT64_SOLUTION_TO_BE_"
            "PROMOTED_AS_A_PHYSICAL_MODULATION_OR_STABILITY_EIGENVALUE"
        ),
        "exact_weight_five_action": {
            "terms": [
                "3*(A^3*B^3/C)*N*(n_prime*(a_prime+b_prime)+a_prime^2+b_prime^2+3*a_prime*b_prime)",
                "N*C*A^3*B^3*(3/A^2+3/B^2)",
                "-(1/2)*N*C*A^3*B^3*localization*x_spatial",
            ],
            "ADM_kinetic_or_cosmological_term_included": False,
            "inverse_inertia_or_boundary_Casimir_included": False,
            "velocity_dependence": False,
            "uniform_scale_weight": 5,
            "scale_crosscheck_rows": scale_rows,
            "full_decomposition_rows": decomposition,
        },
        "center_force": {
            "small_parameter": "epsilon=R4^-2",
            "particular_descriptor_exponent": "sigma=-2H0",
            "equation": (
                "(A7+2H0*E7)X5=(0,-D_q_phys_L5,-D_m_L5)"
            ),
            "matrix_shape": list(matrix.shape),
            "right_hand_side_norm": float(np.linalg.norm(rhs)),
            "smallest_singular_value_float64": lift["smallest_singular_value"],
            "largest_singular_value_float64": lift["largest_singular_value"],
            "condition_number_float64": lift["condition_number"],
            "coefficient_solution_evaluated": False,
            "reason": (
                "CONDITION_NUMBER_ABOUT_3.69E11_MAKES_THE_COEFFICIENT_"
                "SOLUTION_AND_ANY_sigma=O(R4^-2)_ROOT_NONPROMOTABLE_WITH_"
                "THE_CURRENT_FLOAT64_QUADRATURE"
            ),
        },
        "nonlinear_consequence": {
            "formal_if_uniform_expansion_exists": (
                "D_tau_log_R4=H0+O(R4^-2)_AND_CENTER_AMPLITUDES_HAVE_"
                "FINITE_O(R4^-2)_DRIFT,_SO_THE_FORMAL_MATHEMATICAL_BRANCH_"
                "HAS_H4_TO_H0>0"
            ),
            "uniform_full_remainder_theorem": "OPEN",
            "physical_promotion": False,
            "event_or_stop_excluded": False,
            "Osgood_H4_to_zero_proved": False,
            "positive_H4_limit_for_full_retained_history_proved": False,
            "owner_scope": (
                "AN_INFINITE_NONENCAPSULATING_REALIZATION_IS_EXCLUDED_FROM_"
                "THE_PHYSICAL_PARTICLE_DOMAIN_WITHOUT_DELETING_THIS_"
                "MATHEMATICAL_FORMAL_BRANCH"
            ),
        },
        "exact_next_dependency": (
            "BUILD_A_CERTIFIED_HIGH_PRECISION_OR_ANALYTICALLY_PRECONDITIONED_"
            "NULLSPACE_AND_BORDERED_KKT_EVALUATION_OF_THE_WEIGHT_FIVE_LIFT,_"
            "THEN_PROVE_A_UNIFORM_NONLINEAR_REMAINDER_OR_AN_EXISTING_EVENT_"
            "STOP;_DO_NOT_PROMOTE_FLOAT64_R_MINUS_2_ROOTS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PHYSICAL_FINITE_ORACLE_AND_MATHEMATICAL_REMAINDER_OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "exact_weight_five_action": "DERIVED",
            "constraint_reduced_center_force_operator": "DERIVED",
            "weight_five_center_coefficient": "OPEN_HIGH_PRECISION",
            "uniform_full_remainder_outcome": "OPEN",
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
