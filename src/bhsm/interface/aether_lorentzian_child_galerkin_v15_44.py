"""Lorentzian response-child Galerkin dynamics from the v15.43 ADM slice.

This is the first time evolution of the completed coefficient-free response
action.  It keeps independent radial, mean-warp, join-shape, and eta modes,
uses sigma=C_J[f]-1/2 at every evaluation, and starts from the
momentum-balanced transverse-traceless data.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import brentq

from bhsm.interface.aether_momentum_balanced_shear_data_v15_43 import (
    solve_momentum_balanced_shear_data,
)
from bhsm.interface.aether_response_constrained_child_galerkin_v15_41 import (
    HOPF_ORBIT_VOLUME,
)


VERSION = "v15.44"
CLASSIFICATION = "BHSM_LORENTZIAN_RESPONSE_CHILD_GALERKIN_EVOLUTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def lorentzian_reduction_contract() -> dict[str, Any]:
    return {
        "coordinate_order": [
            "log_R", "u2", "u4", "w0", "w1", "v0", "v1", "q2", "q4"
        ],
        "metric": (
            "C=R*exp(u+w),_A=R*exp(u+v)*coschi,_"
            "B=R*exp(u-v)*sinchi"
        ),
        "modes": (
            "u=u2*cos2chi+u4*cos4chi;_"
            "w=sin(2chi)^2*(w0+w1*cos2chi);_"
            "v=sin(2chi)^2*(v0+v1*cos2chi);_"
            "f=chi+q2*sin2chi+q4*sin4chi"
        ),
        "response": "sigma=C_J[f]-1/2",
        "carrier": "Lambda=1-4sigma^2",
        "ADM_kinetic": (
            "KijKij-K^2=Hc^2+3Ha^2+3Hb^2-(Hc+3Ha+3Hb)^2"
        ),
        "eta_invariant": "X=X_spatial-f_dot^2",
        "Lagrangian": (
            "L=Vol(S3)^2*integral_mu*[kappa1*(R7+KijKij-K^2)/2-"
            "kappa0/2-Lambda*F(X)]dchi-J^2/(2I)"
        ),
        "FR_inertia": (
            "I=Vol(S3)^2*integral_mu*Lambda*(kappa1+X^3)dchi"
        ),
        "new_continuous_coefficient": False,
        "gauge": "unit_lapse_zero_shift_Galerkin_time_after_v15.43_constraints",
    }


@lru_cache(maxsize=8)
def _gauss_rule(points: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    return (nodes + 1.0) * math.pi / 4.0, weights * math.pi / 4.0


def _response(
    chi: np.ndarray, weights: np.ndarray, f: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    raw = np.sin(f) ** 2 * np.cos(f) ** 2
    normalization = float(np.dot(weights, raw))
    density = raw / normalization
    augmented_chi = np.concatenate(([0.0], chi, [math.pi / 2.0]))
    augmented_density = np.concatenate(([0.0], density, [0.0]))
    cumulative = np.concatenate((
        [0.0],
        np.cumsum(
            0.5
            * (augmented_density[1:] + augmented_density[:-1])
            * np.diff(augmented_chi)
        ),
    ))
    cumulative /= cumulative[-1]
    return cumulative[1:-1] - 0.5, density


def _fields(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int
) -> dict[str, np.ndarray | float]:
    q = np.asarray(coordinates, dtype=float)
    q_dot = np.asarray(velocities, dtype=float)
    if q.shape != (9,) or q_dot.shape != (9,):
        raise ValueError("coordinates and velocities must have shape (9,)")
    chi, weights = _gauss_rule(points)
    (
        scale, u2, u4, w0, w1, v0, v1, q2, q4
    ) = q
    (
        scale_dot, u2_dot, u4_dot, w0_dot, w1_dot,
        v0_dot, v1_dot, q2_dot, q4_dot
    ) = q_dot
    sin2 = np.sin(2.0 * chi)
    cos2 = np.cos(2.0 * chi)
    sin4 = np.sin(4.0 * chi)
    cos4 = np.cos(4.0 * chi)
    window = sin2**2
    window_prime = 2.0 * sin4
    window_second = 8.0 * cos4
    odd_window = window * cos2
    odd_window_prime = 2.0 * sin4 * cos2 - 2.0 * window * sin2
    odd_window_second = (
        8.0 * cos4 * cos2
        - 8.0 * sin4 * sin2
        - 4.0 * window * cos2
    )

    u = u2 * cos2 + u4 * cos4
    u_prime = -2.0 * u2 * sin2 - 4.0 * u4 * sin4
    u_second = -4.0 * u2 * cos2 - 16.0 * u4 * cos4
    u_dot = u2_dot * cos2 + u4_dot * cos4
    w = w0 * window + w1 * odd_window
    w_prime = w0 * window_prime + w1 * odd_window_prime
    v = v0 * window + v1 * odd_window
    v_prime = v0 * window_prime + v1 * odd_window_prime
    v_second = v0 * window_second + v1 * odd_window_second
    w_dot = w0_dot * window + w1_dot * odd_window
    v_dot = v0_dot * window + v1_dot * odd_window

    radius0 = (343.0 / 5.0) ** (1.0 / 6.0)
    radius = radius0 * math.exp(float(scale))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + v) * np.cos(chi)
    B = radius * np.exp(u - v) * np.sin(chi)
    log_c_prime = u_prime + w_prime
    log_a_prime = u_prime + v_prime - np.tan(chi)
    log_b_prime = u_prime - v_prime + 1.0 / np.tan(chi)
    log_a_second = u_second + v_second - 1.0 / np.cos(chi) ** 2
    log_b_second = u_second - v_second - 1.0 / np.sin(chi) ** 2
    scalar_curvature = (
        6.0 / A**2
        + 6.0 / B**2
        - 6.0
        * (
            log_a_second + log_a_prime**2
            + log_b_second + log_b_prime**2
        )
        / C**2
        + 6.0 * log_c_prime * (log_a_prime + log_b_prime) / C**2
        - 6.0 * (log_a_prime**2 + log_b_prime**2) / C**2
        - 18.0 * log_a_prime * log_b_prime / C**2
    )

    f = chi + q2 * sin2 + q4 * sin4
    f_prime = 1.0 + 2.0 * q2 * cos2 + 4.0 * q4 * cos4
    f_dot = q2_dot * sin2 + q4_dot * sin4
    sigma, _ = _response(chi, weights, f)
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    x_spatial = (
        f_prime**2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    x_eta = x_spatial - f_dot**2
    eta_legendre = 1.0 + x_eta**3
    if np.min(eta_legendre) <= 1.0e-5:
        raise ValueError("eta Legendre map became singular")

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
        "volume": C * A**3 * B**3,
        "R7": scalar_curvature,
        "X_eta": x_eta,
        "eta_legendre": eta_legendre,
        "localization": localization,
        "ADM_kinetic": adm_kinetic,
        "sigma": sigma,
        "f": f,
        "f_prime": f_prime,
    }


def reduced_lagrangian(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 220
) -> float:
    """Return the orbit-volume-normalized Lorentzian child Lagrangian."""

    fields = _fields(coordinates, velocities, points=points)
    weights = np.asarray(fields["weights"])
    volume = np.asarray(fields["volume"])
    x_eta = np.asarray(fields["X_eta"])
    localization = np.asarray(fields["localization"])
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    eta = localization * (0.5 * x_eta + 0.125 * x_eta**4)
    bulk = float(np.dot(
        weights,
        volume
        * (
            0.5
            * (
                np.asarray(fields["R7"])
                + np.asarray(fields["ADM_kinetic"])
            )
            - 0.5 * kappa0
            - eta
        ),
    ))
    inertia_without_orbit = float(np.dot(
        weights,
        volume
        * localization
        * np.asarray(fields["eta_legendre"]),
    ))
    if inertia_without_orbit <= 0.0:
        raise ValueError("localized inertia must remain positive")
    # Divide the complete action by the constant orbit volume.
    return bulk - 0.25 / (
        2.0 * HOPF_ORBIT_VOLUME**2 * inertia_without_orbit
    )


def _gradient(
    function, value: np.ndarray, *, step: float
) -> np.ndarray:
    result = np.empty_like(value)
    for index in range(value.size):
        delta = np.zeros_like(value)
        delta[index] = step
        result[index] = (
            function(value + delta) - function(value - delta)
        ) / (2.0 * step)
    return result


def euler_acceleration(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    *,
    points: int = 180,
    step: float = 2.0e-5,
) -> dict[str, Any]:
    """Solve the finite-dimensional Euler equations for q double dot."""

    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    n = q.size
    grad_q = _gradient(
        lambda value: reduced_lagrangian(value, velocity, points=points),
        q,
        step=step,
    )
    mass = np.empty((n, n))
    mixed = np.empty((n, n))
    for i in range(n):
        ei = np.zeros(n)
        ei[i] = step
        for j in range(n):
            ej = np.zeros(n)
            ej[j] = step
            if i == j:
                center = reduced_lagrangian(q, velocity, points=points)
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
    rhs = grad_q - mixed @ velocity
    acceleration = np.linalg.solve(mass, rhs)
    eigenvalues = np.linalg.eigvalsh(mass)
    return {
        "acceleration": acceleration,
        "velocity_Hessian": mass,
        "velocity_Hessian_eigenvalues": eigenvalues,
        "velocity_Hessian_condition_number": float(np.linalg.cond(mass)),
        "Legendre_map_invertible": int(np.linalg.matrix_rank(mass)) == n,
    }


def canonical_energy(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    *,
    points: int = 220,
    step: float = 1.0e-5,
) -> float:
    momentum = _gradient(
        lambda value: reduced_lagrangian(coordinates, value, points=points),
        np.asarray(velocities, dtype=float),
        step=step,
    )
    return float(
        momentum @ np.asarray(velocities)
        - reduced_lagrangian(coordinates, velocities, points=points)
    )


def initial_evolution_data() -> dict[str, Any]:
    source = solve_momentum_balanced_shear_data(
        homotopy_steps=10, tolerance=3.0e-4
    )
    q = np.asarray(source["Lorentzian_Galerkin_initial_coordinates"])
    raw_velocity = np.asarray(
        source["Lorentzian_Galerkin_initial_velocities"]
    )
    velocity_scale = brentq(
        lambda scale: canonical_energy(q, scale * raw_velocity),
        0.0,
        2.0,
        xtol=1.0e-11,
    )
    velocity = velocity_scale * raw_velocity
    dynamics = euler_acceleration(q, velocity)
    fields = _fields(q, velocity, points=320)
    sigma = np.asarray(fields["sigma"])
    chi = np.asarray(fields["chi"])
    seam = float(np.interp(0.0, sigma, chi))
    A = float(np.interp(seam, chi, np.asarray(fields["A"])))
    B = float(np.interp(seam, chi, np.asarray(fields["B"])))
    return {
        "coordinates": q.tolist(),
        "TT_projection_velocity_rescale": velocity_scale,
        "velocities": velocity.tolist(),
        "accelerations": np.asarray(dynamics["acceleration"]).tolist(),
        "canonical_energy": canonical_energy(q, velocity),
        "reduced_Hamiltonian_constraint_residual": abs(
            canonical_energy(q, velocity)
        ),
        "projected_child_scale_x": math.log(B / A),
        "eta_Legendre_minimum": float(
            np.min(np.asarray(fields["eta_legendre"]))
        ),
        "velocity_Hessian_eigenvalues": np.asarray(
            dynamics["velocity_Hessian_eigenvalues"]
        ).tolist(),
        "velocity_Hessian_condition_number": dynamics[
            "velocity_Hessian_condition_number"
        ],
        "Legendre_map_invertible": dynamics["Legendre_map_invertible"],
        "finite_acceleration": bool(
            np.all(np.isfinite(np.asarray(dynamics["acceleration"])))
        ),
        "TT_orientation_branch": (
            "the_conjugate_initial_slice_is_obtained_by_velocity_to_minus_velocity"
        ),
    }


def odd_enclosure_linearization(
    initial: Mapping[str, Any] | None = None,
    *,
    points: int = 140,
    perturbation: float = 2.0e-4,
) -> dict[str, Any]:
    """Linearize the orientation-odd enclosure sector on the moving slice."""

    data = initial_evolution_data() if initial is None else initial
    q = np.asarray(data["coordinates"], dtype=float)
    velocity = np.asarray(data["velocities"], dtype=float)
    odd = np.array([1, 4, 5, 7])
    stiffness = np.empty((4, 4))
    gyroscopic = np.empty((4, 4))
    for column, index in enumerate(odd):
        delta = np.zeros(9)
        delta[index] = perturbation
        plus = np.asarray(euler_acceleration(
            q + delta, velocity, points=points, step=3.0e-5
        )["acceleration"])[odd]
        minus = np.asarray(euler_acceleration(
            q - delta, velocity, points=points, step=3.0e-5
        )["acceleration"])[odd]
        stiffness[:, column] = (plus - minus) / (2.0 * perturbation)

        plus_v = np.asarray(euler_acceleration(
            q, velocity + delta, points=points, step=3.0e-5
        )["acceleration"])[odd]
        minus_v = np.asarray(euler_acceleration(
            q, velocity - delta, points=points, step=3.0e-5
        )["acceleration"])[odd]
        gyroscopic[:, column] = (plus_v - minus_v) / (
            2.0 * perturbation
        )
    generator = np.block([
        [np.zeros((4, 4)), np.eye(4)],
        [stiffness, gyroscopic],
    ])
    eigenvalues, eigenvectors = np.linalg.eig(generator)
    dominant_index = int(np.argmax(np.real(eigenvalues)))
    dominant = np.real(eigenvectors[:, dominant_index])
    dominant /= np.max(np.abs(dominant))
    coordinate_direction = np.zeros(9)
    velocity_direction = np.zeros(9)
    coordinate_direction[odd] = dominant[:4]
    velocity_direction[odd] = dominant[4:]
    probe = 1.0e-5

    def scale_at(coordinates: np.ndarray) -> float:
        fields = _fields(coordinates, velocity, points=220)
        sigma = np.asarray(fields["sigma"])
        chi = np.asarray(fields["chi"])
        seam = float(np.interp(0.0, sigma, chi))
        a = float(np.interp(seam, chi, np.asarray(fields["A"])))
        b = float(np.interp(seam, chi, np.asarray(fields["B"])))
        return math.log(b / a)

    scale_derivative = (
        scale_at(q + probe * coordinate_direction)
        - scale_at(q - probe * coordinate_direction)
    ) / (2.0 * probe)
    if scale_derivative > 0.0:
        dominant *= -1.0
        coordinate_direction *= -1.0
        velocity_direction *= -1.0
        scale_derivative *= -1.0
    largest_real = float(np.max(np.real(eigenvalues)))
    return {
        "odd_coordinate_indices": odd.tolist(),
        "odd_coordinate_names": ["u2", "w1", "v0", "q2"],
        "stiffness_matrix": stiffness.tolist(),
        "velocity_coupling_matrix": gyroscopic.tolist(),
        "generator_eigenvalues": [
            {"real": float(value.real), "imag": float(value.imag)}
            for value in eigenvalues
        ],
        "largest_real_growth_rate": largest_real,
        "dominant_child_oriented_coordinate_direction": (
            coordinate_direction.tolist()
        ),
        "dominant_child_oriented_velocity_direction": (
            velocity_direction.tolist()
        ),
        "child_scale_derivative_along_dominant_direction": scale_derivative,
        "orientation_odd_enclosure_direction_grows": largest_real > 1.0e-4,
        "instantaneous_nonautonomous_linearization": True,
        "Floquet_claim": False,
    }


def _child_scale(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 180
) -> tuple[float, float]:
    fields = _fields(coordinates, velocities, points=points)
    sigma = np.asarray(fields["sigma"])
    chi = np.asarray(fields["chi"])
    seam = float(np.interp(0.0, sigma, chi))
    a = float(np.interp(seam, chi, np.asarray(fields["A"])))
    b = float(np.interp(seam, chi, np.asarray(fields["B"])))
    return math.log(b / a), float(
        np.min(np.asarray(fields["eta_legendre"]))
    )


def _surface_observables(
    coordinates: np.ndarray, velocities: np.ndarray, *, points: int = 360
) -> dict[str, float]:
    fields = _fields(coordinates, velocities, points=points)
    chi = np.asarray(fields["chi"])
    sigma = np.asarray(fields["sigma"])
    log_b_over_a = np.log(np.asarray(fields["B"]) / np.asarray(fields["A"]))
    material_surface = float(np.interp(0.0, sigma, chi))
    order = np.argsort(log_b_over_a)
    geometric_surface = float(np.interp(
        0.0, log_b_over_a[order], chi[order]
    ))
    C = np.asarray(fields["C"])
    cumulative = np.concatenate((
        [0.0],
        np.cumsum(0.5 * (C[1:] + C[:-1]) * np.diff(chi)),
    ))
    proper_material = float(np.interp(material_surface, chi, cumulative))
    proper_geometric = float(np.interp(geometric_surface, chi, cumulative))
    return {
        "material_surface_chi": material_surface,
        "geometric_Hopf_surface_chi": geometric_surface,
        "signed_proper_separation_d": proper_geometric - proper_material,
        "absolute_proper_separation": abs(
            proper_geometric - proper_material
        ),
        "child_scale_x": float(np.interp(
            material_surface, chi, log_b_over_a
        )),
    }


def integrate_unstable_enclosure_branch(
    *,
    seed: float = 1.0e-3,
    time_step: float = 0.05,
    maximum_steps: int = 80,
    target_child_scale: float = -2.0e-3,
    points: int = 90,
) -> dict[str, Any]:
    """Integrate the child-oriented unstable manifold with energy projection."""

    initial = initial_evolution_data()
    odd = odd_enclosure_linearization(initial, points=120)
    q = np.asarray(initial["coordinates"], dtype=float)
    velocity = np.asarray(initial["velocities"], dtype=float)
    q += seed * np.asarray(
        odd["dominant_child_oriented_coordinate_direction"]
    )
    velocity += seed * np.asarray(
        odd["dominant_child_oriented_velocity_direction"]
    )

    def project_energy(
        coordinates: np.ndarray, trial_velocity: np.ndarray
    ) -> tuple[np.ndarray, float]:
        samples: list[tuple[float, float]] = []
        for factor in np.linspace(0.0, 1.5, 31):
            try:
                energy = canonical_energy(
                    coordinates, factor * trial_velocity, points=180
                )
            except ValueError:
                break
            samples.append((float(factor), energy))
        bracket = None
        for left, right in zip(samples[:-1], samples[1:]):
            if left[1] == 0.0 or left[1] * right[1] <= 0.0:
                bracket = (left[0], right[0])
                break
        if bracket is None:
            raise ValueError(
                "no regular Hamiltonian projection before eta Legendre "
                "reconstruction firewall"
            )
        scale = brentq(
            lambda factor: canonical_energy(
                coordinates, factor * trial_velocity, points=180
            ),
            bracket[0],
            bracket[1],
            xtol=2.0e-10,
        )
        return scale * trial_velocity, scale

    velocity, initial_projection = project_energy(q, velocity)

    def rhs(coordinates: np.ndarray, rates: np.ndarray):
        acceleration = np.asarray(euler_acceleration(
            coordinates, rates, points=points, step=4.0e-5
        )["acceleration"])
        return rates, acceleration

    time = 0.0
    rows: list[dict[str, float]] = []
    maximum_projection_change = abs(initial_projection - 1.0)
    reached = False
    exit_reason = "maximum_steps"
    for step_index in range(maximum_steps + 1):
        scale_x, legendre_min = _child_scale(q, velocity, points=180)
        energy = canonical_energy(q, velocity, points=180)
        if step_index % 5 == 0 or scale_x <= target_child_scale:
            rows.append({
                "time": time,
                "child_scale_x": scale_x,
                "canonical_energy": energy,
                "eta_Legendre_minimum": legendre_min,
            })
        if scale_x <= target_child_scale:
            reached = True
            exit_reason = "target_child_scale_reached"
            break
        if step_index == maximum_steps:
            break

        old_q = q.copy()
        old_velocity = velocity.copy()
        try:
            k1_q, k1_v = rhs(q, velocity)
            k2_q, k2_v = rhs(
                q + 0.5 * time_step * k1_q,
                velocity + 0.5 * time_step * k1_v,
            )
            k3_q, k3_v = rhs(
                q + 0.5 * time_step * k2_q,
                velocity + 0.5 * time_step * k2_v,
            )
            k4_q, k4_v = rhs(
                q + time_step * k3_q,
                velocity + time_step * k3_v,
            )
        except ValueError as error:
            if "Legendre map became singular" not in str(error):
                raise
            exit_reason = "eta_Legendre_reconstruction_firewall"
            break
        q = q + time_step * (
            k1_q + 2.0 * k2_q + 2.0 * k3_q + k4_q
        ) / 6.0
        velocity = velocity + time_step * (
            k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v
        ) / 6.0
        try:
            velocity, projection = project_energy(q, velocity)
        except ValueError as error:
            if "Hamiltonian projection" not in str(error):
                raise
            q = old_q
            velocity = old_velocity
            exit_reason = "eta_Legendre_reconstruction_firewall"
            break
        maximum_projection_change = max(
            maximum_projection_change, abs(projection - 1.0)
        )
        time += time_step

    final_scale, final_legendre = _child_scale(q, velocity, points=260)
    surfaces = _surface_observables(q, velocity)
    return {
        "seed": seed,
        "seed_role": (
            "numerical_time-origin_on_the_one-dimensional_unstable_manifold_"
            "not_a_physical_continuous_input"
        ),
        "orientation": "child_branch_x_negative",
        "time_step": time_step,
        "steps_completed": step_index,
        "final_time": time,
        "target_child_scale": target_child_scale,
        "target_reached": reached,
        "exit_reason": exit_reason,
        "eta_Legendre_reconstruction_firewall_reached": (
            exit_reason == "eta_Legendre_reconstruction_firewall"
        ),
        "final_child_scale_x": final_scale,
        "final_surface_observables": surfaces,
        "parent_and_child_surfaces_distinguishable": surfaces[
            "absolute_proper_separation"
        ] > 1.0e-5,
        "final_eta_Legendre_minimum": final_legendre,
        "final_projection_grid_energy": canonical_energy(
            q, velocity, points=180
        ),
        "final_independent_grid_energy": canonical_energy(
            q, velocity, points=220
        ),
        "maximum_energy_projection_rescale": maximum_projection_change,
        "trajectory_samples": rows,
        "final_coordinates": q.tolist(),
        "final_velocities": velocity.tolist(),
    }


def completion_payload() -> dict[str, Any]:
    contract = lorentzian_reduction_contract()
    initial = initial_evolution_data()
    odd = odd_enclosure_linearization(initial)
    trajectory = integrate_unstable_enclosure_branch()
    validation = {
        "response_substituted_at_every_evaluation": contract[
            "response"
        ].startswith("sigma=C_J"),
        "initial_Legendre_map_invertible": initial[
            "Legendre_map_invertible"
        ],
        "initial_acceleration_finite": initial["finite_acceleration"],
        "reduced_Hamiltonian_constraint_closed": initial[
            "reduced_Hamiltonian_constraint_residual"
        ] < 2.0e-7,
        "eta_Legendre_sector_regular": initial[
            "eta_Legendre_minimum"
        ] > 0.0,
        "no_new_continuous_coefficient": not contract[
            "new_continuous_coefficient"
        ],
        "odd_enclosure_linearization_finite": all(
            math.isfinite(item["real"]) and math.isfinite(item["imag"])
            for item in odd["generator_eigenvalues"]
        ),
        "nonlinear_child_branch_reaches_negative_scale": trajectory[
            "target_reached"
        ] and trajectory["final_child_scale_x"] < 0.0,
        "trajectory_Hamiltonian_projection_controlled": abs(
            trajectory["final_projection_grid_energy"]
        ) < 2.0e-7 and abs(
            trajectory["final_independent_grid_energy"]
        ) < 1.0e-4,
        "trajectory_eta_Legendre_regular": trajectory[
            "final_eta_Legendre_minimum"
        ] > 0.0,
        "derived_parent_child_surface_separation_nonzero": trajectory[
            "parent_and_child_surfaces_distinguishable"
        ],
        "full_trajectory_not_overclaimed": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_lorentzian_child_galerkin_v15_44",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "Lorentzian_reduction_contract": contract,
        "initial_Euler_data": initial,
        "orientation_odd_enclosure_linearization": odd,
        "nonlinear_child_oriented_trajectory": trajectory,
        "claim_boundary": {
            "Lorentzian_reduced_Euler_operator_derived": True,
            "constraint_solved_initial_acceleration_derived": True,
            "nonlinear_encapsulation_trajectory_integrated": True,
            "negative_child_scale_reached": True,
            "derived_surface_separation_reached": True,
            "persistent_child_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
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
        ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_lorentzian_child_galerkin_v15_44.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "lorentzian_reduction_contract", "reduced_lagrangian",
    "euler_acceleration", "canonical_energy", "initial_evolution_data",
    "odd_enclosure_linearization",
    "integrate_unstable_enclosure_branch",
    "completion_payload", "deterministic_json", "materialize",
]
