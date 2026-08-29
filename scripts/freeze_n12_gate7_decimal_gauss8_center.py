"""Freeze the converged Decimal Gauss-8 Gate-7 linear correction center."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.npz"
OLD_GAUSS8 = BASE / "BHSM_N12_GATE7_SIGNED_Y_QUADRATURE_GAUSS08_PROP16_RECONNAISSANCE.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
TANGENT_JSON = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json"
Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
DESCRIPTOR_ORDERS = {
    order: BASE / (
        f"BHSM_N12_GATE7_SIGNED_Y_QUADRATURE_GAUSS{order:02d}_"
        "PROP16_RECONNAISSANCE.npz"
    )
    for order in (8, 12, 16, 20)
}
RESULT = BASE / "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER.json"
DATA_RESULT = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _dense(
    left: np.ndarray, coefficients: np.ndarray, fraction: float,
) -> np.ndarray:
    value = np.zeros(left.shape, dtype=float)
    for index, coefficient in enumerate(reversed(coefficients)):
        value += coefficient
        value *= fraction if index % 2 == 0 else 1.0 - fraction
    return value + left


def main() -> None:
    with np.load(CENTER) as data:
        fine_times = np.asarray(data["fine_grid_action_lengths"], dtype=float)
        fine_values = np.asarray(data["fine_grid_augmented_action_values"], dtype=float)
        coefficients = np.asarray(data["fine_grid_DOP853_dense_coefficients"], dtype=float)
        bracket = int(data["stop_bracket_fine_grid_index"][0])
        stop_fraction = float(data["stop_dense_fraction"][0])
    with np.load(GREEN) as data:
        correction_times = np.asarray(data["fine_action_lengths"], dtype=float)
        state_correction = np.asarray(data["Gauss8_correction_profile"], dtype=float)
        cross_order_increment = np.asarray(
            data["cross_order_profile_increment"], dtype=float,
        )
    with np.load(OLD_GAUSS8) as data:
        old_state_correction = np.asarray(
            data["fine_ambient_correction_profile"], dtype=float,
        )
        old_descriptor_correction = np.asarray(
            data["fine_descriptor_correction_profile"], dtype=float,
        )
    with np.load(JACOBIAN) as data:
        descriptor_gradient = np.asarray(
            data["descriptor_gradient_action"], dtype=float,
        )

    terminal_time = fine_times[bracket] + stop_fraction * (
        fine_times[bracket + 1] - fine_times[bracket]
    )
    expected_times = np.concatenate((fine_times[:bracket + 1], [terminal_time]))
    if not np.allclose(correction_times, expected_times, atol=1.0e-13, rtol=0.0):
        raise RuntimeError("Decimal correction and quarter-step center grids differ")
    if any(array.shape != (bracket + 2, 98) for array in (
        state_correction, old_state_correction, descriptor_gradient,
    )):
        raise RuntimeError("complete 371-node state/descriptor profiles required")

    # The old descriptor profile is split without changing its source ledger:
    # q = Dlambda[c_old] + q_direct.  Replace only c_old by the converged
    # Decimal state correction, retaining the same separately integrated
    # descriptor source exactly once.
    direct_descriptor = old_descriptor_correction - np.einsum(
        "ij,ij->i", descriptor_gradient, old_state_correction,
    )
    descriptor_correction = direct_descriptor + np.einsum(
        "ij,ij->i", descriptor_gradient, state_correction,
    )

    base_nodes = np.vstack((
        fine_values[:bracket + 1],
        _dense(fine_values[bracket], coefficients[bracket], stop_fraction),
    ))
    corrected_nodes = base_nodes.copy()
    corrected_nodes[:, :-1] += state_correction
    corrected_nodes[:, -1] += descriptor_correction

    descriptor_profiles = {}
    for order, path in DESCRIPTOR_ORDERS.items():
        with np.load(path) as data:
            descriptor_profiles[order] = np.asarray(
                data["fine_descriptor_correction_profile"], dtype=float,
            )
    descriptor_increments = {
        f"Gauss{left}_to_{right}": float(np.max(np.abs(
            descriptor_profiles[right] - descriptor_profiles[left]
        )))
        for left, right in ((8, 12), (12, 16), (16, 20))
    }
    maximum_descriptor_increment = max(descriptor_increments.values())
    tangent = json.loads(TANGENT_JSON.read_text(encoding="utf-8"))
    crossing = float(tangent["summary"][
        "terminal_descriptor_crossing_on_physical_tangent"
    ])
    shift = -float(corrected_nodes[-1, -1]) / crossing
    remaining_terminal_cell_time = float(
        fine_times[bracket + 1] - terminal_time
    )
    radius = float(json.loads(Z2.read_text(encoding="utf-8"))[
        "domain"
    ]["candidate_nonlinear_action_radius"])
    descriptor_radius = float(
        np.max(np.linalg.norm(descriptor_gradient, axis=1)) * radius
    )
    preterminal_node_lower = float(np.min(corrected_nodes[:-1, -1]))
    last_complete_node_margin = float(corrected_nodes[-2, -1])

    np.savez_compressed(
        DATA_RESULT,
        fine_action_lengths=correction_times,
        base_augmented_action_values=base_nodes,
        state_correction_profile=state_correction,
        direct_descriptor_correction_profile=direct_descriptor,
        descriptor_correction_profile=descriptor_correction,
        corrected_augmented_action_values=corrected_nodes,
        Gauss6_to8_state_profile_increment=cross_order_increment,
    )
    validation = {
        "same_371_node_quarter_step_stop_grid": corrected_nodes.shape == (371, 99),
        "Gauss8_state_correction_frozen_without_refit": True,
        "descriptor_internal_state_and_direct_parts_counted_once": np.allclose(
            descriptor_correction,
            direct_descriptor + np.einsum(
                "ij,ij->i", descriptor_gradient, state_correction,
            ),
            atol=0.0, rtol=0.0,
        ),
        "descriptor_cross_order_increment_below_nonlinear_radius": (
            maximum_descriptor_increment < radius
        ),
        "all_stored_complete_preterminal_nodes_remain_positive": (
            preterminal_node_lower > 0.0
        ),
        "last_complete_node_margin_exceeds_descriptor_rounding_and_halo": (
            last_complete_node_margin
            > maximum_descriptor_increment + descriptor_radius
        ),
        "linearized_shift_remains_inside_terminal_dense_cell": (
            0.0 < shift < remaining_terminal_cell_time
        ),
        "not_promoted_to_continuous_interval_first_hit": True,
    }
    inputs = [CENTER, GREEN, OLD_GAUSS8, JACOBIAN, TANGENT_JSON, Z2]
    inputs.extend(DESCRIPTOR_ORDERS.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER",
        "authority": "FROZEN_NUMERICAL_LINEAR_CENTER_NOT_INTERVAL_FIXED_POINT_AUTHORITY",
        "identity": {
            "state_center": "DECIMAL_GAUSS8_PROP16_SIGNED_GREEN_CORRECTION",
            "descriptor_split": "Dlambda_c_PLUS_EXISTING_DIRECT_DESCRIPTOR_SOURCE",
            "source_terms_added": 0,
            "internal_descriptor_term_double_counted": False,
        },
        "summary": {
            "maximum_state_correction_2_norm": float(np.max(
                np.linalg.norm(state_correction, axis=1)
            )),
            "terminal_state_correction_2_norm": float(np.linalg.norm(
                state_correction[-1]
            )),
            "maximum_Gauss6_to8_state_profile_increment_2_norm": float(
                np.max(cross_order_increment)
            ),
            "descriptor_cross_order_maximums": descriptor_increments,
            "maximum_descriptor_cross_order_increment": maximum_descriptor_increment,
            "maximum_descriptor_correction_absolute": float(
                np.max(np.abs(descriptor_correction))
            ),
            "corrected_descriptor_at_old_stop": float(corrected_nodes[-1, -1]),
            "minimum_corrected_complete_preterminal_node_descriptor": (
                preterminal_node_lower
            ),
            "last_complete_node_descriptor_margin": last_complete_node_margin,
            "nonlinear_radius_descriptor_linear_image_upper": descriptor_radius,
            "terminal_descriptor_crossing": crossing,
            "linearized_later_stop_time_shift": shift,
            "remaining_terminal_dense_cell_time": remaining_terminal_cell_time,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in dict.fromkeys(inputs)
        },
        "claim_boundary": {
            "Decimal_Gauss8_linear_center": "FROZEN",
            "outward_Y_Z1_and_transferred_Z2": "OPEN",
            "continuous_preterminal_margin_and_interval_Newton": "OPEN",
            "Gate7": "ACTIVE",
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
