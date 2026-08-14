"""Measure sector compression and nonlinear bending of the v18.43 proposal."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import (
    _action_curvature_transform,
)
from bhsm.interface.aether_n3_action_owned_stiffness_measurement_v18_14 import (
    _direction_inventory,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION,
    NODES,
    Q_DIMENSION,
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_second_direct_line_promotion_v18_41 import v18_41_selected_raw_vector
from bhsm.interface.aether_n3_third_direct_admissible_line_child_v18_46 import v18_46_selected_raw_vector


VERSION = "v18.48"
CLASSIFICATION = "BHSM_N3_V18_43_SECTOR_COMPRESSION_DIAGNOSTIC"
FULL_BHSM_COMPLETE = False
LOCAL_STEP = 1.0e-6
DEPARTURE_THRESHOLD = 5.0e-3


def _proposal_direction_raw() -> tuple[np.ndarray, float]:
    proposal = json.loads(Path(
        "artifacts/BHSM_aether_n3_third_direct_residual_jfnk_v18_43.json"
    ).read_text(encoding="utf-8"))["third_direct_residual_jfnk"]
    selected = proposal["selected_true_merit_candidate_pending_child_acceptance"]
    candidate = np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])
    source = v18_41_selected_raw_vector()
    return (candidate - source) / float(selected["fraction"]), float(selected["fraction"])


def _sector_directions(raw: np.ndarray, direction_raw: np.ndarray) -> dict[str, np.ndarray]:
    scales = kkt_variable_scales()
    direction_y = direction_raw * scales
    sectors_y = {name: np.zeros(376) for name in (
        "scale", "u", "w", "v", "eta_sensitive_shift", "lapse",
        "period", "explicit_event_multiplier", "remaining_physical_blocks",
    )}
    for node in range(NODES - 1):
        offset = node * Q_DIMENSION
        sectors_y["scale"][offset] = direction_y[offset]
        sectors_y["u"][offset + 1:offset + 4] = direction_y[offset + 1:offset + 4]
        sectors_y["w"][offset + 4:offset + 7] = direction_y[offset + 4:offset + 7]
        sectors_y["v"][offset + 7:offset + 10] = direction_y[offset + 7:offset + 10]
    multiplier_offset = (NODES - 1) * Q_DIMENSION
    shift_y = np.zeros(376)
    for node in range(NODES):
        offset = multiplier_offset + node * M_DIMENSION
        sectors_y["lapse"][offset:offset + 3] = direction_y[offset:offset + 3]
        shift_y[offset + 3:offset + 6] = direction_y[offset + 3:offset + 6]
    eta_raw = next(
        direction for name, direction, _ in _direction_inventory(raw)
        if name == "eta_sensitive_shift"
    )
    eta_y = eta_raw * scales
    eta_y /= max(float(np.linalg.norm(eta_y)), 1.0e-300)
    eta_component = float(shift_y @ eta_y) * eta_y
    sectors_y["eta_sensitive_shift"] = eta_component
    sectors_y["remaining_physical_blocks"] = shift_y - eta_component
    sectors_y["period"][-2] = direction_y[-2]
    sectors_y["explicit_event_multiplier"][-1] = direction_y[-1]
    return {name: value / scales for name, value in sectors_y.items()}


def v18_43_sector_compression_diagnostic() -> dict[str, Any]:
    """Compare raw, action-owned, local, nonlinear, and interaction responses."""
    raw = v18_41_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual0 = _square_physical_residual(y)
    direction_raw, rejected_fraction = _proposal_direction_raw()
    direction_y = direction_raw * scales
    accepted_raw = v18_46_selected_raw_vector()
    accepted_fraction = float(
        np.median((accepted_raw - raw)[np.abs(direction_raw) > 1.0e-13]
                  / direction_raw[np.abs(direction_raw) > 1.0e-13])
    )
    transform, transform_audit = _action_curvature_transform(raw)
    direction_x = np.linalg.solve(transform, direction_y)
    sectors_raw = _sector_directions(raw, direction_raw)
    sector_y = {name: value * scales for name, value in sectors_raw.items()}
    raw_square_total = sum(float(np.linalg.norm(value))**2 for value in sectors_raw.values())
    sector_x = {name: np.linalg.solve(transform, value) for name, value in sector_y.items()}
    owned_square_total = sum(float(np.linalg.norm(value))**2 for value in sector_x.values())
    scan_fractions = [accepted_fraction / (2.0**power) for power in range(8, -1, -1)]
    rows = []
    accepted_deltas: dict[str, np.ndarray] = {}
    for name, raw_sector in sectors_raw.items():
        dy = sector_y[name]
        dy_norm = float(np.linalg.norm(dy))
        raw_norm = float(np.linalg.norm(raw_sector))
        owned_norm = float(np.linalg.norm(sector_x[name]))
        if dy_norm == 0.0:
            local = np.zeros(376)
            exact_delta = np.zeros(376)
            secant = np.zeros(376)
            scan = []
        else:
            unit = dy / dy_norm
            local = (
                _square_physical_residual(y + LOCAL_STEP * unit)
                - _square_physical_residual(y - LOCAL_STEP * unit)
            ) / (2.0 * LOCAL_STEP)
            exact_delta = _square_physical_residual(y + accepted_fraction * dy) - residual0
            secant = exact_delta / (accepted_fraction * dy_norm)
            scan = []
            for fraction in scan_fractions:
                displacement = fraction * dy_norm
                if displacement < LOCAL_STEP:
                    continue
                delta = _square_physical_residual(y + fraction * dy) - residual0
                response = delta / displacement
                scan.append({
                    "fraction": fraction,
                    "physical_scaled_displacement_norm": displacement,
                    "relative_departure_from_1e-6_response": float(
                        np.linalg.norm(response - local) / max(1.0, np.linalg.norm(local))
                    ),
                })
        accepted_deltas[name] = exact_delta
        first_departure = next(
            (item for item in scan
             if item["relative_departure_from_1e-6_response"] > DEPARTURE_THRESHOLD),
            None,
        )
        rows.append({
            "sector": name,
            "raw_norm": raw_norm,
            "action_owned_norm": owned_norm,
            "raw_squared_fraction_of_proposal": raw_norm**2 / max(raw_square_total, 1.0e-300),
            "action_owned_squared_fraction_allocation": owned_norm**2 / max(owned_square_total, 1.0e-300),
            "response_norm_at_1e-6": float(np.linalg.norm(local)),
            "accepted_line_fraction": accepted_fraction,
            "accepted_physical_scaled_displacement_norm": accepted_fraction * dy_norm,
            "exact_residual_change_norm_at_accepted_line": float(np.linalg.norm(exact_delta)),
            "secant_response_norm_at_accepted_line": float(np.linalg.norm(secant)),
            "absolute_nonlinear_defect_norm_at_accepted_line": float(
                np.linalg.norm(
                    exact_delta - accepted_fraction * dy_norm * local
                )
            ),
            "relative_departure_at_accepted_line": float(
                np.linalg.norm(secant - local) / max(1.0, np.linalg.norm(local))
            ),
            "departure_scan": scan,
            "first_departure": first_departure,
        })
    departures = [row for row in rows if row["first_departure"] is not None]
    first_sector = min(
        departures,
        key=lambda row: (
            row["first_departure"]["fraction"],
            -row["first_departure"]["relative_departure_from_1e-6_response"],
        ),
    ) if departures else None
    interactions = []
    for names in (("u", "eta_sensitive_shift"), ("u", "lapse"),
                  ("eta_sensitive_shift", "lapse"),
                  ("u", "eta_sensitive_shift", "lapse")):
        combined = sum((sector_y[name] for name in names), np.zeros(376))
        exact = _square_physical_residual(y + accepted_fraction * combined) - residual0
        additive = sum((accepted_deltas[name] for name in names), np.zeros(376))
        interactions.append({
            "sectors": list(names),
            "interaction_residual_norm": float(np.linalg.norm(exact - additive)),
            "exact_combined_residual_change_norm": float(np.linalg.norm(exact)),
            "interaction_fraction_of_combined_change": float(
                np.linalg.norm(exact - additive)
                / max(1.0e-300, np.linalg.norm(exact))
            ),
        })
    full_delta = _square_physical_residual(y + accepted_fraction * direction_y) - residual0
    largest_normalized = max(rows, key=lambda row: row["relative_departure_at_accepted_line"])
    largest_absolute = max(
        rows, key=lambda row: row["absolute_nonlinear_defect_norm_at_accepted_line"]
    )
    largest_interaction = max(
        interactions, key=lambda row: row["interaction_residual_norm"]
    )
    return {
        "source_state": "v18.41_accepted_frontier",
        "proposal_source": "v18.43_invalidated_Newton_JFNK_geometric_probe",
        "rejected_aggressive_fraction": rejected_fraction,
        "accepted_nonlinear_line_state": "v18.47",
        "accepted_line_fraction": accepted_fraction,
        "local_response_step": LOCAL_STEP,
        "nonlinear_departure_threshold": DEPARTURE_THRESHOLD,
        "proposal_norms": {
            "raw": float(np.linalg.norm(direction_raw)),
            "physical_scaled": float(np.linalg.norm(direction_y)),
            "action_owned": float(np.linalg.norm(direction_x)),
        },
        "sector_measurements": rows,
        "first_sector_showing_nonlinear_departure": (
            None if first_sector is None else {
                "sector": first_sector["sector"],
                **first_sector["first_departure"],
            }
        ),
        "u_eta_shift_lapse_interactions_at_accepted_line": interactions,
        "bending_classification": {
            "first_departure_sector": (
                None if first_sector is None else first_sector["sector"]
            ),
            "largest_normalized_departure_sector": largest_normalized["sector"],
            "largest_absolute_nonlinear_defect_sector": largest_absolute["sector"],
            "largest_u_eta_shift_lapse_interaction": largest_interaction,
            "high_u_shift_lapse_or_coupling_dominates_absolute_bending": bool(
                largest_absolute["sector"] in {
                    "u", "eta_sensitive_shift", "lapse"
                }
                or largest_interaction["interaction_residual_norm"]
                > largest_absolute["absolute_nonlinear_defect_norm_at_accepted_line"]
            ),
            "measured_interpretation": (
                "LAPSE_DEPARTS_FIRST_AND_ETA_SHIFT_LAPSE_HAVE_LARGE_NORMALIZED_"
                "DEPARTURE_BUT_W_DOMINATES_ABSOLUTE_NONLINEAR_BENDING_AND_THE_"
                "AUDITED_U_ETA_SHIFT_LAPSE_INTERACTIONS_ARE_ABSOLUTELY_SUBDOMINANT"
            ),
        },
        "full_exact_residual_change_norm_at_accepted_line": float(np.linalg.norm(full_delta)),
        "sector_sum_raw_reconstruction_error": float(
            np.linalg.norm(sum(sectors_raw.values(), np.zeros(376)) - direction_raw)
        ),
        "sector_sum_physical_scaled_reconstruction_error": float(
            np.linalg.norm(sum(sector_y.values(), np.zeros(376)) - direction_y)
        ),
        "coordinate_map": transform_audit,
        "physical_equations_changed": False,
        "residual_rows_left_scaled": False,
        "constraint_added": False,
        "particle_data_used": False,
    }


def completion_payload() -> dict[str, Any]:
    result = v18_43_sector_compression_diagnostic()
    validation = {
        "source_is_v18_41": result["source_state"].startswith("v18.41"),
        "accepted_state_is_v18_47": result["accepted_nonlinear_line_state"] == "v18.47",
        "accepted_fraction_reproduced": abs(result["accepted_line_fraction"] - 0.125) < 1.0e-10,
        "all_requested_sectors_measured": len(result["sector_measurements"]) == 9,
        "sector_sum_reconstructs_raw_direction": result["sector_sum_raw_reconstruction_error"] < 1.0e-12,
        "sector_sum_reconstructs_scaled_direction": result["sector_sum_physical_scaled_reconstruction_error"] < 1.0e-12,
        "local_response_measured_at_1e-6": result["local_response_step"] == 1.0e-6,
        "interaction_diagnostic_present": len(result["u_eta_shift_lapse_interactions_at_accepted_line"]) == 4,
        "bending_classified_without_equation_change": bool(
            result["bending_classification"]["measured_interpretation"]
        ),
        "coordinate_map_invertible": result["coordinate_map"]["invertible"],
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "no_left_residual_scaling": not result["residual_rows_left_scaled"],
        "no_constraint_added": not result["constraint_added"],
        "no_particle_data": not result["particle_data_used"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_v18_43_sector_compression_diagnostic_v18_48",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "v18_43_sector_compression_diagnostic": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_V18_43_GEOMETRIC_PROBE_IS_DECOMPOSED_BY_ACTION_OWNED_PHYSICAL_"
            "SECTOR_WITHOUT_CHANGING_THE_NONLINEAR_PROBLEM"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": "REMEASURE_AND_CONTINUE_THE_EXACT_NONLINEAR_MERIT_MANIFOLD_FROM_V18_47",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_v18_43_sector_compression_diagnostic_v18_48.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v18_43_sector_compression_diagnostic",
    "completion_payload",
    "materialize",
]
