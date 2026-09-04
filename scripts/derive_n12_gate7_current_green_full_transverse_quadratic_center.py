"""Derive the full current-Green transverse quadratic center operator.

This is the center half of the outward majorant.  It reuses the retained
signed action tensor algebra and evaluates the complete symmetric bilinear
operator on the 73-dimensional complement of the current Green axis.  The
script is restart-safe; it intentionally does not promote interval authority.
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
import time

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from derive_n12_action_signed_interval_majorants import action_bound  # noqa: E402
from derive_n12_gate7_exact_signed_mixed_field_curvature import _exact_jet  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
SCALAR = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS.json"
SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_TRANSVERSE_QUADRATIC_SEED.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_full_transverse_quadratic_center_work"
THIS_SCRIPT = Path(__file__).resolve()
ACTION_SCRIPT = ROOT / "scripts/derive_n12_action_signed_interval_majorants.py"
JET_SCRIPT = ROOT / "scripts/derive_n12_gate7_exact_signed_mixed_field_curvature.py"
METRIC_SCRIPT = ROOT / "src/bhsm/interface/aether_forward_c2_descriptor_cover.py"

QDIM = 37
REDUCED = 61
STATE = 98
COORDINATES = 74
TRANSVERSE = 73
OUTPUTS = 99
SELECTED = 24
DESCRIPTOR_SCALE = 1.0e-7
SHARD_REVISION = 4
ALGORITHM_ID = "CURRENT_GREEN_FULL_TRANSVERSE_CENTER_EXACT_SIGNED_TENSOR_V4_COMPONENTWISE"


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _campaign_fingerprint() -> str:
    sources = (
        ENDPOINT.with_suffix(".npz"), REPLAY.with_suffix(".npz"),
        JACOBIAN.with_suffix(".npz"), PARTITION.with_suffix(".npz"),
        SCALAR.with_suffix(".npz"), ACTION_SCRIPT, JET_SCRIPT, METRIC_SCRIPT,
    )
    digest = hashlib.sha256(ALGORITHM_ID.encode("ascii"))
    for source in sources:
        digest.update(source.read_bytes())
    return digest.hexdigest().upper()


def _frame(tangent: np.ndarray) -> np.ndarray:
    result = np.zeros((OUTPUTS, COORDINATES))
    result[:STATE, :TRANSVERSE] = tangent
    result[STATE, TRANSVERSE] = DESCRIPTOR_SCALE
    return result


def _pair_columns(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    result = np.empty((left.shape[0], 2 * left.shape[1]))
    result[:, 0::2] = left
    result[:, 1::2] = right
    return result


def _signed(state: np.ndarray, *directions: np.ndarray) -> np.ndarray:
    indices = tuple(
        index for index, direction in enumerate(directions)
        if np.asarray(direction).ndim == 2
    )
    return np.asarray(action_bound(
        state, mixed_directions=list(directions),
        exact_signed_tensor_indices=indices,
    ).d[-1], dtype=float)


def _kind_shard(kind: str, index: int) -> Path:
    return WORK / f"{kind}_{index:03d}.npz"


def _valid(path: Path, kind: str, index: int, fingerprint: str) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return bool(
                str(source["kind"].item()) == kind
                and int(source["index"]) == index
                and int(source["shard_revision"]) == SHARD_REVISION
                and str(source["campaign_fingerprint"].item()) == fingerprint
                and np.isfinite(float(source["quadratic_Frobenius_norm"]))
                and source["quadratic_output_Frobenius_norms"].shape == (OUTPUTS,)
                and np.all(np.isfinite(source["quadratic_output_Frobenius_norms"]))
                and source["quadratic_output_maximum_component_absolute"].shape == (OUTPUTS,)
                and np.all(np.isfinite(source["quadratic_output_maximum_component_absolute"]))
            )
    except Exception:
        return False


def _quadratic_row(
    kind: str,
    index: int,
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
    tangent: np.ndarray,
    axis: np.ndarray,
    field_reference: np.ndarray,
    axis_projection_residual: float,
) -> dict[str, float | int | str | np.ndarray]:
    q_weights, reduced_weights, _, _ = metric_data()
    gradient, hessian = _exact_jet(state)
    gradient = np.asarray(gradient, dtype=float)
    hessian = np.asarray(hessian, dtype=float)
    reduced_hessian = 0.5 * (
        hessian[QDIM:, QDIM:] + hessian[QDIM:, QDIM:].T
    )
    eigenvalues, eigenvectors = np.linalg.eigh(reduced_hessian)
    psi = eigenvectors[:, SELECTED]
    if float(psi @ reference) < 0.0:
        eigenvectors[:, SELECTED] *= -1.0
        psi = -psi
    gap = float(min(abs(
        eigenvalues[SELECTED] - np.delete(eigenvalues, SELECTED)
    )))

    basis = null_space(np.asarray(axis, dtype=float).reshape(1, -1))
    if basis.shape != (COORDINATES, TRANSVERSE):
        raise RuntimeError("current Green complement changed rank")
    augmented = _frame(tangent) @ basis
    state_V = augmented[:STATE]
    descriptor_V = augmented[STATE]

    reduced_lift = np.zeros((STATE, REDUCED))
    reduced_lift[QDIM:] = reduced_weights[:, None] * np.eye(REDUCED)
    full_lift = np.diag(weights)
    configuration = q_weights * state[QDIM:2 * QDIM]
    configuration_action = np.zeros(STATE)
    configuration_action[:QDIM] = configuration
    gradient_action = gradient / weights
    hessian_action = hessian / weights[:, None] / weights[None, :]
    forcing = reduced_weights * (
        np.concatenate((
            q_weights * gradient_action[:QDIM], np.zeros(REDUCED - QDIM),
        )) - hessian_action[QDIM:, :QDIM] @ configuration
    )
    bordered = np.block([
        [
            reduced_hessian - eigenvalues[SELECTED] * np.eye(REDUCED),
            psi[:, None],
        ],
        [psi[None, :], np.zeros((1, 1))],
    ])
    response = np.linalg.solve(
        bordered, np.concatenate((forcing, np.zeros(1))),
    )
    hard = response[:-1]
    bpsi = float(response[-1])

    raw_V = state_V / weights[:, None]
    configuration_V = q_weights[:, None] * raw_V[QDIM:2 * QDIM]
    # One signed action traversal replaces 73 separate complex-step Hessians.
    H_V = _signed(state, full_lift, full_lift, state_V)
    H_V_reduced = 0.5 * (
        H_V[QDIM:, QDIM:, :] + H_V[QDIM:, QDIM:, :].transpose(1, 0, 2)
    )
    H_V_psi = np.einsum("abj,b->aj", H_V_reduced, psi, optimize=True)
    H_V_psi_eigen = eigenvectors.T @ H_V_psi
    lambda_V = H_V_psi_eigen[SELECTED]
    other = np.arange(REDUCED) != SELECTED
    denominators = eigenvalues - eigenvalues[SELECTED]
    psi_V_coefficients = np.zeros_like(H_V_psi_eigen)
    psi_V_coefficients[other] = (
        -H_V_psi_eigen[other] / denominators[other, None]
    )
    psi_V = eigenvectors @ psi_V_coefficients

    right_vectors = np.column_stack((
        reduced_lift @ psi,
        reduced_lift @ hard,
        configuration_action,
    ))
    D4 = _signed(
        state, reduced_lift, state_V, state_V, right_vectors,
    )
    H_VV_psi = D4[:, :, :, 0]
    H_VV_hard = D4[:, :, :, 1]
    H_VV_configuration = D4[:, :, :, 2]
    eigen_cross = np.einsum("aj,ak->jk", psi_V, H_V_psi, optimize=True)
    lambda_VV = (
        np.einsum("a,ajk->jk", psi, H_VV_psi, optimize=True)
        + eigen_cross + eigen_cross.T
    )
    H_V_psi_V = np.einsum(
        "abj,bk->ajk", H_V_reduced, psi_V, optimize=True,
    )
    eigen_source = (
        H_VV_psi + H_V_psi_V + H_V_psi_V.transpose(0, 2, 1)
        - psi[:, None, None] * lambda_VV[None, :, :]
        - psi_V[:, None, :] * lambda_V[None, :, None]
        - psi_V[:, :, None] * lambda_V[None, None, :]
    )
    eigen_coefficients = np.einsum(
        "ab,bjk->ajk", eigenvectors.T, eigen_source, optimize=True,
    )
    psi_VV_coefficients = np.zeros_like(eigen_coefficients)
    psi_VV_coefficients[other] = (
        -eigen_coefficients[other] / denominators[other, None, None]
    )
    psi_VV_coefficients[SELECTED] = -(psi_V.T @ psi_V)
    psi_VV = np.einsum(
        "ab,bjk->ajk", eigenvectors, psi_VV_coefficients, optimize=True,
    )

    gradient_V = hessian @ raw_V
    hessian_V_action = H_V / (
        weights[:, None, None] * weights[None, :, None]
    )
    forcing_V = reduced_weights[:, None] * (
        np.vstack((
            q_weights[:, None] * gradient_V[:QDIM] / weights[:QDIM, None],
            np.zeros((REDUCED - QDIM, TRANSVERSE)),
        ))
        - np.einsum(
            "abj,b->aj", hessian_V_action[QDIM:, :QDIM], configuration,
            optimize=True,
        )
        - hessian_action[QDIM:, :QDIM] @ configuration_V
    )
    gradient_VV = np.einsum(
        "abj,bk->ajk", H_V, raw_V, optimize=True,
    )
    gradient_VV = 0.5 * (gradient_VV + gradient_VV.transpose(0, 2, 1))
    hessian_configuration_cross = np.einsum(
        "abj,bk->ajk", hessian_V_action[QDIM:, :QDIM], configuration_V,
        optimize=True,
    )
    forcing_VV = reduced_weights[:, None, None] * (
        np.concatenate((
            q_weights[:, None, None] * gradient_VV[:QDIM]
            / weights[:QDIM, None, None],
            np.zeros((REDUCED - QDIM, TRANSVERSE, TRANSVERSE)),
        ), axis=0)
        - hessian_configuration_cross
        - hessian_configuration_cross.transpose(0, 2, 1)
    ) - H_VV_configuration

    def K_V_times(vector: np.ndarray) -> np.ndarray:
        vector_hard, multiplier = vector[:-1], float(vector[-1])
        top = (
            np.einsum("abj,b->aj", H_V_reduced, vector_hard, optimize=True)
            - vector_hard[:, None] * lambda_V[None, :]
            + multiplier * psi_V
        )
        return np.vstack((top, psi_V.T @ vector_hard))

    response_V = np.linalg.solve(
        bordered,
        np.vstack((forcing_V, np.zeros((1, TRANSVERSE))))
        - K_V_times(response),
    )
    hard_V = response_V[:-1]
    b_V = response_V[-1]
    K_VV_response = np.concatenate((
        H_VV_hard - hard[:, None, None] * lambda_VV[None, :, :]
        + bpsi * psi_VV,
        np.einsum("ajk,a->jk", psi_VV, hard, optimize=True)[None, :, :],
    ), axis=0)
    K_V_response_V = np.concatenate((
        np.einsum("abj,bk->ajk", H_V_reduced, hard_V, optimize=True)
        - hard_V[:, None, :] * lambda_V[None, :, None]
        + psi_V[:, :, None] * b_V[None, None, :],
        np.einsum("aj,ak->jk", psi_V, hard_V, optimize=True)[None, :, :],
    ), axis=0)
    response_VV_rhs = (
        np.concatenate((forcing_VV, np.zeros((1, TRANSVERSE, TRANSVERSE))), axis=0)
        - K_VV_response - K_V_response_V
        - K_V_response_V.transpose(0, 2, 1)
    )
    response_VV = np.linalg.solve(
        bordered, response_VV_rhs.reshape((REDUCED + 1, -1)),
    ).reshape((REDUCED + 1, TRANSVERSE, TRANSVERSE))
    hard_VV = response_VV[:-1]
    b_VV = response_VV[-1]

    numerator = np.concatenate((
        descriptor * configuration,
        reduced_weights * (bpsi * psi + descriptor * hard),
    ))
    numerator_norm = float(np.linalg.norm(numerator))
    field = numerator / numerator_norm
    numerator_V = np.vstack((
        configuration[:, None] * descriptor_V[None, :]
        + descriptor * configuration_V,
        reduced_weights[:, None] * (
            psi[:, None] * b_V[None, :] + bpsi * psi_V
            + hard[:, None] * descriptor_V[None, :] + descriptor * hard_V
        ),
    ))
    configuration_descriptor_cross = (
        configuration_V[:, :, None] * descriptor_V[None, None, :]
    )
    response_psi_cross = psi_V[:, :, None] * b_V[None, None, :]
    response_descriptor_cross = (
        hard_V[:, :, None] * descriptor_V[None, None, :]
    )
    numerator_VV = np.concatenate((
        configuration_descriptor_cross
        + configuration_descriptor_cross.transpose(0, 2, 1),
        reduced_weights[:, None, None] * (
            psi[:, None, None] * b_VV[None, :, :]
            + response_psi_cross + response_psi_cross.transpose(0, 2, 1)
            + bpsi * psi_VV
            + hard[:, None, None] * 0.0
            + response_descriptor_cross
            + response_descriptor_cross.transpose(0, 2, 1)
            + descriptor * hard_VV
        ),
    ), axis=0)
    projector = np.eye(STATE) - np.outer(field, field)
    field_V = projector @ numerator_V / numerator_norm
    alpha = field @ numerator_V
    field_VV = (
        np.einsum("ab,bjk->ajk", projector, numerator_VV, optimize=True)
        / numerator_norm
        - field_V[:, :, None] * alpha[None, None, :] / numerator_norm
        - field_V[:, None, :] * alpha[None, :, None] / numerator_norm
        - field[:, None, None] * (field_V.T @ field_V)[None, :, :]
    )

    p_action = reduced_lift @ psi
    hard_action = np.concatenate((configuration, reduced_weights * hard))
    last_action = np.column_stack((p_action, hard_action))
    p_V_action = reduced_lift @ psi_V
    hard_V_action = np.vstack((configuration_V, reduced_weights[:, None] * hard_V))
    last_V_action = _pair_columns(p_V_action, hard_V_action)
    p_VV_action = np.einsum("ab,bjk->ajk", reduced_lift, psi_VV, optimize=True)
    hard_VV_action = np.concatenate((
        np.zeros((QDIM, TRANSVERSE, TRANSVERSE)),
        reduced_weights[:, None, None] * hard_VV,
    ), axis=0)

    cR = _signed(state, p_action, p_action, last_action).reshape(2)
    cR_V = (
        _signed(state, state_V, p_action, p_action, last_action).reshape(TRANSVERSE, 2)
        + 2 * _signed(state, p_V_action, p_action, last_action).reshape(TRANSVERSE, 2)
        + _signed(state, p_action, p_action, last_V_action).reshape(TRANSVERSE, 2)
    )
    term_A = _signed(
        state, state_V, state_V, p_action, p_action, last_action,
    ).reshape(TRANSVERSE, TRANSVERSE, 2)
    term_B = _signed(
        state, state_V, p_V_action, p_action, last_action,
    ).reshape(TRANSVERSE, TRANSVERSE, 2)
    term_C = _signed(
        state, state_V, p_action, p_action, last_V_action,
    ).reshape(TRANSVERSE, TRANSVERSE, 2)
    p_VV_covector = _signed(
        state, full_lift, p_action, last_action,
    ).reshape(STATE, 2)
    term_D = np.einsum(
        "ac,ajk->jkc", p_VV_covector, p_VV_action, optimize=True,
    )
    term_E = _signed(
        state, p_V_action, p_V_action, last_action,
    ).reshape(TRANSVERSE, TRANSVERSE, 2)
    term_F = _signed(
        state, p_V_action, p_action, last_V_action,
    ).reshape(TRANSVERSE, TRANSVERSE, 2)
    last_covector = _signed(
        state, p_action, p_action, full_lift,
    ).reshape(STATE)
    term_G = np.empty((TRANSVERSE, TRANSVERSE, 2))
    term_G[:, :, 0] = np.einsum(
        "a,ajk->jk", last_covector, p_VV_action, optimize=True,
    )
    term_G[:, :, 1] = np.einsum(
        "a,ajk->jk", last_covector, hard_VV_action, optimize=True,
    )
    cR_VV = (
        term_A + 2 * term_B + 2 * term_B.transpose(1, 0, 2)
        + term_C + term_C.transpose(1, 0, 2) + 2 * term_D + 2 * term_E
        + 2 * term_F + 2 * term_F.transpose(1, 0, 2) + term_G
    )
    cpsi, remainder = cR
    c_V, remainder_V = cR_V.T
    c_VV = cR_VV[:, :, 0]
    remainder_VV = cR_VV[:, :, 1]
    delta = cpsi * bpsi + descriptor * remainder
    delta_V = (
        c_V * bpsi + cpsi * b_V + descriptor_V * remainder
        + descriptor * remainder_V
    )
    delta_VV = (
        c_VV * bpsi + c_V[:, None] * b_V[None, :]
        + c_V[None, :] * b_V[:, None] + cpsi * b_VV
        + descriptor_V[:, None] * remainder_V[None, :]
        + descriptor_V[None, :] * remainder_V[:, None]
        + descriptor * remainder_VV
    )
    norm_V = alpha
    norm_VV = (
        numerator_V.T @ numerator_V
        + np.einsum("a,ajk->jk", numerator, numerator_VV, optimize=True)
        - norm_V[:, None] * norm_V[None, :]
    ) / numerator_norm
    scalar_VV = (
        delta_VV / numerator_norm
        - delta_V[:, None] * norm_V[None, :] / numerator_norm**2
        - delta_V[None, :] * norm_V[:, None] / numerator_norm**2
        - delta * norm_VV / numerator_norm**2
        + 2 * delta * norm_V[:, None] * norm_V[None, :] / numerator_norm**3
    )
    quadratic = np.concatenate((field_VV, scalar_VV[None, :, :]), axis=0)

    base_residual = bordered @ response - np.concatenate((forcing, [0.0]))
    first_residual = (
        bordered @ response_V + K_V_times(response)
        - np.vstack((forcing_V, np.zeros((1, TRANSVERSE))))
    )
    second_residual = (
        np.einsum("ab,bjk->ajk", bordered, response_VV, optimize=True)
        - response_VV_rhs
    )
    return {
        "kind": kind,
        "index": index,
        "quadratic_Frobenius_norm": float(np.linalg.norm(quadratic)),
        "quadratic_maximum_component_absolute": float(np.max(abs(quadratic))),
        "quadratic_output_Frobenius_norms": np.linalg.norm(
            quadratic, axis=(1, 2),
        ),
        "quadratic_output_maximum_component_absolute": np.max(
            abs(quadratic), axis=(1, 2),
        ),
        "field_quadratic_Frobenius_norm": float(np.linalg.norm(field_VV)),
        "scalar_quadratic_Frobenius_norm": float(np.linalg.norm(scalar_VV)),
        "minimum_selected_eigenline_gap": gap,
        "normalized_field_reference_difference_2_norm": float(
            np.linalg.norm(field - field_reference)
        ),
        "axis_projection_residual_2_norm": axis_projection_residual,
        "base_response_residual_2_norm": float(np.linalg.norm(base_residual)),
        "first_response_relative_Frobenius_residual": float(
            np.linalg.norm(first_residual) / max(np.linalg.norm(response_V), np.finfo(float).tiny)
        ),
        "second_response_relative_Frobenius_residual": float(
            np.linalg.norm(second_residual) / max(np.linalg.norm(response_VV), np.finfo(float).tiny)
        ),
        "second_eigenline_normalization_Frobenius_residual": float(np.linalg.norm(
            np.einsum("a,ajk->jk", psi, psi_VV, optimize=True) + psi_V.T @ psi_V
        )),
        "second_field_normalization_Frobenius_residual": float(np.linalg.norm(
            np.einsum("a,ajk->jk", field, field_VV, optimize=True) + field_V.T @ field_V
        )),
    }


def _load_inputs():
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        endpoint_states = np.asarray(source["projected_states"], dtype=float)
        endpoint_descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_values = np.asarray(source["midpoint_augmented_action_values"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        endpoint_tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
        midpoint_tangents = np.asarray(source["midpoint_physical_tangent_action"], dtype=float)
        endpoint_rates = np.asarray(source["exact_endpoint_augmented_rates"], dtype=float)
        midpoint_rates = np.asarray(source["exact_midpoint_augmented_rates"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        endpoint_axes = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
    with np.load(SCALAR.with_suffix(".npz")) as source:
        midpoint_directions = np.asarray(source["midpoint_direction_mid"], dtype=float)
    midpoint_axes = np.empty((370, COORDINATES))
    midpoint_axis_residuals = np.empty(370)
    for interval in range(370):
        midpoint_frame = _frame(midpoint_tangents[interval])
        coordinate = np.linalg.lstsq(
            midpoint_frame, midpoint_directions[interval], rcond=None,
        )[0]
        midpoint_axis_residuals[interval] = np.linalg.norm(
            midpoint_frame @ coordinate - midpoint_directions[interval]
        )
        midpoint_axes[interval] = coordinate / np.linalg.norm(coordinate)
    return {
        "endpoint": (
            endpoint_states, endpoint_descriptors, endpoint_tangents,
            endpoint_axes, endpoint_rates[:, :STATE], np.zeros(371),
        ),
        "midpoint": (
            midpoint_values[:, :STATE] / weights,
            midpoint_values[:, STATE], midpoint_tangents,
            midpoint_axes, midpoint_rates[:, :STATE], midpoint_axis_residuals,
        ),
        "weights": weights,
        "reference": reference,
    }


def _worker(kind: str, indices: list[int]) -> dict[str, float]:
    inputs = _load_inputs()
    fingerprint = _campaign_fingerprint()
    states, descriptors, tangents, axes, fields, axis_residuals = inputs[kind]
    WORK.mkdir(parents=True, exist_ok=True)
    computed = reused = 0
    elapsed = 0.0
    for index in indices:
        target = _kind_shard(kind, index)
        if _valid(target, kind, index, fingerprint):
            reused += 1
            continue
        started = time.perf_counter()
        row = _quadratic_row(
            kind, index, states[index], float(descriptors[index]),
            inputs["weights"], inputs["reference"], tangents[index], axes[index],
            fields[index], float(axis_residuals[index]),
        )
        duration = time.perf_counter() - started
        np.savez_compressed(
            target, **{key: np.asarray(value) for key, value in row.items()},
            elapsed_seconds=np.asarray(duration),
            worker_id=np.asarray(os.getpid()), shard_revision=np.asarray(SHARD_REVISION),
            campaign_fingerprint=np.asarray(fingerprint),
        )
        computed += 1
        elapsed += duration
        print(json.dumps({"kind": kind, "index": index, "elapsed_seconds": duration}), flush=True)
    return {"computed": computed, "reused": reused, "elapsed_seconds": elapsed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("endpoint", "midpoint"), required=True)
    parser.add_argument("--indices", required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    indices = [int(value) for value in args.indices.split(",") if value]
    groups = [indices[index::args.workers] for index in range(args.workers)]
    totals = {"computed": 0.0, "reused": 0.0, "elapsed_seconds": 0.0}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(_worker, args.kind, group) for group in groups if group]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row[key]
            print(json.dumps({"totals": totals}), flush=True)


if __name__ == "__main__":
    main()
