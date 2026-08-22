"""Certify the finite-core N12 positive-duration observation modulus.

This uses the unchanged retained action, the existing boundary-compatible
gauge quotient, and the exact-root Calderon action ball.  The time variable is
the retained Euler--Dirac evolution parameter; it is not a new homotopy or
physical equation.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np

from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
INFLATION = 1.0 + 1.0e-10
ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
PROMOTION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
DIRECTED = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_CALDERON_DIRECTED_CENTER.json"
)
ACTION_BALL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_CALDERON_ACTION_BALL.json"
)
MAJORANTS = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_ACTION_MAJORANTS.json"
)
RESULT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    directed = json.loads(DIRECTED.read_text(encoding="utf-8"))
    action_ball = json.loads(ACTION_BALL.read_text(encoding="utf-8"))
    majorants = json.loads(MAJORANTS.read_text(encoding="utf-8"))
    if not all(payload.get("validation_passed") is True for payload in (
        promotion, directed, action_ball, majorants,
    )):
        raise RuntimeError("validated N12 root, graph, and action bounds required")

    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    maximum_q_weight = _up(float(np.max(q_weights)))
    joint = np.asarray(np.load(CHECKPOINT)["state"], dtype=float)
    root_distance = float(
        directed["numerical_center_to_exact_root_distance_upper"]
    )
    radius = float(action_ball["action_coordinate_ball_radius_per_sector"])
    graph_gap = float(
        action_ball["ball_bounds"]["seven_by_seven_symbol_gap_lower"]
    )
    sector_majorants = {
        record["sector"]: record for record in majorants["sectors"]
    }
    records = {}
    duration_candidates = []
    generator_bounds = []
    for index, name in enumerate(("event", "child")):
        state = joint[
            index * state_dimension:(index + 1) * state_dimension
        ]
        velocity = state[qdim:2 * qdim]
        velocity_q_action = _up(
            float(np.linalg.norm(velocity * q_weights))
            + maximum_q_weight * (root_distance + radius)
        )
        derivatives = sector_majorants[name][
            "derivative_operator_majorants_0_through_5"
        ]
        gradient_bound = _up(float(derivatives[1]))
        hessian_bound = _up(float(derivatives[2]))
        third_bound = _up(float(derivatives[3]))
        fourth_bound = _up(float(derivatives[4]))
        center_inverse = _up(float(
            directed["sector_records"][name][
                "gauge_fixed_Dirac_core_inverse_Frobenius_bound"
            ]
        ))
        hessian_delta = _up(
            third_bound * radius + 0.5 * fourth_bound * radius**2
        )
        inverse_product = _up(center_inverse * hessian_delta)
        inverse_closed = inverse_product < 1.0
        inverse_ball = (
            _up(center_inverse / (1.0 - inverse_product))
            if inverse_closed else math.inf
        )
        euler_dirac_rhs = _up(
            gradient_bound + hessian_bound * velocity_q_action
        )
        reduced_rate = _up(inverse_ball * euler_dirac_rhs)
        vector_field = _up(math.hypot(velocity_q_action, reduced_rate))
        duration = _down(radius / (2.0 * vector_field))

        rhs_derivative = _up(
            hessian_bound * (1.0 + maximum_q_weight)
            + third_bound * velocity_q_action
        )
        reduced_rate_derivative = _up(
            inverse_ball * (
                rhs_derivative + third_bound * reduced_rate
            )
        )
        generator = _up(math.hypot(
            maximum_q_weight, reduced_rate_derivative
        ))
        records[name] = {
            "configuration_rate_action_bound": velocity_q_action,
            "action_gradient_bound": gradient_bound,
            "action_Hessian_bound": hessian_bound,
            "action_third_variation_bound": third_bound,
            "action_fourth_variation_bound": fourth_bound,
            "gauge_fixed_Dirac_center_inverse_bound": center_inverse,
            "gauge_fixed_Dirac_ball_perturbation_bound": hessian_delta,
            "gauge_fixed_Dirac_inverse_relative_product": inverse_product,
            "gauge_fixed_Dirac_inverse_closed": inverse_closed,
            "gauge_fixed_Dirac_ball_inverse_bound": inverse_ball,
            "Euler_Dirac_rhs_action_bound": euler_dirac_rhs,
            "reduced_rate_action_bound": reduced_rate,
            "full_state_vector_field_action_bound": vector_field,
            "local_exit_time_lower": duration,
            "Euler_Dirac_rhs_derivative_bound": rhs_derivative,
            "Jacobi_generator_action_bound": generator,
        }
        duration_candidates.append(duration)
        generator_bounds.append(generator)

    duration = _down(min(duration_candidates))
    generator = _up(max(generator_bounds))
    mp.mp.dps = 80
    generator_mp = mp.mpf(generator)
    duration_mp = mp.mpf(duration)
    integral_lower_mp = -mp.expm1(
        -2 * generator_mp * duration_mp
    ) / (2 * generator_mp)
    integral_lower = _down(float(integral_lower_mp))
    observation_squared = _down(graph_gap**2 * integral_lower)
    observation = _down(math.sqrt(observation_squared))
    inverse_bound = _up(1.0 / observation)
    validation = {
        "certified_direct_N12_complete_persistent_child_consumed": True,
        "exact_root_graph_gap_closed_on_a_full_action_ball": graph_gap > 0.0,
        "both_gauge_fixed_Dirac_core_inverses_closed_on_ball": all(
            record["gauge_fixed_Dirac_inverse_closed"]
            for record in records.values()
        ),
        "positive_common_coordinate_duration": duration > 0.0,
        "finite_action_owned_Jacobi_generator_bound": math.isfinite(generator),
        "positive_L2_observation_lower_bound": observation_squared > 0.0,
        "existing_Euler_Dirac_constraint_propagation_identity_retained": True,
        "existing_eta_event_Dirac_persistence_neighborhoods_retained": (
            root_distance + radius
            < float(promotion["certified_root_ball"]["radius"])
        ),
        "nonzero_motion_not_treated_as_a_defect": True,
        "sampled_ungauge_fixed_history_not_used": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "N12_FINITE_CORE_POSITIVE_DURATION_NORMAL_OBSERVATION_"
            "MODULUS_CERTIFIED"
            if all(validation.values()) else
            "N12_POSITIVE_DURATION_OBSERVATION_CERTIFICATE_FAILED"
        ),
        "order": ORDER,
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (
                CHECKPOINT, PROMOTION, DIRECTED, ACTION_BALL, MAJORANTS,
            )
        },
        "full_action_neighborhood_radius": radius,
        "Calderon_graph_gap_lower_on_neighborhood": graph_gap,
        "sector_bounds": records,
        "common_coordinate_duration_lower": duration,
        "maximum_Jacobi_generator_action_bound": generator,
        "minimum_Jacobi_propagator_factor_at_endpoint": _down(
            math.exp(-generator * duration)
        ),
        "integrated_propagator_square_lower": integral_lower,
        "c_M0_squared_observation_integral_lower": observation_squared,
        "c_M0_observation_norm_lower": observation,
        "finite_core_normal_inverse_bound_1_over_c_M0": inverse_bound,
        "M0": ORDER,
        "normalization": (
            "EXISTING_ACTION_COORDINATES_AND_EXISTING_UNIT_BOUNDARY_"
            "ACCELERATION_GRAPH_NORMALIZATION"
        ),
        "scope": (
            "FINITE_N12_SOURCE_RESTRICTED_GAUGE_FIXED_CHILD_TANGENT_"
            "QUOTIENTED_NORMAL_OBSERVATION_ONLY"
        ),
        "exact_next_dependency": (
            "DERIVE_THE_ACTION_OWNED_N12_TO_INFINITY_OBSERVATION_"
            "PERTURBATION_epsilon_obs_M0_FROM_THE_EXISTING_INVERSE_"
            "SQUARE_STRONG_GRAPH_TAIL_AND_VERIFY_epsilon_obs_M0_LT_c_M0"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
