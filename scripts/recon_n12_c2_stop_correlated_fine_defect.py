"""Transport the DOP853 defect with the signed correlated Green operator.

For ``d = y_hat' - F(y_hat)``, the center-to-exact correction obeys
``e' = J e - d + N(e)``.  This reconnaissance script keeps that minus sign,
propagates each three-point Gauss source through a fine constant-generator
variation-of-constants step, and only projects to the 73-dimensional
constraint tangent at the established macro seams.  It does not supply the
between-node Jacobian remainder needed for interval authority.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import math

import numpy as np
from scipy.sparse.linalg import expm_multiply


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
JACOBIAN_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_JACOBIAN_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.npz"),
))
TANGENT_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_TANGENT_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"),
))
RESIDUAL_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_DENSE_RESIDUAL_DATA",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_DENSE_RESIDUAL_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_CORRELATED_DEFECT_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_CORRELATED_FINE_DEFECT_RECONNAISSANCE.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")


def _macro_index(time: float, action_lengths: np.ndarray) -> int:
    return min(
        int(np.searchsorted(action_lengths, time, side="right") - 1),
        action_lengths.size - 2,
    )


def _interpolated_jacobian(
    time: float, jacobian_times: np.ndarray, jacobians: np.ndarray,
) -> np.ndarray:
    index = _macro_index(time, jacobian_times)
    left = float(jacobian_times[index])
    right = float(jacobian_times[index + 1])
    fraction = min(max((time - left) / (right - left), 0.0), 1.0)
    return (1.0 - fraction) * jacobians[index] + fraction * jacobians[index + 1]


def _propagate(
    value: np.ndarray,
    left: float,
    right: float,
    maximum_step: float,
    jacobian_times: np.ndarray,
    jacobians: np.ndarray,
) -> np.ndarray:
    if right <= left:
        return value.copy()
    count = max(1, int(math.ceil((right - left) / maximum_step)))
    step = (right - left) / count
    result = value.copy()
    for substep in range(count):
        midpoint = left + (substep + 0.5) * step
        generator = _interpolated_jacobian(
            midpoint, jacobian_times, jacobians,
        )
        result = expm_multiply(step * generator, result)
    return result


def build_payload() -> dict[str, object]:
    with np.load(CENTER_DATA) as source:
        action_lengths = np.asarray(source["action_lengths"], dtype=float)
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(JACOBIAN_DATA) as source:
        jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
        descriptor_gradients = np.asarray(
            source["descriptor_gradient_action"], dtype=float,
        )
        jacobian_times = (
            np.asarray(source["action_lengths"], dtype=float)
            if "action_lengths" in source.files
            else action_lengths
        )
    if jacobians.shape[0] != jacobian_times.size:
        raise RuntimeError("Jacobian node count does not match its time grid")
    if jacobian_times.size < 2 or np.any(np.diff(jacobian_times) <= 0.0):
        raise RuntimeError("Jacobian time grid must be strictly increasing")
    if jacobian_times[0] > fine_times[0] or jacobian_times[-1] < action_lengths[-1]:
        raise RuntimeError("Jacobian time grid does not cover the center history")
    with np.load(TANGENT_DATA) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
        terminal_descriptor = np.asarray(
            source["terminal_descriptor_physical"], dtype=float,
        )
    with np.load(RESIDUAL_DATA) as source:
        intervals = np.asarray(source["interval"], dtype=int)
        fractions = np.asarray(source["fraction"], dtype=float)
        residual = np.asarray(source["augmented_rate_residual"], dtype=float)

    interval_count = int(np.max(intervals)) + 1
    if residual.shape[0] % interval_count != 0 or residual.shape[1] != 99:
        raise RuntimeError("equal Gauss samples on every fine interval required")
    samples_per_interval = residual.shape[0] // interval_count
    fine_step = float(fine_times[1] - fine_times[0])
    propagator_substeps = int(os.environ.get(
        "BHSM_N12_FINE_PROPAGATOR_SUBSTEPS", "1",
    ))
    if propagator_substeps < 1:
        raise ValueError("positive fine propagator substep count required")
    maximum_propagator_step = fine_step / propagator_substeps
    gauss_nodes, gauss_weights = np.polynomial.legendre.leggauss(
        samples_per_interval
    )
    expected_unit = 0.5 * (gauss_nodes + 1.0)

    correction = np.zeros(98)
    fundamental = tangents[0].copy()
    correction_profile = [correction.copy()]
    fine_correction_profile = [correction.copy()]
    fine_descriptor_correction_profile = [0.0]
    fine_correction_times = [float(fine_times[0])]
    fine_propagated_sources = []
    macro_step_maps = []
    tangent_leakage = []
    direct_descriptor_correction = 0.0
    next_macro = 1
    for interval in range(interval_count):
        mask = intervals == interval
        local_residual = residual[mask]
        local_fractions = fractions[mask]
        right_fraction = stop_fraction if interval == interval_count - 1 else 1.0
        if not np.allclose(local_fractions, right_fraction * expected_unit):
            raise RuntimeError("residual samples do not match the retained Gauss rule")
        duration = fine_step * right_fraction
        left_time = float(fine_times[interval])
        propagated_source = np.zeros(98)
        for unit, weight, sample_residual in zip(
            local_fractions / right_fraction,
            gauss_weights,
            local_residual,
            strict=True,
        ):
            propagated_source -= (
                0.5 * duration * weight
                * _propagate(
                    sample_residual[:-1],
                    left_time + float(unit) * duration,
                    left_time + duration,
                    maximum_propagator_step,
                    jacobian_times,
                    jacobians,
                )
            )
            direct_descriptor_correction -= (
                0.5 * duration * weight * float(sample_residual[-1])
            )
        fine_propagated_sources.append(propagated_source.copy())
        correction = _propagate(
            correction, left_time, left_time + duration,
            maximum_propagator_step, jacobian_times, jacobians,
        ) + propagated_source
        fundamental = _propagate(
            fundamental, left_time, left_time + duration,
            maximum_propagator_step, jacobian_times, jacobians,
        )

        right_time = left_time + duration
        if (
            next_macro < action_lengths.size
            and abs(right_time - float(action_lengths[next_macro])) < 1.0e-9
        ):
            target = tangents[next_macro]
            physical_map = target.T @ fundamental
            leakage = float(np.linalg.norm(
                fundamental - target @ physical_map, ord=2,
            ))
            tangent_leakage.append(leakage)
            macro_step_maps.append(physical_map)
            correction = target @ (target.T @ correction)
            correction_profile.append(correction.copy())
            fundamental = target.copy()
            next_macro += 1
        right_descriptor_gradient = np.asarray([
            np.interp(
                right_time, jacobian_times, descriptor_gradients[:, column],
            )
            for column in range(descriptor_gradients.shape[1])
        ])
        fine_correction_profile.append(correction.copy())
        fine_descriptor_correction_profile.append(float(
            right_descriptor_gradient @ correction
            + direct_descriptor_correction
        ))
        fine_correction_times.append(right_time)

    if next_macro != action_lengths.size:
        raise RuntimeError("fine grid did not land on every retained macro seam")
    terminal_physical = tangents[-1].T @ correction
    state_descriptor_correction = float(
        terminal_descriptor @ terminal_physical
    )
    combined = state_descriptor_correction + direct_descriptor_correction
    tangent_payload = json.loads(
        TANGENT_DATA.with_suffix(".json").read_text(encoding="utf-8")
    )
    crossing = float(tangent_payload["summary"][
        "terminal_descriptor_crossing_on_physical_tangent"
    ])
    time_shift = -combined / crossing

    np.savez_compressed(
        DATA_RESULT,
        ambient_correction_profile=np.asarray(correction_profile),
        fine_action_lengths=np.asarray(fine_correction_times),
        fine_ambient_correction_profile=np.asarray(fine_correction_profile),
        fine_descriptor_correction_profile=np.asarray(
            fine_descriptor_correction_profile,
        ),
        fine_propagated_sources=np.asarray(fine_propagated_sources),
        terminal_physical_correction=terminal_physical,
        physical_macro_step_maps=np.asarray(macro_step_maps),
        macro_tangent_leakage=np.asarray(tangent_leakage),
    )
    summary = {
        "fine_intervals": interval_count,
        "Gauss_samples_per_interval": samples_per_interval,
        "fine_action_step": fine_step,
        "fine_propagator_substeps": propagator_substeps,
        "maximum_ambient_correction_profile_2_norm": float(np.max(
            np.linalg.norm(correction_profile, axis=1)
        )),
        "terminal_physical_state_correction_2_norm": float(
            np.linalg.norm(terminal_physical)
        ),
        "maximum_macro_tangent_leakage_operator_2_norm": float(
            np.max(tangent_leakage)
        ),
        "state_induced_terminal_s_correction": state_descriptor_correction,
        "direct_descriptor_correction": direct_descriptor_correction,
        "combined_terminal_s_correction": combined,
        "terminal_descriptor_crossing": crossing,
        "linearized_stop_time_shift": time_shift,
    }
    source_norms = np.linalg.norm(np.asarray(fine_propagated_sources), axis=1)
    source_owner = int(np.argmax(source_norms))
    summary["maximum_fine_propagated_source_2_norm"] = float(
        source_norms[source_owner]
    )
    summary["maximum_fine_propagated_source_owner_interval"] = source_owner
    return {
        "artifact": "BHSM_N12_C2_STOP_CORRELATED_FINE_DEFECT_RECONNAISSANCE",
        "authority": "SIGNED_FINE_GREEN_CENTER_DIAGNOSTIC_NOT_INTERVAL_AUTHORITY",
        "identity": {
            "defect": "d=y_hat_prime-F(y_hat)",
            "shadow_equation": "e_prime=J*e-d+N(e)",
            "source_sign": "MINUS_DEFECT",
            "fine_propagator": (
                "PIECEWISE_MIDPOINT_EXPONENTIAL_PRODUCT_ON_THE_"
                f"DOP853_INTERVAL_WITH_{propagator_substeps}_SUBSTEPS"
            ),
            "Jacobian_grid_nodes": int(jacobian_times.size),
            "constraint_handling": "PROJECT_ONLY_AT_THE_47_RETAINED_MACRO_SEAMS",
        },
        "summary": summary,
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "validation_passed": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
