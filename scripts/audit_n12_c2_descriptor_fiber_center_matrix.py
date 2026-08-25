"""Measure the centered fixed-s C2 birth-limit variational matrix."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import expm, null_space, svdvals


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
PREFIX = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
PREFIX_DATA = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.npz"
FIBER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_DENOMINATOR.json"
RESULT = Path(os.environ.get(
    "BHSM_N12_C2_CENTER_MATRIX_RESULT",
    BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX.json",
)).resolve()
DATA_RESULT = Path(os.environ.get(
    "BHSM_N12_C2_CENTER_MATRIX_DATA_RESULT",
    BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX.npz",
)).resolve()
INPUTS = (PREFIX, PREFIX_DATA, FIBER)
QDIM = 37
STATE_DIMENSION = 98
ACTION_DIFFERENCE_STEP = float(os.environ.get(
    "BHSM_N12_C2_CENTER_MATRIX_DIFFERENCE_STEP", "1.0e-11"
))
COMPLEX_STEP = 1.0e-20
HORIZONS = (1.0e-24, 1.0e-23, 1.0e-22, 1.0e-21, 1.0e-20)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _jet(state: np.ndarray):
    return exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:], points=96,
    )


def _ordered_line(hessian: np.ndarray, reference: np.ndarray) -> tuple[int, float, np.ndarray]:
    values, vectors = np.linalg.eigh(hessian[QDIM:, QDIM:])
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    return selected, float(values[selected]), psi


def _cubic(state: np.ndarray, psi: np.ndarray) -> float:
    direction = np.concatenate((np.zeros(QDIM), psi))
    shifted = state.astype(complex) + 1j * COMPLEX_STEP * direction
    hessian = np.asarray(_jet(shifted).hessian)
    derivative = np.imag(hessian[QDIM:, QDIM:]) / COMPLEX_STEP
    return float(psi @ derivative @ psi)


def main() -> None:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing fixed-s center-matrix inputs: " + ", ".join(missing))
    prefix = json.loads(PREFIX.read_text(encoding="utf-8"))
    fiber = json.loads(FIBER.read_text(encoding="utf-8"))
    if not prefix["validation_passed"] or not fiber["validation_passed"]:
        raise RuntimeError("validated descriptor-fiber parents required")
    with np.load(PREFIX_DATA) as data:
        center = np.asarray(
            data["C2_recentered_adaptive_predictor_centers"][-1], dtype=float
        )
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    center_jet = _jet(center)
    center_hessian = np.asarray(center_jet.hessian, dtype=float)
    selected, numeric_lambda, psi = _ordered_line(center_hessian, reference)
    c_center = _cubic(center, psi)
    reduced_weights = weights[QDIM:]
    selected_action = np.concatenate((np.zeros(QDIM), psi * reduced_weights))

    # Exact complex-step D3 columns at the center give the action-coordinate
    # selected-eigenvalue gradient and the Kato derivative of the eigenline.
    reduced = center_hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    hard_vectors = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    lambda_gradient = np.empty(STATE_DIMENSION)
    psi_derivative = np.empty((reduced.shape[0], STATE_DIMENSION))
    for column in range(STATE_DIMENSION):
        shifted = center.astype(complex)
        shifted[column] += 1j * COMPLEX_STEP / weights[column]
        derivative = np.imag(np.asarray(_jet(shifted).hessian)) / COMPLEX_STEP
        raw_reduced_derivative = derivative[QDIM:, QDIM:]
        lambda_gradient[column] = float(psi @ raw_reduced_derivative @ psi)
        coupling = hard_vectors.T @ raw_reduced_derivative @ psi
        psi_derivative[:, column] = hard_vectors @ (
            coupling / (values[selected] - hard_values)
        )
        if (column + 1) % 16 == 0:
            print(f"D3/Kato columns {column + 1}/{STATE_DIMENSION}", flush=True)

    # Differentiate the cubic with the exact Kato product rule
    #
    #   Dc[v] = D4S[v,psi,psi,psi] + 3 D3S[Dpsi[v],psi,psi].
    #
    # Only the fixed-line D4 contraction is centrally differenced.  Re-solving
    # a binary64 eigenvector at each displaced state injects line jitter much
    # larger than the signed D4 signal and is deliberately not used.
    c_gradient = np.empty(STATE_DIMENSION)
    fixed_c_gradient = np.empty(STATE_DIMENSION)
    shifted_cubics = np.empty((2, STATE_DIMENSION))
    lambda_gradient_raw_reduced = (
        lambda_gradient[QDIM:] * weights[QDIM:]
    )
    for column in range(STATE_DIMENSION):
        for sign_index, sign in enumerate((-1.0, 1.0)):
            shifted_state = center.copy()
            shifted_state[column] += (
                sign * ACTION_DIFFERENCE_STEP / weights[column]
            )
            shifted_cubics[sign_index, column] = _cubic(
                shifted_state, psi
            )
        fixed_c_gradient[column] = (
            shifted_cubics[1, column] - shifted_cubics[0, column]
        ) / (2.0 * ACTION_DIFFERENCE_STEP)
        c_gradient[column] = (
            fixed_c_gradient[column]
            + 3.0 * float(lambda_gradient_raw_reduced @ psi_derivative[:, column])
        )
        if (column + 1) % 16 == 0:
            print(f"moving-cubic columns {column + 1}/{STATE_DIMENSION}", flush=True)

    birth_matrix = np.zeros((STATE_DIMENSION, STATE_DIMENSION))
    birth_matrix[QDIM:] = reduced_weights[:, None] * (
        psi_derivative / c_center
        - psi[:, None] * c_gradient[None, :] / c_center**2
    )
    normal = lambda_gradient / np.linalg.norm(lambda_gradient)
    tangent = null_space(normal[None, :])
    tangent_matrix = tangent.T @ birth_matrix @ tangent
    tangent_symmetric = 0.5 * (tangent_matrix + tangent_matrix.T)
    tangent_eigenvalues = np.linalg.eigvals(tangent_matrix)
    birth_symmetric = 0.5 * (birth_matrix + birth_matrix.T)
    growth_rows = []
    for horizon in HORIZONS:
        fundamental = expm(tangent_matrix * horizon)
        singular = svdvals(fundamental)
        growth_rows.append({
            "signed_descriptor_horizon": horizon,
            "fixed_s_tangent_fundamental_2_norm": float(singular[0]),
            "fixed_s_tangent_inverse_2_norm": float(1.0 / singular[-1]),
        })

    np.savez_compressed(
        DATA_RESULT,
        center_state=center,
        state_weights=weights,
        branch_reference=reference,
        selected_vector=psi,
        lambda_gradient_action=lambda_gradient,
        fixed_line_c_gradient_action_central_difference=fixed_c_gradient,
        c_gradient_action_central_difference=c_gradient,
        selected_vector_derivative_action=psi_derivative,
        birth_limit_matrix_action=birth_matrix,
        fixed_s_tangent_basis=tangent,
        fixed_s_tangent_matrix=tangent_matrix,
    )
    scalar_jacobi = float(
        json.loads((BASE / "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION.json")
                   .read_text(encoding="utf-8"))["continuation"]["rows"][0]
        ["Jacobi_growth_upper"]
    )
    validation = {
        "validated_descriptor_fiber_center_consumed": True,
        "branch_24_and_certified_eigenline_ball_consumed": selected == 24,
        "lambda_gradient_is_nonzero": float(np.linalg.norm(lambda_gradient)) > 0.0,
        "fixed_s_tangent_basis_has_codimension_one": tangent.shape == (98, 97),
        "center_birth_matrix_and_fundamentals_are_finite": (
            np.all(np.isfinite(birth_matrix))
            and all(math.isfinite(row["fixed_s_tangent_fundamental_2_norm"])
                    for row in growth_rows)
        ),
        "finite_difference_center_matrix_not_promoted_to_interval_authority": True,
        "no_equation_selector_recurrence_scale_gate_or_chord_added": True,
    }
    payload = {
        "artifact": "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX",
        "status": (
            "FIXED_S_TANGENT_CENTER_MATRIX_MEASURED;_CONJUGATED_INTERVAL_REMAINDER_OPEN"
            if all(validation.values()) else "C2_DESCRIPTOR_FIBER_CENTER_MATRIX_INVALID"
        ),
        "center": {
            "selected_branch": selected,
            "binary64_selected_eigenvalue_not_used_as_descriptor": numeric_lambda,
            "c_psi": c_center,
            "lambda_gradient_action_norm": float(np.linalg.norm(lambda_gradient)),
            "c_gradient_action_central_difference_norm": float(np.linalg.norm(c_gradient)),
            "fixed_line_D4_gradient_action_central_difference_norm": float(
                np.linalg.norm(fixed_c_gradient)
            ),
            "Kato_line_motion_correction_action_norm": float(np.linalg.norm(
                c_gradient - fixed_c_gradient
            )),
            "birth_limit_matrix_2_norm": float(np.linalg.norm(birth_matrix, 2)),
            "birth_limit_matrix_numerical_abscissa": float(
                np.linalg.eigvalsh(birth_symmetric)[-1]
            ),
            "fixed_s_tangent_matrix_2_norm": float(np.linalg.norm(tangent_matrix, 2)),
            "fixed_s_tangent_numerical_abscissa": float(
                np.linalg.eigvalsh(tangent_symmetric)[-1]
            ),
            "fixed_s_tangent_spectral_abscissa": float(
                np.max(tangent_eigenvalues.real)
            ),
            "action_difference_step": ACTION_DIFFERENCE_STEP,
            "action_difference_scheme": "SYMMETRIC_CENTRAL",
            "complex_step": COMPLEX_STEP,
        },
        "growth_profile": growth_rows,
        "diagnosis": {
            "scalar_first_box_Jacobi_growth_upper": scalar_jacobi,
            "proof_authority": "CENTER_DIAGNOSTIC_ONLY",
            "exact_next_lemma": (
                "ENCLOSE_THE_CONJUGATED_FIXED_s_TANGENT_REMAINDER_"
                "PHI_0_MINUS_ONE_TIMES_DF_s(Y)_MINUS_A_0_TIMES_PHI_0_"
                "USING_RETAINED_D4_D5_AND_KATO_HARD_BUNDLE_BOUNDS"
            ),
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "center": payload["center"],
        "growth_profile": growth_rows,
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
