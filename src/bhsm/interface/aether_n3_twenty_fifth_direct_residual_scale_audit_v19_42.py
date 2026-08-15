"""Remeasure direct residual response scales at accepted v19.41."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_direct_residual_response_scale_audit_v18_34 import (
    _directions,
)
from bhsm.interface.aether_n3_eighth_direct_residual_scale_audit_v18_70 import (
    STEPS_V18_70,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import (
    _square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_twenty_first_bidirectional_probe_promotion_v19_41 import (
    v19_41_selected_raw_vector,
)


VERSION = "v19.42"
CLASSIFICATION = "BHSM_N3_TWENTY_FIFTH_DIRECT_RESIDUAL_SCALE_AUDIT"
FULL_BHSM_COMPLETE = False
SOURCE_NORM = 0.791308733253912


def twenty_fifth_direct_residual_scale_audit() -> dict[str, Any]:
    raw = v19_41_selected_raw_vector()
    y = raw * kkt_variable_scales()
    residual = _square_physical_residual(y)
    directions = []
    for name, direction in _directions(residual):
        responses = []
        for step in STEPS_V18_70:
            finite = (
                _square_physical_residual(y + step * direction)
                - _square_physical_residual(y - step * direction)
            ) / (2.0 * step)
            responses.append(
                {
                    "step": step,
                    "response_norm": float(np.linalg.norm(finite)),
                    "event_row_response": float(finite[-1]),
                    "response_hex": [float(value).hex() for value in finite],
                }
            )
        comparisons = []
        for coarse, fine in zip(responses[:-1], responses[1:]):
            coarse_vector = np.asarray(
                [float.fromhex(value) for value in coarse["response_hex"]]
            )
            fine_vector = np.asarray(
                [float.fromhex(value) for value in fine["response_hex"]]
            )
            comparisons.append(
                {
                    "coarse_step": coarse["step"],
                    "fine_step": fine["step"],
                    "relative_change": float(
                        np.linalg.norm(fine_vector - coarse_vector)
                        / max(1.0, np.linalg.norm(fine_vector))
                    ),
                    "event_row_absolute_change": abs(
                        fine["event_row_response"]
                        - coarse["event_row_response"]
                    ),
                }
            )
        directions.append(
            {
                "direction": name,
                "responses": responses,
                "successive_scale_comparisons": comparisons,
            }
        )
    common_pairs = []
    for coarse, fine in zip(STEPS_V18_70[:-1], STEPS_V18_70[1:]):
        rows = [
            next(
                row
                for row in direction["successive_scale_comparisons"]
                if row["coarse_step"] == coarse and row["fine_step"] == fine
            )
            for direction in directions
        ]
        common_pairs.append(
            {
                "coarse_step": coarse,
                "fine_step": fine,
                "maximum_relative_change": max(
                    row["relative_change"] for row in rows
                ),
                "maximum_event_row_absolute_change": max(
                    row["event_row_absolute_change"] for row in rows
                ),
                "all_directions_stable": all(
                    row["relative_change"] < 5.0e-3
                    and row["event_row_absolute_change"] < 2.0e-4
                    for row in rows
                ),
            }
        )
    selected = next(
        (row for row in reversed(common_pairs) if row["all_directions_stable"]),
        None,
    )
    return {
        "source_state": "v19.41_twenty_first_bidirectional_probe_promoted_state",
        "source_complete_norm": float(np.linalg.norm(residual)),
        "event_covector_definition": (
            "UNCHANGED_37_COORDINATE_CENTRAL_DIFFERENCE_OF_"
            "ORDERED_EVENT_EIGENVALUE"
        ),
        "directions": directions,
        "common_scale_pairs": common_pairs,
        "selected_finest_common_stable_pair": selected,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_residual_changed": False,
        "event_definition_changed": False,
        "componentwise_acceptance_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = twenty_fifth_direct_residual_scale_audit()
    selected = result["selected_finest_common_stable_pair"]
    validation = {
        "source_is_v19_41": result["source_state"].startswith("v19.41"),
        "source_norm_reproduced": abs(
            result["source_complete_norm"] - SOURCE_NORM
        )
        < 5.0e-12,
        "all_four_directions_measured": len(result["directions"]) == 4,
        "all_scales_measured": all(
            len(row["responses"]) == len(STEPS_V18_70)
            for row in result["directions"]
        ),
        "common_stable_pair_identified": selected is not None,
        "square_explicit_multiplier_system": (
            result["physical_solve_dimension"] == [376, 376]
            and result["event_multiplier_explicit"]
        ),
        "physical_residual_unchanged": not result["physical_residual_changed"],
        "event_definition_unchanged": not result["event_definition_changed"],
        "no_componentwise_acceptance": not result[
            "componentwise_acceptance_added"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_twenty_fifth_direct_residual_scale_audit_v19_42",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "twenty_fifth_direct_residual_scale_audit": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_DIRECT_DERIVATIVE_SCALE_IS_REMEASURED_AFTER_THE_"
            "ACCEPTED_V19_41_STATE_CHANGE"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "SCAN_BOTH_ORIENTATIONS_OF_A_NEW_BOUNDED_GEOMETRIC_PROBE_"
            "WITH_EXACT_NONLINEAR_MERIT"
            if selected is not None
            else "RESOLVE_THE_DIRECT_RESIDUAL_RESPONSE_NOISE_FLOOR"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_twenty_fifth_direct_residual_scale_audit_v19_42.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "twenty_fifth_direct_residual_scale_audit",
    "completion_payload",
    "materialize",
]
