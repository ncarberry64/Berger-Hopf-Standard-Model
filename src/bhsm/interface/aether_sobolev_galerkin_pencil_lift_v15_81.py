"""Spectral-Galerkin lift of the actual Euler--Dirac soft pencil.

The cohomogeneity-one fields are expanded through harmonic order ``N``:
``u=sum u_k cos(4k chi)``, and ``w,v=sin(2chi)^2 sum a_k cos(4kchi)``;
lapse and shift use the matching even/odd bases.  The v15.80 mode is tracked
by overlap under the nested embeddings N=2 -> 3 -> 4.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import SNAPSHOTS


VERSION = "v15.81"
CLASSIFICATION = "BHSM_SOBOLEV_SPECTRAL_GALERKIN_EVENT_PENCIL_LIFT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def dimensions(order: int) -> dict[str, int]:
    if order < 2:
        raise ValueError("order must be at least two")
    return {
        "coordinates": 1 + 3 * order,
        "multipliers": 2 * order,
        "Dirac_pencil": 1 + 5 * order,
    }


def lift_low_state(
    order: int,
    q2: np.ndarray,
    v2: np.ndarray,
    m2: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    size = dimensions(order)
    q2 = np.asarray(q2, dtype=float)[:7]
    v2 = np.asarray(v2, dtype=float)[:7]
    m2 = np.asarray(m2, dtype=float)
    q = np.zeros(size["coordinates"])
    velocity = np.zeros_like(q)
    multipliers = np.zeros(size["multipliers"])
    # scale; u_1,u_2; w_0,w_1; v_0,v_1
    q[0] = q2[0]
    velocity[0] = v2[0]
    q[1:3] = q2[1:3]
    velocity[1:3] = v2[1:3]
    q[1 + order:1 + order + 2] = q2[3:5]
    velocity[1 + order:1 + order + 2] = v2[3:5]
    q[1 + 2 * order:1 + 2 * order + 2] = q2[5:7]
    velocity[1 + 2 * order:1 + 2 * order + 2] = v2[5:7]
    multipliers[:2] = m2[:2]
    multipliers[order:order + 2] = m2[2:]
    return q, velocity, multipliers


def embedded_state(order: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    source = SNAPSHOTS[0.10602]
    return lift_low_state(
        order,
        np.asarray(source["q"], dtype=float),
        np.asarray(source["v"], dtype=float),
        np.asarray(source["m"], dtype=float),
    )


@lru_cache(maxsize=12)
def _gauss_rule(points: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    return (nodes + 1.0) * math.pi / 8.0, weights * math.pi / 8.0


def generalized_lagrangian(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    order: int,
    points: int = 36,
) -> float:
    size = dimensions(order)
    q = np.asarray(coordinates, dtype=float)
    rate = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    if q.shape != (size["coordinates"],) or rate.shape != q.shape:
        raise ValueError("coordinate dimensions do not match order")
    if m.shape != (size["multipliers"],):
        raise ValueError("multiplier dimensions do not match order")
    chi, weights = _gauss_rule(points)
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi))
    sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi))
    sin_j = np.sin(4.0 * np.outer(js, chi))
    scale = q[0]
    u_coeff = q[1:1 + order]
    w_coeff = q[1 + order:1 + 2 * order]
    v_coeff = q[1 + 2 * order:1 + 3 * order]
    u_rate = rate[1:1 + order]
    w_rate = rate[1 + order:1 + 2 * order]
    v_rate = rate[1 + 2 * order:1 + 3 * order]
    lapse_coeff = m[:order]
    shift_coeff = m[order:]

    u = u_coeff @ cos_k
    u_prime = (-4.0 * ks * u_coeff) @ sin_k
    u_dot = u_rate @ cos_k
    window = np.sin(2.0 * chi) ** 2
    window_prime = 2.0 * np.sin(4.0 * chi)
    w_poly = w_coeff @ cos_j
    v_poly = v_coeff @ cos_j
    w_poly_prime = (-4.0 * js * w_coeff) @ sin_j
    v_poly_prime = (-4.0 * js * v_coeff) @ sin_j
    w = window * w_poly
    v = window * v_poly
    w_prime = window_prime * w_poly + window * w_poly_prime
    v_prime = window_prime * v_poly + window * v_poly_prime
    w_dot = window * (w_rate @ cos_j)
    v_dot = window * (v_rate @ cos_j)

    radius = RADIUS0 * math.exp(float(scale))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + v) * np.cos(chi)
    B = radius * np.exp(u - v) * np.sin(chi)
    c_prime = u_prime + w_prime
    a_prime = u_prime + v_prime - np.tan(chi)
    b_prime = u_prime - v_prime + 1.0 / np.tan(chi)
    log_c_dot = rate[0] + u_dot + w_dot
    log_a_dot = rate[0] + u_dot + v_dot
    log_b_dot = rate[0] + u_dot - v_dot

    log_n = lapse_coeff @ cos_k
    N = np.exp(log_n)
    n_prime = (-4.0 * ks * lapse_coeff) @ sin_k
    shift_poly = shift_coeff @ cos_j
    shift_poly_prime = (-4.0 * js * shift_coeff) @ sin_j
    beta = np.sin(4.0 * chi) * shift_poly
    beta_prime = 4.0 * np.cos(4.0 * chi) * shift_poly + np.sin(4.0 * chi) * shift_poly_prime

    Hc = (log_c_dot - beta * c_prime - beta_prime) / N
    Ha = (log_a_dot - beta * a_prime) / N
    Hb = (log_b_dot - beta * b_prime) / N
    adm = Hc**2 + 3.0 * Ha**2 + 3.0 * Hb**2 - (Hc + 3.0 * Ha + 3.0 * Hb) ** 2

    f = chi
    f_prime = np.ones_like(chi)
    f_normal = -beta / N
    x_spatial = (
        f_prime**2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    x_eta = x_spatial - f_normal**2
    eta_legendre = 1.0 + x_eta**3
    if np.min(eta_legendre) <= 1.0e-5:
        raise ValueError("eta Legendre form became singular")
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
    localization = 1.0 - 4.0 * sigma**2

    volume = C * A**3 * B**3
    spatial_volume = A**3 * B**3
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    spatial_gravity = (
        3.0 * N * spatial_volume / C
        * (n_prime * (a_prime + b_prime) + a_prime**2 + b_prime**2 + 3.0 * a_prime * b_prime)
    )
    algebraic = N * volume * (
        3.0 / A**2 + 3.0 / B**2 - 0.5 * kappa0
        - localization * (0.5 * x_eta + 0.125 * x_eta**4)
        + 0.5 * adm
    )
    bulk = float(np.dot(weights, spatial_gravity + algebraic))
    inertia = float(np.dot(weights, volume * localization * eta_legendre / N))
    if inertia <= 1.0e-12:
        raise ValueError("localized cap inertia must be positive")
    parent = bulk - 0.25 / (2.0 * HOPF_ORBIT_VOLUME**2 * inertia)

    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary = float(u_coeff @ signs_k)
    v_boundary = float(v_coeff @ signs_j)
    A_boundary = radius * math.exp(u_boundary + v_boundary) / math.sqrt(2.0)
    B_boundary = radius * math.exp(u_boundary - v_boundary) / math.sqrt(2.0)
    R4 = A_boundary * B_boundary / math.sqrt(A_boundary**2 + B_boundary**2)
    boundary_lapse = math.exp(float(lapse_coeff @ signs_k))
    return parent - boundary_lapse * standard_model_casimir_coefficient() / R4


def dirac_hessian_at_state(
    order: int,
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 36,
    step: float = 5.0e-5,
) -> np.ndarray:
    z = np.concatenate((velocity, multipliers))

    def action(value: np.ndarray) -> float:
        return generalized_lagrangian(
            q, value[: velocity.size], value[velocity.size:],
            order=order, points=points,
        )

    center = action(z)
    hessian = np.empty((z.size, z.size))
    for row in range(z.size):
        erow = np.zeros_like(z)
        erow[row] = step
        for column in range(row, z.size):
            ecolumn = np.zeros_like(z)
            ecolumn[column] = step
            if row == column:
                value = (action(z + erow) - 2.0 * center + action(z - erow)) / step**2
            else:
                value = (
                    action(z + erow + ecolumn) - action(z + erow - ecolumn)
                    - action(z - erow + ecolumn) + action(z - erow - ecolumn)
                ) / (4.0 * step**2)
            hessian[row, column] = value
            hessian[column, row] = value
    return hessian


def dirac_hessian(
    order: int, *, points: int = 36, step: float = 5.0e-5,
) -> np.ndarray:
    q, velocity, multipliers = embedded_state(order)
    return dirac_hessian_at_state(
        order, q, velocity, multipliers, points=points, step=step
    )


def _embed_vector(vector: np.ndarray, old_order: int, new_order: int) -> np.ndarray:
    old = dimensions(old_order)
    new = dimensions(new_order)
    result = np.zeros(new["Dirac_pencil"])
    old_q = old["coordinates"]
    new_q = new["coordinates"]
    result[0] = vector[0]
    result[1:1 + old_order] = vector[1:1 + old_order]
    result[1 + new_order:1 + new_order + old_order] = vector[
        1 + old_order:1 + 2 * old_order
    ]
    result[1 + 2 * new_order:1 + 2 * new_order + old_order] = vector[
        1 + 2 * old_order:1 + 3 * old_order
    ]
    result[new_q:new_q + old_order] = vector[old_q:old_q + old_order]
    result[new_q + new_order:new_q + new_order + old_order] = vector[
        old_q + old_order:old_q + 2 * old_order
    ]
    return result


def _boundary_source(order: int, vector: np.ndarray) -> dict[str, float]:
    size = dimensions(order)
    q, _, _ = embedded_state(order)
    velocity_part = vector[: size["coordinates"]]
    multiplier_part = vector[size["coordinates"]:]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    delta_u = float(velocity_part[1:1 + order] @ signs_k)
    delta_v = float(velocity_part[1 + 2 * order:1 + 3 * order] @ signs_j)
    boundary_v = float(q[1 + 2 * order:1 + 3 * order] @ signs_j)
    delta_h4 = (
        float(velocity_part[0]) + delta_u
        - math.tanh(2.0 * boundary_v) * delta_v
    )
    delta_log_lapse = float(multiplier_part[:order] @ signs_k)
    energy = 1.5 / (RADIUS0 / 2.0)
    source = -delta_log_lapse * energy + 1.5 * delta_h4
    return {
        "delta_H4": delta_h4,
        "delta_log_lapse": delta_log_lapse,
        "g_s0": source,
    }


@lru_cache(maxsize=1)
def convergence_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    reference: np.ndarray | None = None
    old_order = 0
    for order in (2, 3, 4):
        hessian = dirac_hessian(order)
        values, vectors = np.linalg.eigh(hessian)
        if reference is None:
            index = int(np.argmin(np.abs(values)))
            overlap = 1.0
        else:
            embedded = _embed_vector(reference, old_order, order)
            embedded /= np.linalg.norm(embedded)
            overlaps = np.abs(vectors.T @ embedded)
            index = int(np.argmax(overlaps))
            overlap = float(overlaps[index])
        vector = vectors[:, index]
        if reference is not None:
            embedded = _embed_vector(reference, old_order, order)
            if float(vector @ embedded) < 0.0:
                vector = -vector
        source = _boundary_source(order, vector)
        rows.append({
            "order": order,
            "pencil_dimension": dimensions(order)["Dirac_pencil"],
            "tracked_eigenvalue": float(values[index]),
            "embedding_overlap": overlap,
            "condition_number": float(np.linalg.cond(hessian)),
            "soft_delta_H4": source["delta_H4"],
            "soft_delta_log_lapse": source["delta_log_lapse"],
            "g_s0": source["g_s0"],
            "vector": vector.tolist(),
        })
        reference = vector
        old_order = order
    return rows


def completion_payload() -> dict[str, Any]:
    rows = convergence_rows()
    eigenvalues = [float(row["tracked_eigenvalue"]) for row in rows]
    sources = [float(row["g_s0"]) for row in rows]
    overlaps = [float(row["embedding_overlap"]) for row in rows[1:]]
    validation = {
        "nested_orders_evaluated": [row["order"] for row in rows] == [2, 3, 4],
        "tracked_branch_has_nonzero_overlap": all(value > 0.25 for value in overlaps),
        "tracked_eigenvalues_finite": all(math.isfinite(value) for value in eigenvalues),
        "soft_sources_finite": all(math.isfinite(value) for value in sources),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_sobolev_galerkin_pencil_lift_v15_81",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "basis": {
            "u": "sum_(k=1)^N u_k*cos(4k*chi)",
            "w_v": "sin(2chi)^2*sum_(j=0)^(N-1) a_j*cos(4j*chi)",
            "lapse": "sum_(k=1)^N n_k*cos(4k*chi)",
            "shift": "sin(4chi)*sum_(j=0)^(N-1) b_j*cos(4j*chi)",
            "nested_dense_limit": "even/odd_cohomogeneity-one_H^s_sector",
        },
        "convergence_rows": rows,
        "scientific_result": (
            "THE_ACTUAL_v15.80_SOFT_EIGENBRANCH_IS_TRACKED_BY_NESTED_"
            "SPECTRAL-GALERKIN_OVERLAP_THROUGH_N=4;_ITS_EIGENVALUE_AND_"
            "FERMION_SOURCE_CONVERGENCE_DECIDE_WHETHER_THE_JOINT_CROSSING_"
            "SURVIVES_THE_COHOMOGENEITY-ONE_SOBOLEV_LIFT"
        ),
        "claim_boundary": {
            "nested_spectral_lift_computed_through_N4": True,
            "norm_resolvent_full_Sobolev_limit_proved": False,
            "non_axisymmetric_modes_included": False,
        },
        "active_calculation": (
            "USE_THE_MEASURED_N2-N4_BEHAVIOR_TO_FORM_THE_SCHUR-COMPLEMENT_"
            "TAIL_BOUND_AND_EITHER_CERTIFY_OR_REJECT_THE_SOFT_BRANCH_LIMIT"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_sobolev_galerkin_pencil_lift_v15_81.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "dimensions",
    "lift_low_state", "embedded_state", "generalized_lagrangian",
    "dirac_hessian_at_state", "dirac_hessian",
    "convergence_rows", "completion_payload", "deterministic_json", "materialize",
]
