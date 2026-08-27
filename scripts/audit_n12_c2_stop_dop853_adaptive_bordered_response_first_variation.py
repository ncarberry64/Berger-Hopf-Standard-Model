"""Assemble the exact center first variation of the DOP853 bordered response.

This is the one-dimensional variation along the stored action-time dense
polynomial.  It combines ``D rhs`` and ``D K x`` before solving and checks the
result with the analytical selected-line spectral solve.  The artifact is a
center diagnostic until a cellwise second-variation remainder is attached.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response as response  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CERTIFICATE = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_RESPONSE_CERTIFICATE",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_RESPONSE_FIRST_VARIATION",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")
QDIM = response.QDIM


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _cell_center_and_rate(
    interval: int, subspan: int, subdivisions: int,
) -> tuple[np.ndarray, np.ndarray, float, float, np.ndarray, np.ndarray]:
    values, coefficients, times, weights, reference, bracket_raw, stop_raw = (
        response.dense._dense_arrays()
    )
    bracket = int(bracket_raw[0])
    right = float(stop_raw[0]) if interval == bracket else 1.0
    controls = response.dense._dense_bernstein_controls(
        values[interval], coefficients[interval],
    )
    controls = response.dense._restrict(controls, 0.0, right)
    controls = response.dense._restrict(
        controls, subspan / subdivisions, (subspan + 1) / subdivisions,
    )[:, :-1]
    center_action = response.dense._split(controls, 0.5)[0][-1]
    derivative_controls = 7.0 * (controls[1:] - controls[:-1])
    derivative_local = response.dense._split(derivative_controls, 0.5)[0][-1]
    duration = float(times[interval + 1] - times[interval]) * right / subdivisions
    center_time = (
        float(times[interval])
        + float(times[interval + 1] - times[interval]) * right
        * (subspan + 0.5) / subdivisions
    )
    return (
        center_action / weights,
        derivative_local / duration,
        duration,
        center_time,
        weights,
        reference,
    )


def _row(task: tuple[int, int, int]) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    interval, subspan, subdivisions = task
    center, rate_action, duration, center_time, weights, reference = (
        _cell_center_and_rate(interval, subspan, subdivisions)
    )
    jet = response.dense.cluster.local.exact_full_action_jet_at_state(
        12,
        center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:],
        points=response.dense.cluster.local.POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    if selected != 24:
        raise RuntimeError("selected branch changed")
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    hard_indices = np.asarray(
        [index for index in range(values.size) if index != selected], dtype=int,
    )
    hard = vectors[:, hard_indices]
    denominators = values[hard_indices] - values[selected]

    shifted = np.asarray(center, dtype=complex) + (
        1j * response.dense.COMPLEX_STEP * rate_action / weights
    )
    shifted_jet = response.dense.cluster.local.exact_full_action_jet_at_state(
        12,
        shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
        points=response.dense.cluster.local.POINTS,
    )
    hessian_rate = (
        np.imag(np.asarray(shifted_jet.hessian)[QDIM:, QDIM:])
        / response.dense.COMPLEX_STEP
    )
    eigenvalue_rate = float(psi @ hessian_rate @ psi)
    selected_vector_rate = hard @ (
        (hard.T @ hessian_rate @ psi)
        / (values[selected] - values[hard_indices])
    )

    bordered = np.block([
        [hessian - values[selected] * np.eye(values.size), psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    rhs = np.asarray(response._exact_rhs(center, weights), dtype=float)
    forcing = np.concatenate((rhs, np.zeros(1)))
    center_response = np.linalg.solve(bordered, forcing)
    rhs_rate = (
        np.imag(response._exact_rhs(shifted, weights))
        / response.dense.COMPLEX_STEP
    )
    bordered_rate = np.block([
        [
            hessian_rate - eigenvalue_rate * np.eye(values.size),
            selected_vector_rate[:, None],
        ],
        [selected_vector_rate[None, :], np.zeros((1, 1))],
    ])
    separate_rhs = np.concatenate((rhs_rate, np.zeros(1)))
    operator_response = bordered_rate @ center_response
    combined_rhs = separate_rhs - operator_response
    direct_variation = np.linalg.solve(bordered, combined_rhs)

    # Exact selected-line spectral inverse of the bordered center system.
    spectral_state = (
        hard @ ((hard.T @ combined_rhs[:-1]) / denominators)
        + combined_rhs[-1] * psi
    )
    spectral_variation = np.concatenate((
        spectral_state,
        np.asarray([float(psi @ combined_rhs[:-1])]),
    ))
    residual = _up(float(np.linalg.norm(
        bordered @ direct_variation - combined_rhs,
    )))
    spectral_residual = _up(float(np.linalg.norm(
        bordered @ spectral_variation - combined_rhs,
    )))
    discrepancy = float(np.linalg.norm(direct_variation - spectral_variation))
    inverse_upper = _up(max(1.0, 1.0 / float(np.min(np.abs(denominators)))))
    comparison_backward_error = _up(
        inverse_upper * (residual + spectral_residual)
    )
    cancellation_denominator = (
        float(np.linalg.norm(separate_rhs))
        + float(np.linalg.norm(operator_response))
    )
    cancellation_ratio = (
        float(np.linalg.norm(combined_rhs)) / cancellation_denominator
        if cancellation_denominator > 0.0 else 0.0
    )
    return ({
        "interval": interval,
        "subspan": subspan,
        "subdivisions": subdivisions,
        "action_time_center": center_time,
        "action_time_duration": duration,
        "selected_branch": selected,
        "selected_to_hard_center_gap": float(np.min(np.abs(denominators))),
        "state_action_rate_2_norm": float(np.linalg.norm(rate_action)),
        "bordered_K_action_time_derivative_2_norm": float(
            np.linalg.norm(bordered_rate, ord=2)
        ),
        "internal_rhs_action_time_derivative_2_norm": float(
            np.linalg.norm(separate_rhs)
        ),
        "bordered_derivative_times_response_2_norm": float(
            np.linalg.norm(operator_response)
        ),
        "combined_differentiated_rhs_2_norm": float(np.linalg.norm(combined_rhs)),
        "combined_before_norm_cancellation_ratio": cancellation_ratio,
        "center_bordered_response_2_norm": float(np.linalg.norm(center_response)),
        "center_bordered_response_first_variation_2_norm": float(
            np.linalg.norm(direct_variation)
        ),
        "center_bordered_response_first_variation_residual_upper": residual,
        "spectral_first_variation_residual_upper": spectral_residual,
        "spectral_vs_direct_first_variation_discrepancy": discrepancy,
        "spectral_vs_direct_comparison_backward_error_upper": (
            comparison_backward_error
        ),
        "all_center_quantities_finite": bool(
            np.all(np.isfinite(center_response))
            and np.all(np.isfinite(direct_variation))
            and np.all(np.isfinite(spectral_variation))
        ),
    }, center_response, spectral_variation)


def build_payload() -> dict[str, Any]:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    if certificate.get("validation_passed") is not True:
        raise RuntimeError("certified adaptive bordered response cover required")
    tasks = [
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"]))
        for row in certificate["rows"]
    ]
    workers = min(
        int(os.environ.get("BHSM_N12_STOP_WORKERS", "16")),
        os.cpu_count() or 1,
    )
    rows: list[dict[str, Any]] = []
    responses: list[np.ndarray] = []
    variations: list[np.ndarray] = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, (row, center_response, variation) in enumerate(
            executor.map(_row, tasks, chunksize=1), 1,
        ):
            rows.append(row)
            responses.append(center_response)
            variations.append(variation)
            if index % 64 == 0 or index == len(tasks):
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "maximum_center_first_variation_so_far": max(
                        item["center_bordered_response_first_variation_2_norm"]
                        for item in rows
                    ),
                }), flush=True)
    validation = {
        "exact_response_cover_consumed_in_order": [
            (row["interval"], row["subspan"], row["subdivisions"])
            for row in rows
        ] == tasks,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_center_quantities_finite": all(
            row["all_center_quantities_finite"] for row in rows
        ),
        "all_differentiated_bordered_residuals_small": all(
            row["center_bordered_response_first_variation_residual_upper"] < 1.0e-7
            for row in rows
        ),
        "all_spectral_and_direct_first_variations_agree": all(
            row["spectral_vs_direct_first_variation_discrepancy"]
            <= row["spectral_vs_direct_comparison_backward_error_upper"]
            for row in rows
        ),
        "D_rhs_and_DK_times_x_combined_before_norms": True,
        "analytical_selected_line_spectral_solve_used": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
        "cellwise_second_variation_remainder_not_claimed": True,
    }
    passed = all(validation.values())
    np.savez_compressed(
        DATA_RESULT,
        interval=np.asarray([row["interval"] for row in rows], dtype=int),
        subspan=np.asarray([row["subspan"] for row in rows], dtype=int),
        subdivisions=np.asarray([row["subdivisions"] for row in rows], dtype=int),
        action_time_center=np.asarray([row["action_time_center"] for row in rows]),
        bordered_response_center=np.asarray(responses),
        bordered_response_action_time_first_variation=np.asarray(variations),
    )
    owner = max(
        rows,
        key=lambda row: row["center_bordered_response_first_variation_2_norm"],
    )
    generator = ROOT / "scripts" / Path(__file__).name
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION",
        "status": (
            "DOP853_BORDERED_RESPONSE_CENTER_FIRST_VARIATION_ASSEMBLED;_CELLWISE_SECOND_VARIATION_REMAINDER_OPEN"
            if passed else "DOP853_BORDERED_RESPONSE_CENTER_FIRST_VARIATION_INVALID"
        ),
        "authority": "EXACT_CENTER_DIFFERENTIATED_BORDERED_IDENTITY_NOT_YET_AN_INTERVAL_RESPONSE_VARIATION_TUBE",
        "identity": "D_xi_x=K^-1*(D_xi_rhs-(D_xi_K)*x)",
        "mesh": {
            "response_cover_cells": len(rows),
            "workers": workers,
        },
        "summary": {
            "maximum_bordered_K_action_time_derivative_2_norm": max(
                row["bordered_K_action_time_derivative_2_norm"] for row in rows
            ),
            "maximum_internal_rhs_action_time_derivative_2_norm": max(
                row["internal_rhs_action_time_derivative_2_norm"] for row in rows
            ),
            "maximum_combined_differentiated_rhs_2_norm": max(
                row["combined_differentiated_rhs_2_norm"] for row in rows
            ),
            "maximum_center_bordered_response_first_variation_2_norm": owner[
                "center_bordered_response_first_variation_2_norm"
            ],
            "maximum_differentiated_bordered_residual_upper": max(
                row["center_bordered_response_first_variation_residual_upper"]
                for row in rows
            ),
            "maximum_spectral_vs_direct_discrepancy": max(
                row["spectral_vs_direct_first_variation_discrepancy"]
                for row in rows
            ),
            "maximum_spectral_vs_direct_comparison_backward_error_upper": max(
                row["spectral_vs_direct_comparison_backward_error_upper"]
                for row in rows
            ),
            "owner": owner,
        },
        "rows": rows,
        "data": _relative(DATA_RESULT),
        "data_SHA256": _sha256(DATA_RESULT),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "exact_center_D_xi_K": "ASSEMBLED" if passed else "OPEN",
            "exact_center_D_xi_internal_rhs": "ASSEMBLED" if passed else "OPEN",
            "exact_center_D_xi_bordered_response": "ASSEMBLED" if passed else "OPEN",
            "cellwise_response_first_variation_tube": "OPEN",
            "correlated_Y_Z1_Z2": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_CELLWISE_SECOND_VARIATION_OF_THE_COMBINED_DIFFERENTIATED_BORDERED_IDENTITY_ON_THIS_IDENTICAL_RESPONSE_COVER"
        ),
        "inputs": {
            _relative(CERTIFICATE): _sha256(CERTIFICATE),
            _relative(response.dense.CENTER_DATA): _sha256(response.dense.CENTER_DATA),
            "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py": _sha256(
                ROOT / "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py"
            ),
            _relative(generator): _sha256(generator),
        },
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
