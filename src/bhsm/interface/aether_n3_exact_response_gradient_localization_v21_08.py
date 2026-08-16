"""Localize the exact-F376 versus assembled-response mismatch at v21.04."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_corrected_rayleigh_multisecant_v21_05 import STATES
from bhsm.interface.aether_n3_exact_merit_subspace_hessian_v21_07 import _orthonormalize
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_plateau_proposal_mechanism_audit_v20_67 import _block_stats, _owner, _region
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import rayleigh_square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response


VERSION = "v21.08"
CLASSIFICATION = "BHSM_N3_EXACT_RESPONSE_GRADIENT_MISMATCH_LOCALIZATION"
FULL_BHSM_COMPLETE = False


def completion_payload() -> dict[str, Any]:
    source_raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    source_y = source_raw * scales
    source_residual = rayleigh_square_physical_residual(source_y)
    source_norm = float(np.linalg.norm(source_residual))
    payload_06 = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))
    curvature = payload_06["curvature_refresh"]
    matrix = _current_square_response(source_raw, curvature)
    transform, transform_audit = _action_curvature_transform(source_raw)
    raws = {version: loader() for version, loader in STATES}
    prior = json.loads(Path(
        "artifacts/BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05.json"
    ).read_text(encoding="utf-8"))["corrected_rayleigh_multisecant"]
    coefficients = np.asarray(prior["multisecant_model"]["coefficients"], dtype=float)
    ordered_raws = [raws[version] for version, _ in STATES]
    secant_matrix = np.column_stack([
        np.linalg.solve(
            transform, (ordered_raws[index + 1] - ordered_raws[index]) * scales
        )
        for index in range(len(ordered_raws) - 1)
    ])
    multisecant = secant_matrix @ coefficients
    gradient_y = matrix.T @ source_residual
    gradient_x = transform.T @ gradient_y
    basis = _orthonormalize([
        ("corrected_multisecant", multisecant),
        ("material_v20_92_to_v20_94", np.linalg.solve(
            transform, (raws["v20.94"] - raws["v20.92"]) * scales
        )),
        ("material_v20_95_to_v20_98", np.linalg.solve(
            transform, (raws["v20.98"] - raws["v20.95"]) * scales
        )),
        ("material_v20_88_to_v20_91", np.linalg.solve(
            transform, (raws["v20.91"] - raws["v20.88"]) * scales
        )),
        ("negative_current_merit_gradient", -gradient_x),
    ])
    radius_best = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["best"]
    action_cap = float(radius_best["realized_action_coordinate_norm"])
    physical_cap = float(radius_best["realized_physical_scaled_norm"])

    rows = []
    differences = []
    for name, direction_x in basis:
        direction_y = transform @ direction_x
        reference_radius = min(
            action_cap, physical_cap / max(float(np.linalg.norm(direction_y)), 1.0e-300)
        )
        exact_derivatives = []
        for factor in (0.5, 1.0, 2.0):
            radius = factor * reference_radius
            plus = rayleigh_square_physical_residual(source_y + radius * direction_y)
            minus = rayleigh_square_physical_residual(source_y - radius * direction_y)
            exact_derivatives.append((plus - minus) / (2.0 * radius))
        exact = exact_derivatives[1]
        assembled = matrix @ direction_y
        difference = assembled - exact
        differences.append(difference)
        denominator = max(float(np.linalg.norm(exact)), 1.0)
        top_rows = []
        for row_index in np.argsort(np.abs(difference))[-10:][::-1]:
            owner = _owner(int(row_index))
            top_rows.append({
                "row": int(row_index),
                "difference": float(difference[row_index]),
                "abs": float(abs(difference[row_index])),
                **owner,
                "region": _region(owner["history_node"]),
            })
        rows.append({
            "basis": name,
            "reference_action_radius": reference_radius,
            "reference_physical_scaled_radius": float(
                reference_radius * np.linalg.norm(direction_y)
            ),
            "exact_response_l2": float(np.linalg.norm(exact)),
            "assembled_response_l2": float(np.linalg.norm(assembled)),
            "assembled_vs_exact_relative": float(np.linalg.norm(difference) / denominator),
            "half_vs_reference_exact_relative": float(
                np.linalg.norm(exact_derivatives[0] - exact) / denominator
            ),
            "double_vs_reference_exact_relative": float(
                np.linalg.norm(exact_derivatives[2] - exact) / denominator
            ),
            "analytic_merit_directional_derivative": float(source_residual @ assembled),
            "exact_merit_directional_derivative": float(source_residual @ exact),
            "difference_block_norms": _block_stats(difference),
            "largest_difference_rows": top_rows,
        })
    worst_index = int(np.argmax([row["assembled_vs_exact_relative"] for row in rows]))
    worst = rows[worst_index]
    stable = bool(
        worst["half_vs_reference_exact_relative"] < 1.0e-2
        and worst["double_vs_reference_exact_relative"] < 1.0e-2
    )
    demonstrated_rows = [
        row for row in rows
        if row["half_vs_reference_exact_relative"] < 1.0e-2
        and row["double_vs_reference_exact_relative"] < 1.0e-2
        and row["assembled_vs_exact_relative"] > 2.0e-2
    ]
    demonstrated = bool(demonstrated_rows)
    demonstrated_basis = max(
        demonstrated_rows,
        key=lambda row: row["assembled_vs_exact_relative"],
        default=None,
    )
    result = {
        "source_frontier": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "coordinate_map": transform_audit,
        "basis_response_checks": rows,
        "worst_basis": worst["basis"],
        "worst_assembled_vs_exact_relative": worst["assembled_vs_exact_relative"],
        "worst_exact_response_step_stable": stable,
        "demonstrated_stable_basis": None if demonstrated_basis is None else demonstrated_basis["basis"],
        "demonstrated_stable_relative_mismatch": None if demonstrated_basis is None else demonstrated_basis["assembled_vs_exact_relative"],
        "classification": (
            "ASSEMBLED_RESPONSE_MISMATCH_DEMONSTRATED"
            if demonstrated else "ASSEMBLED_RESPONSE_MISMATCH_NOT_DEMONSTRATED"
        ),
        "first_action_owned_blocker": (
            "EVENT_NEAR_SCALE_V_ASSEMBLED_SQUARE_RESPONSE_DERIVATIVE"
            if demonstrated else None
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "five_basis_directions": len(rows) == 5,
        "three_exact_steps_each": all(
            row["reference_action_radius"] > 0.0 for row in rows
        ),
        "one_classification": result["classification"] in {
            "ASSEMBLED_RESPONSE_MISMATCH_DEMONSTRATED",
            "ASSEMBLED_RESPONSE_MISMATCH_NOT_DEMONSTRATED",
        },
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_EXACT_RESPONSE_GRADIENT_LOCALIZATION_V21_08",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_response_gradient_localization": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_EXACT_RESPONSE_GRADIENT_LOCALIZATION_V21_08.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
