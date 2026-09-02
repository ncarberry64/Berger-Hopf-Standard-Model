"""Materialize the proper-time gauge first jet on the affine 72D carrier."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_affine72_gauge_calderon_first_jet import (
    ACTION_VERSION,
    CLASSIFICATION,
    affine72_gauge_brst_first_jet,
    claim_boundary,
)
from bhsm.interface.aether_cancelled_arc_proper_time_pullback import (
    assemble_cancelled_arc_proper_time_coefficient_first_jet,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (
    boundary_geometry_action_covectors,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
AFFINE = F / "BHSM_N12_GATE7_EXACT_AFFINE_72D_HISTORY_FIRST_JET.json"
AFFINE_DATA = AFFINE.with_suffix(".npz")
TRANSFER = F / "BHSM_N12_GATE7_AFFINE_72D_NONLINEAR_TRANSFER_AUDIT.json"
MOVING = F / "BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json"
CENTER = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
CENTER_DATA = CENTER.with_suffix(".npz")
FIRST_HIT = F / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"
STOP_GAUGE = A / "BHSM_AE4_CURRENT_C2_STOP_GAUGE_BRST_CALDERON.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET.json"
INPUTS = (
    AFFINE,
    AFFINE_DATA,
    TRANSFER,
    MOVING,
    CENTER,
    CENTER_DATA,
    FIRST_HIT,
    STOP_GAUGE,
    ROOT / "src/bhsm/interface/ae4_current_c2_affine72_gauge_calderon_first_jet.py",
    ROOT / "src/bhsm/interface/aether_cancelled_arc_proper_time_pullback.py",
    ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py",
    ROOT / "scripts/materialize_ae4_current_c2_affine72_gauge_calderon_first_jet.py",
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


def _truncate(values: np.ndarray, left: int, fraction: float) -> np.ndarray:
    terminal = values[left] + fraction * (values[left + 1] - values[left])
    return np.concatenate((values[: left + 1], terminal[None, ...]), axis=0)


@lru_cache(maxsize=1)
def build_affine72_proper_time_carrier() -> dict[str, Any]:
    """Return the shared stopped proper-time path and its affine 72D jet."""

    for path in (AFFINE, AFFINE_DATA, CENTER, CENTER_DATA, FIRST_HIT):
        if not path.is_file():
            raise FileNotFoundError(str(path))
    affine, center, first_hit = (
        _load(path) for path in (AFFINE, CENTER, FIRST_HIT)
    )
    if not all(
        row.get("validation_passed") is True
        for row in (affine, center, first_hit)
    ):
        raise RuntimeError("validated affine and canonical-stop center inputs required")
    with np.load(AFFINE_DATA) as source:
        affine_arc = np.asarray(source["action_lengths"], dtype=float)
        affine_jacobi = np.asarray(
            source["ambient_fixed_time_Jacobi_midpoint"], dtype=float
        )
        affine_radius = np.asarray(
            source["ambient_fixed_time_Jacobi_component_radius"], dtype=float
        )
        terminal_hit_jacobi = np.asarray(
            source["terminal_first_hit_Jacobi_midpoint"], dtype=float
        )
    with np.load(CENTER_DATA) as source:
        arc = np.asarray(source["collocation_arc_parameters"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptor = np.asarray(
            source["independent_signed_descriptors"], dtype=float
        )
        norm = np.asarray(source["cancelled_field_action_norm"], dtype=float)
        norm_state = np.asarray(
            source["cancelled_norm_state_gradient_action"], dtype=float
        )
        norm_descriptor = np.asarray(
            source["cancelled_norm_descriptor_derivative"], dtype=float
        )
        descriptor_gradient = np.asarray(
            source["descriptor_gradient_action_diagnostic"], dtype=float
        )
        weights = np.asarray(source["state_weights"], dtype=float)

    stop = float(first_hit["interval_Newton"]["first_hit_action_time_midpoint"])
    right = int(np.searchsorted(arc, stop, side="right"))
    left = right - 1
    fraction = float((stop - arc[left]) / (arc[right] - arc[left]))
    stopped_arc = np.concatenate((arc[: left + 1], np.asarray((stop,))))
    stopped_states = _truncate(states, left, fraction)
    stopped_descriptor = _truncate(descriptor, left, fraction)
    stopped_descriptor[-1] = 0.0
    stopped_norm = _truncate(norm, left, fraction)
    stopped_norm_state = _truncate(norm_state, left, fraction)
    stopped_norm_descriptor = _truncate(norm_descriptor, left, fraction)
    stopped_descriptor_gradient = _truncate(descriptor_gradient, left, fraction)

    state_first = np.asarray(
        CubicSpline(affine_arc, affine_jacobi, axis=0)(stopped_arc), dtype=float
    )
    state_first_radius = np.asarray(
        PchipInterpolator(affine_arc, affine_radius, axis=0)(stopped_arc),
        dtype=float,
    )
    descriptor_first = np.einsum(
        "ni,nij->nj", stopped_descriptor_gradient, state_first, optimize=True
    )
    descriptor_first[-1] = 0.0
    terminal_geometry = boundary_geometry_action_covectors(
        state=stopped_states[-1], weights=weights
    )
    terminal_log_radius_first = (
        np.asarray(terminal_geometry["D_log_R4_action_dual"], dtype=float)
        @ terminal_hit_jacobi
    )
    pulled = assemble_cancelled_arc_proper_time_coefficient_first_jet(
        arc_nodes=stopped_arc,
        states=stopped_states,
        state_action_first_jet=state_first,
        state_weights=weights,
        signed_descriptor=stopped_descriptor,
        signed_descriptor_first_jet=descriptor_first,
        cancelled_field_action_norm=stopped_norm,
        cancelled_norm_state_gradient_action=stopped_norm_state,
        cancelled_norm_descriptor_derivative=stopped_norm_descriptor,
        terminal_log_radius_first_jet=terminal_log_radius_first,
    )
    return {
        "pulled": pulled,
        "stop": stop,
        "terminal_descriptor": float(stopped_descriptor[-1]),
        "terminal_descriptor_first_jet": descriptor_first[-1],
        "maximum_interpolated_affine_component_radius": float(
            np.max(state_first_radius)
        ),
    }


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    affine, transfer, moving, center, first_hit, stop_gauge = (
        _load(path)
        for path in (AFFINE, TRANSFER, MOVING, CENTER, FIRST_HIT, STOP_GAUGE)
    )
    if not all(
        row.get("validation_passed") is True
        for row in (affine, transfer, moving, center, first_hit, stop_gauge)
    ):
        raise RuntimeError("validated affine, stop, moving-endpoint, and gauge inputs required")

    carrier = build_affine72_proper_time_carrier()
    pulled = carrier["pulled"]
    result = affine72_gauge_brst_first_jet(
        log_radii=np.asarray(pulled["log_radius"], dtype=float),
        normalized_proper_times=np.asarray(
            pulled["normalized_proper_times"], dtype=float
        ),
        proper_duration=float(pulled["proper_duration"]),
        log_radius_first_jet=np.asarray(
            pulled["log_radius_normalized_proper_time_first_jet"], dtype=float
        ),
        proper_duration_first_jet=np.asarray(
            pulled["proper_duration_first_jet"], dtype=float
        ),
        spectral_parameter=-1.0,
    )
    coexact_jet = np.asarray(result["coexact"]["D_parameter_Weyl"], dtype=float)
    coexact_radius_part = np.asarray(
        result["coexact"]["D_parameter_Weyl_radius_part"], dtype=float
    )
    coexact_duration_part = np.asarray(
        result["coexact"]["D_parameter_Weyl_duration_part"], dtype=float
    )
    scalar_jet = np.asarray(
        result["BRST_scalar"]["D_parameter_Weyl"], dtype=float
    )
    radius_part_norm = float(np.linalg.norm(coexact_radius_part))
    duration_part_norm = float(np.linalg.norm(coexact_duration_part))
    midpoint_stop_value = float(
        stop_gauge["scientific_result"]["midpoint_refinement_4"][
            "coexact_Weyl_birth_value"
        ]
    )
    boundary = claim_boundary()
    validation = {
        "existing_moving_endpoint_chain_rule_reused": moving["claim_boundary"][
            "moving_endpoint_two_jet_chain_rule"
        ]
        == "DERIVED",
        "all_72_affine_directions_consumed": coexact_jet.shape == (72,),
        "affine_component_radii_retained_as_nonpromotion_warning": bool(
            carrier["maximum_interpolated_affine_component_radius"] > 0.0
        ),
        "proper_time_pullback_not_action_arc": pulled[
            "arc_parameter_not_identified_with_proper_time"
        ],
        "proper_duration_matches_stop_center_scale": 1.4e-4
        < pulled["proper_duration"]
        < 1.6e-4,
        "moving_stop_descriptor_and_jet_zero": (
            carrier["terminal_descriptor"] == 0.0
            and np.all(carrier["terminal_descriptor_first_jet"] == 0.0)
        ),
        "base_coexact_value_matches_stop_center": abs(
            result["coexact"]["Weyl_birth_value"] - midpoint_stop_value
        )
        < 1.0e-8,
        "coexact_and_scalar_first_jets_finite": bool(
            np.all(np.isfinite(coexact_jet)) and np.all(np.isfinite(scalar_jet))
        ),
        "moving_duration_contribution_not_dropped": (
            duration_part_norm > 1.0e6 * radius_part_norm
        ),
        "BRST_first_jet_cancels_exactly": result[
            "BRST_first_jet_cancellation_residual_norm"
        ]
        == 0.0,
        "rejected_nonlinear_transfer_not_promoted": (
            transfer["adjudication"][
                "affine_jet_may_be_used_as_complete_operator_authority"
            ]
            is False
            and not boundary[
                "AE4_CURRENT_C2_NONLINEAR72_GAUGE_CALDERON_FIRST_JET_DERIVED"
            ]
        ),
    }
    return _canonical(
        {
            "artifact": "BHSM_AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET",
            "action_version": ACTION_VERSION,
            "classification": CLASSIFICATION,
            "carrier": {
                "base_path": "ACCEPTED_CANONICAL_STOP_CENTER_PROPER_TIME_PATH",
                "first_jet": "EXISTING_72D_EXACT_AFFINE_CARRIER_INTERPOLATED_TO_CENTER_NODES",
                "moving_endpoint": "EXISTING_TRANSVERSE_FIRST_HIT_CHAIN_RULE",
                "nonlinear_exact_family_authority": False,
                "reason": "THE_REPOSITORY_TRANSFER_AUDIT_REJECTS_THE_CURRENT_AFFINE_TO_NONLINEAR_BOUND",
            },
            "proper_time_pullback": {
                "node_count": int(len(pulled["log_radius"])),
                "proper_duration": pulled["proper_duration"],
                "parameter_count": pulled["parameter_count"],
                "terminal_descriptor": carrier["terminal_descriptor"],
                "maximum_interpolated_affine_component_radius": carrier[
                    "maximum_interpolated_affine_component_radius"
                ],
            },
            "gauge_BRST_first_jet": result,
            "scientific_result": {
                "coexact_first_jet_2_norm": float(np.linalg.norm(coexact_jet)),
                "coexact_first_jet_max_abs": float(np.max(np.abs(coexact_jet))),
                "coexact_first_jet_argmax": int(np.argmax(np.abs(coexact_jet))),
                "coexact_log_radius_part_2_norm": radius_part_norm,
                "coexact_moving_duration_part_2_norm": duration_part_norm,
                "moving_duration_to_log_radius_norm_ratio": (
                    duration_part_norm / radius_part_norm
                ),
                "BRST_scalar_first_jet_2_norm": float(np.linalg.norm(scalar_jet)),
                "BRST_first_jet_cancellation_residual": result[
                    "BRST_first_jet_cancellation_residual_norm"
                ],
                "interpretation": (
                    "AFFINE_CARRIER_OPERATOR_JET_CANDIDATE_DOMINATED_BY_"
                    "MOVING_STOP_DURATION__NOT_PHYSICAL_NONLINEAR_AUTHORITY"
                ),
            },
            "claim_boundary": boundary,
            "exact_next_calculation": (
                "CLOSE_THE_ALREADY_LOCALIZED_SAME_CENTER_74D_INTERVAL_"
                "CONTRACTION_OR_EQUIVALENT_CONTINUOUS_OUTWARD_VARIATIONAL_"
                "CARRIER,_THEN_REPEAT_THIS_IDENTICAL_PROPER_TIME_COTANGENT_"
                "CONTRACTION_WITH_NONLINEAR_AUTHORITY"
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
        raise SystemExit("affine72 gauge Calderon first-jet validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
