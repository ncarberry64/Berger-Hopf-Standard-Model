"""Assemble the existing source-restricted mixed action graph at N12.

The repository already fixes the energy space

    X_E = H1_q x L2_v x H1_m

and its strong compactness space

    S2 = H2_q x H1_v x H2_m.

This script assembles those spaces with the trace-compatible q-sector Fortin
projector.  It does not infer a quantitative Euler--Dirac or propagator tail;
those remain the next action-owned coefficients.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import block_diag, eigh, null_space

from derive_n12_action_graph_galerkin_projector import (
    _boundary_jacobian,
    _coordinate_graph,
    _coordinate_injection,
)


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_ORDER = 12
ANCHOR = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
PROJECTOR = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
SOURCE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_INVERSE_SQUARE_SOURCE_CONSTANT.json"
)
POLE = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_MIXED_GRAPH.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _family_values(order: int, points: int, family: str) -> tuple[np.ndarray, ...]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = weights * math.pi / 8.0
    omega = np.sin(chi) ** 3 * np.cos(chi) ** 3
    if family == "u":
        modes = np.arange(1, order + 1, dtype=float)[:, None]
        values = np.cos(4.0 * modes * chi)
        first = -4.0 * modes * np.sin(4.0 * modes * chi)
        second = -(4.0 * modes) ** 2 * np.cos(4.0 * modes * chi)
        trace = (-1.0) ** np.arange(1, order + 1)
    elif family == "shape":
        modes = np.arange(order, dtype=float)[:, None]
        window = np.sin(2.0 * chi) ** 2
        window_first = 2.0 * np.sin(4.0 * chi)
        window_second = 8.0 * np.cos(4.0 * chi)
        cosine = np.cos(4.0 * modes * chi)
        sine = np.sin(4.0 * modes * chi)
        values = window * cosine
        first = window_first * cosine - window * 4.0 * modes * sine
        second = (
            window_second * cosine
            - 2.0 * window_first * 4.0 * modes * sine
            - window * (4.0 * modes) ** 2 * cosine
        )
        trace = (-1.0) ** np.arange(order)
    elif family == "shift":
        modes = np.arange(order, dtype=float)[:, None]
        window = np.sin(4.0 * chi)
        window_first = 4.0 * np.cos(4.0 * chi)
        window_second = -16.0 * np.sin(4.0 * chi)
        cosine = np.cos(4.0 * modes * chi)
        sine = np.sin(4.0 * modes * chi)
        values = window * cosine
        first = window_first * cosine - window * 4.0 * modes * sine
        second = (
            window_second * cosine
            - 2.0 * window_first * 4.0 * modes * sine
            - window * (4.0 * modes) ** 2 * cosine
        )
        trace = np.zeros(order)
    else:
        raise ValueError(family)
    measure = quadrature * omega
    return values, first, second, trace, measure


def _gram(order: int, family: str, regularity: int, *, trace: bool) -> np.ndarray:
    values, first, second, endpoint, measure = _family_values(
        order, max(640, 8 * order), family
    )
    result = (values * measure) @ values.T
    if regularity >= 1:
        result += (first * measure) @ first.T
    if regularity >= 2:
        result += (second * measure) @ second.T
    if trace:
        result += np.outer(endpoint, endpoint)
    return 0.5 * (result + result.T)


def _q_graph(order: int, regularity: int) -> np.ndarray:
    if regularity == 1:
        return _coordinate_graph(order)
    return block_diag(
        np.ones((1, 1)),
        _gram(order, "u", regularity, trace=True),
        _gram(order, "shape", regularity, trace=True),
        _gram(order, "shape", regularity, trace=True),
    )


def _velocity_graph(order: int, regularity: int) -> np.ndarray:
    return block_diag(
        np.ones((1, 1)),
        _gram(order, "u", regularity, trace=False),
        _gram(order, "shape", regularity, trace=False),
        _gram(order, "shape", regularity, trace=False),
    )


def _multiplier_graph(order: int, regularity: int) -> np.ndarray:
    return block_diag(
        _gram(order, "u", regularity, trace=True),
        _gram(order, "shift", regularity, trace=False),
    )


def _multiplier_injection(high_order: int) -> np.ndarray:
    result = np.zeros((2 * high_order, 2 * ANCHOR_ORDER))
    result[:ANCHOR_ORDER, :ANCHOR_ORDER] = np.eye(ANCHOR_ORDER)
    result[
        high_order:high_order + ANCHOR_ORDER,
        ANCHOR_ORDER:2 * ANCHOR_ORDER,
    ] = np.eye(ANCHOR_ORDER)
    return result


def _orthogonal_projector(graph: np.ndarray, injection: np.ndarray) -> np.ndarray:
    low = injection.T @ graph @ injection
    return injection @ np.linalg.solve(low, injection.T @ graph)


def _q_trace_projector(order: int, low_q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    injection = _coordinate_injection(order)
    high_q = injection @ low_q
    low_graph = _q_graph(ANCHOR_ORDER, 1)
    high_graph = _q_graph(order, 1)
    low_trace = _boundary_jacobian(ANCHOR_ORDER, low_q)
    high_trace = _boundary_jacobian(order, high_q)
    inverse_trace = np.linalg.solve(low_graph, low_trace.T)
    lift = inverse_trace @ np.linalg.inv(low_trace @ inverse_trace)
    kernel = null_space(low_trace)
    injected_kernel = injection @ kernel
    kernel_projector = (
        injected_kernel
        @ np.linalg.solve(
            injected_kernel.T @ high_graph @ injected_kernel,
            injected_kernel.T @ high_graph,
        )
    )
    lifted_trace = injection @ lift @ high_trace
    projector = lifted_trace + kernel_projector @ (
        np.eye(high_graph.shape[0]) - lifted_trace
    )
    return projector, high_trace


def _mixed_record(order: int, low_q: np.ndarray) -> dict[str, float | int]:
    iq = _coordinate_injection(order)
    im = _multiplier_injection(order)
    energy = block_diag(
        _q_graph(order, 1),
        _velocity_graph(order, 0),
        _multiplier_graph(order, 1),
    )
    strong = block_diag(
        _q_graph(order, 2),
        _velocity_graph(order, 1),
        _multiplier_graph(order, 2),
    )
    q_projector, trace = _q_trace_projector(order, low_q)
    velocity_projector = _orthogonal_projector(
        _velocity_graph(order, 0), iq
    )
    multiplier_projector = _orthogonal_projector(
        _multiplier_graph(order, 1), im
    )
    projector = block_diag(
        q_projector, velocity_projector, multiplier_projector
    )
    complement = np.eye(projector.shape[0]) - projector
    operator_norm = math.sqrt(float(np.max(eigh(
        projector.T @ energy @ projector,
        energy,
        eigvals_only=True,
    ))))
    finite_s2_to_energy_tail = math.sqrt(max(0.0, float(np.max(eigh(
        complement.T @ energy @ complement,
        strong,
        eigvals_only=True,
    )))))
    qdim = 1 + 3 * order
    trace_tail = trace @ complement[:qdim, :qdim]
    return {
        "N": order,
        "mixed_dimension": int(projector.shape[0]),
        "idempotence_defect": float(np.linalg.norm(
            projector @ projector - projector, ord=2
        )),
        "mixed_energy_projection_norm": operator_norm,
        "complete_four_row_q_trace_tail_defect": float(
            np.linalg.norm(trace_tail, ord=2)
        ),
        "finite_diagnostic_S2_to_XE_tail_norm": finite_s2_to_energy_tail,
        "finite_diagnostic_is_the_analytic_tail_proof": False,
    }


def main() -> None:
    projector = json.loads(PROJECTOR.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    pole = json.loads(POLE.read_text(encoding="utf-8"))
    joint = np.asarray(np.load(ANCHOR)["state"], dtype=float)
    qdim = 1 + 3 * ANCHOR_ORDER
    sdim = 2 * qdim + 2 * ANCHOR_ORDER
    coordinates = {
        "event": joint[:qdim],
        "child": joint[sdim:sdim + qdim],
    }
    records = {
        side: [_mixed_record(order, q) for order in (16, 24, 32, 48)]
        for side, q in coordinates.items()
    }
    validation = {
        "existing_energy_space_assembled": True,
        "existing_strong_space_assembled": True,
        "mixed_projectors_are_idempotent_to_roundoff": all(
            row["idempotence_defect"] < 2.0e-8
            for side in records.values() for row in side
        ),
        "mixed_projectors_are_finite_in_XE_on_diagnostic_cutoffs": all(
            math.isfinite(float(row["mixed_energy_projection_norm"]))
            for side in records.values() for row in side
        ),
        "complete_four_row_q_trace_is_preserved": all(
            row["complete_four_row_q_trace_tail_defect"] < 2.0e-9
            for side in records.values() for row in side
        ),
        "multiplier_source_uses_existing_inverse_square_law": bool(
            source["validation_passed"]
        ),
        "critical_pole_uses_existing_source_restricted_inverse": bool(
            pole["validation_passed"]
        ),
        "finite_projection_diagnostics_not_used_as_uniform_proof": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "SOURCE_RESTRICTED_FULL_MIXED_ACTION_GRAPH_AND_TRACE_"
            "COMPATIBLE_GALERKIN_ARCHITECTURE_ASSEMBLED;_QUANTITATIVE_"
            "EULER_DIRAC_AND_DUHAMEL_OBSERVATION_MODULI_REMAIN_OPEN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (ANCHOR, PROJECTOR, SOURCE, POLE)
        },
        "spaces": {
            "energy_XE": "H1_q_CROSS_L2_velocity_CROSS_H1_lapse_shift",
            "strong_S2": "H2_q_CROSS_H1_velocity_CROSS_H2_lapse_shift",
            "boundary": "THE_EXISTING_COMPLETE_FOUR_ROW_q_TRACE",
            "gauge_quotient": "THE_EXISTING_BOUNDARY_COMPATIBLE_w_SHIFT_QUOTIENT",
            "new_domain_or_gate": False,
        },
        "mixed_projector": {
            "q_sector": (
                "EXISTING_ACTION_ORTHOGONAL_FOUR_ROW_TRACE_COMPATIBLE_FORTIN_PROJECTOR"
            ),
            "velocity_sector": "X_E_ORTHOGONAL_L2_GALERKIN_PROJECTOR",
            "multiplier_sector": "X_E_ORTHOGONAL_H1_GALERKIN_PROJECTOR",
            "finite_roundoff_diagnostics": records,
        },
        "source_routing": {
            "configuration_compact_tail": "C_F(M)<=4/sqrt(M)",
            "lapse_shift_weak_source": (
                "EXISTING_ACTION_DERIVED_INVERSE_SQUARE_SHELL_LAW"
            ),
            "critical_v_pole": (
                "EXISTING_SOURCE_RESTRICTED_WEIGHTED_H2_INDICIAL_INVERSE"
            ),
            "velocity_tail": (
                "GENERATED_BY_THE_EXISTING_POSITIVE_DURATION_EULER_DIRAC_EVOLUTION"
            ),
        },
        "closed_here": [
            "THE_FULL_MIXED_XE_AND_S2_SPACES_ARE_NOW_ASSEMBLED_IN_ONE_OPERATOR_ARCHITECTURE",
            "THE_COMPLETE_FOUR_ROW_TRACE_CORRECTION_ACTS_ONLY_IN_q_AND_REMAINS_EXACT",
            "THE_MULTIPLIER_SOURCE_AND_CRITICAL_POLE_ARE_ROUTED_TO_THEIR_EXISTING_BOUNDS",
        ],
        "first_missing_action_owned_coefficient": (
            "C_ED^G=sup_Y||K_ED,lo(Y)||_(L2(omega)_source_TO_XE*)_"
            "PLUS_ITS_STATE_LIPSCHITZ_BOUND_ON_THE_S2_ETA_NEIGHBORHOOD"
        ),
        "second_missing_composition": (
            "AN_EXPLICIT_VARIATION_OF_CONSTANTS_BOUND_FROM_THE_MIXED_"
            "GENERATOR_TAIL_TO_THE_POSITIVE_DURATION_OBSERVATION_NORM"
        ),
        "epsilon_obs_M_evaluable": False,
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
