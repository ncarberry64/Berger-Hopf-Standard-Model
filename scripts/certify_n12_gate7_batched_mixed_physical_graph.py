"""Batched Arb evaluation of the existing physical mixed derivative graph.

The retained action and parent producer remain unchanged. See
``theory/n12_gate7_batched_physical_mixed_graph.md`` for the exact regrouping.
This module supplies an evaluation graph, not an all-domain certificate.
"""
from __future__ import annotations
import hashlib
import inspect
import numpy as np
from flint import arb, arb_mat
import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as original
from bhsm.interface.prescribed_arb_action_jet import (
    batched_scalar_curvature as _batch_scalar,
    batched_fixed_contractions as _batch_fixed,
    batched_first_variation_contractions as _batch_first,
    affine_action_contraction as _affine_contraction,
)

PARENT_FUNCTION_SHA256 = "3298A913728CB02E2C5E964127BB8B64D932D0C6B3466F0F77DAEE97F8B17B8C"
if hashlib.sha256(inspect.getsource(original._mixed_axis_map).encode()).hexdigest().upper() != PARENT_FUNCTION_SHA256:
    raise RuntimeError("The frozen parent physical graph changed; explicit reconciliation is required")
cert = original.cert
_solve = original._solve
_pair_columns = original._pair_columns
OUTPUTS = original.OUTPUTS


def batched_axis_map(state: np.ndarray, descriptor: float, weights: np.ndarray, reference: np.ndarray, axis_direction: np.ndarray, transverse_directions: np.ndarray) -> np.ndarray:
    """Return D2(rate)[axis, transverse columns] as correlated Arb balls."""
    jets = cert._arb_action_jets(state)
    dense_maps = jets.dense_maps
    psi, eigenvalue, _, _ = cert._eigenline(jets.hessian_arb, jets.hessian_mid, reference)
    q_weights, reduced_weights, _, _ = cert.metric_data()
    w = np.asarray(weights, dtype=float)
    count = transverse_directions.shape[1]
    u = np.asarray([arb(float(value)) for value in axis_direction], dtype=object)
    V = np.asarray([[arb(float(value)) for value in row] for row in transverse_directions], dtype=object)
    raw_u = np.asarray([u[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)
    raw_V = np.asarray([[V[i, k] / arb(float(w[i])) for k in range(count)] for i in range(cert.STATE)], dtype=object)
    ds_u = u[cert.STATE]
    ds_V = V[cert.STATE]
    gradient = np.asarray([jets.gradient_arb[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)
    H_action = np.asarray([[jets.hessian_arb[i, j] / arb(float(w[i])) / arb(float(w[j])) for j in range(cert.STATE)] for i in range(cert.STATE)], dtype=object)
    configuration = np.asarray([arb(float(q_weights[i])) * arb(float(state[cert.QDIM + i])) for i in range(cert.QDIM)], dtype=object)
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
    configuration_u = np.asarray([arb(float(q_weights[i])) * raw_u[cert.QDIM + i] for i in range(cert.QDIM)], dtype=object)
    configuration_V = np.asarray([[arb(float(q_weights[i])) * raw_V[cert.QDIM + i, k] for k in range(count)] for i in range(cert.QDIM)], dtype=object)
    for i in range(cert.QDIM):
        qdirection[i] = configuration[i] / arb(float(w[i]))
        q_u[i] = configuration_u[i] / arb(float(w[i]))
        for k in range(count):
            q_V[i, k] = configuration_V[i, k] / arb(float(w[i]))
    fixed = np.column_stack((p, hfull, qdirection))
    first_u, first_V, second = _batch_fixed(cert, state, dense_maps, out_reduced, fixed, raw_u, raw_V)

    def first_solution(raw: np.ndarray, ds: np.ndarray | arb, config_first: np.ndarray, first: np.ndarray):
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
                response_rhs[i, k] = drhs - (Hhard - slopes[k] * hard[i] + bpsi * psi_first[i, k])
            response_rhs[cert.REDUCED, k] = -cert._arb_dot(psi_first[:, k], hard)
        response_first = _solve(K, response_rhs)
        return (slopes, psi_first, response_first[:cert.REDUCED], response_first[cert.REDUCED])
    lambda_u, psi_u, hard_u, b_u = first_solution(raw_u, ds_u, configuration_u, first_u)
    lambda_u = lambda_u[0]
    psi_u = psi_u[:, 0]
    hard_u = hard_u[:, 0]
    b_u = b_u[0]
    lambda_V, psi_V, hard_V, b_V = first_solution(raw_V, ds_V, configuration_V, first_V)
    p_u = np.asarray([arb(0)] * cert.QDIM + list(psi_u), dtype=object)
    p_V = np.vstack((np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object), psi_V))
    h_u_full = np.asarray([arb(0)] * cert.QDIM + list(hard_u), dtype=object)
    h_V_full = np.vstack((np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object), hard_V))
    H_u_psi_V, H_u_qV, H_u_hV, H_V_psi_u, H_V_qu, H_V_hu = _batch_first(cert, state, dense_maps, out_reduced, p_V, q_V, h_V_full, p_u, q_u, h_u_full, raw_u, raw_V)
    lambda_uv = np.empty(count, dtype=object)
    eig_second_rhs = np.empty((cert.REDUCED + 1, count), dtype=object)
    for k in range(count):
        lambda_uv[k] = cert._arb_dot(psi, second[:, 0, k]) + cert._arb_dot(psi_V[:, k], first_u[:, 0]) + cert._arb_dot(psi_u, first_V[:, 0, k])
        for i in range(cert.REDUCED):
            eig_second_rhs[i, k] = -(second[i, 0, k] + H_u_psi_V[i, k] + H_V_psi_u[i, k] - lambda_uv[k] * psi[i] - lambda_u * psi_V[i, k] - lambda_V[k] * psi_u[i])
        eig_second_rhs[cert.REDUCED, k] = -cert._arb_dot(psi_u, psi_V[:, k])
    psi_uv = _solve(K, eig_second_rhs)[:cert.REDUCED]
    gradient_uv = _affine_contraction(cert, state, dense_maps, out_full, raw_u, raw_V).reshape(cert.STATE, count)
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
            response_second_rhs[i, k] = rhs_uv - (second[i, 1, k] - lambda_uv[k] * hard[i] + bpsi * psi_uv[i, k] + H_u_hV[i, k] - lambda_u * hard_V[i, k] + b_V[k] * psi_u[i] + H_V_hu[i, k] - lambda_V[k] * hard_u[i] + b_u * psi_V[i, k])
        response_second_rhs[cert.REDUCED, k] = -(cert._arb_dot(psi_uv[:, k], hard) + cert._arb_dot(psi_u, hard_V[:, k]) + cert._arb_dot(psi_V[:, k], hard_u))
    response_uv = _solve(K, response_second_rhs)
    hard_uv = response_uv[:cert.REDUCED]
    b_uv = response_uv[cert.REDUCED]
    psi_action = np.asarray([arb(0)] * cert.QDIM + [arb(float(reduced_weights[i])) * psi[i] for i in range(cert.REDUCED)], dtype=object)
    hard_action = np.asarray(list(configuration) + [arb(float(reduced_weights[i])) * hard[i] for i in range(cert.REDUCED)], dtype=object)
    a = np.asarray([psi_action[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)
    d = np.asarray([hard_action[i] / arb(float(w[i])) for i in range(cert.STATE)], dtype=object)

    def weighted_variations(psi_x: np.ndarray, hard_x: np.ndarray, q_x: np.ndarray):
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
        return (ax, dx)
    a_u, d_u = weighted_variations(psi_u, hard_u, q_u[:cert.QDIM])
    a_u = a_u[:, 0]
    d_u = d_u[:, 0]
    a_V, d_V = weighted_variations(psi_V, hard_V, q_V[:cert.QDIM])
    zero_q = np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object)
    a_uv, d_uv = weighted_variations(psi_uv, hard_uv, zero_q)
    p_uv = np.vstack((np.asarray([[arb(0) for _ in range(count)] for _ in range(cert.QDIM)], dtype=object), psi_uv))
    last = np.column_stack((a, d))
    last_u = np.column_stack((a_u, d_u))
    last_V = _pair_columns(a_V, d_V)
    last_uv = _pair_columns(a_uv, d_uv)
    cR, first_cR_u, first_cR_V, second_cR = _batch_scalar(cert, state, dense_maps, raw_u, raw_V, p, p_u, p_V, p_uv, last, last_u, last_V, last_uv)
    cpsi, remainder = cR
    c_u, R_u = first_cR_u
    s = arb(descriptor)
    delta = cpsi * bpsi + s * remainder
    delta_u = c_u * bpsi + cpsi * b_u + ds_u * remainder + s * R_u
    numerator = np.asarray([s * item for item in configuration] + [arb(float(reduced_weights[i])) * (bpsi * psi[i] + s * hard[i]) for i in range(cert.REDUCED)], dtype=object)
    numerator_u = np.asarray([ds_u * configuration[i] + s * configuration_u[i] for i in range(cert.QDIM)] + [arb(float(reduced_weights[i])) * (b_u * psi[i] + bpsi * psi_u[i] + ds_u * hard[i] + s * hard_u[i]) for i in range(cert.REDUCED)], dtype=object)
    numerator_V = np.empty((cert.STATE, count), dtype=object)
    numerator_uv = np.empty((cert.STATE, count), dtype=object)
    delta_V = np.empty(count, dtype=object)
    delta_uv = np.empty(count, dtype=object)
    for k in range(count):
        c_v, R_v = first_cR_V[k]
        c_uv, R_uv = second_cR[k]
        delta_V[k] = c_v * bpsi + cpsi * b_V[k] + ds_V[k] * remainder + s * R_v
        delta_uv[k] = c_uv * bpsi + c_u * b_V[k] + c_v * b_u + cpsi * b_uv[k] + ds_u * R_v + ds_V[k] * R_u + s * R_uv
        for i in range(cert.QDIM):
            numerator_V[i, k] = ds_V[k] * configuration[i] + s * configuration_V[i, k]
            numerator_uv[i, k] = ds_u * configuration_V[i, k] + ds_V[k] * configuration_u[i]
        for i in range(cert.REDUCED):
            row = cert.QDIM + i
            factor = arb(float(reduced_weights[i]))
            numerator_V[row, k] = factor * (b_V[k] * psi[i] + bpsi * psi_V[i, k] + ds_V[k] * hard[i] + s * hard_V[i, k])
            numerator_uv[row, k] = factor * (b_uv[k] * psi[i] + b_u * psi_V[i, k] + b_V[k] * psi_u[i] + bpsi * psi_uv[i, k] + ds_u * hard_V[i, k] + ds_V[k] * hard_u[i] + s * hard_uv[i, k])
    norm = cert._arb_dot(numerator, numerator).sqrt()
    norm_u = cert._arb_dot(numerator, numerator_u) / norm
    result = np.empty((OUTPUTS, count), dtype=object)
    for k in range(count):
        norm_v = cert._arb_dot(numerator, numerator_V[:, k]) / norm
        norm_uv = (cert._arb_dot(numerator_u, numerator_V[:, k]) + cert._arb_dot(numerator, numerator_uv[:, k]) - norm_u * norm_v) / norm
        for i in range(cert.STATE):
            result[i, k] = numerator_uv[i, k] / norm - numerator_u[i] * norm_v / norm ** 2 - numerator_V[i, k] * norm_u / norm ** 2 - numerator[i] * norm_uv / norm ** 2 + 2 * numerator[i] * norm_u * norm_v / norm ** 3
        result[cert.STATE, k] = delta_uv[k] / norm - delta_u * norm_v / norm ** 2 - delta_V[k] * norm_u / norm ** 2 - delta * norm_uv / norm ** 2 + 2 * delta * norm_u * norm_v / norm ** 3
    return result
