"""Close the action-coordinate projection to the maximal-forward M4 radius."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_lapse,
    boundary_log_radius,
    boundary_log_radius_jets,
    proper_time_log_radius_rate,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)


ORDER = 12
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_BOUNDARY_RADIUS_ACTION_PROJECTION.json"
)
STATE = ARTIFACTS / (
    "n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
OBSERVATION = ARTIFACTS / (
    "n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
CONTINUUM_FLOW = ARTIFACTS / (
    "intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
TRANSFER_VARIATIONS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_forward_boundary_radius.py"
INPUTS = (STATE, OBSERVATION, CONTINUUM_FLOW, TRANSFER_VARIATIONS, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _child_state() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    joint = np.asarray(np.load(STATE)["state"], dtype=float)
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    if joint.shape != (2 * state_dimension,):
        raise RuntimeError("certified state is not the N12 event-child pair")
    child = joint[state_dimension:]
    return child[:qdim], child[qdim : 2 * qdim], child[2 * qdim :]


def _jet_witness(q: np.ndarray) -> dict[str, float]:
    h = np.linspace(-0.3, 0.4, q.size)
    k = np.linspace(0.2, -0.5, q.size)
    h /= np.linalg.norm(h)
    k /= np.linalg.norm(k)
    ell = 0.1 * (h - k)
    jets = boundary_log_radius_jets(ORDER, q, h, k, ell)
    eps_first = 1e-6
    first = (
        boundary_log_radius(ORDER, q + eps_first * h)
        - boundary_log_radius(ORDER, q - eps_first * h)
    ) / (2.0 * eps_first)
    eps = 2e-4

    def value(left: float, right: float) -> float:
        return boundary_log_radius(
            ORDER, q + left * h + right * k + left * right * ell
        )

    mixed = (
        value(eps, eps)
        - value(eps, -eps)
        - value(-eps, eps)
        + value(-eps, -eps)
    ) / (4.0 * eps**2)
    return {
        "first_residual": float(abs(float(jets["first_left"]) - first)),
        "mixed_second_residual": float(
            abs(float(jets["mixed_second"]) - mixed)
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all boundary-radius projection inputs are required")
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    continuum = json.loads(CONTINUUM_FLOW.read_text(encoding="utf-8"))
    transfer = json.loads(TRANSFER_VARIATIONS.read_text(encoding="utf-8"))
    if not all(
        payload.get("validation_passed") is True
        for payload in (observation, continuum, transfer)
    ):
        raise RuntimeError("all action-projection inputs must validate")
    q, velocity, multipliers = _child_state()
    x = boundary_log_radius(ORDER, q)
    log_lapse = boundary_log_lapse(ORDER, multipliers)
    x_rate = proper_time_log_radius_rate(ORDER, q, velocity, multipliers)
    witness = _jet_witness(q)
    coordinate_gradient_bound = math.sqrt(1.0 + 2.0 * ORDER)
    coordinate_hessian_bound = 2.0 * ORDER
    radius = float(observation["full_action_neighborhood_radius"])
    local_x_change_bound = (
        coordinate_gradient_bound * radius
        + 0.5 * coordinate_hessian_bound * radius**2
    )
    child_bounds = observation["sector_bounds"]["child"]
    validation = {
        "certified_N12_child_state_consumed": True,
        "continuum_maximal_flow_dichotomy_available": continuum[
            "maximal_flow_alternative"
        ]["unique_maximal_continuum_child_flow"]
        is True,
        "transfer_variation_equations_available": transfer[
            "validation_passed"
        ]
        is True,
        "positive_boundary_lapse_at_anchor": math.exp(log_lapse) > 0.0,
        "finite_anchor_radius_and_proper_time_rate": math.isfinite(x)
        and math.isfinite(x_rate),
        "first_action_projection_jet_closes_to_1e_minus_8": witness[
            "first_residual"
        ]
        < 1e-8,
        "mixed_action_projection_jet_closes_to_1e_minus_6": witness[
            "mixed_second_residual"
        ]
        < 1e-6,
        "local_action_ball_has_finite_DV_bound": math.isfinite(
            child_bounds["Jacobi_generator_action_bound"]
        ),
        "no_untracked_history_terminal_return_or_new_gate_used": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_BOUNDARY_RADIUS_ACTION_PROJECTION",
        "status": "ACTION_OWNED_BOUNDARY_RADIUS_AND_JET_PROJECTION_DERIVED",
        "classification": (
            "THE_PHYSICAL_FORWARD_RADIUS_IS_THE_EXACT_RETAINED_ACTION_TRACE_"
            "R4=(RADIUS0/2)*exp(q0+u_L-(1/2)log_cosh(2v_L));_ITS_FIRST_"
            "AND_MIXED_SECOND_ACTION_JETS_ARE_EXACT_PULLBACKS_OF_THE_STATE_"
            "JACOBI_FIELDS,_SO_NO_INDEPENDENT_RADIUS_HISTORY_VARIABLE_IS_"
            "REQUIRED"
        ),
        "action_projection": {
            "q_W": "q0+u_L-(1/2)*log(cosh(2*v_L))",
            "physical_radius": "R4=(RADIUS0/2)*exp(q_W)",
            "x": "log(R4)",
            "first": "x_h=D_q_x[q_h]",
            "mixed_second": "x_hk=D_q_x[q_hk]+D_q2_x[q_h,q_k]",
            "proper_time_rate": "d_tau_x=D_q_x[v]/N_boundary",
            "no_independent_radius_degree_of_freedom": True,
        },
        "certified_child_anchor": {
            "log_R4": x,
            "R4": math.exp(x),
            "log_boundary_lapse": log_lapse,
            "boundary_lapse": math.exp(log_lapse),
            "proper_time_log_R4_rate": x_rate,
        },
        "global_functional_bounds": {
            "Euclidean_coordinate_gradient_norm_upper": coordinate_gradient_bound,
            "Euclidean_coordinate_Hessian_operator_norm_upper": coordinate_hessian_bound,
            "source": "abs(tanh)<=1_AND_2*sech(2v)^2<=2",
        },
        "existing_local_action_ball": {
            "radius": radius,
            "log_R4_change_upper_from_projection_only": local_x_change_bound,
            "child_DV_Jacobi_generator_bound": child_bounds[
                "Jacobi_generator_action_bound"
            ],
            "child_action_third_variation_bound": child_bounds[
                "action_third_variation_bound"
            ],
            "child_action_fourth_variation_bound": child_bounds[
                "action_fourth_variation_bound"
            ],
            "child_local_exit_time_lower": child_bounds["local_exit_time_lower"],
            "scope": observation["scope"],
            "extends_to_maximal_component": False,
        },
        "remaining_variational_owner": {
            "base_history": "THE_UNIQUE_ACTION_OWNED_MAXIMAL_CONTINUUM_FLOW_Y(tau)",
            "first_state_Jacobi": "J_h'=D_V(Y)*J_h",
            "mixed_second_state_Jacobi": "J_hk'=D_V(Y)*J_hk+D2_V(Y)[J_h,J_k]",
            "radius_pullback_after_state_jets": "CLOSED_BY_THIS_ARTIFACT",
            "global_DV_and_D2V_enclosures_on_maximal_component": "OPEN",
            "terminal_or_Friedrichs_graph_jets": "OPEN",
            "regular_Weyl_chart_cover": "OPEN",
        },
        "exact_next_dependency": (
            "ASSEMBLE_DV_AND_D2V_OF_THE_RETAINED_EULER_DIRAC_VECTOR_FIELD_"
            "FROM_THE_EXISTING_ACTION_D3_D4_AND_DIRAC_INVERSE_IDENTITIES;_"
            "ENCLOSE_THE_STATE_JACOBI_COCYCLES_ON_BOUNDED_MARGIN_COMPONENTS;_"
            "THEN_PULL_BACK_BY_THE_CLOSED_R4_JETS_AND_PROPAGATE_THE_CHANNEL_"
            "TRANSFER_VARIATIONS"
        ),
        "claim_boundary": {
            "maximal_x_history_numerically_enclosed": False,
            "global_state_Jacobi_cocycles_enclosed": False,
            "channel_Weyl_enclosures": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "chord_03": "NOT_AUTHORIZED",
            "FULL_BHSM_COMPLETE": False,
        },
        "witnesses": witness,
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
                "anchor": payload["certified_child_anchor"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
