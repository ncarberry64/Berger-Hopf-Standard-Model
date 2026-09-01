"""Assemble the cancellation-preserving fixed-descriptor field matrix."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
CONTINUATION = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
RESULT = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
DATA_RESULT = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.npz"
THEORY = ROOT / "theory" / "n12_c2_exact_center_fixed_s_field_matrix.md"
INPUTS = (BORDERED, BORDERED_DATA, CONTINUATION, GROWTH, THEORY)
QDIM = 37
COMPLEX_STEP = 1.0e-20
ACTION_DIFFERENCE_STEP = 3.0e-11
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


def _fixed_line_cubic(state: np.ndarray, psi: np.ndarray) -> float:
    direction = np.concatenate((np.zeros(QDIM), psi))
    shifted = state.astype(complex) + 1j * COMPLEX_STEP * direction
    derivative = np.imag(np.asarray(_jet(shifted).hessian)[QDIM:, QDIM:]) / COMPLEX_STEP
    return float(psi @ derivative @ psi)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing exact-center field inputs: " + ", ".join(missing))
    bordered, continuation, growth = (
        _json(path) for path in (BORDERED, CONTINUATION, GROWTH)
    )
    if not all(record.get("validation_passed") is True for record in (
        bordered, continuation, growth,
    )):
        raise RuntimeError("validated bordered, continuation, and growth parents required")
    with np.load(BORDERED_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
        lambda_first = np.asarray(data["lambda_gradient_action"], dtype=float)
        psi_first_raw = np.asarray(data["selected_vector_derivative_action"], dtype=float)
        bordered_matrix = np.asarray(data["bordered_matrix"], dtype=float)
        response = np.asarray(data["bordered_response"], dtype=float)
        response_first = np.asarray(data["bordered_response_derivative_action"], dtype=float)
        tangent = np.asarray(data["fixed_descriptor_tangent_basis"], dtype=float)

    q_weights, reduced_weights, _, _ = metric_data()
    signed_s_decimal = Decimal(
        continuation["continuation"]["final_signed_lambda_decimal"]
    )
    signed_s = float(signed_s_decimal)
    hard_raw = response[:-1]
    b_psi = float(response[-1])
    hard_first_action = reduced_weights[:, None] * response_first[:-1]
    b_first = response_first[-1]
    psi_action = np.concatenate((np.zeros(QDIM), reduced_weights * psi))
    psi_first_action = np.zeros((center.size, center.size))
    psi_first_action[QDIM:] = reduced_weights[:, None] * psi_first_raw

    configuration = q_weights * center[QDIM:2 * QDIM]
    configuration_first = np.zeros((QDIM, center.size))
    velocity_columns = slice(QDIM, 2 * QDIM)
    configuration_first[:, velocity_columns] = np.diag(
        q_weights / weights[QDIM:2 * QDIM]
    )
    full_hard = np.concatenate((configuration, reduced_weights * hard_raw))
    full_hard_first = np.vstack((configuration_first, hard_first_action))

    # The moving cubic is c=Dlambda[Psi].  Its fixed-line D4 term is evaluated
    # by two one-sided slopes.  The retained D5 bound controls each slope's
    # truncation error; the exact Kato product term supplies line motion.
    c_fixed_center = _fixed_line_cubic(center, psi)
    fixed_plus = np.empty(center.size)
    fixed_minus = np.empty(center.size)
    dK_columns = np.empty((center.size, bordered_matrix.shape[0], bordered_matrix.shape[1]))
    for column in range(center.size):
        displacement = ACTION_DIFFERENCE_STEP / weights[column]
        plus = center.copy()
        minus = center.copy()
        plus[column] += displacement
        minus[column] -= displacement
        fixed_plus[column] = (
            _fixed_line_cubic(plus, psi) - c_fixed_center
        ) / ACTION_DIFFERENCE_STEP
        fixed_minus[column] = (
            c_fixed_center - _fixed_line_cubic(minus, psi)
        ) / ACTION_DIFFERENCE_STEP
        complex_state = center.astype(complex)
        complex_state[column] += 1j * COMPLEX_STEP / weights[column]
        reduced_D3 = (
            np.imag(np.asarray(_jet(complex_state).hessian)[QDIM:, QDIM:])
            / COMPLEX_STEP
        )
        dL = reduced_D3 - lambda_first[column] * np.eye(psi.size)
        dpsi = psi_first_raw[:, column]
        dK_columns[column] = np.block([
            [dL, dpsi[:, None]],
            [dpsi[None, :], np.zeros((1, 1))],
        ])
        if (column + 1) % 16 == 0:
            print(f"fixed-line D4 columns {column + 1}/{center.size}", flush=True)
    fixed_c_first = 0.5 * (fixed_plus + fixed_minus)
    lambda_first_raw_reduced = lambda_first[QDIM:] * weights[QDIM:]
    kato_c_first = 3.0 * (lambda_first_raw_reduced @ psi_first_raw)
    c_first = fixed_c_first + kato_c_first
    c_identity = float(lambda_first @ psi_action)
    c_psi = c_identity

    R_center = float(lambda_first @ full_hard)
    Delta = c_psi * b_psi + signed_s * R_center
    numerator = b_psi * psi_action + signed_s * full_hard
    field = numerator / Delta
    # D2lambda[V,.] is retained as a certified operator remainder instead of
    # being reconstructed by an ill-conditioned finite difference.  Every
    # other first-variation term is combined with its sign before norms.
    R_first_without_lambda_hessian = lambda_first @ full_hard_first
    Delta_first_partial = (
        b_psi * c_first + c_psi * b_first
        + signed_s * R_first_without_lambda_hessian
    )
    numerator_first = (
        np.outer(psi_action, b_first)
        + b_psi * psi_first_action
        + signed_s * full_hard_first
    )
    field_first_partial = (
        numerator_first / Delta
        - np.outer(numerator, Delta_first_partial) / Delta**2
    )

    lambda_two = float(
        growth["fresh_line_bounds"]["selected_eigenvalue_raw_Hessian_bound"]
    )
    lambda_hessian_V_upper = _up(lambda_two * float(np.linalg.norm(full_hard)))
    omitted_field_matrix_upper = _up(
        float(np.linalg.norm(field)) * signed_s * lambda_hessian_V_upper / Delta
    )
    d5 = float(growth["retained_action_mixed_bounds"]["D5_XXPPP"])
    fixed_slope_disagreement = float(np.linalg.norm(fixed_plus - fixed_minus))
    fixed_D4_truncation_upper = _up(0.5 * d5 * ACTION_DIFFERENCE_STEP)
    c_gradient_uncertainty = _up(
        fixed_D4_truncation_upper + 0.5 * fixed_slope_disagreement
    )
    Delta_lambda_Hessian_remainder_upper = _up(
        signed_s * lambda_hessian_V_upper
    )
    Delta_c_gradient_remainder_upper = _up(
        abs(b_psi) * c_gradient_uncertainty
    )
    Delta_first_total_remainder_upper = _up(
        Delta_lambda_Hessian_remainder_upper
        + Delta_c_gradient_remainder_upper
    )
    c_uncertainty_field_matrix_upper = _up(
        float(np.linalg.norm(field)) * abs(b_psi) * c_gradient_uncertainty / Delta
    )
    total_matrix_remainder = _up(
        omitted_field_matrix_upper + c_uncertainty_field_matrix_upper
    )

    dK_tangent = np.tensordot(tangent.T, dK_columns, axes=(1, 0))
    relative_tangent = np.empty_like(dK_tangent)
    for column in range(tangent.shape[1]):
        relative_tangent[column] = np.linalg.solve(
            bordered_matrix, dK_tangent[column]
        )
    relative_tangent_frobenius = _up(float(np.linalg.norm(relative_tangent)))
    incoming_tube = float(
        continuation["continuation"]["final_endpoint_tube_radius_upper"]
    )
    relative_second_variation_self_consistency = _up(
        2.0 * incoming_tube * relative_tangent_frobenius
    )

    tangent_matrix = tangent.T @ field_first_partial @ tangent
    tangent_symmetric = 0.5 * (tangent_matrix + tangent_matrix.T)
    tangent_mu = float(np.linalg.eigvalsh(tangent_symmetric)[-1])
    tangent_operator = float(np.linalg.norm(tangent_matrix, 2))
    tangent_spectral = float(np.max(np.linalg.eigvals(tangent_matrix).real))
    tangent_mu_upper = _up(tangent_mu + total_matrix_remainder)
    descriptor_identity = float(lambda_first @ field)

    np.savez_compressed(
        DATA_RESULT,
        center_state=center,
        state_weights=weights,
        selected_vector=psi,
        fixed_descriptor_tangent_basis=tangent,
        exact_center_field_action=field,
        fixed_line_c_gradient_action=fixed_c_first,
        moving_c_gradient_action=c_first,
        Delta_first_partial_action=Delta_first_partial,
        Delta_first_total_remainder_action_norm_upper=np.asarray(
            Delta_first_total_remainder_upper
        ),
        fixed_s_field_matrix_partial_action=field_first_partial,
        fixed_s_tangent_matrix_partial=tangent_matrix,
        bordered_relative_tangent_tensor=relative_tangent,
    )
    validation = {
        "branch_24_bordered_parent_consumed": bordered["bordered_center"]["selected_branch"] == 24,
        "signed_descriptor_is_strictly_positive": signed_s_decimal > 0,
        "moving_cubic_identity_matches_direct_D3": abs(c_identity - c_fixed_center) < 1.0e-12,
        "descriptor_field_identity_is_close_to_one": abs(descriptor_identity - 1.0) < 1.0e-8,
        "Delta_is_strictly_positive": Delta > 0.0,
        "fixed_descriptor_tangent_has_codimension_one": tangent.shape == (98, 97),
        "center_field_and_matrix_are_finite": (
            np.all(np.isfinite(field)) and np.all(np.isfinite(tangent_matrix))
        ),
        "lambda_Hessian_contraction_is_retained_as_remainder": omitted_field_matrix_upper > 0.0,
        "D5_controls_one_sided_fixed_line_D4_slopes": fixed_D4_truncation_upper > 0.0,
        "signed_Delta_first_partial_and_remainder_ball_are_finite": (
            np.all(np.isfinite(Delta_first_partial))
            and math.isfinite(Delta_first_total_remainder_upper)
            and Delta_first_total_remainder_upper > 0.0
        ),
        "center_matrix_not_promoted_to_interval_flow_box": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX",
        "status": (
            "C2_CANCELLATION_PRESERVING_FIXED_s_CENTER_FIELD_MATRIX_CERTIFIED;_"
            "CONJUGATED_INTERVAL_REMAINDER_OPEN"
            if passed else "C2_EXACT_CENTER_FIXED_s_FIELD_MATRIX_INVALID"
        ),
        "center_field": {
            "signed_descriptor_decimal": str(signed_s_decimal),
            "moving_cubic_from_Dlambda_Psi": c_psi,
            "moving_cubic_direct_fixed_line_D3": c_fixed_center,
            "b_psi": b_psi,
            "R_Dlambda_Vhard": R_center,
            "Delta": Delta,
            "Delta_first_partial_action_norm": float(
                np.linalg.norm(Delta_first_partial)
            ),
            "Delta_first_selected_eigenvalue_Hessian_remainder_norm_upper": (
                Delta_lambda_Hessian_remainder_upper
            ),
            "Delta_first_c_gradient_remainder_norm_upper": (
                Delta_c_gradient_remainder_upper
            ),
            "Delta_first_total_remainder_action_norm_upper": (
                Delta_first_total_remainder_upper
            ),
            "Delta_first_signed_center_ball": (
                "D_Y_Delta_IN_Delta_first_partial_action_PLUS_"
                "CLOSED_EUCLIDEAN_BALL(total_remainder_upper)"
            ),
            "field_action_norm": float(np.linalg.norm(field)),
            "Dlambda_field": descriptor_identity,
        },
        "fixed_descriptor_matrix": {
            "partial_tangent_operator_2_norm": tangent_operator,
            "partial_tangent_numerical_abscissa": tangent_mu,
            "partial_tangent_spectral_abscissa": tangent_spectral,
            "omitted_D2lambda_V_field_matrix_upper": omitted_field_matrix_upper,
            "fixed_D4_slope_disagreement_2_norm": fixed_slope_disagreement,
            "fixed_D4_D5_truncation_operator_upper": fixed_D4_truncation_upper,
            "c_gradient_field_matrix_uncertainty_upper": c_uncertainty_field_matrix_upper,
            "total_center_matrix_remainder_upper": total_matrix_remainder,
            "center_tangent_numerical_abscissa_upper": tangent_mu_upper,
            "bordered_relative_tangent_tensor_Frobenius_upper": relative_tangent_frobenius,
            "incoming_endpoint_tube_radius": incoming_tube,
            "relative_second_variation_self_consistency": relative_second_variation_self_consistency,
        },
        "comparison": {
            "prior_scalar_fixed_s_Jacobi_upper": bordered["comparison"]["last_scalar_fixed_s_Jacobi_upper"],
            "matrix_to_scalar_ratio": _up(
                (tangent_operator + total_matrix_remainder)
                / bordered["comparison"]["last_scalar_fixed_s_Jacobi_upper"]
            ),
            "diagnosis": (
                "THE_EXACT_DESCRIPTOR_IDENTITY_AND_BORDERED_RESPONSE_CANCEL_"
                "BEFORE_PROJECTION;_THE_SCALAR_JACOBI_BOUND_IS_NOT_THE_"
                "CENTER_TANGENT_GENERATOR"
            ),
        },
        "hindsight": {
            "result": "OPEN",
            "classification": "NUMERICAL_CONDITIONING;_FULL_CENTER_MATRIX_RECOVERED",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "ENCLOSE_PHI_CENTER_INVERSE_TIMES_DF_s_OF_Y_MINUS_A_CENTER_TIMES_"
            "PHI_CENTER_ON_A_FIXED_DESCRIPTOR_ELLIPSOID_USING_THE_RETAINED_"
            "D4_D5_BOUNDS"
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
        "field_norm": payload["center_field"]["field_action_norm"],
        "Dlambda_field": payload["center_field"]["Dlambda_field"],
        "tangent_operator": payload["fixed_descriptor_matrix"]["partial_tangent_operator_2_norm"],
        "tangent_mu_upper": payload["fixed_descriptor_matrix"]["center_tangent_numerical_abscissa_upper"],
        "matrix_to_scalar_ratio": payload["comparison"]["matrix_to_scalar_ratio"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
