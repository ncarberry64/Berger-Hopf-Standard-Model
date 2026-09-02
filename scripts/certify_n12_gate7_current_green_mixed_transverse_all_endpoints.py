"""Certify the current mixed Green/transverse map at all 371 endpoints.

The rate Hessian is evaluated bilinearly: the Green axis is the first leg and
all 74 projected transverse columns share the second leg.  This preserves the
Arb dependency graph and avoids two polarized quadratic evaluations per
column.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import certify_n12_gate7_current_green_correlated_scalar_interval355 as scalar  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_SEED.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_mixed_transverse_all_endpoints_work"
THEORY = ROOT / "theory/n12_gate7_current_green_mixed_transverse_all_endpoints.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = 512
NODES = 371
COORDINATES = 74
OUTPUTS = cert.STATE + 1
SHARD_REVISION = 1
INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PARTITION, PARTITION.with_suffix(".npz"),
    SEED, SEED.with_suffix(".npz"),
    Path(cert.__file__).resolve(), Path(scalar.__file__).resolve(),
    THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _shard(node: int) -> Path:
    return WORK / f"node_{node:03d}.npz"


def _valid(path: Path, node: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return (
                int(source["node"]) == node
                and int(source["precision_bits"]) == PRECISION
                and int(source["shard_revision"]) == SHARD_REVISION
                and source["mixed_arb"].shape == (OUTPUTS, COORDINATES)
            )
    except Exception:
        return False


def _solve(K: arb_mat, rhs: np.ndarray) -> np.ndarray:
    array = np.asarray(rhs, dtype=object)
    solved = cert._verified_solve(K, cert._mat(array))
    return cert._array(solved).reshape(array.shape)


def _dot_columns(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left = np.asarray(left, dtype=object)
    right = np.asarray(right, dtype=object)
    if left.ndim == 1:
        left = np.repeat(left[:, None], right.shape[1], axis=1)
    if right.ndim == 1:
        right = np.repeat(right[:, None], left.shape[1], axis=1)
    result = np.empty(left.shape[1], dtype=object)
    for column in range(left.shape[1]):
        result[column] = cert._arb_dot(left[:, column], right[:, column])
    return result


def _pair_columns(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    result = np.empty((left.shape[0], 2 * left.shape[1]), dtype=object)
    result[:, 0::2] = left
    result[:, 1::2] = right
    return result


def _mixed_axis_map(
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
    axis_direction: np.ndarray,
    transverse_directions: np.ndarray,
) -> np.ndarray:
    """Return D2(rate)[axis, transverse columns] as correlated Arb balls."""
    jets = cert._arb_action_jets(state)
    dense_maps = jets.dense_maps
    psi, eigenvalue, _, _ = cert._eigenline(
        jets.hessian_arb, jets.hessian_mid, reference,
    )
    q_weights, reduced_weights, _, _ = cert.metric_data()
    w = np.asarray(weights, dtype=float)
    count = transverse_directions.shape[1]
    u = np.asarray([arb(float(value)) for value in axis_direction], dtype=object)
    V = np.asarray([
        [arb(float(value)) for value in row]
        for row in transverse_directions
    ], dtype=object)
    raw_u = np.asarray([u[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)
    raw_V = np.asarray([
        [V[i, k] / arb(float(w[i])) for k in range(count)]
        for i in range(cert.STATE)
    ], dtype=object)
    ds_u = u[cert.STATE]
    ds_V = V[cert.STATE]

    gradient = np.asarray([
        jets.gradient_arb[i] / arb(float(w[i])) for i in range(cert.STATE)
    ], dtype=object)
    H_action = np.asarray([[
        jets.hessian_arb[i, j] / arb(float(w[i])) / arb(float(w[j]))
        for j in range(cert.STATE)] for i in range(cert.STATE)
    ], dtype=object)
    configuration = np.asarray([
        arb(float(q_weights[i])) * arb(float(state[cert.QDIM + i]))
        for i in range(cert.QDIM)
    ], dtype=object)
    rhs = np.empty(cert.REDUCED, dtype=object)
    for i in range(cert.REDUCED):
        source = arb(0)
        if i < cert.QDIM:
            source += arb(float(q_weights[i])) * gradient[i]
        for j in range(cert.QDIM):
            source -= H_action[cert.QDIM + i, j] * configuration[j]
        rhs[i] = arb(float(reduced_weights[i])) * source

    Hraw = np.asarray(jets.hessian_arb[cert.QDIM:, cert.QDIM:], dtype=object)
    K = arb_mat(cert.REDUCED + 1, cert.REDUCED + 1)
    for i in range(cert.REDUCED):
        for j in range(cert.REDUCED):
            K[i, j] = Hraw[i, j] - (eigenvalue if i == j else 0)
        K[i, cert.REDUCED] = psi[i]
        K[cert.REDUCED, i] = psi[i]
    base_rhs = np.asarray(list(rhs) + [arb(0)], dtype=object).reshape(-1, 1)
    response = _solve(K, base_rhs)[:, 0]
    hard = response[:cert.REDUCED]
    bpsi = response[cert.REDUCED]

    out_reduced = np.zeros((cert.STATE, cert.REDUCED), dtype=object)
    out_full = np.zeros((cert.STATE, cert.STATE), dtype=object)
    for i in range(cert.REDUCED):
        out_reduced[cert.QDIM + i, i] = arb(1)
    for i in range(cert.STATE):
        out_full[i, i] = arb(1)
    p = np.asarray([arb(0)] * cert.QDIM + list(psi), dtype=object)
    hfull = np.asarray([arb(0)] * cert.QDIM + list(hard), dtype=object)
    qdirection = np.asarray([arb(0) for _ in range(cert.STATE)], dtype=object)
    q_u = np.asarray([arb(0) for _ in range(cert.STATE)], dtype=object)
    q_V = np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.STATE)], dtype=object)
    configuration_u = np.asarray([
        arb(float(q_weights[i])) * raw_u[cert.QDIM + i]
        for i in range(cert.QDIM)
    ], dtype=object)
    configuration_V = np.asarray([[
        arb(float(q_weights[i])) * raw_V[cert.QDIM + i, k]
        for k in range(count)] for i in range(cert.QDIM)
    ], dtype=object)
    for i in range(cert.QDIM):
        qdirection[i] = configuration[i] / arb(float(w[i]))
        q_u[i] = configuration_u[i] / arb(float(w[i]))
        for k in range(count):
            q_V[i, k] = configuration_V[i, k] / arb(float(w[i]))

    fixed = np.column_stack((p, hfull, qdirection))
    first_u = cert._mixed_contraction(
        state, dense_maps, out_reduced, fixed, raw_u,
    ).reshape(cert.REDUCED, 3)
    first_V = cert._mixed_contraction(
        state, dense_maps, out_reduced, fixed, raw_V,
    ).reshape(cert.REDUCED, 3, count)

    def first_solution(raw: np.ndarray, ds: np.ndarray | arb,
                       config_first: np.ndarray, first: np.ndarray):
        matrix = raw if raw.ndim == 2 else raw[:, None]
        columns = matrix.shape[1]
        dgradient = cert._array(cert._mat(jets.hessian_arb) * cert._mat(matrix))
        slopes = np.empty(columns, dtype=object)
        eig_rhs = np.empty((cert.REDUCED + 1, columns), dtype=object)
        for k in range(columns):
            slopes[k] = cert._arb_dot(psi, first[:, 0, k] if first.ndim == 3 else first[:, 0])
            for i in range(cert.REDUCED):
                Hpsi = first[i, 0, k] if first.ndim == 3 else first[i, 0]
                eig_rhs[i, k] = -(Hpsi - slopes[k] * psi[i])
            eig_rhs[cert.REDUCED, k] = arb(0)
        psi_first = _solve(K, eig_rhs)[:cert.REDUCED]
        response_rhs = np.empty((cert.REDUCED + 1, columns), dtype=object)
        for k in range(columns):
            for i in range(cert.REDUCED):
                source = arb(0)
                if i < cert.QDIM:
                    source += arb(float(q_weights[i])) * dgradient[i, k] / arb(float(w[i]))
                Hconfig = first[i, 2, k] if first.ndim == 3 else first[i, 2]
                source -= Hconfig / arb(float(w[cert.QDIM + i]))
                for j in range(cert.QDIM):
                    value = config_first[j, k] if config_first.ndim == 2 else config_first[j]
                    source -= H_action[cert.QDIM + i, j] * value
                drhs = arb(float(reduced_weights[i])) * source
                Hhard = first[i, 1, k] if first.ndim == 3 else first[i, 1]
                response_rhs[i, k] = drhs - (
                    Hhard - slopes[k] * hard[i] + bpsi * psi_first[i, k]
                )
            response_rhs[cert.REDUCED, k] = -cert._arb_dot(psi_first[:, k], hard)
        response_first = _solve(K, response_rhs)
        return slopes, psi_first, response_first[:cert.REDUCED], response_first[cert.REDUCED]

    lambda_u, psi_u, hard_u, b_u = first_solution(
        raw_u, ds_u, configuration_u, first_u,
    )
    lambda_u = lambda_u[0]; psi_u = psi_u[:, 0]
    hard_u = hard_u[:, 0]; b_u = b_u[0]
    lambda_V, psi_V, hard_V, b_V = first_solution(
        raw_V, ds_V, configuration_V, first_V,
    )

    second = cert._mixed_contraction(
        state, dense_maps, out_reduced, fixed, raw_u, raw_V,
    ).reshape(cert.REDUCED, 3, count)
    p_u = np.asarray([arb(0)] * cert.QDIM + list(psi_u), dtype=object)
    p_V = np.vstack((
        np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object),
        psi_V,
    ))
    H_u_psi_V = cert._mixed_contraction(
        state, dense_maps, out_reduced, p_V, raw_u,
    ).reshape(cert.REDUCED, count)
    H_V_psi_u = cert._mixed_contraction(
        state, dense_maps, out_reduced, p_u, raw_V,
    ).reshape(cert.REDUCED, count)
    lambda_uv = np.empty(count, dtype=object)
    eig_second_rhs = np.empty((cert.REDUCED + 1, count), dtype=object)
    for k in range(count):
        lambda_uv[k] = (
            cert._arb_dot(psi, second[:, 0, k])
            + cert._arb_dot(psi_V[:, k], first_u[:, 0])
            + cert._arb_dot(psi_u, first_V[:, 0, k])
        )
        for i in range(cert.REDUCED):
            eig_second_rhs[i, k] = -(
                second[i, 0, k] + H_u_psi_V[i, k] + H_V_psi_u[i, k]
                - lambda_uv[k] * psi[i] - lambda_u * psi_V[i, k]
                - lambda_V[k] * psi_u[i]
            )
        eig_second_rhs[cert.REDUCED, k] = -cert._arb_dot(psi_u, psi_V[:, k])
    psi_uv = _solve(K, eig_second_rhs)[:cert.REDUCED]

    gradient_uv = cert._mixed_contraction(
        state, dense_maps, out_full, raw_u, raw_V,
    ).reshape(cert.STATE, count)
    H_u_qV = cert._mixed_contraction(
        state, dense_maps, out_reduced, q_V, raw_u,
    ).reshape(cert.REDUCED, count)
    H_V_qu = cert._mixed_contraction(
        state, dense_maps, out_reduced, q_u, raw_V,
    ).reshape(cert.REDUCED, count)
    h_u_full = np.asarray([arb(0)] * cert.QDIM + list(hard_u), dtype=object)
    h_V_full = np.vstack((
        np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object),
        hard_V,
    ))
    H_u_hV = cert._mixed_contraction(
        state, dense_maps, out_reduced, h_V_full, raw_u,
    ).reshape(cert.REDUCED, count)
    H_V_hu = cert._mixed_contraction(
        state, dense_maps, out_reduced, h_u_full, raw_V,
    ).reshape(cert.REDUCED, count)
    response_second_rhs = np.empty((cert.REDUCED + 1, count), dtype=object)
    for k in range(count):
        for i in range(cert.REDUCED):
            source = arb(0)
            if i < cert.QDIM:
                source += arb(float(q_weights[i])) * gradient_uv[i, k] / arb(float(w[i]))
            source -= second[i, 2, k] / arb(float(w[cert.QDIM + i]))
            source -= H_u_qV[i, k] / arb(float(w[cert.QDIM + i]))
            source -= H_V_qu[i, k] / arb(float(w[cert.QDIM + i]))
            rhs_uv = arb(float(reduced_weights[i])) * source
            response_second_rhs[i, k] = rhs_uv - (
                second[i, 1, k] - lambda_uv[k] * hard[i] + bpsi * psi_uv[i, k]
                + H_u_hV[i, k] - lambda_u * hard_V[i, k] + b_V[k] * psi_u[i]
                + H_V_hu[i, k] - lambda_V[k] * hard_u[i] + b_u * psi_V[i, k]
            )
        response_second_rhs[cert.REDUCED, k] = -(
            cert._arb_dot(psi_uv[:, k], hard)
            + cert._arb_dot(psi_u, hard_V[:, k])
            + cert._arb_dot(psi_V[:, k], hard_u)
        )
    response_uv = _solve(K, response_second_rhs)
    hard_uv = response_uv[:cert.REDUCED]
    b_uv = response_uv[cert.REDUCED]

    psi_action = np.asarray([arb(0)] * cert.QDIM + [
        arb(float(reduced_weights[i])) * psi[i] for i in range(cert.REDUCED)
    ], dtype=object)
    hard_action = np.asarray(list(configuration) + [
        arb(float(reduced_weights[i])) * hard[i] for i in range(cert.REDUCED)
    ], dtype=object)
    a = np.asarray([psi_action[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)
    d = np.asarray([hard_action[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)

    def weighted_variations(psi_x: np.ndarray, hard_x: np.ndarray,
                            q_x: np.ndarray):
        columns = 1 if psi_x.ndim == 1 else psi_x.shape[1]
        px = psi_x[:, None] if psi_x.ndim == 1 else psi_x
        hx = hard_x[:, None] if hard_x.ndim == 1 else hard_x
        qx = q_x[:, None] if q_x.ndim == 1 else q_x
        ax = np.asarray([[arb(0) for _ in range(columns)] for _ in range(cert.STATE)], dtype=object)
        dx = np.asarray([[arb(0) for _ in range(columns)] for _ in range(cert.STATE)], dtype=object)
        for k in range(columns):
            for i in range(cert.QDIM):
                dx[i, k] = qx[i, k]
            for i in range(cert.REDUCED):
                ax[cert.QDIM + i, k] = arb(float(reduced_weights[i])) * px[i, k] / arb(float(w[cert.QDIM + i]))
                dx[cert.QDIM + i, k] = arb(float(reduced_weights[i])) * hx[i, k] / arb(float(w[cert.QDIM + i]))
        return ax, dx

    a_u, d_u = weighted_variations(psi_u, hard_u, q_u[:cert.QDIM])
    a_u = a_u[:, 0]; d_u = d_u[:, 0]
    a_V, d_V = weighted_variations(psi_V, hard_V, q_V[:cert.QDIM])
    zero_q = np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object)
    a_uv, d_uv = weighted_variations(psi_uv, hard_uv, zero_q)
    p_uv = np.vstack((
        np.asarray(
            [[arb(0) for _ in range(count)] for _ in range(cert.QDIM)],
            dtype=object,
        ),
        psi_uv,
    ))
    last = np.column_stack((a, d))
    last_u = np.column_stack((a_u, d_u))
    last_V = _pair_columns(a_V, d_V)
    last_uv = _pair_columns(a_uv, d_uv)

    cR = cert._mixed_contraction(state, dense_maps, p, p, last).reshape(2)
    first_cR_u = (
        cert._mixed_contraction(state, dense_maps, raw_u, p, p, last).reshape(2)
        + 2 * cert._mixed_contraction(state, dense_maps, p_u, p, last).reshape(2)
        + cert._mixed_contraction(state, dense_maps, p, p, last_u).reshape(2)
    )
    first_cR_V = (
        cert._mixed_contraction(state, dense_maps, raw_V, p, p, last).reshape(count, 2)
        + 2 * cert._mixed_contraction(state, dense_maps, p_V, p, last).reshape(count, 2)
        + cert._mixed_contraction(state, dense_maps, p, p, last_V).reshape(count, 2)
    )
    second_cR = (
        cert._mixed_contraction(state, dense_maps, raw_u, raw_V, p, p, last).reshape(count, 2)
        + 2 * cert._mixed_contraction(state, dense_maps, raw_u, p_V, p, last).reshape(count, 2)
        + 2 * cert._mixed_contraction(state, dense_maps, raw_V, p_u, p, last).reshape(count, 2)
        + cert._mixed_contraction(state, dense_maps, raw_u, p, p, last_V).reshape(count, 2)
        + cert._mixed_contraction(state, dense_maps, raw_V, p, p, last_u).reshape(count, 2)
        + 2 * cert._mixed_contraction(
            state, dense_maps, p_uv, p, last,
        ).reshape(count, 2)
        + 2 * cert._mixed_contraction(state, dense_maps, p_u, p_V, last).reshape(count, 2)
        + 2 * cert._mixed_contraction(state, dense_maps, p_u, p, last_V).reshape(count, 2)
        + 2 * cert._mixed_contraction(state, dense_maps, p_V, p, last_u).reshape(count, 2)
        + cert._mixed_contraction(state, dense_maps, p, p, last_uv).reshape(count, 2)
    )

    cpsi, remainder = cR
    c_u, R_u = first_cR_u
    s = arb(descriptor)
    delta = cpsi * bpsi + s * remainder
    delta_u = c_u * bpsi + cpsi * b_u + ds_u * remainder + s * R_u

    numerator = np.asarray(
        [s * item for item in configuration]
        + [arb(float(reduced_weights[i])) * (bpsi * psi[i] + s * hard[i]) for i in range(cert.REDUCED)],
        dtype=object,
    )
    numerator_u = np.asarray(
        [ds_u * configuration[i] + s * configuration_u[i] for i in range(cert.QDIM)]
        + [arb(float(reduced_weights[i])) * (
            b_u * psi[i] + bpsi * psi_u[i] + ds_u * hard[i] + s * hard_u[i]
        ) for i in range(cert.REDUCED)], dtype=object,
    )
    numerator_V = np.empty((cert.STATE, count), dtype=object)
    numerator_uv = np.empty((cert.STATE, count), dtype=object)
    delta_V = np.empty(count, dtype=object)
    delta_uv = np.empty(count, dtype=object)
    for k in range(count):
        c_v, R_v = first_cR_V[k]
        c_uv, R_uv = second_cR[k]
        delta_V[k] = c_v * bpsi + cpsi * b_V[k] + ds_V[k] * remainder + s * R_v
        delta_uv[k] = (
            c_uv * bpsi + c_u * b_V[k] + c_v * b_u + cpsi * b_uv[k]
            + ds_u * R_v + ds_V[k] * R_u + s * R_uv
        )
        for i in range(cert.QDIM):
            numerator_V[i, k] = ds_V[k] * configuration[i] + s * configuration_V[i, k]
            numerator_uv[i, k] = ds_u * configuration_V[i, k] + ds_V[k] * configuration_u[i]
        for i in range(cert.REDUCED):
            row = cert.QDIM + i
            factor = arb(float(reduced_weights[i]))
            numerator_V[row, k] = factor * (
                b_V[k] * psi[i] + bpsi * psi_V[i, k]
                + ds_V[k] * hard[i] + s * hard_V[i, k]
            )
            numerator_uv[row, k] = factor * (
                b_uv[k] * psi[i] + b_u * psi_V[i, k] + b_V[k] * psi_u[i]
                + bpsi * psi_uv[i, k] + ds_u * hard_V[i, k]
                + ds_V[k] * hard_u[i] + s * hard_uv[i, k]
            )

    norm = cert._arb_dot(numerator, numerator).sqrt()
    norm_u = cert._arb_dot(numerator, numerator_u) / norm
    result = np.empty((OUTPUTS, count), dtype=object)
    for k in range(count):
        norm_v = cert._arb_dot(numerator, numerator_V[:, k]) / norm
        norm_uv = (
            cert._arb_dot(numerator_u, numerator_V[:, k])
            + cert._arb_dot(numerator, numerator_uv[:, k]) - norm_u * norm_v
        ) / norm
        for i in range(cert.STATE):
            result[i, k] = (
                numerator_uv[i, k] / norm
                - numerator_u[i] * norm_v / norm**2
                - numerator_V[i, k] * norm_u / norm**2
                - numerator[i] * norm_uv / norm**2
                + 2 * numerator[i] * norm_u * norm_v / norm**3
            )
        result[cert.STATE, k] = (
            delta_uv[k] / norm - delta_u * norm_v / norm**2
            - delta_V[k] * norm_u / norm**2 - delta * norm_uv / norm**2
            + 2 * delta * norm_u * norm_v / norm**3
        )
    return result


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty_like(midpoint)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def _worker(nodes: list[int]) -> dict[str, int]:
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
    computed = reused = 0
    for index, node in enumerate(nodes, 1):
        target = _shard(node)
        if _valid(target, node):
            reused += 1
            continue
        axis = scalar._normalized_central_axis(unit_mid[node])
        projector = np.eye(COORDINATES) - np.outer(axis, axis)
        frame = cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE)
        mixed = _mixed_axis_map(
            states[node], float(descriptors[node]), weights, reference,
            frame @ axis, frame @ projector,
        )
        midpoint, radius = _export(mixed)
        np.savez_compressed(
            target, mixed_mid=midpoint, mixed_radius=radius,
            mixed_arb=cert._arb_string_array(mixed), node=np.asarray(node),
            precision_bits=np.asarray(PRECISION),
            shard_revision=np.asarray(SHARD_REVISION),
        )
        computed += 1
        print(json.dumps({"worker": os.getpid(), "completed": index,
                          "assigned": len(nodes), "node": node}), flush=True)
    return {"computed": computed, "reused": reused}


def run_workers(workers: int, nodes: list[int]) -> None:
    groups = [nodes[index::workers] for index in range(workers)]
    totals = {"computed": 0, "reused": 0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_worker, group) for group in groups if group]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"all_endpoint_progress": totals}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--nodes", default="")
    args = parser.parse_args()
    nodes = list(range(NODES)) if not args.nodes else [
        int(value) for value in args.nodes.split(",")
    ]
    run_workers(max(1, min(args.workers, len(nodes))), nodes)


if __name__ == "__main__":
    main()
