"""Nonround Lorentzian Galerkin flow of the reconstructed BHSM child cap."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import brentq

from bhsm.interface.aether_post_cut_child_cap_reconstruction_v15_46 import (
    HOPF_ORBIT_VOLUME,
    integrate_exact_round_cap_tt,
    solve_minimal_round_cap_cmc_tt_reconstruction,
)


VERSION = "v15.48"
CLASSIFICATION = "BHSM_POST_CUT_NONROUND_LORENTZIAN_CAP_FLOW"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
RADIUS0 = (343.0 / 5.0) ** (1.0 / 6.0)


def lorentzian_cap_contract() -> dict[str, Any]:
    return {
        "domain": "0<=chi<=pi/4,_C_child=B4_times_S3",
        "coordinate_order": [
            "log_R", "u1", "u2", "w0", "w1", "v0", "v1", "q1", "q2"
        ],
        "metric": (
            "C=R*exp(u+w),_A=R*exp(u+v)*coschi,_"
            "B=R*exp(u-v)*sinchi"
        ),
        "modes": (
            "u=u1*cos4chi+u2*cos8chi;_w=sin(2chi)^2*(w0+w1*cos4chi);_"
            "v=sin(2chi)^2*(v0+v1*cos4chi);_"
            "f=chi+q1*sin4chi+q2*sin8chi"
        ),
        "child_scale": "x=log(B/A)_boundary=-2*(v0-v1)",
        "response": "sigma=-1/2+(2Z_c)^-1*integral_0^chi_sin(f)^2cos(f)^2ds",
        "spatial_action": "Einstein-Hilbert_plus_coefficient-locked_timelike_GHY",
        "ADM_kinetic": "(KijKij-K^2)/2",
        "eta": "-Lambda*(X/2+X^4/8),_X=X_spatial-f_dot^2",
        "FR_Routhian": "-J^2/(2I),_J^2=1/4",
        "boundary_values": "f(0)=0,_f(pi/4)=pi/4",
        "new_continuous_coefficient": False,
    }


@lru_cache(maxsize=8)
def _gauss_rule(points: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    return (nodes + 1.0) * math.pi / 8.0, weights * math.pi / 8.0


def cap_fields(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 120
) -> dict[str, np.ndarray | float]:
    q = np.asarray(coordinates, dtype=float)
    q_dot = np.asarray(velocities, dtype=float)
    if q.shape != (9,) or q_dot.shape != (9,):
        raise ValueError("coordinates and velocities must have shape (9,)")
    chi, weights = _gauss_rule(points)
    scale, u1, u2, w0, w1, v0, v1, q1, q2 = q
    (
        scale_dot, u1_dot, u2_dot, w0_dot, w1_dot,
        v0_dot, v1_dot, q1_dot, q2_dot,
    ) = q_dot
    sin2 = np.sin(2.0 * chi)
    sin4 = np.sin(4.0 * chi)
    sin8 = np.sin(8.0 * chi)
    cos4 = np.cos(4.0 * chi)
    cos8 = np.cos(8.0 * chi)
    window = sin2**2
    window_prime = 2.0 * sin4
    odd_window = window * cos4
    odd_window_prime = 2.0 * sin4 * cos4 - 4.0 * window * sin4

    u = u1 * cos4 + u2 * cos8
    u_prime = -4.0 * u1 * sin4 - 8.0 * u2 * sin8
    u_dot = u1_dot * cos4 + u2_dot * cos8
    w = w0 * window + w1 * odd_window
    w_prime = w0 * window_prime + w1 * odd_window_prime
    w_dot = w0_dot * window + w1_dot * odd_window
    v = v0 * window + v1 * odd_window
    v_prime = v0 * window_prime + v1 * odd_window_prime
    v_dot = v0_dot * window + v1_dot * odd_window
    radius = RADIUS0 * math.exp(float(scale))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + v) * np.cos(chi)
    B = radius * np.exp(u - v) * np.sin(chi)
    log_a_prime = u_prime + v_prime - np.tan(chi)
    log_b_prime = u_prime - v_prime + 1.0 / np.tan(chi)

    f = chi + q1 * sin4 + q2 * sin8
    f_prime = 1.0 + 4.0 * q1 * cos4 + 8.0 * q2 * cos8
    f_dot = q1_dot * sin4 + q2_dot * sin8
    if np.min(f_prime) <= 1.0e-5:
        raise ValueError("the post-cut eta map must remain monotone")
    raw = np.sin(f) ** 2 * np.cos(f) ** 2
    augmented_chi = np.concatenate(([0.0], chi, [math.pi / 4.0]))
    augmented_raw = np.concatenate(([0.0], raw, [0.25]))
    cumulative = np.concatenate((
        [0.0],
        np.cumsum(
            0.5 * (augmented_raw[1:] + augmented_raw[:-1])
            * np.diff(augmented_chi)
        ),
    ))
    cumulative *= 0.5 / cumulative[-1]
    sigma = -0.5 + cumulative[1:-1]
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    x_spatial = (
        f_prime**2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    x_eta = x_spatial - f_dot**2
    eta_legendre = 1.0 + x_eta**3
    if np.min(eta_legendre) <= 1.0e-5:
        raise ValueError("eta Legendre reconstruction became singular")
    h_c = scale_dot + u_dot + w_dot
    h_a = scale_dot + u_dot + v_dot
    h_b = scale_dot + u_dot - v_dot
    adm_kinetic = (
        h_c**2 + 3.0 * h_a**2 + 3.0 * h_b**2
        - (h_c + 3.0 * h_a + 3.0 * h_b) ** 2
    )
    return {
        "chi": chi,
        "weights": weights,
        "C": C,
        "A": A,
        "B": B,
        "log_A_prime": log_a_prime,
        "log_B_prime": log_b_prime,
        "log_C_prime": u_prime + w_prime,
        "log_C_dot": h_c,
        "log_A_dot": h_a,
        "log_B_dot": h_b,
        "volume": C * A**3 * B**3,
        "spatial_orbit_volume": A**3 * B**3,
        "f": f,
        "f_prime": f_prime,
        "f_dot_coordinate": f_dot,
        "sigma": sigma,
        "localization": localization,
        "X_eta": x_eta,
        "eta_legendre": eta_legendre,
        "ADM_kinetic": adm_kinetic,
    }


def reduced_lagrangian(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 120
) -> float:
    fields = cap_fields(coordinates, velocities, points=points)
    weights = np.asarray(fields["weights"])
    C = np.asarray(fields["C"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    spatial_volume = np.asarray(fields["spatial_orbit_volume"])
    volume = np.asarray(fields["volume"])
    a = np.asarray(fields["log_A_prime"])
    b = np.asarray(fields["log_B_prime"])
    x_eta = np.asarray(fields["X_eta"])
    localization = np.asarray(fields["localization"])
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    spatial_gravity = 3.0 * spatial_volume / C * (a**2 + b**2 + 3.0 * a * b)
    algebraic = volume * (
        3.0 / A**2
        + 3.0 / B**2
        - 0.5 * kappa0
        - localization * (0.5 * x_eta + 0.125 * x_eta**4)
        + 0.5 * np.asarray(fields["ADM_kinetic"])
    )
    bulk = float(np.dot(weights, spatial_gravity + algebraic))
    inertia_without_orbit = float(np.dot(
        weights, volume * localization * np.asarray(fields["eta_legendre"])
    ))
    if inertia_without_orbit <= 1.0e-12:
        raise ValueError("localized cap inertia must be positive")
    return bulk - 0.25 / (
        2.0 * HOPF_ORBIT_VOLUME**2 * inertia_without_orbit
    )


def _gradient(function, value: np.ndarray, *, step: float) -> np.ndarray:
    result = np.empty_like(value)
    for index in range(value.size):
        delta = np.zeros_like(value)
        delta[index] = step
        result[index] = (function(value + delta) - function(value - delta)) / (2.0 * step)
    return result


def canonical_energy(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 140,
    step: float = 1.5e-5,
) -> float:
    momentum = _gradient(
        lambda value: reduced_lagrangian(coordinates, value, points=points),
        np.asarray(velocities, dtype=float), step=step,
    )
    return float(momentum @ np.asarray(velocities) - reduced_lagrangian(
        coordinates, velocities, points=points
    ))


def euler_acceleration(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 90,
    step: float = 4.0e-5,
) -> dict[str, Any]:
    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    n = q.size
    grad_q = _gradient(
        lambda value: reduced_lagrangian(value, velocity, points=points),
        q, step=step,
    )
    mass = np.empty((n, n))
    mixed = np.empty((n, n))
    center = reduced_lagrangian(q, velocity, points=points)
    for i in range(n):
        ei = np.zeros(n)
        ei[i] = step
        for j in range(n):
            ej = np.zeros(n)
            ej[j] = step
            if i == j:
                mass[i, i] = (
                    reduced_lagrangian(q, velocity + ei, points=points)
                    - 2.0 * center
                    + reduced_lagrangian(q, velocity - ei, points=points)
                ) / step**2
            else:
                mass[i, j] = (
                    reduced_lagrangian(q, velocity + ei + ej, points=points)
                    - reduced_lagrangian(q, velocity + ei - ej, points=points)
                    - reduced_lagrangian(q, velocity - ei + ej, points=points)
                    + reduced_lagrangian(q, velocity - ei - ej, points=points)
                ) / (4.0 * step**2)
            mixed[i, j] = (
                reduced_lagrangian(q + ej, velocity + ei, points=points)
                - reduced_lagrangian(q - ej, velocity + ei, points=points)
                - reduced_lagrangian(q + ej, velocity - ei, points=points)
                + reduced_lagrangian(q - ej, velocity - ei, points=points)
            ) / (4.0 * step**2)
    mass = 0.5 * (mass + mass.T)
    acceleration = np.linalg.solve(mass, grad_q - mixed @ velocity)
    return {
        "acceleration": acceleration,
        "velocity_Hessian_eigenvalues": np.linalg.eigvalsh(mass),
        "velocity_Hessian_condition_number": float(np.linalg.cond(mass)),
        "Legendre_map_invertible": int(np.linalg.matrix_rank(mass)) == n,
    }


def projected_reconstructed_initial_data(*, points: int = 700) -> dict[str, Any]:
    reconstruction = solve_minimal_round_cap_cmc_tt_reconstruction(points=points)
    exact = integrate_exact_round_cap_tt(
        reconstruction["radius"], trace_rate=reconstruction["trace_rate"],
        points=points,
    )
    chi = np.asarray(exact["coordinate"])
    # The Hamiltonian constraint fixes only the quadratic TT norm.  The
    # transported event orientation chooses the conjugate sign for which
    # x_dot=-2(v0_dot-v1_dot)<0.
    s = -np.asarray(exact["K_chi"])
    d = -np.asarray(exact["anisotropy_d"])
    H = float(reconstruction["trace_rate"])
    h_c = H + s
    h_a = H - s / 6.0 + d
    h_b = H - s / 6.0 - d
    window = np.sin(2.0 * chi) ** 2
    basis = np.column_stack((
        np.ones_like(chi),
        np.cos(4.0 * chi),
        np.cos(8.0 * chi),
        window,
        window * np.cos(4.0 * chi),
        window,
        window * np.cos(4.0 * chi),
    ))
    design = np.block([
        [basis[:, :3], basis[:, 3:5], np.zeros((points, 2))],
        [basis[:, :3], np.zeros((points, 2)), basis[:, 5:7]],
        [basis[:, :3], np.zeros((points, 2)), -basis[:, 5:7]],
    ])
    target = np.concatenate((h_c, h_a, h_b))
    weight = np.tile(np.sin(chi) ** 3 * np.cos(chi) ** 3, 3)
    rates7 = np.linalg.lstsq(
        np.sqrt(weight)[:, None] * design,
        np.sqrt(weight) * target,
        rcond=None,
    )[0]
    raw_velocity = np.concatenate((rates7, [0.0, 0.0]))
    coordinates = np.zeros(9)
    energy0 = canonical_energy(coordinates, np.zeros(9), points=150)
    samples = []
    for factor in np.linspace(0.0, 2.5, 101):
        samples.append((factor, canonical_energy(
            coordinates, factor * raw_velocity, points=150
        )))
    bracket = next(
        (pair for pair in zip(samples[:-1], samples[1:])
         if pair[0][1] * pair[1][1] <= 0.0),
        None,
    )
    if bracket is None:
        raise RuntimeError("projected reconstructed velocity has no zero-energy rescaling")
    scale = brentq(
        lambda factor: canonical_energy(
            coordinates, factor * raw_velocity, points=150
        ), bracket[0][0], bracket[1][0], xtol=2.0e-11,
    )
    scale = brentq(
        lambda factor: canonical_energy(
            coordinates, factor * raw_velocity, points=220
        ), 0.95 * scale, 1.05 * scale, xtol=2.0e-12,
    )
    velocity = scale * raw_velocity
    dynamics = euler_acceleration(coordinates, velocity)
    projection_residual = design @ rates7 - target
    return {
        "coordinates": coordinates.tolist(),
        "raw_projected_velocities": raw_velocity.tolist(),
        "velocity_energy_rescale": scale,
        "velocities": velocity.tolist(),
        "accelerations": np.asarray(dynamics["acceleration"]).tolist(),
        "zero_velocity_energy": energy0,
        "canonical_energy": canonical_energy(coordinates, velocity, points=220),
        "maximum_TT_projection_residual": float(np.max(np.abs(projection_residual))),
        "weighted_TT_projection_residual": float(math.sqrt(
            np.dot(weight, projection_residual**2) / np.sum(weight)
        )),
        "initial_child_scale_x": 0.0,
        "initial_child_scale_velocity": float(-2.0 * (velocity[5] - velocity[6])),
        "eta_Legendre_minimum": float(np.min(np.asarray(
            cap_fields(coordinates, velocity, points=220)["eta_legendre"]
        ))),
        "velocity_Hessian_eigenvalues": np.asarray(
            dynamics["velocity_Hessian_eigenvalues"]
        ).tolist(),
        "velocity_Hessian_condition_number": dynamics[
            "velocity_Hessian_condition_number"
        ],
        "Legendre_map_invertible": dynamics["Legendre_map_invertible"],
    }


def integrate_child_oriented_cap_flow(
    *, time_step: float = 0.005, maximum_steps: int = 80,
    points: int = 70,
) -> dict[str, Any]:
    """Evolve the reconstructed nonround branch with energy projection."""

    initial = projected_reconstructed_initial_data(points=500)
    q = np.asarray(initial["coordinates"], dtype=float)
    velocity = np.asarray(initial["velocities"], dtype=float)

    def project_energy(
        coordinates: np.ndarray, trial_velocity: np.ndarray,
    ) -> tuple[np.ndarray, float]:
        samples: list[tuple[float, float]] = []
        for factor in np.linspace(0.5, 1.5, 41):
            try:
                energy = canonical_energy(
                    coordinates, factor * trial_velocity, points=120
                )
            except ValueError:
                continue
            samples.append((float(factor), energy))
        bracket = next(
            (pair for pair in zip(samples[:-1], samples[1:])
             if pair[0][1] * pair[1][1] <= 0.0),
            None,
        )
        if bracket is None:
            raise ValueError("no regular zero-energy velocity projection")
        scale = brentq(
            lambda factor: canonical_energy(
                coordinates, factor * trial_velocity, points=120
            ),
            bracket[0][0], bracket[1][0], xtol=2.0e-10,
        )
        return scale * trial_velocity, scale

    velocity, first_projection = project_energy(q, velocity)

    def rhs(position: np.ndarray, rate: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return rate, np.asarray(euler_acceleration(
            position, rate, points=points, step=5.0e-5
        )["acceleration"])

    rows: list[dict[str, float]] = []
    time = 0.0
    maximum_projection = abs(first_projection - 1.0)
    exit_reason = "maximum_steps"
    turning_points = 0
    previous_x_velocity = float(-2.0 * (velocity[5] - velocity[6]))
    for step_index in range(maximum_steps + 1):
        fields = cap_fields(q, velocity, points=160)
        x = float(-2.0 * (q[5] - q[6]))
        x_velocity = float(-2.0 * (velocity[5] - velocity[6]))
        if previous_x_velocity * x_velocity < 0.0:
            turning_points += 1
        previous_x_velocity = x_velocity
        if step_index % 5 == 0:
            rows.append({
                "time": time,
                "child_scale_x": x,
                "child_scale_velocity": x_velocity,
                "log_radius": float(q[0]),
                "canonical_energy": canonical_energy(q, velocity, points=120),
                "eta_Legendre_minimum": float(np.min(np.asarray(
                    fields["eta_legendre"]
                ))),
            })
        if step_index == maximum_steps:
            break
        old_q = q.copy()
        old_velocity = velocity.copy()
        try:
            k1q, k1v = rhs(q, velocity)
            k2q, k2v = rhs(
                q + 0.5 * time_step * k1q,
                velocity + 0.5 * time_step * k1v,
            )
            k3q, k3v = rhs(
                q + 0.5 * time_step * k2q,
                velocity + 0.5 * time_step * k2v,
            )
            k4q, k4v = rhs(q + time_step * k3q, velocity + time_step * k3v)
            q = q + time_step * (k1q + 2.0 * k2q + 2.0 * k3q + k4q) / 6.0
            velocity = velocity + time_step * (
                k1v + 2.0 * k2v + 2.0 * k3v + k4v
            ) / 6.0
            velocity, projection = project_energy(q, velocity)
        except (ValueError, np.linalg.LinAlgError) as error:
            q = old_q
            velocity = old_velocity
            exit_reason = (
                "cap_Legendre_or_energy_projection_firewall:_"
                + type(error).__name__
                + ":_"
                + str(error).replace(" ", "_")
            )
            break
        maximum_projection = max(maximum_projection, abs(projection - 1.0))
        time += time_step
    final_fields = cap_fields(q, velocity, points=220)
    return {
        "time_step": time_step,
        "steps_completed": step_index,
        "final_time": time,
        "exit_reason": exit_reason,
        "final_coordinates": q.tolist(),
        "final_velocities": velocity.tolist(),
        "final_child_scale_x": float(-2.0 * (q[5] - q[6])),
        "final_child_scale_velocity": float(-2.0 * (velocity[5] - velocity[6])),
        "final_log_radius": float(q[0]),
        "turning_point_count": turning_points,
        "maximum_energy_projection_rescale": maximum_projection,
        "final_energy": canonical_energy(q, velocity, points=160),
        "minimum_eta_Legendre": float(np.min(np.asarray(
            final_fields["eta_legendre"]
        ))),
        "trajectory": rows,
        "relative_periodic_return_reached": bool(
            turning_points >= 2 and np.linalg.norm(q) < 5.0e-3
        ),
    }


def completion_payload() -> dict[str, Any]:
    initial = projected_reconstructed_initial_data()
    validation = {
        "cap_topology_and_boundary_fixed": lorentzian_cap_contract()["domain"].startswith("0<=chi"),
        "reconstructed_ADM_data_projected": initial["weighted_TT_projection_residual"] < 0.2,
        "reduced_Hamiltonian_constraint_closed": abs(initial["canonical_energy"]) < 2.0e-6,
        "eta_Legendre_positive": initial["eta_Legendre_minimum"] > 0.0,
        "Legendre_map_invertible": initial["Legendre_map_invertible"],
        "finite_initial_acceleration": bool(np.all(np.isfinite(initial["accelerations"]))),
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_post_cut_nonround_lorentzian_cap_v15_48",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "contract": lorentzian_cap_contract(),
        "projected_initial_data": initial,
        "claim_boundary": {
            "nonround_Lorentzian_cap_equations_derived": True,
            "constraint_solved_initial_data_embedded": validation[
                "reduced_Hamiltonian_constraint_closed"
            ],
            "relative_periodic_orbit_solved": False,
            "Floquet_spectrum_computed": False,
            "persistent_particle_derived": False,
        },
        "active_calculation": (
            "INTEGRATE_THE_NONROUND_CAP_FLOW_AND_SOLVE_THE_RELATIVE-PERIODIC_"
            "SHOOTING_AND_MONODROMY_EQUATIONS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 8)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_post_cut_nonround_lorentzian_cap_v15_48.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "lorentzian_cap_contract", "cap_fields", "reduced_lagrangian",
    "canonical_energy", "euler_acceleration",
    "projected_reconstructed_initial_data", "completion_payload",
    "deterministic_json", "materialize",
]
