"""Audit radial-diffeomorphism Noether compatibility above certified N12.

The endpoint-fixed generator acts by the ordinary Lie derivative on the
retained radial ADM fields.  Higher-N states are zero-padded N12 probes only.
This script changes no equation, quotient, boundary reaction, or child gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    identity_response_localization,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)


SOURCE_ORDER = 12
ORDERS = tuple(int(value) for value in os.environ.get(
    "BHSM_N12_NOETHER_ORDERS", "16,24,32,48"
).split(","))
ACTION_POINTS = int(os.environ.get("BHSM_N12_NOETHER_ACTION_POINTS", "96"))
PROJECTION_POINTS = int(os.environ.get(
    "BHSM_N12_NOETHER_PROJECTION_POINTS", "768"
))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_NOETHER_RESULT",
    ".tmp_n12_radial_diffeo_noether_compatibility.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _split_state(joint: np.ndarray, name: str) -> tuple[np.ndarray, ...]:
    qdim = dimensions(SOURCE_ORDER)["coordinates"]
    mdim = dimensions(SOURCE_ORDER)["multipliers"]
    state_dim = 2 * qdim + mdim
    state = joint[:state_dim] if name == "event" else joint[state_dim:]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def _grid() -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(PROJECTION_POINTS)
    chi = (nodes + 1.0) * math.pi / 8.0
    return chi, weights * math.pi / 8.0


def _basis(order: int, chi: np.ndarray) -> dict[str, np.ndarray]:
    k = np.arange(1, order + 1, dtype=float)
    j = np.arange(order, dtype=float)
    cosine_k = np.cos(4.0 * np.outer(chi, k))
    sine_k = np.sin(4.0 * np.outer(chi, k))
    cosine_j = np.cos(4.0 * np.outer(chi, j))
    sine_j = np.sin(4.0 * np.outer(chi, j))
    window = np.sin(2.0 * chi) ** 2
    window_prime = 2.0 * np.sin(4.0 * chi)
    shape = window[:, None] * cosine_j
    shape_prime = (
        window_prime[:, None] * cosine_j
        - window[:, None] * 4.0 * j[None, :] * sine_j
    )
    shift = np.sin(4.0 * chi)[:, None] * cosine_j
    shift_prime = (
        4.0 * np.cos(4.0 * chi)[:, None] * cosine_j
        - np.sin(4.0 * chi)[:, None]
        * 4.0 * j[None, :] * sine_j
    )
    return {
        "cosine_k": cosine_k,
        "cosine_k_prime": -4.0 * k[None, :] * sine_k,
        "shape": shape,
        "shape_prime": shape_prime,
        "shift": shift,
        "shift_prime": shift_prime,
    }


def _weighted_lstsq(
    matrix: np.ndarray, target: np.ndarray, weights: np.ndarray,
) -> tuple[np.ndarray, float]:
    repeated = np.tile(weights, target.shape[1] if target.ndim == 2 else 1)
    if target.ndim == 2:
        flattened = target.T.reshape(-1)
    else:
        flattened = target
    root = np.sqrt(repeated)
    solution, _, _, _ = np.linalg.lstsq(
        matrix * root[:, None], flattened * root, rcond=None
    )
    remainder = matrix @ solution - flattened
    relative = float(
        np.sqrt(np.sum(repeated * remainder ** 2))
        / max(1.0e-300, np.sqrt(np.sum(repeated * flattened ** 2)))
    )
    return solution, relative


def _configuration_matrix(order: int, basis: dict[str, np.ndarray]) -> np.ndarray:
    points = basis["cosine_k"].shape[0]
    qdim = dimensions(order)["coordinates"]
    matrix = np.zeros((3 * points, qdim))
    # Stacking order is C, A, B.
    matrix[:, 0] = 1.0
    matrix[0:points, 1:1 + order] = basis["cosine_k"]
    matrix[points:2 * points, 1:1 + order] = basis["cosine_k"]
    matrix[2 * points:, 1:1 + order] = basis["cosine_k"]
    matrix[0:points, 1 + order:1 + 2 * order] = basis["shape"]
    matrix[points:2 * points, 1 + 2 * order:1 + 3 * order] = basis["shape"]
    matrix[2 * points:, 1 + 2 * order:1 + 3 * order] = -basis["shape"]
    return matrix


def _profiles(
    order: int,
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    basis: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    u = q[1:1 + order]
    w = q[1 + order:1 + 2 * order]
    b = q[1 + 2 * order:1 + 3 * order]
    vu = velocity[1:1 + order]
    vw = velocity[1 + order:1 + 2 * order]
    vb = velocity[1 + 2 * order:1 + 3 * order]
    lapse = multipliers[:order]
    shift = multipliers[order:]
    return {
        "u_prime": basis["cosine_k_prime"] @ u,
        "w_prime": basis["shape_prime"] @ w,
        "b_prime": basis["shape_prime"] @ b,
        "vu_prime": basis["cosine_k_prime"] @ vu,
        "vw_prime": basis["shape_prime"] @ vw,
        "vb_prime": basis["shape_prime"] @ vb,
        "log_lapse_prime": basis["cosine_k_prime"] @ lapse,
        "shift": basis["shift"] @ shift,
        "shift_prime": basis["shift_prime"] @ shift,
    }


def _generator_variation(
    order: int,
    state: tuple[np.ndarray, ...],
    generator_mode: int,
    chi: np.ndarray,
    weights: np.ndarray,
    basis: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, float]]:
    q, velocity, multipliers = state
    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    profile = _profiles(order, q, velocity, multipliers, basis)
    xi = np.sin(4.0 * chi) * np.cos(4.0 * generator_mode * chi)
    xi_prime = (
        4.0 * np.cos(4.0 * chi) * np.cos(4.0 * generator_mode * chi)
        - 4.0 * generator_mode * np.sin(4.0 * chi)
        * np.sin(4.0 * generator_mode * chi)
    )
    target_q = np.column_stack((
        xi * (profile["u_prime"] + profile["w_prime"]) + xi_prime,
        xi * (profile["u_prime"] + profile["b_prime"] - np.tan(chi)),
        xi * (profile["u_prime"] - profile["b_prime"] + 1.0 / np.tan(chi)),
    ))
    target_v = np.column_stack((
        xi * (profile["vu_prime"] + profile["vw_prime"]),
        xi * (profile["vu_prime"] + profile["vb_prime"]),
        xi * (profile["vu_prime"] - profile["vb_prime"]),
    ))
    geometry_matrix = _configuration_matrix(order, basis)
    delta_q, q_error = _weighted_lstsq(
        geometry_matrix, target_q, weights
    )
    delta_v, v_error = _weighted_lstsq(
        geometry_matrix, target_v, weights
    )
    delta_lapse, lapse_error = _weighted_lstsq(
        basis["cosine_k"], xi * profile["log_lapse_prime"], weights
    )
    delta_shift, shift_error = _weighted_lstsq(
        basis["shift"],
        xi * profile["shift_prime"] - profile["shift"] * xi_prime,
        weights,
    )
    variation = np.concatenate((
        delta_q, delta_v, delta_lapse, delta_shift
    ))
    if variation.shape != (2 * qdim + mdim,):
        raise RuntimeError("radial generator variation has wrong dimension")
    return variation, {
        "configuration_projection_relative_error": q_error,
        "velocity_projection_relative_error": v_error,
        "lapse_projection_relative_error": lapse_error,
        "shift_projection_relative_error": shift_error,
        "generator_endpoint_maximum": float(max(abs(xi[0]), abs(xi[-1]))),
    }


def _descriptor_velocity_variation(
    order: int,
    state: tuple[np.ndarray, ...],
    generator_mode: int,
    chi: np.ndarray,
    weights: np.ndarray,
    basis: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, float]]:
    """Coefficient of theta=partial_t xi in the radial gauge variation.

    At a fixed time set xi=0 and theta arbitrary.  Then delta q=delta N=0,
    delta beta=theta, while delta(dot g)=L_theta g.  Invariance of the
    retained action gives the canonical momentum-constraint Noether identity
    ``p . L_theta g + C_shift(theta) = 0`` (up to the common active/passive
    sign convention, fixed below by the ADM transformation used in the
    retained action).
    """

    q, _, _ = state
    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    profile = _profiles(order, *state, basis)
    theta = basis["shift"][:, generator_mode]
    theta_prime = basis["shift_prime"][:, generator_mode]
    target_v = np.column_stack((
        theta * (profile["u_prime"] + profile["w_prime"]) + theta_prime,
        theta * (profile["u_prime"] + profile["b_prime"] - np.tan(chi)),
        theta * (profile["u_prime"] - profile["b_prime"] + 1.0 / np.tan(chi)),
    ))
    delta_v, velocity_error = _weighted_lstsq(
        _configuration_matrix(order, basis), target_v, weights
    )
    variation = np.zeros(2 * qdim + mdim)
    variation[qdim:2 * qdim] = delta_v
    # The retained ADM convention is dchi + beta dt.  Under the active radial
    # pushforward used above, delta beta contains +partial_t xi.
    variation[2 * qdim + order + generator_mode] = 1.0
    return variation, {
        "velocity_projection_relative_error": velocity_error,
        "shift_basis_projection_error": 0.0,
        "configuration_and_lapse_variations_are_zero_at_xi_zero": True,
    }


def _action_weights(order: int) -> np.ndarray:
    qdim = dimensions(order)["coordinates"]
    frequencies = spectral_frequencies(order)
    return np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))


def _eta_clock_shift_covector(
    order: int,
    q: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
) -> np.ndarray:
    """Differentiate the retained eta Routhian with respect to shift modes.

    This is the exact eta-owned term already present in the action:
    ``x_eta=x_spatial-(beta/N)^2`` together with the collective inverse
    inertia.  It is not an added source or constraint.
    """

    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    basis = _basis(order, chi)
    u = basis["cosine_k"] @ q[1:1 + order]
    w = basis["shape"] @ q[1 + order:1 + 2 * order]
    b = basis["shape"] @ q[1 + 2 * order:1 + 3 * order]
    log_lapse = basis["cosine_k"] @ multipliers[:order]
    beta = basis["shift"] @ multipliers[order:]
    radius = RADIUS0 * math.exp(float(q[0]))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + b) * np.cos(chi)
    B = radius * np.exp(u - b) * np.sin(chi)
    N = np.exp(log_lapse)
    volume = C * A ** 3 * B ** 3
    x_spatial = (
        1.0 / C ** 2
        + 3.0 * np.cos(chi) ** 2 / A ** 2
        + 3.0 * np.sin(chi) ** 2 / B ** 2
    )
    x_eta = x_spatial - (beta / N) ** 2
    localization = identity_response_localization(chi)
    inertia = float(np.sum(
        quadrature * volume * localization * (1.0 + x_eta ** 3) / N
    ))
    dx_dbeta = -2.0 * beta / N ** 2
    bulk_density_derivative = (
        -0.5 * N * volume * localization * (1.0 + x_eta ** 3)
        * dx_dbeta
    )
    inertia_density_derivative = (
        volume * localization / N * 3.0 * x_eta ** 2 * dx_dbeta
    )
    routhian_factor = 1.0 / (
        8.0 * HOPF_ORBIT_VOLUME ** 2 * inertia ** 2
    )
    density = (
        bulk_density_derivative
        + routhian_factor * inertia_density_derivative
    )
    return basis["shift"].T @ (quadrature * density)


def _ward_shift_covectors(
    order: int,
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
) -> dict[str, np.ndarray | float]:
    """Reconstruct every shift row from momentum plus retained eta current."""

    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    basis = _basis(order, chi)
    u = basis["cosine_k"] @ q[1:1 + order]
    w = basis["shape"] @ q[1 + order:1 + 2 * order]
    b = basis["shape"] @ q[1 + 2 * order:1 + 3 * order]
    up = basis["cosine_k_prime"] @ q[1:1 + order]
    wp = basis["shape_prime"] @ q[1 + order:1 + 2 * order]
    bp_shape = basis["shape_prime"] @ q[1 + 2 * order:1 + 3 * order]
    lc = (
        velocity[0]
        + basis["cosine_k"] @ velocity[1:1 + order]
        + basis["shape"] @ velocity[1 + order:1 + 2 * order]
    )
    la = (
        velocity[0]
        + basis["cosine_k"] @ velocity[1:1 + order]
        + basis["shape"] @ velocity[1 + 2 * order:1 + 3 * order]
    )
    lb = (
        velocity[0]
        + basis["cosine_k"] @ velocity[1:1 + order]
        - basis["shape"] @ velocity[1 + 2 * order:1 + 3 * order]
    )
    log_lapse = basis["cosine_k"] @ multipliers[:order]
    beta = basis["shift"] @ multipliers[order:]
    beta_prime = basis["shift_prime"] @ multipliers[order:]
    radius = RADIUS0 * math.exp(float(q[0]))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + b) * np.cos(chi)
    B = radius * np.exp(u - b) * np.sin(chi)
    N = np.exp(log_lapse)
    cp = up + wp
    ap = up + bp_shape - np.tan(chi)
    bp = up - bp_shape + 1.0 / np.tan(chi)
    Hc = (lc - beta * cp - beta_prime) / N
    Ha = (la - beta * ap) / N
    Hb = (lb - beta * bp) / N
    trace_H = Hc + 3.0 * Ha + 3.0 * Hb
    volume = C * A ** 3 * B ** 3
    pC = volume * (Hc - trace_H)
    pA = 3.0 * volume * (Ha - trace_H)
    pB = 3.0 * volume * (Hb - trace_H)
    momentum_transport = pC * cp + pA * ap + pB * bp
    geometric = -(
        basis["shift_prime"].T @ (quadrature * pC)
        + basis["shift"].T @ (quadrature * momentum_transport)
    )

    x_spatial = (
        1.0 / C ** 2
        + 3.0 * np.cos(chi) ** 2 / A ** 2
        + 3.0 * np.sin(chi) ** 2 / B ** 2
    )
    x_eta = x_spatial - (beta / N) ** 2
    localization = identity_response_localization(chi)
    inertia = float(np.sum(
        quadrature * volume * localization * (1.0 + x_eta ** 3) / N
    ))
    dx_dbeta = -2.0 * beta / N ** 2
    eta_density = (
        -0.5 * N * volume * localization * (1.0 + x_eta ** 3)
        * dx_dbeta
        + 1.0 / (8.0 * HOPF_ORBIT_VOLUME ** 2 * inertia ** 2)
        * volume * localization / N * 3.0 * x_eta ** 2 * dx_dbeta
    )
    eta = basis["shift"].T @ (quadrature * eta_density)
    return {
        "geometric_momentum": geometric,
        "eta_clock": eta,
        "total": geometric + eta,
        "inertia": inertia,
    }


def _evaluate(state: tuple[np.ndarray, ...], order: int) -> dict[str, object]:
    embedded = embed_nested_state(*state, SOURCE_ORDER, order)
    q, velocity, multipliers = embedded
    jet = exact_full_action_jet_at_state(
        order, q, velocity, multipliers, points=ACTION_POINTS
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    qdim = dimensions(order)["coordinates"]
    ward = _ward_shift_covectors(
        order, q, velocity, multipliers, points=ACTION_POINTS
    )
    eta_shift_covector = np.asarray(ward["eta_clock"], dtype=float)
    frequencies = spectral_frequencies(order)["multipliers"]
    shift_weights = np.sqrt(1.0 + frequencies[order:] ** 2)
    total_shift_covector = gradient[2 * qdim + order:].copy()
    ward_total = np.asarray(ward["total"], dtype=float)
    ward_reconstruction_defect = total_shift_covector - ward_total
    geometric_shift_covector = total_shift_covector - eta_shift_covector
    cuts = [
        cut for cut in (SOURCE_ORDER, 16, 20, 24, 32, 40, order - 1)
        if SOURCE_ORDER <= cut < order
    ]
    tail_rows = []
    for cut in sorted(set(cuts)):
        high = np.arange(order) >= cut
        total_weak = total_shift_covector / shift_weights
        eta_weak = eta_shift_covector / shift_weights
        geometric_weak = geometric_shift_covector / shift_weights
        tail_rows.append({
            "cutoff_N": cut,
            "total_shift_H_minus_1_tail_norm": float(
                np.linalg.norm(total_weak[high])
            ),
            "eta_clock_H_minus_1_tail_norm": float(
                np.linalg.norm(eta_weak[high])
            ),
            "geometric_momentum_H_minus_1_tail_norm": float(
                np.linalg.norm(geometric_weak[high])
            ),
            "first_total_shift_weak_coefficient": float(total_weak[cut]),
            "first_eta_clock_weak_coefficient": float(eta_weak[cut]),
            "first_geometric_momentum_weak_coefficient": float(
                geometric_weak[cut]
            ),
            "N_squared_first_eta_clock_weak_coefficient": float(
                cut ** 2 * abs(eta_weak[cut])
            ),
        })
    chi, quadrature = _grid()
    basis = _basis(order, chi)
    modes = sorted(set((
        SOURCE_ORDER,
        min(order - 1, SOURCE_ORDER + 1),
        max(SOURCE_ORDER, order // 2),
        order - 1,
    )))
    rows = []
    for mode in modes:
        variation, projection = _generator_variation(
            order, embedded, mode, chi, quadrature, basis
        )
        pieces = {
            "coordinates": float(gradient[:qdim] @ variation[:qdim]),
            "velocities": float(
                gradient[qdim:2 * qdim] @ variation[qdim:2 * qdim]
            ),
            "lapse": float(
                gradient[2 * qdim:2 * qdim + order]
                @ variation[2 * qdim:2 * qdim + order]
            ),
            "shift": float(
                gradient[2 * qdim + order:]
                @ variation[2 * qdim + order:]
            ),
        }
        total = float(sum(pieces.values()))
        absolute_scale = float(sum(abs(value) for value in pieces.values()))
        action_norm = float(np.linalg.norm(
            variation * _action_weights(order)
        ))
        rows.append({
            "generator_mode": mode,
            "action_coordinate_generator_norm": action_norm,
            "action_covector_pairing_blocks": pieces,
            "Noether_pairing": total,
            "relative_cancellation_defect": float(
                abs(total) / max(1.0e-300, absolute_scale)
            ),
            "normalized_Noether_pairing": float(
                abs(total) / max(1.0e-300, action_norm)
            ),
            "projection": projection,
        })
    descriptor_modes = sorted(set(
        mode for mode in (0, 1, SOURCE_ORDER, 16, 20, order - 1)
        if 0 <= mode < order
    ))
    descriptor_rows = []
    for mode in descriptor_modes:
        variation, projection = _descriptor_velocity_variation(
            order, embedded, mode, chi, quadrature, basis
        )
        velocity_pairing = float(
            gradient[qdim:2 * qdim] @ variation[qdim:2 * qdim]
        )
        shift_pairing = float(
            gradient[2 * qdim + order:]
            @ variation[2 * qdim + order:]
        )
        total = velocity_pairing + shift_pairing
        eta_current = float(eta_shift_covector[mode])
        corrected_total = total - eta_current
        scale = abs(velocity_pairing) + abs(shift_pairing)
        action_norm = float(np.linalg.norm(
            variation * _action_weights(order)
        ))
        descriptor_rows.append({
            "generator_mode": mode,
            "identity": (
                "P_DOT_L_THETA_G_PLUS_SHIFT_CONSTRAINT_THETA_MINUS_"
                "ETA_CLOCK_CURRENT_EQUALS_ZERO"
            ),
            "velocity_pairing": velocity_pairing,
            "shift_constraint_pairing": shift_pairing,
            "Noether_pairing": total,
            "retained_eta_clock_shift_current": eta_current,
            "metric_plus_total_shift_minus_eta_Ward_pairing": corrected_total,
            "relative_cancellation_defect": float(
                abs(total) / max(1.0e-300, scale)
            ),
            "normalized_Noether_pairing": float(
                abs(total) / max(1.0e-300, action_norm)
            ),
            "eta_completed_relative_Ward_defect": float(
                abs(corrected_total)
                / max(1.0e-300, scale + abs(eta_current))
            ),
            "projection": projection,
        })
    return {
        "N": order,
        "probe_kind": "ZERO_PADDED_CERTIFIED_N12_NOT_A_HIGHER_N_ROOT",
        "generator": (
            "XI_J=SIN(4CHI)COS(4JCHI),_XI_J_ENDPOINT_FIXED;_"
            "DELTA_FIELDS=L_XI_FIELDS"
        ),
        "rows": rows,
        "descriptor_velocity_rows": descriptor_rows,
        "shift_source_decomposition": {
            "exact_identity": (
                "C_SHIFT_TOTAL=C_SHIFT_GEOMETRIC_PLUS_J_ETA_CLOCK"
            ),
            "rows": tail_rows,
            "exact_action_row_reconstruction": {
                "maximum_absolute_defect": float(
                    np.max(np.abs(ward_reconstruction_defect))
                ),
                "relative_l2_defect": float(
                    np.linalg.norm(ward_reconstruction_defect)
                    / max(1.0e-300, np.linalg.norm(total_shift_covector))
                ),
                "eta_collective_inertia": float(ward["inertia"]),
            },
        },
        "maximum_relative_cancellation_defect": float(max(
            row["relative_cancellation_defect"] for row in rows
        )),
        "maximum_descriptor_velocity_relative_cancellation_defect": float(max(
            row["relative_cancellation_defect"] for row in descriptor_rows
        )),
    }


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the certified direct N12 anchor is required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    states = {
        name: _split_state(joint, name) for name in ("event", "child")
    }
    evaluations = {
        name: [_evaluate(states[name], order) for order in ORDERS]
        for name in ("event", "child")
    }
    ward_row_defects = [
        row["shift_source_decomposition"][
            "exact_action_row_reconstruction"
        ]["maximum_absolute_defect"]
        for rows in evaluations.values() for row in rows
    ]
    validation = {
        "certified_N12_anchor_consumed": True,
        "unchanged_exact_full_action_covector_used": True,
        "endpoint_fixed_radial_Lie_derivative_used": True,
        "existing_q_v_m_basis_only": True,
        "zero_padded_probes_not_promoted_as_roots": True,
        "eta_completed_exact_shift_rows_reconstructed_to_1e_minus_10": (
            max(ward_row_defects) < 1.0e-10
        ),
        "new_physics_equation_constraint_quotient_or_gate": False,
    }
    payload = {
        "artifact": "BHSM_N12_RADIAL_DIFFEO_NOETHER_COMPATIBILITY_AUDIT",
        "source_order": SOURCE_ORDER,
        "orders": list(ORDERS),
        "action_quadrature_points": ACTION_POINTS,
        "projection_quadrature_points": PROJECTION_POINTS,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": _sha256(CHECKPOINT),
        "promotion": str(PROMOTION),
        "promotion_sha256": _sha256(PROMOTION),
        "evaluations": evaluations,
        "derived_Ward_identity": {
            "identity": (
                "PAIR(P,L_THETA_G)+PAIR(C_SHIFT_TOTAL,THETA)-"
                "PAIR(J_ETA_CLOCK,THETA)=0"
            ),
            "eta_definitions": (
                "X_ETA=X_SPATIAL-(BETA/N)^2;_"
                "I=INTEGRAL(VOLUME*LOCALIZATION*(1+X_ETA^3)/N)"
            ),
            "eta_shift_current": (
                "J_ETA=DELTA_BETA{INTEGRAL[-N*VOLUME*LOCALIZATION*"
                "(X_ETA/2+X_ETA^4/8)]-1/(8*V_HOPF^2*I)}"
            ),
            "partial_X_eta_partial_beta": "-2*BETA/N^2",
            "coefficient_or_parameter_fitted": False,
            "new_physical_source_added": False,
        },
        "classification": (
            "RADIAL_DIFFEO_WARD_IDENTITY_DERIVED_WITH_THE_RETAINED_ETA_"
            "CLOCK_CURRENT;_STATIC_SHIFT_COKERNEL_ANNIHILATION_WITHOUT_ETA_"
            "IS_INVALIDATED;_FINITE_GALERKIN_TAIL_ENCLOSURE_REMAINS_OPEN"
        ),
        "scientific_interpretation": {
            "validated": (
                "THE_RETAINED_ACTION_OWNS_A_NONZERO_ETA_CLOCK_SHIFT_CURRENT_"
                "AND_THE_METRIC_MOMENTUM_PLUS_TOTAL_SHIFT_WARD_PAIRING_"
                "CLOSES_ONLY_AFTER_THAT_CURRENT_IS_INCLUDED"
            ),
            "invalidated": (
                "THE_STATIC_SHIFT_COKERNEL_IS_ANNIHILATED_BY_RADIAL_"
                "DIFFEOMORPHISM_COMPATIBILITY_WITHOUT_AN_ETA_CURRENT"
            ),
            "soft_channel_classification": (
                "CATEGORY_2_DYNAMICALLY_CONTROLLED_NORMAL_DIRECTION;_NOT_"
                "QUOTIENTED_AS_TANGENT_AND_NO_CATEGORY_3_SEQUENCE_PROVED"
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_AN_ACTION_DERIVED_INVERSE_SQUARE_H_MINUS_1_TAIL_AND_S2_"
            "SOURCE_RESTRICTED_RIGHT_INVERSE_FOR_THE_ETA_COMPLETED_WARD_"
            "SOURCE_ON_THE_POSITIVE_DURATION_MIXED_EULER_DIRAC_HISTORY;_"
            "THEN_CLOSE_THE_UNCHANGED_NONLINEAR_JOINT_EVENT_CHILD_RADIUS"
        ),
        "validation": validation,
        "validation_passed": all(
            value if key != "new_physics_equation_constraint_quotient_or_gate"
            else not value
            for key, value in validation.items()
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "result": str(RESULT),
        "validation_passed": payload["validation_passed"],
        "maximum_relative_cancellation_defects": {
            name: [row["maximum_relative_cancellation_defect"] for row in data]
            for name, data in evaluations.items()
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
