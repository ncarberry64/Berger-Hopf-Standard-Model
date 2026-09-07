"""Binary64 signed mixed Hessian of the frozen augmented Gate-7 rate.

This is the rectangular counterpart of the already-certified symmetric
transverse center kernel.  It evaluates ``D2(rate)[u,V]`` for one ambient
direction and an arbitrary matrix of ambient directions without forming a
dense third-, fourth-, or fifth-order action tensor.

The routine is center algebra only.  Its caller must attach rounding and
outward neighborhood enclosures before using it in a Gate-7 certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_current_green_full_transverse_quadratic_center as center  # noqa: E402


@dataclass(frozen=True)
class MixedRateDiagnostics:
    """Residuals retained with one rectangular mixed-rate evaluation."""

    base_response_residual_2_norm: float
    left_first_response_relative_residual: float
    right_first_response_relative_residual: float
    mixed_response_relative_residual: float
    mixed_eigenline_normalization_residual: float


def _pair_columns(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    result = np.empty((left.shape[0], 2 * left.shape[1]))
    result[:, 0::2] = left
    result[:, 1::2] = right
    return result


def mixed_rate_map(
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
    left_direction: np.ndarray,
    right_directions: np.ndarray,
) -> tuple[np.ndarray, MixedRateDiagnostics]:
    """Return the signed ``D2(rate)[left,right columns]`` center tensor."""

    state = np.asarray(state, dtype=float)
    weights = np.asarray(weights, dtype=float)
    reference = np.asarray(reference, dtype=float)
    u = np.asarray(left_direction, dtype=float)
    v = np.asarray(right_directions, dtype=float)
    if (
        state.shape != (center.STATE,)
        or weights.shape != (center.STATE,)
        or reference.shape != (center.REDUCED,)
        or u.shape != (center.OUTPUTS,)
        or v.ndim != 2
        or v.shape[0] != center.OUTPUTS
        or v.shape[1] < 1
    ):
        raise ValueError("mixed-rate inputs have incompatible shapes")
    if not all(np.all(np.isfinite(item)) for item in (
        state, weights, reference, u, v,
    )) or not np.isfinite(descriptor):
        raise ValueError("mixed-rate inputs must be finite")

    q_weights, reduced_weights, _, _ = center.metric_data()
    gradient, hessian = center._exact_jet(state)
    gradient = np.asarray(gradient, dtype=float)
    hessian = np.asarray(hessian, dtype=float)
    reduced_hessian = 0.5 * (
        hessian[center.QDIM:, center.QDIM:]
        + hessian[center.QDIM:, center.QDIM:].T
    )
    eigenvalues, eigenvectors = np.linalg.eigh(reduced_hessian)
    psi = eigenvectors[:, center.SELECTED]
    if float(psi @ reference) < 0.0:
        eigenvectors[:, center.SELECTED] *= -1.0
        psi = eigenvectors[:, center.SELECTED]

    reduced_lift = np.zeros((center.STATE, center.REDUCED))
    reduced_lift[center.QDIM:] = reduced_weights[:, None] * np.eye(center.REDUCED)
    full_lift = np.diag(weights)
    configuration = q_weights * state[center.QDIM:2 * center.QDIM]
    configuration_action = np.zeros(center.STATE)
    configuration_action[:center.QDIM] = configuration
    gradient_action = gradient / weights
    hessian_action = hessian / weights[:, None] / weights[None, :]
    forcing = reduced_weights * (
        np.concatenate((
            q_weights * gradient_action[:center.QDIM],
            np.zeros(center.REDUCED - center.QDIM),
        ))
        - hessian_action[center.QDIM:, :center.QDIM] @ configuration
    )
    bordered = np.block([
        [
            reduced_hessian
            - eigenvalues[center.SELECTED] * np.eye(center.REDUCED),
            psi[:, None],
        ],
        [psi[None, :], np.zeros((1, 1))],
    ])
    response = np.linalg.solve(
        bordered, np.concatenate((forcing, np.zeros(1))),
    )
    hard = response[:-1]
    bpsi = float(response[-1])

    state_u, ds_u = u[:center.STATE], float(u[center.STATE])
    state_v, ds_v = v[:center.STATE], v[center.STATE]
    raw_u = state_u / weights
    raw_v = state_v / weights[:, None]
    configuration_u = q_weights * raw_u[center.QDIM:2 * center.QDIM]
    configuration_v = (
        q_weights[:, None] * raw_v[center.QDIM:2 * center.QDIM]
    )

    h_u = center._signed(state, full_lift, full_lift, state_u)
    h_v = center._signed(state, full_lift, full_lift, state_v)
    h_u_reduced = 0.5 * (
        h_u[center.QDIM:, center.QDIM:]
        + h_u[center.QDIM:, center.QDIM:].T
    )
    h_v_reduced = 0.5 * (
        h_v[center.QDIM:, center.QDIM:]
        + h_v[center.QDIM:, center.QDIM:].transpose(1, 0, 2)
    )
    other = np.arange(center.REDUCED) != center.SELECTED
    denominators = eigenvalues - eigenvalues[center.SELECTED]

    def first_variation(
        state_direction: np.ndarray,
        raw_direction: np.ndarray,
        configuration_direction: np.ndarray,
        h_direction: np.ndarray,
        h_reduced: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        matrix = (
            state_direction[:, None]
            if state_direction.ndim == 1 else state_direction
        )
        raw = raw_direction[:, None] if raw_direction.ndim == 1 else raw_direction
        config = (
            configuration_direction[:, None]
            if configuration_direction.ndim == 1
            else configuration_direction
        )
        h_tensor = h_direction[:, :, None] if h_direction.ndim == 2 else h_direction
        h_red = h_reduced[:, :, None] if h_reduced.ndim == 2 else h_reduced
        count = matrix.shape[1]
        h_psi = np.einsum("abj,b->aj", h_red, psi, optimize=True)
        h_psi_eigen = eigenvectors.T @ h_psi
        slopes = h_psi_eigen[center.SELECTED]
        coefficients = np.zeros_like(h_psi_eigen)
        coefficients[other] = (
            -h_psi_eigen[other] / denominators[other, None]
        )
        psi_first = eigenvectors @ coefficients

        gradient_first = hessian @ raw
        h_action_first = (
            h_tensor / weights[:, None, None] / weights[None, :, None]
        )
        forcing_first = reduced_weights[:, None] * (
            np.vstack((
                q_weights[:, None]
                * gradient_first[:center.QDIM]
                / weights[:center.QDIM, None],
                np.zeros((center.REDUCED - center.QDIM, count)),
            ))
            - np.einsum(
                "abj,b->aj",
                h_action_first[center.QDIM:, :center.QDIM],
                configuration,
                optimize=True,
            )
            - hessian_action[center.QDIM:, :center.QDIM] @ config
        )
        k_first_response = np.vstack((
            np.einsum("abj,b->aj", h_red, hard, optimize=True)
            - hard[:, None] * slopes[None, :]
            + bpsi * psi_first,
            psi_first.T @ hard,
        ))
        response_first_rhs = (
            np.vstack((forcing_first, np.zeros((1, count))))
            - k_first_response
        )
        response_first = np.linalg.solve(bordered, response_first_rhs)
        residual = (
            bordered @ response_first + k_first_response
            - np.vstack((forcing_first, np.zeros((1, count))))
        )
        return slopes, psi_first, response_first, h_psi, residual

    lambda_u, psi_u_m, response_u_m, h_u_psi_m, residual_u = first_variation(
        state_u, raw_u, configuration_u, h_u, h_u_reduced,
    )
    lambda_u = float(lambda_u[0])
    psi_u = psi_u_m[:, 0]
    response_u = response_u_m[:, 0]
    hard_u, b_u = response_u[:-1], float(response_u[-1])
    h_u_psi = h_u_psi_m[:, 0]
    lambda_v, psi_v, response_v, h_v_psi, residual_v = first_variation(
        state_v, raw_v, configuration_v, h_v, h_v_reduced,
    )
    hard_v, b_v = response_v[:-1], response_v[-1]

    right_vectors = np.column_stack((
        reduced_lift @ psi,
        reduced_lift @ hard,
        configuration_action,
    ))
    fourth = center._signed(
        state, reduced_lift, state_u, state_v, right_vectors,
    ).reshape(center.REDUCED, v.shape[1], 3)
    h_uv_psi = fourth[:, :, 0]
    h_uv_hard = fourth[:, :, 1]
    h_uv_configuration = fourth[:, :, 2]
    h_u_psi_v = h_u_reduced @ psi_v
    h_v_psi_u = np.einsum(
        "abj,b->aj", h_v_reduced, psi_u, optimize=True,
    )
    lambda_uv = (
        psi @ h_uv_psi
        + np.einsum("aj,a->j", psi_v, h_u_psi, optimize=True)
        + psi_u @ h_v_psi
    )
    eigen_source = (
        h_uv_psi + h_u_psi_v + h_v_psi_u
        - psi[:, None] * lambda_uv[None, :]
        - psi_v * lambda_u
        - psi_u[:, None] * lambda_v[None, :]
    )
    eigen_coefficients = eigenvectors.T @ eigen_source
    psi_uv_coefficients = np.zeros_like(eigen_coefficients)
    psi_uv_coefficients[other] = (
        -eigen_coefficients[other] / denominators[other, None]
    )
    psi_uv_coefficients[center.SELECTED] = -(psi_u @ psi_v)
    psi_uv = eigenvectors @ psi_uv_coefficients

    gradient_uv = center._signed(state, full_lift, state_u, state_v)
    h_u_action = h_u / weights[:, None] / weights[None, :]
    h_v_action = h_v / weights[:, None, None] / weights[None, :, None]
    forcing_uv = reduced_weights[:, None] * (
        np.vstack((
            q_weights[:, None]
            * gradient_uv[:center.QDIM]
            / weights[:center.QDIM, None],
            np.zeros((center.REDUCED - center.QDIM, v.shape[1])),
        ))
        - h_u_action[center.QDIM:, :center.QDIM] @ configuration_v
        - np.einsum(
            "abj,b->aj",
            h_v_action[center.QDIM:, :center.QDIM],
            configuration_u,
            optimize=True,
        )
    ) - h_uv_configuration

    k_uv_response = np.vstack((
        h_uv_hard - hard[:, None] * lambda_uv[None, :] + bpsi * psi_uv,
        psi_uv.T @ hard,
    ))
    k_u_response_v = np.vstack((
        h_u_reduced @ hard_v - hard_v * lambda_u + psi_u[:, None] * b_v,
        psi_u @ hard_v,
    ))
    k_v_response_u = np.vstack((
        np.einsum("abj,b->aj", h_v_reduced, hard_u, optimize=True)
        - hard_u[:, None] * lambda_v[None, :]
        + psi_v * b_u,
        psi_v.T @ hard_u,
    ))
    response_uv_rhs = (
        np.vstack((forcing_uv, np.zeros((1, v.shape[1]))))
        - k_uv_response - k_u_response_v - k_v_response_u
    )
    response_uv = np.linalg.solve(bordered, response_uv_rhs)
    hard_uv, b_uv = response_uv[:-1], response_uv[-1]

    numerator = np.concatenate((
        descriptor * configuration,
        reduced_weights * (bpsi * psi + descriptor * hard),
    ))
    numerator_norm = float(np.linalg.norm(numerator))
    field = numerator / numerator_norm
    numerator_u = np.concatenate((
        ds_u * configuration + descriptor * configuration_u,
        reduced_weights * (
            b_u * psi + bpsi * psi_u + ds_u * hard + descriptor * hard_u
        ),
    ))
    numerator_v = np.vstack((
        configuration[:, None] * ds_v[None, :] + descriptor * configuration_v,
        reduced_weights[:, None] * (
            psi[:, None] * b_v[None, :] + bpsi * psi_v
            + hard[:, None] * ds_v[None, :] + descriptor * hard_v
        ),
    ))
    numerator_uv = np.vstack((
        configuration_u[:, None] * ds_v[None, :]
        + configuration_v * ds_u,
        reduced_weights[:, None] * (
            psi[:, None] * b_uv[None, :]
            + psi_u[:, None] * b_v[None, :]
            + psi_v * b_u + bpsi * psi_uv
            + hard_u[:, None] * ds_v[None, :]
            + hard_v * ds_u + descriptor * hard_uv
        ),
    ))
    projector = np.eye(center.STATE) - np.outer(field, field)
    field_u = projector @ numerator_u / numerator_norm
    field_v = projector @ numerator_v / numerator_norm
    norm_u = float(field @ numerator_u)
    norm_v = field @ numerator_v
    norm_uv = (
        numerator_u @ numerator_v + numerator @ numerator_uv
        - norm_u * norm_v
    ) / numerator_norm
    field_uv = (
        projector @ numerator_uv / numerator_norm
        - field_u[:, None] * norm_v[None, :] / numerator_norm
        - field_v * norm_u / numerator_norm
        - field[:, None] * (field_u @ field_v)[None, :]
    )

    p_action = reduced_lift @ psi
    p_u_action = reduced_lift @ psi_u
    p_v_action = reduced_lift @ psi_v
    p_uv_action = reduced_lift @ psi_uv
    hard_action = np.concatenate((configuration, reduced_weights * hard))
    hard_u_action = np.concatenate((configuration_u, reduced_weights * hard_u))
    hard_v_action = np.vstack((configuration_v, reduced_weights[:, None] * hard_v))
    hard_uv_action = np.vstack((
        np.zeros((center.QDIM, v.shape[1])),
        reduced_weights[:, None] * hard_uv,
    ))
    last_action = np.column_stack((p_action, hard_action))
    last_u_action = np.column_stack((p_u_action, hard_u_action))
    last_v_action = _pair_columns(p_v_action, hard_v_action)
    last_uv_action = _pair_columns(p_uv_action, hard_uv_action)

    cr = center._signed(state, p_action, p_action, last_action).reshape(2)
    cr_u = (
        center._signed(state, state_u, p_action, p_action, last_action).reshape(2)
        + 2 * center._signed(state, p_u_action, p_action, last_action).reshape(2)
        + center._signed(state, p_action, p_action, last_u_action).reshape(2)
    )
    cr_v = (
        center._signed(state, state_v, p_action, p_action, last_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, p_v_action, p_action, last_action).reshape(v.shape[1], 2)
        + center._signed(state, p_action, p_action, last_v_action).reshape(v.shape[1], 2)
    )
    cr_uv = (
        center._signed(state, state_u, state_v, p_action, p_action, last_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, state_u, p_v_action, p_action, last_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, state_v, p_u_action, p_action, last_action).reshape(v.shape[1], 2)
        + center._signed(state, state_u, p_action, p_action, last_v_action).reshape(v.shape[1], 2)
        + center._signed(state, state_v, p_action, p_action, last_u_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, p_uv_action, p_action, last_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, p_u_action, p_v_action, last_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, p_u_action, p_action, last_v_action).reshape(v.shape[1], 2)
        + 2 * center._signed(state, p_v_action, p_action, last_u_action).reshape(v.shape[1], 2)
        + center._signed(state, p_action, p_action, last_uv_action).reshape(v.shape[1], 2)
    )
    cpsi, remainder = cr
    c_u, remainder_u = cr_u
    c_v, remainder_v = cr_v.T
    c_uv, remainder_uv = cr_uv.T
    delta = cpsi * bpsi + descriptor * remainder
    delta_u = (
        c_u * bpsi + cpsi * b_u + ds_u * remainder
        + descriptor * remainder_u
    )
    delta_v = (
        c_v * bpsi + cpsi * b_v + ds_v * remainder
        + descriptor * remainder_v
    )
    delta_uv = (
        c_uv * bpsi + c_u * b_v + c_v * b_u + cpsi * b_uv
        + ds_u * remainder_v + ds_v * remainder_u
        + descriptor * remainder_uv
    )
    scalar_uv = (
        delta_uv / numerator_norm
        - delta_u * norm_v / numerator_norm**2
        - delta_v * norm_u / numerator_norm**2
        - delta * norm_uv / numerator_norm**2
        + 2 * delta * norm_u * norm_v / numerator_norm**3
    )
    result = np.vstack((field_uv, scalar_uv[None, :]))

    base_residual = bordered @ response - np.concatenate((forcing, [0.0]))
    mixed_residual = bordered @ response_uv - response_uv_rhs
    tiny = np.finfo(float).tiny
    diagnostics = MixedRateDiagnostics(
        base_response_residual_2_norm=float(np.linalg.norm(base_residual)),
        left_first_response_relative_residual=float(
            np.linalg.norm(residual_u) / max(np.linalg.norm(response_u_m), tiny)
        ),
        right_first_response_relative_residual=float(
            np.linalg.norm(residual_v) / max(np.linalg.norm(response_v), tiny)
        ),
        mixed_response_relative_residual=float(
            np.linalg.norm(mixed_residual) / max(np.linalg.norm(response_uv), tiny)
        ),
        mixed_eigenline_normalization_residual=float(np.linalg.norm(
            psi @ psi_uv + psi_u @ psi_v
        )),
    )
    if not np.all(np.isfinite(result)):
        raise RuntimeError("mixed-rate tensor is nonfinite")
    return result, diagnostics
