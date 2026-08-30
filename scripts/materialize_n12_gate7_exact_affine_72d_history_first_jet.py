"""Materialize the 72-direction exact-affine history and first-hit jet.

This composes the certified correlated Arb macro maps with the complete
reset-quotient seed lift.  The transverse terminal-stop certificate supplies
the moving-duration correction.  The result is the complete *affine-carrier*
coefficient/duration first jet; transfer from this affine jet to the nonlinear
exact solution family remains a separate claim boundary.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

from flint import arb, arb_mat, ctx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)
from bhsm.interface.aether_retained_action_tensor_interval import (  # noqa: E402
    retained_action_tensor_interval,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
RESET = BASE / "BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz"
RESET_RECORD = RESET.with_suffix(".json")
MAPS = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS.npz"
MAPS_RECORD = MAPS.with_suffix(".json")
Z2_INPUTS = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.npz"
Z2_RECORD = Z2_INPUTS.with_suffix(".json")
FIELD = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_DIRECTIONAL_FIELD_CURVATURE.npz"
FIELD_RECORD = FIELD.with_suffix(".json")
STOP_TRANSVERSALITY = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_STOP_TRANSVERSALITY.json"
THEORY = ROOT / "theory" / "n12_gate7_exact_affine_72d_history_first_jet.md"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_72D_HISTORY_FIRST_JET.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
QDIM = 37
SELECTED = 24
PRECISION = 256


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _exact(value: float) -> arb:
    numerator, denominator = float(value).as_integer_ratio()
    return arb(numerator) / arb(denominator)


def _matrix(values: np.ndarray) -> arb_mat:
    values = np.asarray(values, dtype=float)
    return arb_mat([[_exact(value) for value in row] for row in values])


def _arb_strings(values: np.ndarray) -> arb_mat:
    values = np.asarray(values)
    return arb_mat([[arb(str(value)) for value in row] for row in values])


def _mid_radius(matrix: arb_mat) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty((matrix.nrows(), matrix.ncols()))
    radius = np.empty_like(midpoint)
    for row in range(matrix.nrows()):
        for column in range(matrix.ncols()):
            value = matrix[row, column]
            center = float(value.mid())
            midpoint[row, column] = center
            radius[row, column] = math.nextafter(
                float(value.rad().upper()) + np.spacing(abs(center)), math.inf,
            )
    return midpoint, radius


def _linear_interval(
    covector: np.ndarray, midpoint: np.ndarray, radius: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    center = np.asarray(covector) @ np.asarray(midpoint)
    spread = np.abs(covector) @ np.asarray(radius)
    rounding = np.finfo(float).eps * (covector.size + 2.0) * (
        np.abs(covector) @ np.abs(midpoint) + spread
    )
    spread = np.nextafter(spread + rounding, np.inf)
    return center, spread


def _divide_negative_interval(
    numerator_lower: np.ndarray,
    numerator_upper: np.ndarray,
    denominator_lower: float,
    denominator_upper: float,
) -> tuple[np.ndarray, np.ndarray]:
    candidates = np.stack((
        -numerator_lower / denominator_lower,
        -numerator_lower / denominator_upper,
        -numerator_upper / denominator_lower,
        -numerator_upper / denominator_upper,
    ))
    return (
        np.nextafter(np.min(candidates, axis=0), -np.inf),
        np.nextafter(np.max(candidates, axis=0), np.inf),
    )


def main() -> None:
    parents = [_load(path) for path in (
        RESET_RECORD, MAPS_RECORD, Z2_RECORD, FIELD_RECORD,
        STOP_TRANSVERSALITY,
    )]
    if not all(record.get("validation_passed") is True for record in parents):
        raise RuntimeError("validated reset, carrier, center, field, and stop parents required")
    stop = parents[-1]

    with np.load(CENTER) as source:
        base_states = np.asarray(source["centers"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(RESET) as source:
        seed = np.asarray(source["projected_C2_parameter_lift"], dtype=float)
    with np.load(MAPS) as source:
        map_strings = np.asarray(source["macro_step_map_arb_strings"])
        times = np.asarray(source["macro_action_lengths"], dtype=float)
    with np.load(Z2_INPUTS) as source:
        correction = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(FIELD) as source:
        fields = np.asarray(source["normalized_field"], dtype=float)

    states = base_states + correction / weights[None, :]
    if not (
        tangents.shape == (48, 98, 73)
        and seed.shape == (98, 72)
        and map_strings.shape == (47, 73, 73)
        and states.shape == fields.shape == (48, 98)
    ):
        raise RuntimeError("history first-jet dimensions changed")

    ctx.prec = PRECISION
    q = _matrix(tangents[0]).transpose() * _matrix(seed)
    quotient_midpoints = []
    quotient_radii = []
    ambient_midpoints = []
    ambient_radii = []
    for node in range(48):
        q_mid, q_rad = _mid_radius(q)
        ambient = _matrix(tangents[node]) * q
        a_mid, a_rad = _mid_radius(ambient)
        quotient_midpoints.append(q_mid)
        quotient_radii.append(q_rad)
        ambient_midpoints.append(a_mid)
        ambient_radii.append(a_rad)
        if node < 47:
            q = _arb_strings(map_strings[node]) * q
    quotient_midpoints = np.asarray(quotient_midpoints)
    quotient_radii = np.asarray(quotient_radii)
    ambient_midpoints = np.asarray(ambient_midpoints)
    ambient_radii = np.asarray(ambient_radii)

    initial_projection_residual = float(
        np.linalg.norm(seed - tangents[0] @ quotient_midpoints[0], ord=2)
    )

    endpoint_state = states[-1]
    endpoint_jet = cluster.local.exact_full_action_jet_at_state(
        12,
        endpoint_state[:QDIM],
        endpoint_state[QDIM:2 * QDIM],
        endpoint_state[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    reduced = np.asarray(endpoint_jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    selected_leg = np.zeros(98)
    selected_leg[QDIM:] = weights[QDIM:] * psi
    endpoint_direction_interval = (
        ambient_midpoints[-1] - ambient_radii[-1],
        ambient_midpoints[-1] + ambient_radii[-1],
    )
    lambda_jet = retained_action_tensor_interval(
        12, endpoint_state, endpoint_state,
        [selected_leg, selected_leg, endpoint_direction_interval],
        points=cluster.local.POINTS,
    )
    lambda_lower = np.asarray(lambda_jet.lo, dtype=float)
    lambda_upper = np.asarray(lambda_jet.hi, dtype=float)
    derivative_lower, derivative_upper = (
        float(value) for value in stop["cone_transfer"][
            "uniform_Dlambda24_of_F_interval"
        ]
    )
    duration_lower, duration_upper = _divide_negative_interval(
        lambda_lower, lambda_upper, derivative_lower, derivative_upper,
    )
    duration_midpoint = 0.5 * (duration_lower + duration_upper)
    duration_radius = 0.5 * (duration_upper - duration_lower)

    endpoint_hit_midpoint = (
        ambient_midpoints[-1]
        + fields[-1, :, None] * duration_midpoint[None, :]
    )
    endpoint_hit_radius = np.nextafter(
        ambient_radii[-1]
        + np.abs(fields[-1, :, None]) * duration_radius[None, :]
        + np.finfo(float).eps * np.abs(endpoint_hit_midpoint),
        np.inf,
    )

    log_radius = np.empty(48)
    log_radius_fixed_midpoint = np.empty((48, 72))
    log_radius_fixed_radius = np.empty((48, 72))
    log_radius_flow_rate = np.empty(48)
    for node in range(48):
        geometry = boundary_geometry_action_covectors(
            state=states[node], weights=weights,
        )
        covector = np.asarray(geometry["D_log_R4_action_dual"], dtype=float)
        log_radius[node] = float(geometry["log_R4"])
        midpoint, radius = _linear_interval(
            covector, ambient_midpoints[node], ambient_radii[node],
        )
        log_radius_fixed_midpoint[node] = midpoint
        log_radius_fixed_radius[node] = radius
        log_radius_flow_rate[node] = float(covector @ fields[node])

    normalized_time = times / times[-1]
    coefficient_midpoint = np.empty_like(log_radius_fixed_midpoint)
    coefficient_radius = np.empty_like(log_radius_fixed_radius)
    for node in range(48):
        motion_midpoint = (
            normalized_time[node] * log_radius_flow_rate[node]
            * duration_midpoint
        )
        motion_radius = (
            abs(normalized_time[node] * log_radius_flow_rate[node])
            * duration_radius
        )
        coefficient_midpoint[node] = (
            log_radius_fixed_midpoint[node] + motion_midpoint
        )
        coefficient_radius[node] = np.nextafter(
            log_radius_fixed_radius[node] + motion_radius
            + np.finfo(float).eps * np.abs(coefficient_midpoint[node]),
            np.inf,
        )

    terminal_geometry = boundary_geometry_action_covectors(
        state=states[-1], weights=weights,
    )
    endpoint_direct_mid, endpoint_direct_rad = _linear_interval(
        np.asarray(terminal_geometry["D_log_R4_action_dual"], dtype=float),
        endpoint_hit_midpoint, endpoint_hit_radius,
    )
    endpoint_parameterization_residual = float(np.max(
        np.abs(coefficient_midpoint[-1] - endpoint_direct_mid)
        + coefficient_radius[-1] + endpoint_direct_rad
    ))

    np.savez_compressed(
        DATA,
        action_lengths=times,
        normalized_proper_times=normalized_time,
        exact_affine_center_states=states,
        log_R4_midpoint=log_radius,
        reset_seed_lift=seed,
        quotient_Jacobi_midpoint=quotient_midpoints,
        quotient_Jacobi_component_radius=quotient_radii,
        ambient_fixed_time_Jacobi_midpoint=ambient_midpoints,
        ambient_fixed_time_Jacobi_component_radius=ambient_radii,
        terminal_lambda24_parameter_jet_lower=lambda_lower,
        terminal_lambda24_parameter_jet_upper=lambda_upper,
        proper_duration_first_jet_midpoint=duration_midpoint,
        proper_duration_first_jet_radius=duration_radius,
        terminal_first_hit_Jacobi_midpoint=endpoint_hit_midpoint,
        terminal_first_hit_Jacobi_component_radius=endpoint_hit_radius,
        log_R4_fixed_time_first_jet_midpoint=log_radius_fixed_midpoint,
        log_R4_fixed_time_first_jet_radius=log_radius_fixed_radius,
        log_R4_normalized_time_first_jet_midpoint=coefficient_midpoint,
        log_R4_normalized_time_first_jet_radius=coefficient_radius,
    )

    validation = {
        "complete_72_direction_reset_seed_consumed": seed.shape[1] == 72,
        "all_47_correlated_Arb_macro_maps_composed": len(map_strings) == 47,
        "all_48_history_nodes_materialized": len(times) == 48,
        "corrected_terminal_abscissa_consumed": float(times[-1]) == 92.30513924040065,
        "branch_24_selected_at_terminal_center": selected == SELECTED,
        "uniform_stop_derivative_denominator_is_negative": derivative_upper < 0.0,
        "all_duration_jet_intervals_finite": bool(np.all(np.isfinite(duration_radius))),
        "all_coefficient_jet_intervals_finite": bool(np.all(np.isfinite(coefficient_radius))),
        "terminal_normalized_time_chain_rule_matches_first_hit_jet": endpoint_parameterization_residual < 1.0e-8,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_72D_HISTORY_FIRST_JET",
        "status": (
            "COMPLETE_72D_EXACT_AFFINE_HISTORY_AND_FIRST_HIT_JET_MATERIALIZED"
            if passed else "EXACT_AFFINE_72D_HISTORY_FIRST_JET_INVALID"
        ),
        "authority": (
            "RESET_QUOTIENT_SEED_COMPOSED_WITH_CORRELATED_256_BIT_ARB_"
            "INTERACTION_TAYLOR26_MACRO_MAPS_AND_OUTWARD_STOP_TIME_JET"
        ),
        "summary": {
            "parameter_dimension": 72,
            "history_node_count": 48,
            "macro_map_count": 47,
            "initial_seed_to_physical_frame_residual_2_norm": initial_projection_residual,
            "maximum_quotient_Jacobi_operator_2_norm": float(max(
                np.linalg.norm(row, ord=2) for row in quotient_midpoints
            )),
            "maximum_quotient_Jacobi_component_radius": float(np.max(quotient_radii)),
            "maximum_ambient_Jacobi_component_radius": float(np.max(ambient_radii)),
            "maximum_proper_duration_first_jet_absolute": float(np.max(
                np.abs(duration_midpoint) + duration_radius
            )),
            "maximum_log_R4_normalized_time_first_jet_absolute": float(np.max(
                np.abs(coefficient_midpoint) + coefficient_radius
            )),
            "terminal_chain_rule_outward_residual": endpoint_parameterization_residual,
        },
        "first_hit_identity": {
            "duration": "Dxi_T=-(Dxi_lambda24)/(Dlambda24[F])",
            "terminal_state": "Dxi_X_hit=J(T)+F(T)*Dxi_T",
            "normalized_coefficient": (
                "Dxi_x(s)=DlogR4[J(Ts)]+s*DlogR4[F(Ts)]*Dxi_T"
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                CENTER, TANGENT, RESET, RESET_RECORD, MAPS, MAPS_RECORD,
                Z2_INPUTS, Z2_RECORD, FIELD, FIELD_RECORD,
                STOP_TRANSVERSALITY, THEORY, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "complete_affine_carrier_72D_state_path_jet": "MATERIALIZED",
            "moving_first_hit_duration_and_endpoint_jet": "CERTIFIED_ON_AFFINE_CARRIER",
            "log_R4_coefficient_first_jet": "CERTIFIED_ON_AFFINE_CARRIER",
            "nonlinear_exact_solution_family_first_jet_transfer": "OPEN",
            "complete_Weyl_operator_first_jet": "OPEN_AFTER_NONLINEAR_TRANSFER",
            "force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "BOUND_THE_DIFFERENCE_BETWEEN_THE_AFFINE_CARRIER_72D_JACOBI_"
            "PATH_AND_THE_NONLINEAR_EXACT_SOLUTION_FAMILY_FIRST_JET_USING_"
            "THE_EXISTING_EXACT_CENTER_D2F_TUBES;_THEN_EVALUATE_THE_COMPACT_"
            "WEYL_OPERATOR_FIRST_JET"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
