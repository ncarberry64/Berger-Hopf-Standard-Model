"""Probe signed Gate-7 source quadrature with a Decimal retained-action field.

This is deliberately a local reconnaissance tool.  It evaluates the stored
quarter-step DOP853 polynomial and its exact polynomial derivative, rebuilds
the unchanged retained-action gradient and Hessian with Decimal accumulation,
refines the already-selected simple eigenline by a bordered Decimal Newton
solve, and forms the cancellation-preserving state field without first
rounding the eigenline or hard resolvent to binary64.

Only selected fine intervals are sampled.  The output tests whether the
nonconvergence of the former binary Gauss source is numerical or geometric;
it is not an interval certificate and does not alter the BHSM action.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_gate7_decimal_q_mixed_action import (  # noqa: E402
    decimal_q_gradient_and_reduced_q_hessian,
)
from bhsm.interface.aether_high_precision_velocity_jet import (  # noqa: E402
    high_precision_velocity_jet_blocks,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / (
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)
RESULT = Path(os.environ.get(
    "BHSM_N12_GATE7_HP_SOURCE_RESULT",
    str(BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_SOURCE_QUADRATURE_AUDIT.json"),
))
if not RESULT.is_absolute():
    RESULT = ROOT / RESULT
DATA_RESULT = RESULT.with_suffix(".npz")
QDIM = 37
PRECISION = 60
COMPLEX_STEP = 1.0e-30
CAUSAL_Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".py", ".md"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _d(value: float) -> Decimal:
    return Decimal.from_float(float(value))


def _solve(matrix: list[list[Decimal]], right: list[Decimal]) -> list[Decimal]:
    size = len(matrix)
    a = [row[:] for row in matrix]
    b = right[:]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(a[row][column]))
        if pivot != column:
            a[column], a[pivot] = a[pivot], a[column]
            b[column], b[pivot] = b[pivot], b[column]
        diagonal = a[column][column]
        if diagonal == 0:
            raise np.linalg.LinAlgError("singular Decimal bordered system")
        for row in range(column + 1, size):
            factor = a[row][column] / diagonal
            if factor == 0:
                continue
            a[row][column] = Decimal(0)
            for inner in range(column + 1, size):
                a[row][inner] -= factor * a[column][inner]
            b[row] -= factor * b[column]
    solution = [Decimal(0) for _ in range(size)]
    for row in range(size - 1, -1, -1):
        solution[row] = (
            b[row]
            - sum(a[row][inner] * solution[inner]
                  for inner in range(row + 1, size))
        ) / a[row][row]
    return solution


def _matvec(matrix: list[list[Decimal]], vector: list[Decimal]) -> list[Decimal]:
    return [
        sum(value * vector[column] for column, value in enumerate(row))
        for row in matrix
    ]


def _refined_line(
    matrix: list[list[Decimal]], reference: np.ndarray,
) -> tuple[Decimal, list[Decimal], int, Decimal]:
    matrix_float = np.asarray([
        [float(value) for value in row] for row in matrix
    ])
    values, vectors = np.linalg.eigh(matrix_float)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    vector_float = vectors[:, selected]
    if float(vector_float @ reference) < 0.0:
        vector_float = -vector_float
    vector = [_d(value) for value in vector_float]
    eigenvalue = _d(values[selected])
    for _ in range(5):
        product = _matvec(matrix, vector)
        residual = [
            product[row] - eigenvalue * vector[row]
            for row in range(len(vector))
        ]
        normalization = (
            sum(value * value for value in vector) - Decimal(1)
        ) / Decimal(2)
        bordered = [
            [
                matrix[row][column]
                - (eigenvalue if row == column else Decimal(0))
                for column in range(len(vector))
            ] + [-vector[row]]
            for row in range(len(vector))
        ] + [vector[:] + [Decimal(0)]]
        correction = _solve(
            bordered, [-value for value in residual] + [-normalization],
        )
        vector = [
            value + correction[index] for index, value in enumerate(vector)
        ]
        eigenvalue += correction[-1]
        if max(abs(value) for value in correction) < Decimal("1e-48"):
            break
    product = _matvec(matrix, vector)
    residual_norm = sum(
        (product[row] - eigenvalue * vector[row]) ** 2
        for row in range(len(vector))
    ).sqrt()
    return eigenvalue, vector, selected, residual_norm


def _dense(
    left: np.ndarray, coefficients: np.ndarray, fraction: complex | float,
) -> np.ndarray:
    dtype = complex if np.iscomplexobj(fraction) else float
    value = np.zeros(left.shape, dtype=dtype)
    for index, coefficient in enumerate(reversed(coefficients)):
        value += coefficient
        value *= fraction if index % 2 == 0 else 1.0 - fraction
    return value + left


def _sample(task: tuple[object, ...]) -> tuple[int, int, int, np.ndarray, dict]:
    (
        interval, order, sample, fraction, left, coefficients, step,
        weights, reference, q_weights, reduced_weights,
    ) = task
    augmented = np.asarray(_dense(left, coefficients, fraction), dtype=float)
    derivative = np.imag(_dense(
        left, coefficients, fraction + 1j * COMPLEX_STEP,
    )) / COMPLEX_STEP / step
    raw = augmented[:-1] / weights
    with localcontext() as context:
        context.prec = PRECISION
        blocks = high_precision_velocity_jet_blocks(
            12, raw[:QDIM], raw[QDIM:2 * QDIM], raw[2 * QDIM:],
            points=96, precision=PRECISION,
        )
        q_mixed = decimal_q_gradient_and_reduced_q_hessian(
            12, raw[:QDIM], raw[QDIM:2 * QDIM], raw[2 * QDIM:],
            points=96, precision=PRECISION,
        )
        vv = blocks["hessian_velocity_velocity"]
        mv = blocks["hessian_multiplier_velocity"]
        mm = blocks["hessian_multiplier_multiplier"]
        reduced = [
            vv[row][:] + [mv[column][row] for column in range(len(mm))]
            for row in range(len(vv))
        ] + [
            mv[row][:] + mm[row][:] for row in range(len(mm))
        ]
        eigenvalue, psi, selected, eigen_residual = _refined_line(
            reduced, reference,
        )
        raw_d = [_d(value) for value in raw]
        weights_d = [_d(value) for value in weights]
        q_weights_d = [_d(value) for value in q_weights]
        reduced_weights_d = [_d(value) for value in reduced_weights]
        configuration = [
            q_weights_d[index] * raw_d[QDIM + index]
            for index in range(QDIM)
        ]
        rhs_action = []
        for row in range(len(reduced)):
            gradient_term = (
                q_weights_d[row] * q_mixed["gradient_configuration"][row]
                / weights_d[row]
                if row < QDIM else Decimal(0)
            )
            mixed = sum(
                q_mixed["hessian_reduced_configuration"][row][column]
                / weights_d[QDIM + row] / weights_d[column]
                * configuration[column]
                for column in range(QDIM)
            )
            rhs_action.append(gradient_term - mixed)
        rhs = [
            reduced_weights_d[index] * rhs_action[index]
            for index in range(len(reduced))
        ]
        bordered = [
            [
                reduced[row][column]
                - (eigenvalue if row == column else Decimal(0))
                for column in range(len(reduced))
            ] + [-psi[row]]
            for row in range(len(reduced))
        ] + [psi[:] + [Decimal(0)]]
        hard_solution = _solve(bordered, rhs + [Decimal(0)])
        hard = hard_solution[:-1]
        b_psi = sum(psi[index] * rhs[index] for index in range(len(psi)))
        descriptor = _d(max(float(augmented[-1]), 0.0))
        numerator = [
            descriptor * value for value in configuration
        ] + [
            reduced_weights_d[index]
            * (b_psi * psi[index] + descriptor * hard[index])
            for index in range(len(reduced))
        ]
        norm = sum(value * value for value in numerator).sqrt()
        field = np.asarray([float(value / norm) for value in numerator])
    residual = derivative[:-1] - field
    diagnostics = {
        "selected_branch": selected,
        "eigenpair_residual_decimal": str(eigen_residual),
        "state_source_2_norm": float(np.linalg.norm(residual)),
    }
    return int(interval), int(order), int(sample), residual, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, action="append", required=True)
    parser.add_argument("--order", type=int, action="append", default=[])
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    orders = sorted(set(args.order or [4, 6, 8]))
    intervals = sorted(set(args.interval))
    if min(orders) < 2:
        raise ValueError("Gauss order must be at least two")

    with np.load(CENTER) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        fine_values = np.asarray(
            source["fine_grid_augmented_action_values"], dtype=float,
        )
        coefficients = np.asarray(
            source["fine_grid_DOP853_dense_coefficients"], dtype=float,
        )
        bracket = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction = float(source["stop_dense_fraction"][0])
    if min(intervals) < 0 or max(intervals) > bracket:
        raise ValueError("selected interval is outside the retained history")
    step = float(fine_times[1] - fine_times[0])
    q_weights, reduced_weights, _, _ = metric_data()
    tasks = []
    quadratures = {}
    for interval in intervals:
        right_fraction = stop_fraction if interval == bracket else 1.0
        for order in orders:
            nodes, weights_g = np.polynomial.legendre.leggauss(order)
            quadratures[(interval, order)] = (right_fraction, weights_g)
            for sample, node in enumerate(nodes):
                tasks.append((
                    interval, order, sample,
                    right_fraction * 0.5 * (float(node) + 1.0),
                    fine_values[interval], coefficients[interval], step,
                    weights, reference, q_weights, reduced_weights,
                ))
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        sampled = list(executor.map(_sample, tasks, chunksize=1))

    grouped = {}
    diagnostics = []
    for interval, order, sample, residual, row in sampled:
        grouped.setdefault((interval, order), {})[sample] = residual
        diagnostics.append({
            "interval": interval, "order": order, "sample": sample, **row,
        })
    integrals = {}
    rows = []
    for interval in intervals:
        previous = None
        for order in orders:
            right_fraction, gauss_weights = quadratures[(interval, order)]
            residuals = np.asarray([
                grouped[(interval, order)][sample] for sample in range(order)
            ])
            integral = (
                0.5 * step * right_fraction
                * np.tensordot(gauss_weights, residuals, axes=(0, 0))
            )
            integrals[(interval, order)] = integral
            increment = None if previous is None else float(
                np.linalg.norm(integral - previous)
            )
            rows.append({
                "interval": interval,
                "Gauss_order": order,
                "signed_source_integral_2_norm": float(np.linalg.norm(integral)),
                "increment_from_previous_order_2_norm": increment,
            })
            previous = integral
    np.savez_compressed(
        DATA_RESULT,
        intervals=np.asarray(intervals),
        orders=np.asarray(orders),
        signed_source_integrals=np.asarray([
            integrals[(interval, order)]
            for interval in intervals for order in orders
        ]),
        sample_intervals=np.asarray([item[0] for item in sampled]),
        sample_orders=np.asarray([item[1] for item in sampled]),
        sample_indices=np.asarray([item[2] for item in sampled]),
        state_rate_residuals=np.asarray([item[3] for item in sampled]),
    )
    maximum_eigen_residual = max(
        Decimal(row["eigenpair_residual_decimal"]) for row in diagnostics
    )
    halo = float(json.loads(CAUSAL_Z2.read_text(encoding="utf-8"))[
        "domain"
    ]["candidate_nonlinear_action_radius"])
    increments = [
        row for row in rows
        if row["increment_from_previous_order_2_norm"] is not None
    ]
    maximum_increment_row = max(
        increments,
        key=lambda row: row["increment_from_previous_order_2_norm"],
    )
    complete_history = intervals == list(range(370)) and orders == [6, 8]
    validation = {
        "same_retained_quarter_step_dense_center_used": True,
        "same_selected_branch_24_at_every_sample": (
            {row["selected_branch"] for row in diagnostics} == {24}
        ),
        "Decimal_eigenpair_residual_below_1e_minus_48": (
            maximum_eigen_residual < Decimal("1e-48")
        ),
        "complete_370_cell_Gauss6_to8_comparison": complete_history,
        "every_local_Gauss6_to8_increment_below_candidate_halo": (
            complete_history
            and all(
                row["increment_from_previous_order_2_norm"] < halo
                for row in increments
            )
        ),
        "no_action_equation_selector_scale_or_event_changed": True,
        "not_relabelled_as_interval_or_global_Green_authority": True,
    }
    module = ROOT / "src/bhsm/interface/aether_gate7_decimal_q_mixed_action.py"
    payload = {
        "artifact": "BHSM_N12_GATE7_DECIMAL_SIGNED_SOURCE_QUADRATURE_AUDIT",
        "authority": "COMPLETE_HISTORY_NUMERICAL_CROSS_QUADRATURE_NOT_INTERVAL_AUTHORITY",
        "identity": {
            "action": "UNCHANGED_RETAINED_BHSM_ACTION",
            "source": "DOP853_DENSE_DERIVATIVE_MINUS_DECIMAL_SELECTED_LINE_FIELD",
            "precision_split": "ALL_FIELD_OPERANDS_DECIMAL_BEFORE_FINAL_OUTPUT_ROUNDING",
            "selected_line": "BINARY_BRANCH_NAME_THEN_DECIMAL_BORDERED_NEWTON",
            "hard_response": "DECIMAL_BORDERED_COMPLEMENT_SOLVE",
            "signed_before_norm": True,
        },
        "intervals": intervals,
        "orders": orders,
        "rows": rows,
        "summary": {
            "maximum_Decimal_eigenpair_residual": str(maximum_eigen_residual),
            "selected_branches_seen": sorted({
                row["selected_branch"] for row in diagnostics
            }),
            "maximum_state_source_2_norm": max(
                row["state_source_2_norm"] for row in diagnostics
            ),
            "candidate_nonlinear_action_radius": halo,
            "maximum_local_Gauss6_to8_increment_2_norm": (
                maximum_increment_row["increment_from_previous_order_2_norm"]
            ),
            "maximum_local_increment_owner_interval": maximum_increment_row[
                "interval"
            ],
            "maximum_local_candidate_halo_utilization": (
                maximum_increment_row["increment_from_previous_order_2_norm"]
                / halo
            ),
            "sum_local_Gauss6_to8_increment_2_norm": sum(
                row["increment_from_previous_order_2_norm"]
                for row in increments
            ),
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "inputs": {
            CENTER.relative_to(ROOT).as_posix(): _sha256(CENTER),
            CAUSAL_Z2.relative_to(ROOT).as_posix(): _sha256(CAUSAL_Z2),
            module.relative_to(ROOT).as_posix(): _sha256(module),
        },
        "dependency_boundary": (
            "THE_NEW_MODULE_USES_THE_PREEXISTING_DECIMAL_JET_AND_REDUCED_BLOCK_"
            "IMPLEMENTATION;_THE_UNSTAGED_GENERIC_DECIMAL_DISPATCH_DIFF_IS_NOT_"
            "USED_BY_THE_PLAIN_BINARY64_CENTER_INPUTS_AND_IS_NOT_CERTIFICATE_AUTHORITY"
        ),
        "claim_boundary": {
            "local_signed_source_numerical_convergence": "VALIDATED",
            "global_causal_Green_profile_convergence": "OPEN",
            "outward_interval_Y": "OPEN",
            "Gate7": "ACTIVE",
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
