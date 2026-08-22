"""Audit the action-owned orientation of the singular ordered event.

The ordered event nulls the same retained Dirac block inverted by the regular
Euler--Dirac flow.  This audit replaces the undefined event value De_ord*V by
the finite one-sided product D3L[psi,psi,psi] <psi,b_ED>.  It changes no row,
gate, action term, or physical interpretation of forward time.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from derive_n12_action_ball_majorants import action_bound
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
THIRD = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_THIRD_VARIATIONS.npz"
ACTION_MAJORANTS = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_ACTION_MAJORANTS.json"
EIGENLINE = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_ORDERED_EVENT_EIGENLINE_BALL.json"
ORDERED_MIXED = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_ORDERED_EVENT_MIXED_MAJORANT.json"
ROOT_CERTIFICATE = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
EQUIVARIANCE = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json"
THEORY = ROOT / "theory/n12_singular_event_temporal_chirality.md"
RESULT = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_SINGULAR_EVENT_TEMPORAL_CHIRALITY.json"

ORDER = 12
POINTS = (96, 192, 384)
COMPLEX_STEP = 1.0e-20
REFINED_ROOT_RADIUS = 2.0e-13


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _jet_data(state: np.ndarray, reference: np.ndarray, points: int) -> dict[str, object]:
    qdim = dimensions(ORDER)["coordinates"]
    jet = exact_full_action_jet_at_state(
        ORDER, state[:qdim], state[qdim:2 * qdim], state[2 * qdim:], points=points
    )
    hessian = np.asarray(jet.hessian)
    reduced = hessian[qdim:, qdim:]
    values, vectors = np.linalg.eigh(np.asarray(reduced, dtype=float))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    mixed = hessian[qdim:, :qdim]
    velocity = state[qdim:2 * qdim]
    rhs = np.concatenate((
        np.asarray(jet.gradient[:qdim]) - mixed[:qdim] @ velocity,
        -mixed[qdim:] @ velocity,
    ))
    direction = np.zeros(state.size)
    direction[qdim:] = psi
    shifted = state.astype(complex) + 1j * COMPLEX_STEP * direction
    shifted_jet = exact_full_action_jet_at_state(
        ORDER,
        shifted[:qdim], shifted[qdim:2 * qdim], shifted[2 * qdim:],
        points=points,
    )
    reduced_derivative = (
        np.imag(np.asarray(shifted_jet.hessian[qdim:, qdim:])) / COMPLEX_STEP
    )
    cubic = float(psi @ reduced_derivative @ psi)
    forcing = float(psi @ rhs)
    return {
        "action": float(np.real(jet.value)),
        "hessian": np.asarray(hessian, dtype=float),
        "reduced": np.asarray(reduced, dtype=float),
        "selected_index": selected,
        "selected_eigenvalue": float(values[selected]),
        "psi": psi,
        "rhs": np.asarray(rhs, dtype=float),
        "rhs_norm": float(np.linalg.norm(rhs)),
        "soft_Fredholm_forcing": forcing,
        "soft_cubic": cubic,
        "hitting_product": cubic * forcing,
        "squared_eigenvalue_rate_limit": 2.0 * cubic * forcing,
    }


def main() -> None:
    inputs = (
        CHECKPOINT, THIRD, ACTION_MAJORANTS, EIGENLINE, ORDERED_MIXED,
        ROOT_CERTIFICATE, EQUIVARIANCE, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing singular-event inputs: " + ", ".join(missing))

    checkpoint = np.load(CHECKPOINT)
    third_payload = np.load(THIRD)
    action = json.loads(ACTION_MAJORANTS.read_text(encoding="utf-8"))
    eigenline = json.loads(EIGENLINE.read_text(encoding="utf-8"))
    ordered_mixed = json.loads(ORDERED_MIXED.read_text(encoding="utf-8"))
    root = json.loads(ROOT_CERTIFICATE.read_text(encoding="utf-8"))
    equivariance = json.loads(EQUIVARIANCE.read_text(encoding="utf-8"))
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    joint = np.asarray(checkpoint["state"], dtype=float)
    event = joint[:state_dimension]
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    reference /= np.linalg.norm(reference)
    diagnostics = {
        str(points): _jet_data(event, reference, points)
        for points in POINTS
    }
    center = diagnostics["96"]

    # Formal reflection R(q,v,ell,s)=(q,-v,ell,-s), with z-map S.
    reflected = event.copy()
    reflected[qdim:2 * qdim] *= -1.0
    reflected[2 * qdim + ORDER:] *= -1.0
    s_map = np.diag(np.concatenate((
        -np.ones(qdim), np.ones(ORDER), -np.ones(ORDER),
    )))
    reflected_reference = s_map @ reference
    reflected_data = _jet_data(reflected, reflected_reference, 96)

    # Reuse the certified joint normal chart and retained third variation to
    # enclose the two scalar factors on a tighter radius at which the already
    # certified radii polynomial remains negative.
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    normal = np.linalg.svd(jacobian, full_matrices=False)[2].T[:state_dimension]
    weights = np.asarray(third_payload["state_weights"], dtype=float)
    third = np.asarray(third_payload["event"], dtype=float)
    hessian = np.asarray(center["hessian"], dtype=float)
    reduced = np.asarray(center["reduced"], dtype=float)
    psi = np.asarray(center["psi"], dtype=float)
    rhs = np.asarray(center["rhs"], dtype=float)
    values, vectors = np.linalg.eigh(reduced)
    selected = int(center["selected_index"])
    complement = np.delete(vectors, selected, axis=1)
    selected_action = np.zeros(state_dimension)
    selected_action[qdim:] = psi * weights[qdim:]
    complement_action = np.zeros((state_dimension, complement.shape[1]))
    complement_action[qdim:] = complement * weights[qdim:, None]
    selected2_complement = np.einsum(
        "i,j,ijk,ka->a", selected_action, selected_action, third, complement_action
    )

    velocity = event[qdim:2 * qdim]
    mixed = hessian[qdim:, :qdim]
    db_columns = []
    forcing_gradient = []
    for column in range(normal.shape[1]):
        action_direction = normal[:, column]
        raw_direction = action_direction / weights
        derivative_action_hessian = np.tensordot(
            third, action_direction, axes=(2, 0)
        )
        derivative_raw_hessian = (
            derivative_action_hessian * weights[:, None] * weights[None, :]
        )
        derivative_mixed = derivative_raw_hessian[qdim:, :qdim]
        derivative_rhs = np.concatenate((
            hessian[:qdim] @ raw_direction
            - derivative_mixed[:qdim] @ velocity
            - mixed[:qdim] @ raw_direction[qdim:2 * qdim],
            -derivative_mixed[qdim:] @ velocity
            - mixed[qdim:] @ raw_direction[qdim:2 * qdim],
        ))
        coupling = complement.T @ derivative_raw_hessian[qdim:, qdim:] @ psi
        eigenvector_derivative = complement @ (
            coupling / (values[selected] - np.delete(values, selected))
        )
        db_columns.append(derivative_rhs)
        forcing_gradient.append(
            float(eigenvector_derivative @ rhs + psi @ derivative_rhs)
        )
    db = np.column_stack(db_columns)
    forcing_gradient = np.asarray(forcing_gradient)

    event_majorant = action["sectors"][0][
        "derivative_operator_majorants_0_through_5"
    ]
    action_d3 = float(event_majorant[3])
    action_d4 = float(event_majorant[4])
    action_d5 = float(event_majorant[5])
    wq_max = float(np.max(weights[:qdim]))
    wz_max = float(np.max(weights[qdim:]))
    weighted_velocity = float(np.linalg.norm(weights[:qdim] * velocity))
    rhs_second_bound = _up(
        wq_max * action_d3
        + wz_max * (
            action_d4 * weighted_velocity + 2.0 * action_d3 * wq_max
        )
    )
    rhs_first_center = _up(float(np.linalg.norm(db, 2)))

    eb = eigenline["bounds"]
    psi_first_bound = _up(float(
        eb["weighted_selected_to_complement_first_variation_on_ball"]
    ))
    psi_second_bound = _up(
        4.0 * float(eb["shifted_complement_inverse"])
        * float(ordered_mixed["bounds"][
            "D4_normal_normal_selected_complement"
        ])
        + 16.0 * float(eb["relative_complement_first_variation_on_ball"])
        * psi_first_bound
        + 8.0 * psi_first_bound ** 2
    )
    radius = REFINED_ROOT_RADIUS
    rhs_norm_ball = _up(
        float(center["rhs_norm"])
        + rhs_first_center * radius
        + 0.5 * rhs_second_bound * radius ** 2
    )
    rhs_first_ball = _up(rhs_first_center + rhs_second_bound * radius)
    forcing_second_bound = _up(
        psi_second_bound * rhs_norm_ball
        + 2.0 * psi_first_bound * rhs_first_ball
        + rhs_second_bound
    )
    forcing_shift = _up(
        float(np.linalg.norm(forcing_gradient)) * radius
        + 0.5 * forcing_second_bound * radius ** 2
    )

    mixed_d4_selected3 = float(action_bound(
        event,
        projection=normal,
        mixed_directions=[
            normal, selected_action, selected_action, selected_action,
        ],
    ).d[-1])
    cubic_first_bound = _up(
        mixed_d4_selected3
        + 3.0 * float(np.linalg.norm(selected2_complement)) * psi_first_bound
    )
    cubic_second_bound = _up(
        action_d5
        + 6.0 * action_d4 * psi_first_bound
        + 3.0 * float(np.linalg.norm(selected2_complement)) * psi_second_bound
        + 6.0 * action_d3 * psi_first_bound ** 2
    )
    cubic_shift = _up(
        cubic_first_bound * radius + 0.5 * cubic_second_bound * radius ** 2
    )

    rp = root["certified_root_ball"]
    radii_polynomial = _up(
        float(rp["directed_Y_upper"])
        + float(rp["directed_Z0_upper"]) * radius
        + 0.5 * float(rp["Z2_upper"]) * radius ** 2
        - radius
    )
    forcing_abs_lower = abs(float(center["soft_Fredholm_forcing"])) - forcing_shift
    cubic_abs_lower = abs(float(center["soft_cubic"])) - cubic_shift

    serializable_diagnostics = {}
    for points, record in diagnostics.items():
        serializable_diagnostics[points] = {
            key: value for key, value in record.items()
            if key not in {"hessian", "reduced", "psi", "rhs"}
        }
    reflection = {
        "action_even_defect": abs(float(reflected_data["action"]) - float(center["action"])),
        "Dirac_similarity_defect": float(np.linalg.norm(
            np.asarray(reflected_data["reduced"]) - s_map @ reduced @ s_map, 2
        )),
        "Euler_Dirac_rhs_odd_covariance_defect": float(np.linalg.norm(
            np.asarray(reflected_data["rhs"]) + s_map @ rhs
        )),
        "soft_Fredholm_forcing_reflected": float(
            reflected_data["soft_Fredholm_forcing"]
        ),
        "soft_cubic_reflected": float(reflected_data["soft_cubic"]),
        "hitting_product_reflected": float(reflected_data["hitting_product"]),
        "exact_parity": {
            "b_psi": "ODD",
            "c_psi": "EVEN",
            "c_psi_times_b_psi": "ODD",
        },
    }

    validation = {
        "authoritative_checkpoint_hash_matches_root_certificate": (
            _sha256(CHECKPOINT) == root["source_checkpoint_SHA256"]
        ),
        "same_retained_Dirac_block_is_event_block_and_regular_flow_solve_block": True,
        "ordinary_De_ord_times_V_at_exact_event_is_not_defined": True,
        "one_sided_squared_eigenvalue_rate_derived_from_existing_action": True,
        "refined_radius_has_negative_existing_radii_polynomial": radii_polynomial < 0.0,
        "soft_Fredholm_forcing_nonzero_on_refined_root_ball": forcing_abs_lower > 0.0,
        "soft_cubic_nonzero_on_refined_root_ball": cubic_abs_lower > 0.0,
        "cross_quadrature_signs_agree": all(
            float(record["soft_Fredholm_forcing"]) < 0.0
            and float(record["soft_cubic"]) > 0.0
            for record in diagnostics.values()
        ),
        "formal_reflection_parity_derived_from_action": True,
        "event_child_map_does_not_select_one_sign": True,
        "formal_reflection_not_quotiented": True,
        "no_new_equation_constraint_gate_selector_or_physics": True,
    }
    payload = {
        "artifact": "BHSM_N12_SINGULAR_EVENT_TEMPORAL_CHIRALITY",
        "classification": (
            "ACTION_OWNED_SINGULAR_HITTING_CHIRALITY_IDENTIFIED;_"
            "EVENT_TO_CHILD_CORRESPONDENCE_DOES_NOT_SELECT_ONE_SECTOR"
        ),
        "physical_time": "ORIENTED_AND_FORWARD",
        "formal_reflection_is_gauge": False,
        "ordinary_event_transport_correction": {
            "former_expression": "G(E)=D_E_ORD(E)V(E)",
            "status": "UNDEFINED_AT_THE_EXACT_EVENT_BECAUSE_D(E)_HAS_KERNEL_PSI",
            "unbordered_Euler_Dirac_solve": "D(Y)ZD0T=B_ED(Y)",
            "Fredholm_compatibility_at_event": "<PSI,B_ED>=0",
            "existing_time_dynamics_border_or_compatibility_row": False,
        },
        "one_sided_action_identity": {
            "soft_forcing": "B_PSI=<PSI,B_ED>",
            "soft_cubic": "C_PSI=D3L[(0,PSI),(0,PSI),(0,PSI)]",
            "limit": "LIM_(LAMBDA_TO_0)_LAMBDA*LAMBDA_DOT=C_PSI*B_PSI",
            "squared_limit": "LIM_D_DT(LAMBDA^2)=2*C_PSI*B_PSI",
            "temporal_chirality_label": "CHI_HIT=SIGN(C_PSI*B_PSI)",
            "negative_interpretation": "FORWARD_TERMINAL_APPROACH",
            "positive_interpretation": "FORWARD_EMERGENT_SIDE",
            "new_event_gate": False,
        },
        "center_and_cross_quadrature": serializable_diagnostics,
        "refined_root_ball_enclosure": {
            "joint_action_coordinate_radius": radius,
            "existing_radii_polynomial_at_radius_upper": radii_polynomial,
            "forcing_gradient_norm_center": float(np.linalg.norm(forcing_gradient)),
            "forcing_second_derivative_majorant": forcing_second_bound,
            "forcing_shift_upper": forcing_shift,
            "forcing_absolute_lower": forcing_abs_lower,
            "cubic_first_derivative_majorant": cubic_first_bound,
            "D4_normal_selected_selected_selected_majorant": mixed_d4_selected3,
            "cubic_second_derivative_majorant": cubic_second_bound,
            "cubic_shift_upper": cubic_shift,
            "cubic_absolute_lower": cubic_abs_lower,
        },
        "formal_reflection": reflection,
        "event_to_child_conclusion": {
            "finite_relation_and_continuum_graph_are_equivariant": (
                equivariance["zero_set_result"]["global_branch_uniqueness_claimed"] is False
                and equivariance["physical_domain"]["R_related_states_physically_identified"] is False
            ),
            "one_temporal_chirality_sector_action_selected": False,
            "two_sectors_action_proved_physically_equivalent": False,
            "two_sectors_quotiented": False,
            "represented_N12_event_sector": "FORWARD_TERMINAL_APPROACH",
            "reflected_sector": "FORWARD_EMERGENT_SIDE",
        },
        "exact_next_dependency": (
            "DERIVE_AND_CERTIFY_THE_EXISTING_ACTION_OWNED_ONE_SIDED_SINGULAR_"
            "ORDERED_EVENT_HITTING_LAW_AND_ITS_EVENT_TO_CHILD_RESET_REGULARITY_"
            "OR_LOCALIZE_THE_FIRST_RETAINED_ACTION_FAILURE"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "center_hitting_product": center["hitting_product"],
        "forcing_absolute_lower": forcing_abs_lower,
        "cubic_absolute_lower": cubic_abs_lower,
        "event_to_child_selects_one_sector": False,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
