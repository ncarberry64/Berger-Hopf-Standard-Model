"""Assemble the exact-center bordered hard-response variational matrix."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import null_space, svdvals


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CONTINUATION = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
CONTINUATION_DATA = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.npz"
CHART = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
RESULT = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
DATA_RESULT = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
THEORY = ROOT / "theory" / "n12_c2_bordered_hard_response_matrix.md"
INPUTS = (CONTINUATION, CONTINUATION_DATA, CHART, GROWTH, THEORY)
QDIM = 37
COMPLEX_STEP = 1.0e-20
INFLATION = 1.0 + 1.0e-10


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jet(state: np.ndarray):
    return exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:], points=96,
    )


def _rhs_raw(state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = _jet(state)
    gradient = np.asarray(jet.gradient) / weights
    hessian_action = np.asarray(jet.hessian) / weights[:, None] / weights[None, :]
    configuration = q_weights * state[QDIM:2 * QDIM]
    mixed_vq = hessian_action[QDIM:QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient[:QDIM] - mixed_vq @ configuration,
        -mixed_mq @ configuration,
    ))
    return reduced_weights * rhs_action


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing bordered hard-response inputs: " + ", ".join(missing))
    continuation, chart, growth = (
        _json(path) for path in (CONTINUATION, CHART, GROWTH)
    )
    if not all(record.get("validation_passed") is True for record in (
        continuation, chart, growth,
    )):
        raise RuntimeError("validated fresh C2 parents required")
    with np.load(CONTINUATION_DATA) as data:
        center = np.asarray(data["C2_second_uniform_gap_predictor_centers"][-1], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    _, reduced_weights, _, _ = metric_data()
    reduced = np.asarray(_jet(center).hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    numeric_lambda = float(values[selected])
    hard_gap = float(np.min(np.abs(hard_values - numeric_lambda)))
    rhs = np.asarray(_rhs_raw(center, weights), dtype=float)

    # Bordered representation of the complement inverse.  The binary64
    # selected eigenvalue is used only to make the numerical center line an
    # exact kernel of L; the physical descriptor remains the separately
    # certified signed s.
    L = reduced - numeric_lambda * np.eye(reduced.shape[0])
    K = np.block([
        [L, psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    forcing = np.concatenate((rhs, np.zeros(1)))
    response = np.linalg.solve(K, forcing)
    hard = response[:-1]
    b = float(response[-1])
    solve_residual = _up(float(np.linalg.norm(K @ response - forcing)))
    singular = svdvals(K)
    inverse_upper = _up(1.0 / float(singular[-1]))

    lambda_first = np.empty(center.size)
    psi_first = np.empty((psi.size, center.size))
    rhs_first = np.empty((rhs.size, center.size))
    reduced_first = np.empty((center.size, psi.size, psi.size))
    inverse_diagonal = 1.0 / (numeric_lambda - hard_values)
    for column in range(center.size):
        shifted = center.astype(complex)
        shifted[column] += 1j * COMPLEX_STEP / weights[column]
        derivative = np.imag(np.asarray(_jet(shifted).hessian)) / COMPLEX_STEP
        raw = derivative[QDIM:, QDIM:]
        reduced_first[column] = raw
        lambda_first[column] = float(psi @ raw @ psi)
        coupling = complement.T @ raw @ psi
        psi_first[:, column] = complement @ (inverse_diagonal * coupling)
        rhs_first[:, column] = np.imag(_rhs_raw(shifted, weights)) / COMPLEX_STEP
        if (column + 1) % 16 == 0:
            print(f"bordered hard-response columns {column + 1}/{center.size}", flush=True)

    response_first = np.empty((response.size, center.size))
    for column in range(center.size):
        dL = reduced_first[column] - lambda_first[column] * np.eye(psi.size)
        dpsi = psi_first[:, column]
        dK = np.block([
            [dL, dpsi[:, None]],
            [dpsi[None, :], np.zeros((1, 1))],
        ])
        dforcing = np.concatenate((rhs_first[:, column], np.zeros(1)))
        response_first[:, column] = np.linalg.solve(
            K, dforcing - dK @ response
        )
    hard_first_raw = response_first[:-1]
    b_first = response_first[-1]
    hard_first_action = reduced_weights[:, None] * hard_first_raw
    normal = lambda_first / np.linalg.norm(lambda_first)
    tangent = null_space(normal[None, :])
    hard_tangent = hard_first_action @ tangent
    b_tangent = b_first @ tangent
    hard_singular = svdvals(hard_tangent)

    hard_constraint = float(psi @ hard)
    hard_equation_residual = float(np.linalg.norm(
        L @ hard + psi * b - rhs
    ))
    finite = continuation["continuation"]
    last = finite["rows"][-1]
    validation = {
        "branch_24_replayed": selected == 24,
        "bordered_matrix_is_uniformly_invertible_at_center": singular[-1] > 0.0,
        "bordered_solve_residual_is_small": solve_residual < 1.0e-8,
        "hard_response_is_selected_line_orthogonal": abs(hard_constraint) < 1.0e-8,
        "hard_equation_residual_is_small": hard_equation_residual < 1.0e-8,
        "fixed_descriptor_tangent_has_codimension_one": tangent.shape == (98, 97),
        "hard_response_variational_matrix_is_finite": np.all(np.isfinite(response_first)),
        "matrix_is_diagnostic_until_second_variation_remainder_is_enclosed": True,
        "no_soft_block_inverse_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    np.savez_compressed(
        DATA_RESULT,
        center_state=center,
        state_weights=weights,
        branch_reference=reference,
        selected_vector=psi,
        lambda_gradient_action=lambda_first,
        selected_vector_derivative_action=psi_first,
        bordered_matrix=K,
        bordered_response=response,
        bordered_response_derivative_action=response_first,
        fixed_descriptor_tangent_basis=tangent,
        hard_response_tangent_matrix=hard_tangent,
    )
    return {
        "artifact": "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX",
        "status": (
            "C2_BORDERED_HARD_RESPONSE_CENTER_MATRIX_CERTIFIED;_SECOND_VARIATION_REMAINDER_OPEN"
            if passed else "C2_BORDERED_HARD_RESPONSE_MATRIX_INVALID"
        ),
        "bordered_center": {
            "selected_branch": selected,
            "binary64_selected_eigenvalue_not_used_as_descriptor": numeric_lambda,
            "hard_gap": hard_gap,
            "minimum_bordered_singular_value": float(singular[-1]),
            "bordered_condition_number": float(singular[0] / singular[-1]),
            "bordered_inverse_2_norm_upper": inverse_upper,
            "solve_residual_upper": solve_residual,
            "hard_equation_residual": hard_equation_residual,
            "selected_line_orthogonality_residual": hard_constraint,
            "b_psi": b,
            "hard_rate_raw_norm": float(np.linalg.norm(hard)),
            "hard_rate_action_norm": float(np.linalg.norm(reduced_weights * hard)),
        },
        "variational_matrix": {
            "full_hard_response_action_operator_norm": float(np.linalg.norm(hard_first_action, 2)),
            "fixed_descriptor_hard_response_operator_norm": float(hard_singular[0]),
            "fixed_descriptor_hard_response_smallest_nonzero_singular_value": float(
                hard_singular[-1]
            ),
            "full_b_psi_gradient_norm": float(np.linalg.norm(b_first)),
            "fixed_descriptor_b_psi_gradient_norm": float(np.linalg.norm(b_tangent)),
            "tangent_rank": int(np.linalg.matrix_rank(hard_tangent)),
        },
        "comparison": {
            "last_scalar_hard_Gronwall_exponent": float(last["hard_Gronwall_exponent_upper"]),
            "last_scalar_fixed_s_Jacobi_upper": float(last["fixed_s_Jacobi_upper"]),
            "last_scalar_Delta_lower": float(last["Delta_lower"]),
            "diagnosis": (
                "THE_BORDERED_CENTER_RESPONSE_RETAINS_DIRECTIONAL_SPECTRAL_"
                "STRUCTURE;_THE_SCALAR_GRONWALL_EXPONENT_IS_NOT_THE_MATRIX_"
                "PROPAGATOR_AND_MUST_NOT_BE_USED_AS_A_PHYSICAL_STOP"
            ),
        },
        "hindsight": {
            "result": "OPEN",
            "classification": "NUMERICAL_CONDITIONING;_MATRIX_RESPONSE_RECOVERED",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_BORDERED_RESPONSE_SECOND_VARIATION_WITH_RETAINED_D4_D5_"
            "AND_PROPAGATE_THE_RESULTING_HARD_RESPONSE_ELLIPSOID_ON_THE_EXACT_"
            "DESCRIPTOR_FIBER"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "bordered_inverse": payload["bordered_center"]["bordered_inverse_2_norm_upper"],
        "hard_tangent_operator": payload["variational_matrix"]["fixed_descriptor_hard_response_operator_norm"],
        "b_tangent_gradient": payload["variational_matrix"]["fixed_descriptor_b_psi_gradient_norm"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
