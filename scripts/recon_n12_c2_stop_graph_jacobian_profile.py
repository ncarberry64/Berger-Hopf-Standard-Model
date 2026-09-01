"""Reconnoiter the physical graph Jacobian along the finite C2 stop center.

The retained descriptor graph is ``s=lambda(Y)``.  This script differentiates
the complete internal bordered response and the cancellation-preserving
action-arclength field on that graph.  It reports full and flow-transverse
logarithmic norms at the stored 48 multiple-shooting nodes.  The calculation
is reconnaissance until a between-node action remainder is enclosed.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_JACOBIAN_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_GRAPH_JACOBIAN_PROFILE_RECONNAISSANCE.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")
QDIM = 37
COMPLEX_STEP = 1.0e-20


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _rhs_from_jet(jet: object, state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Assemble the retained reduced Euler--Dirac right-hand side."""
    q_weights, reduced_weights, _, _ = metric_data()
    gradient_action = np.asarray(jet.gradient) / weights
    hessian_action = (
        np.asarray(jet.hessian) / weights[:, None] / weights[None, :]
    )
    configuration = q_weights * state[QDIM:2 * QDIM]
    return reduced_weights * (
        np.concatenate((
            q_weights * gradient_action[:QDIM],
            np.zeros(reduced_weights.size - QDIM),
        )) - hessian_action[QDIM:, :QDIM] @ configuration
    )


def _arrays() -> tuple[np.ndarray, ...]:
    with np.load(CENTER_DATA) as source:
        return (
            np.asarray(source["centers"], dtype=float),
            np.asarray(source["signed_descriptors"], dtype=float),
            np.asarray(source["action_lengths"], dtype=float),
            np.asarray(source["state_weights"], dtype=float),
            np.asarray(source["branch_reference"], dtype=float),
        )


def _node(index: int) -> tuple[dict[str, object], np.ndarray]:
    states, descriptors, action_lengths, weights, reference = _arrays()
    state = states[index]
    descriptor = float(descriptors[index])
    q_weights, reduced_weights, _, _ = metric_data()
    center_jet = cluster.local.exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    reduced_hessian = np.asarray(center_jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced_hessian)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    if selected != 24:
        raise RuntimeError("selected branch changed")
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    hard_indices = np.asarray([j for j in range(values.size) if j != selected])
    complement = vectors[:, hard_indices]
    hard_values = values[hard_indices]
    eigenvalue = float(values[selected])
    denominators = hard_values - eigenvalue
    K = np.block([
        [reduced_hessian - eigenvalue * np.eye(values.size), psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    rhs = np.asarray(_rhs_from_jet(center_jet, state, weights), dtype=float)
    response = np.linalg.solve(K, np.concatenate((rhs, np.zeros(1))))
    hard = response[:-1]
    b_psi = float(response[-1])

    total = state.size
    lambda_first = np.empty(total)
    psi_first = np.empty((psi.size, total))
    response_first = np.empty((response.size, total))
    for column in range(total):
        shifted = np.asarray(state, dtype=complex)
        shifted[column] += 1j * COMPLEX_STEP / weights[column]
        shifted_jet = cluster.local.exact_full_action_jet_at_state(
            12,
            shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
            points=cluster.local.POINTS,
        )
        derivative = np.imag(np.asarray(shifted_jet.hessian)) / COMPLEX_STEP
        reduced_first = derivative[QDIM:, QDIM:]
        slope = float(psi @ reduced_first @ psi)
        lambda_first[column] = slope
        coupling = complement.T @ reduced_first @ psi
        dpsi = complement @ (coupling / (eigenvalue - hard_values))
        psi_first[:, column] = dpsi
        drhs = np.imag(_rhs_from_jet(shifted_jet, shifted, weights)) / COMPLEX_STEP
        dK = np.block([
            [reduced_first - slope * np.eye(values.size), dpsi[:, None]],
            [dpsi[None, :], np.zeros((1, 1))],
        ])
        response_first[:, column] = np.linalg.solve(
            K,
            np.concatenate((drhs, np.zeros(1))) - dK @ response,
        )

    configuration = q_weights * state[QDIM:2 * QDIM]
    configuration_first = np.zeros((QDIM, total))
    configuration_first[:, QDIM:2 * QDIM] = np.diag(
        q_weights / weights[QDIM:2 * QDIM]
    )
    hard_first = response_first[:-1]
    b_first = response_first[-1]
    G = np.concatenate((
        descriptor * configuration,
        reduced_weights * (b_psi * psi + descriptor * hard),
    ))
    G_first = np.vstack((
        descriptor * configuration_first
        + np.outer(configuration, lambda_first),
        reduced_weights[:, None] * (
            np.outer(psi, b_first)
            + b_psi * psi_first
            + np.outer(hard, lambda_first)
            + descriptor * hard_first
        ),
    ))
    G_norm = float(np.linalg.norm(G))
    flow = G / G_norm
    jacobian = (np.eye(total) - np.outer(flow, flow)) @ G_first / G_norm
    transverse = null_space(flow[None, :])
    transverse_jacobian = transverse.T @ jacobian @ transverse
    symmetric = 0.5 * (jacobian + jacobian.T)
    transverse_symmetric = 0.5 * (
        transverse_jacobian + transverse_jacobian.T
    )
    psi_action = np.concatenate((np.zeros(QDIM), reduced_weights * psi))
    psi_unit = psi_action / np.linalg.norm(psi_action)
    descriptor_rate = float(lambda_first @ flow)
    eigenvalues = np.linalg.eigvals(jacobian)
    return ({
        "node": index,
        "action_length": float(action_lengths[index]),
        "signed_descriptor": descriptor,
        "selected_branch": selected,
        "selected_line_gap": float(np.min(np.abs(denominators))),
        "b_psi": b_psi,
        "s_over_b_psi": descriptor / b_psi,
        "hard_raw_norm": float(np.linalg.norm(hard)),
        "hard_graph_correction_raw_norm": float(
            abs(descriptor / b_psi) * np.linalg.norm(hard)
        ),
        "cancelled_field_action_norm": G_norm,
        "flow_to_selected_line_action_distance": float(
            np.linalg.norm(flow - psi_unit)
        ),
        "descriptor_rate_on_graph": descriptor_rate,
        "descriptor_gradient_action_2_norm": float(np.linalg.norm(lambda_first)),
        "full_graph_Jacobian_operator_2_norm": float(np.linalg.norm(jacobian, 2)),
        "full_graph_Jacobian_spectral_abscissa": float(
            np.max(eigenvalues.real)
        ),
        "full_graph_Jacobian_numerical_abscissa": float(
            np.linalg.eigvalsh(symmetric)[-1]
        ),
        "transverse_graph_Jacobian_operator_2_norm": float(
            np.linalg.norm(transverse_jacobian, 2)
        ),
        "transverse_graph_Jacobian_numerical_abscissa": float(
            np.linalg.eigvalsh(transverse_symmetric)[-1]
        ),
        "transverse_graph_Jacobian_minimum_symmetric_rate": float(
            np.linalg.eigvalsh(transverse_symmetric)[0]
        ),
        "selected_line_derivative_operator_2_norm": float(
            np.linalg.norm(psi_first, 2)
        ),
        "hard_response_derivative_operator_2_norm": float(
            np.linalg.norm(hard_first, 2)
        ),
        "b_psi_gradient_2_norm": float(np.linalg.norm(b_first)),
    }, jacobian, lambda_first)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--node", type=int, action="append")
    args = parser.parse_args()
    states, _, _, _, _ = _arrays()
    indices = args.node if args.node is not None else list(range(states.shape[0]))
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = []
        for count, result in enumerate(executor.map(_node, indices), 1):
            results.append(result)
            print(json.dumps({
                "completed": count,
                "total": len(indices),
                "node": result[0]["node"],
                "transverse_mu": result[0][
                    "transverse_graph_Jacobian_numerical_abscissa"
                ],
            }), flush=True)
    rows = [item[0] for item in results]
    matrices = np.asarray([item[1] for item in results])
    descriptor_gradients = np.asarray([item[2] for item in results])
    np.savez_compressed(
        DATA_RESULT,
        node_indices=np.asarray(indices),
        graph_Jacobian_action=matrices,
        descriptor_gradient_action=descriptor_gradients,
    )
    owner = max(
        rows,
        key=lambda row: row["transverse_graph_Jacobian_numerical_abscissa"],
    )
    payload = {
        "artifact": "BHSM_N12_C2_STOP_GRAPH_JACOBIAN_PROFILE_RECONNAISSANCE",
        "authority": "CENTER_RECONNAISSANCE_ONLY_NOT_AN_INTERVAL_CONE_THEOREM",
        "center": CENTER_DATA.relative_to(ROOT).as_posix(),
        "rows": rows,
        "summary": {
            "maximum_transverse_graph_Jacobian_numerical_abscissa": owner[
                "transverse_graph_Jacobian_numerical_abscissa"
            ],
            "transverse_numerical_abscissa_owner": owner,
            "minimum_descriptor_rate_on_graph": min(
                row["descriptor_rate_on_graph"] for row in rows
            ),
            "maximum_descriptor_rate_on_graph": max(
                row["descriptor_rate_on_graph"] for row in rows
            ),
            "maximum_flow_to_selected_line_action_distance": max(
                row["flow_to_selected_line_action_distance"] for row in rows
            ),
            "maximum_graph_Jacobian_spectral_abscissa": max(
                row["full_graph_Jacobian_spectral_abscissa"] for row in rows
            ),
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {
            CENTER_DATA.relative_to(ROOT).as_posix(): _sha256(CENTER_DATA),
            "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py": _sha256(
                ROOT / "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py"
            ),
        },
        "validation_passed": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
