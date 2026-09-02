"""Materialize the canonical-stop current-C2 gauge/BRST response."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_stop_gauge_brst_calderon import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    stop_gauge_brst_calderon,
)
from bhsm.interface.ae4_current_c2_stop_matched_center_diagnostic import (
    refine_piecewise_linear_path,
    stop_matched_center_proper_time_path,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
CENTER = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
CENTER_DATA = CENTER.with_suffix(".npz")
FIRST_HIT = F / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"
ENDPOINT = F / "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
COEXACT = A / "BHSM_AE3_C2_COEXACT_GAUGE_FORM_SHAPE.json"
LORENTZIAN = A / "BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json"
HISTORICAL_BRST = ROOT / "artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_STOP_GAUGE_BRST_CALDERON.json"
INPUTS = (
    CENTER,
    CENTER_DATA,
    FIRST_HIT,
    ENDPOINT,
    COEXACT,
    LORENTZIAN,
    HISTORICAL_BRST,
    ROOT / "src/bhsm/interface/ae4_current_c2_stop_gauge_brst_calderon.py",
    ROOT / "src/bhsm/interface/ae4_current_c2_stop_matched_center_diagnostic.py",
    ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py",
    ROOT / "scripts/materialize_ae4_current_c2_stop_gauge_brst_calderon.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    center, first_hit, endpoint, coexact, lorentzian, historical = (
        _load(path)
        for path in (CENTER, FIRST_HIT, ENDPOINT, COEXACT, LORENTZIAN, HISTORICAL_BRST)
    )
    if not all(
        row.get("validation_passed") is True
        for row in (center, first_hit, endpoint, coexact, lorentzian, historical)
    ):
        raise RuntimeError("validated stop, coexact, Lorentzian, and BRST inputs required")
    interval = first_hit["interval_Newton"]["first_hit_action_time_interval"]
    hit_points = {
        "left": float(interval[0]),
        "midpoint": float(
            first_hit["interval_Newton"]["first_hit_action_time_midpoint"]
        ),
        "right": float(interval[1]),
    }
    with np.load(CENTER_DATA) as source:
        arguments = {
            "arc_nodes": np.asarray(source["collocation_arc_parameters"], dtype=float),
            "states": np.asarray(source["projected_states"], dtype=float),
            "signed_descriptor": np.asarray(
                source["independent_signed_descriptors"], dtype=float
            ),
            "cancelled_field_action_norm": np.asarray(
                source["cancelled_field_action_norm"], dtype=float
            ),
            "cancelled_norm_state_gradient_action": np.asarray(
                source["cancelled_norm_state_gradient_action"], dtype=float
            ),
            "cancelled_norm_descriptor_derivative": np.asarray(
                source["cancelled_norm_descriptor_derivative"], dtype=float
            ),
            "state_weights": np.asarray(source["state_weights"], dtype=float),
        }

    rows: dict[str, Any] = {}
    for label, hit in hit_points.items():
        path = stop_matched_center_proper_time_path(
            **arguments,
            stop_arc_coordinate=hit,
        )
        refinements: dict[str, Any] = {}
        for refinement in (1, 4):
            x, durations = refine_piecewise_linear_path(
                path["log_radius"], path["proper_times"], refinement
            )
            refinements[str(refinement)] = stop_gauge_brst_calderon(
                log_radii=x,
                proper_durations=durations,
                spectral_parameter=-1.0,
                friedrichs_terminal_selected=True,
                decimal_precision=60,
            )
        rows[label] = {
            "stop_arc_coordinate": hit,
            "proper_duration": path["proper_duration"],
            "terminal_descriptor": path["terminal_descriptor"],
            "refinements": refinements,
        }

    convergence = {
        label: {
            key: abs(row["refinements"]["4"][key] - row["refinements"]["1"][key])
            for key in (
                "coexact_Weyl_birth_value",
                "BRST_scalar_Weyl_birth_value",
            )
        }
        for label, row in rows.items()
    }
    finest = [row["refinements"]["4"] for row in rows.values()]
    boundary = claim_boundary()
    validation = {
        "canonical_stop_Friedrichs_domain_action_owned": endpoint[
            "validation"
        ]["canonical_stop_uses_retained_Friedrichs_closure"],
        "corrected_coexact_squared_coefficient_consumed": (
            coexact["CURRENT_C2_COEXACT_GAUGE_SPATIAL_POTENTIAL_CORRECTED"]
            and all(row["coexact_potential_coefficient"] == 4.0 for row in finest)
        ),
        "three_exact_stop_interval_positions_evaluated": set(rows)
        == {"left", "midpoint", "right"},
        "proper_time_not_arc_parameter_used": all(
            1.4e-4 < row["proper_duration"] < 1.6e-4 for row in rows.values()
        ),
        "terminal_descriptor_zero": all(
            row["terminal_descriptor"] == 0.0 for row in rows.values()
        ),
        "coexact_blocks_positive_and_finite": all(
            row["coexact_block_positive"] and row["all_boundary_blocks_finite"]
            for row in finest
        ),
        "BRST_pair_cancels_on_same_stop_domain": all(
            row["same_scalar_operator_and_terminal_domain_for_BRST_pair"]
            and row["BRST_cancellation_residual_norm"] == 0.0
            for row in finest
        ),
        "piecewise_linear_refinement_stable": all(
            value < 1.0e-9 for result in convergence.values() for value in result.values()
        ),
        "historical_BRST_cancellation_reused": historical[
            "validation"
        ]["BRST_quotient_exact"],
        "Lorentzian_mismatch_not_renormalized": (
            not lorentzian["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
            and not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
        ),
        "center_path_not_promoted_to_outward_interval": not boundary[
            "AE4_CURRENT_C2_STOP_MATCHED_NONLINEAR_INTERVAL_GAUGE_BRST_BLOCK_DERIVED"
        ],
    }
    return _canonical(
        {
            "artifact": "BHSM_AE4_CURRENT_C2_STOP_GAUGE_BRST_CALDERON",
            "action_version": ACTION_VERSION,
            "classification": CLASSIFICATION,
            "operator_probe": {
                "spectral_parameter": -1.0,
                "spectral_domain": "REAL_NEGATIVE_AXIS_RESOLVENT_PROBE",
                "terminal_domain": "ACTION_SELECTED_CANONICAL_STOP_FRIEDRICHS",
                "transverse_coexact_level": 0,
                "transverse_curl": 2,
                "transverse_potential": 4,
                "lowest_nonzero_scalar_laplacian": 3,
                "independent_normalization": None,
            },
            "stop_interval_center_rows": rows,
            "refinement_1_to_4_absolute_change": convergence,
            "scientific_result": {
                "midpoint_refinement_4": rows["midpoint"]["refinements"]["4"],
                "BRST_constraint_ghost_pair_cancelled_on_same_Friedrichs_domain": True,
                "surviving_per_generator_block": "THREEFOLD_LOWEST_COEXACT_CALDERON_BLOCK",
                "Lorentzian_residue_status": "UNCHANGED_OPEN_MISMATCH_NOT_RENORMALIZED",
            },
            "claim_boundary": boundary,
            "exact_next_calculation": (
                "LIFT_THIS_CENTER_EVALUATION_TO_THE_CORRELATION_PRESERVING_"
                "OUTWARD_NONLINEAR_STOP_PATH_WITH_MOVING_ENDPOINT_JETS,_THEN_"
                "INSERT_THE_GAUGE_BRST_BLOCK_WITH_THE_HS_AND_FERMION_BLOCKS_IN_"
                "THE_EXISTING_AE4_EVENT_FLUX_ASSEMBLY"
            ),
            "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
            "validation": validation,
            "validation_passed": all(validation.values()),
            "FULL_BHSM_COMPLETE": False,
        }
    )


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("stop-matched gauge/BRST Calderon validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
