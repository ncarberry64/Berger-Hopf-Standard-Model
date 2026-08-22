"""Transfer the N12 root ball through the existing physical neighborhoods.

No gate is added here.  The script bounds the already-required eta domain,
ordered branch, Euler--Dirac invertibility, positive lapse, and nonzero
relative evolution on the same action-coordinate ball used by the direct
N12 radii calculation.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
INFLATION = 1.0 + 1.0e-10
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
EXACT_NORMAL = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced_1e20.npz",
))
THIRD = Path(os.environ.get(
    "BHSM_N12_THIRD_VARIATION_RESULT",
    ".tmp_direct_n12_center_action_third_variations_current.npz",
))
ACTION_MAJORANT = Path(os.environ.get(
    "BHSM_N12_ACTION_MAJORANT_RESULT",
    ".tmp_direct_n12_stable_action_ball_majorants_89_2e11.json",
))
BORDERED = Path(os.environ.get(
    "BHSM_N12_BORDERED_BALL_RESULT",
    ".tmp_direct_n12_bordered_relative_ball_90_2e11_corrected.json",
))
ORDERED = Path(os.environ.get(
    "BHSM_N12_ORDERED_EIGENLINE_BALL_RESULT",
    ".tmp_direct_n12_ordered_event_eigenline_ball_90_2e11_corrected.json",
))
RADII = Path(os.environ.get(
    "BHSM_N12_FULL_RADII_RESULT", ".tmp_direct_n12_full_action_radii.json"
))
PERSISTENCE = Path(os.environ.get(
    "BHSM_N12_PERSISTENCE_RESULT",
    ".tmp_direct_n12_candidate_positive_duration_persistence.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_NEIGHBORHOOD_RESULT",
    ".tmp_direct_n12_physical_neighborhood_transfer.json",
))


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    state_weights = np.concatenate((
        q_weights, np.ones(qdim), m_weights
    ))
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    child = joint[state_dimension:]
    exact = np.load(EXACT_NORMAL)
    normal = np.asarray(exact["normal_basis"], dtype=float)
    child_normal = normal[state_dimension:]
    third_payload = np.load(THIRD)
    third = np.asarray(third_payload["child"])
    majorant = json.loads(ACTION_MAJORANT.read_text(encoding="utf-8"))
    bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
    ordered = json.loads(ORDERED.read_text(encoding="utf-8"))
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    persistence = json.loads(PERSISTENCE.read_text(encoding="utf-8"))
    radius = float(radii["action_coordinate_ball_radius"])

    q = child[:qdim]
    velocity = child[qdim:2 * qdim]
    multipliers = child[2 * qdim:]
    jet = exact_full_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=POINTS
    )
    hessian = (
        np.asarray(jet.hessian)
        / state_weights[:, None]
        / state_weights[None, :]
    )
    reduced = hessian[qdim:, qdim:]
    reduced_inverse = np.linalg.inv(reduced)
    reduced_inverse_residual = float(np.linalg.norm(
        np.eye(reduced.shape[0]) - reduced_inverse @ reduced, 2
    ))
    reduced_inverse_bound = _up(
        float(np.linalg.norm(reduced_inverse, 2))
        / (1.0 - reduced_inverse_residual)
    )
    relative_first = np.asarray([
        reduced_inverse @ np.tensordot(
            third, child_normal[:, column], axes=(2, 0)
        )[qdim:, qdim:]
        for column in range(child_normal.shape[1])
    ])
    relative_first_bound = _up(float(np.linalg.norm(relative_first)))
    child_majorant = next(
        record for record in majorant["sectors"]
        if record["sector"] == "child"
    )
    fourth_bound = float(child_majorant[
        "restricted_derivative_operator_majorants_0_through_5"
    ][4])
    relative_second_bound = _up(reduced_inverse_bound * fourth_bound)
    relative_ball = _up(
        relative_first_bound * radius
        + 0.5 * relative_second_bound * radius ** 2
    )
    dirac_invertible = relative_ball < 1.0
    center_reduced_singular = np.linalg.svd(reduced, compute_uv=False)
    dirac_inverse_ball_bound = (
        _up(reduced_inverse_bound / (1.0 - relative_ball))
        if dirac_invertible else None
    )

    # A global-in-chi eta Lipschitz bound.  The trigonometric basis has
    # modulus at most one, so coefficient l1 bounds enclose the full interval
    # rather than only the sampled minimum used by the gate implementation.
    q0 = float(q[0])
    u_abs = float(np.sum(np.abs(q[1:1 + ORDER])))
    w_abs = float(np.sum(np.abs(q[1 + ORDER:1 + 2 * ORDER])))
    v_abs = float(np.sum(np.abs(q[1 + 2 * ORDER:1 + 3 * ORDER])))
    scale_dual = 1.0 / q_weights[0]
    u_dual = float(np.linalg.norm(1.0 / q_weights[1:1 + ORDER]))
    w_dual = float(np.linalg.norm(
        1.0 / q_weights[1 + ORDER:1 + 2 * ORDER]
    ))
    v_dual = float(np.linalg.norm(
        1.0 / q_weights[1 + 2 * ORDER:1 + 3 * ORDER]
    ))
    log_c_dual = math.sqrt(scale_dual**2 + u_dual**2 + w_dual**2)
    log_a_dual = math.sqrt(scale_dual**2 + u_dual**2 + v_dual**2)
    log_b_dual = log_a_dual
    log_c_lower = q0 - u_abs - w_abs - radius * log_c_dual
    log_a_lower = q0 - u_abs - v_abs - radius * log_a_dual
    log_b_lower = q0 - u_abs - v_abs - radius * log_b_dual
    terms = np.asarray([
        RADIUS0 ** -2 * math.exp(-2.0 * log_c_lower),
        6.0 * RADIUS0 ** -2 * math.exp(-2.0 * log_a_lower),
        6.0 * RADIUS0 ** -2 * math.exp(-2.0 * log_b_lower),
    ])
    spatial_upper = float(np.sum(terms))
    spatial_gradient = 2.0 * float(
        terms @ np.asarray([log_c_dual, log_a_dual, log_b_dual])
    )
    lapse_abs = float(np.sum(np.abs(multipliers[:ORDER])))
    shift_abs = float(np.sum(np.abs(multipliers[ORDER:])))
    lapse_dual = float(np.linalg.norm(1.0 / m_weights[:ORDER]))
    shift_dual = float(np.linalg.norm(1.0 / m_weights[ORDER:]))
    log_lapse_lower = -lapse_abs - radius * lapse_dual
    shift_upper = shift_abs + radius * shift_dual
    shift_ratio_square_upper = (
        shift_upper ** 2 * math.exp(-2.0 * log_lapse_lower)
    )
    shift_ratio_gradient = (
        2.0 * shift_upper * math.exp(-2.0 * log_lapse_lower)
        * shift_dual
        + 2.0 * shift_ratio_square_upper * lapse_dual
    )
    x_absolute_upper = spatial_upper + shift_ratio_square_upper
    eta_lipschitz = _up(
        3.0 * x_absolute_upper ** 2
        * (spatial_gradient + shift_ratio_gradient)
    )
    center_eta = float(persistence["local_existence"][
        "initial_eta_margin"
    ])
    eta_lower = _down(center_eta - eta_lipschitz * radius)

    boundary_lapse_center = float(persistence["local_existence"][
        "initial_boundary_lapse"
    ])
    boundary_lapse_lower = _down(
        boundary_lapse_center * math.exp(-radius * lapse_dual)
    )
    velocity_lower = _down(float(np.linalg.norm(velocity)) - radius)
    ordered_closed = bool(
        ordered["validation_passed"] is True
        and ordered["bounds"]["eigenline_gap_lower"] > 0.0
    )
    bordered_closed = bool(
        bordered["validation_passed"] is True
        and all(record["certified_invertible_on_ball"]
                for record in bordered["records"])
    )
    neighborhoods_closed = bool(
        dirac_invertible
        and eta_lower > 0.0
        and boundary_lapse_lower > 0.0
        and velocity_lower > 0.0
        and ordered_closed
        and bordered_closed
    )
    root_certified = bool(radii.get("validation_passed") is True)
    persistence_measured = bool(
        persistence["validation"]["local_positive_duration_existence"]
        and persistence["validation"]["coarse_fine_numerical_witness"]
    )
    promoted = bool(
        neighborhoods_closed and root_certified and persistence_measured
    )
    payload = {
        "classification": (
            "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"
            if promoted else
            "N12_PHYSICAL_NEIGHBORHOODS_TRANSFERRED_"
            "FORMAL_ROOT_CERTIFICATE_OPEN"
            if neighborhoods_closed else
            "N12_PHYSICAL_NEIGHBORHOOD_TRANSFER_FAILED"
        ),
        "order": ORDER,
        "points": POINTS,
        "action_coordinate_ball_radius": radius,
        "inputs": {
            str(path): _sha256(path) for path in (
                CHECKPOINT, EXACT_NORMAL, THIRD, ACTION_MAJORANT,
                BORDERED, ORDERED, RADII, PERSISTENCE,
            )
        },
        "Dirac_neighborhood": {
            "center_action_normalized_smallest_singular_value": float(
                center_reduced_singular[-1]
            ),
            "center_inverse_bound": reduced_inverse_bound,
            "center_inverse_residual": reduced_inverse_residual,
            "relative_first_variation_bound": relative_first_bound,
            "relative_second_variation_bound": relative_second_bound,
            "relative_ball_perturbation_bound": relative_ball,
            "inverse_ball_bound": dirac_inverse_ball_bound,
            "invertible_on_ball": dirac_invertible,
        },
        "eta_neighborhood": {
            "center_minimum": center_eta,
            "global_chi_action_Lipschitz_bound": eta_lipschitz,
            "ball_lower_bound": eta_lower,
            "admissible_on_ball": eta_lower > 0.0,
        },
        "remaining_existing_gates": {
            "boundary_lapse_ball_lower": boundary_lapse_lower,
            "nonzero_velocity_ball_lower": velocity_lower,
            "corrected_ordered_branch_simple_on_ball": ordered_closed,
            "canonical_bordered_lifts_invertible_on_ball": bordered_closed,
            "candidate_positive_duration_persistence_measured": (
                persistence_measured
            ),
        },
        "validation": {
            "existing_eta_event_Dirac_persistence_neighborhoods_closed": (
                neighborhoods_closed
            ),
            "direct_N12_root_ball_certified": root_certified,
            "new_physics_equation_constraint_or_gate": False,
        },
        "validation_passed": promoted,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": promoted,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
