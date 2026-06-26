from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import json
import numpy as np


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_ALPHA_INV = 137.035999084
FROZEN_BERGER_A = FROZEN_ALPHA_INV / (12.0 * pi**2)

JET_HEAT_STRENGTHENS_HIERARCHY = "JET_HEAT_STRENGTHENS_HIERARCHY"
JET_HEAT_COMPRESSES_HIERARCHY = "JET_HEAT_COMPRESSES_HIERARCHY"
JET_HEAT_MIXED_RESPONSE = "JET_HEAT_MIXED_RESPONSE"
JET_HEAT_NEUTRAL = "JET_HEAT_NEUTRAL"
JET_HEAT_SINGULAR_AUDIT = "JET_HEAT_SINGULAR_AUDIT"
JET_HEAT_OPEN = "JET_HEAT_OPEN"

STACK_JET_HEAT_SUPPORTED = "STACK_JET_HEAT_SUPPORTED"
STACK_JET_HEAT_PARTIAL = "STACK_JET_HEAT_PARTIAL"
STACK_JET_HEAT_REJECTED_AS_PRIMARY = "STACK_JET_HEAT_REJECTED_AS_PRIMARY"
STACK_JET_HEAT_OPEN = "STACK_JET_HEAT_OPEN"
STACK_JET_HEAT_MIXED_OR_NEUTRAL = "STACK_JET_HEAT_MIXED_OR_NEUTRAL"


@dataclass(frozen=True)
class JetHeatSectorResponse:
    sector: str
    eigenvalues: Tuple[float, float, float]
    q_tau: float
    q_mu: float
    q_e: float
    response_condition_q_e_lt_q_mu_lt_q_tau: bool
    sector_verdict: str


def berger_a() -> float:
    """Return the frozen alpha-anchored Berger anisotropy."""

    return FROZEN_BERGER_A


def berger_a_inverse_squared(a: float) -> float:
    return float(a) ** -2


def lambda_berger(n: int, a: float) -> float:
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return 0.0
    return float(n * (n + 1) + n**2 * (float(a) ** -2 - 1.0))


def b20_magnitude(a: float) -> float:
    return float(sqrt(2.0 + float(a) ** -4))


def oriented_jet_heat_operator(a: float) -> Dict[str, List[List[float]] | float | str]:
    """Return the first-order oriented jet-heat generator.

    The first-order operator is
    diag(0, -Lambda_1, -Lambda_2) - sqrt(2+a^{-4}) E_20,
    with E_20 represented as the slot-2 to slot-0 transfer.  The symmetric
    form is reported for real quadratic response estimates.
    """

    lambda1 = lambda_berger(1, a)
    lambda2 = lambda_berger(2, a)
    b20 = b20_magnitude(a)
    diagonal = np.diag([0.0, -lambda1, -lambda2])
    e20 = np.zeros((3, 3), dtype=float)
    e20[0, 2] = 1.0
    first_order = diagonal - b20 * e20
    symmetric = 0.5 * (first_order + first_order.T)
    return {
        "convention": "positive_curvature_cost_L_Berger=-r^2 Delta_Berger",
        "b20_orientation": "negative",
        "Lambda_0": 0.0,
        "Lambda_1": lambda1,
        "Lambda_2": lambda2,
        "b20_magnitude": b20,
        "E_20": e20.tolist(),
        "first_order_operator": first_order.tolist(),
        "symmetric_response_operator": symmetric.tolist(),
    }


def _as_matrix(matrix: Iterable[Iterable[float]]) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.shape != (3, 3):
        raise ValueError("charged jet-heat audit expects a 3x3 matrix")
    if not np.allclose(arr, arr.T, atol=1e-12):
        raise ValueError("charged jet-heat audit expects a symmetric matrix")
    return arr


def amplitude_vector_from_K(K: Iterable[Iterable[float]], a: float, c: Iterable[float]) -> Tuple[float, float, float]:
    """Return sharp-profile amplitudes from K eigenvalues for diagnostics only."""

    del a, c
    values = np.linalg.eigvalsh(_as_matrix(K))
    amplitudes = np.exp(-values)
    return tuple(float(value) for value in amplitudes)  # type: ignore[return-value]


def compute_Y_from_A_and_eigenvectors(
    A: Iterable[Iterable[float]],
    eigenvectors: Iterable[Iterable[float]],
) -> Tuple[float, float, float]:
    """Compute diagonal jet responses in the supplied eigenbasis."""

    operator = _as_matrix(A)
    vectors = np.asarray(eigenvectors, dtype=float)
    if vectors.shape != (3, 3):
        raise ValueError("eigenvectors must be 3x3")
    values = []
    for column in range(3):
        vector = vectors[:, column]
        values.append(float(vector.T @ operator @ vector))
    return tuple(values)  # type: ignore[return-value]


def classify_response_sign(q_ordered: Tuple[float, float, float], tol: float = 1e-12) -> str:
    q_e, q_mu, q_tau = q_ordered
    if any(not np.isfinite(value) for value in q_ordered):
        return JET_HEAT_SINGULAR_AUDIT
    if q_e < q_mu < q_tau:
        return JET_HEAT_STRENGTHENS_HIERARCHY
    if q_tau < q_mu < q_e:
        return JET_HEAT_COMPRESSES_HIERARCHY
    if max(abs(value) for value in q_ordered) <= tol:
        return JET_HEAT_NEUTRAL
    return JET_HEAT_MIXED_RESPONSE


def compute_q_tau_response(
    K: Iterable[Iterable[float]],
    a: float,
    c: Iterable[float],
    branch_label: str,
    sector: str = "lepton",
) -> JetHeatSectorResponse:
    del c, branch_label
    matrix = _as_matrix(K)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    response_operator = np.asarray(
        oriented_jet_heat_operator(a)["symmetric_response_operator"],
        dtype=float,
    )
    q_by_eigen_order = compute_Y_from_A_and_eigenvectors(response_operator, eigenvectors)
    # The exported branch matrices use generation_order=by_y_ascending.  The
    # smallest K eigenvalue is the heavy/tau-like state, followed by middle/mu,
    # then light/e.
    q_tau, q_mu, q_e = q_by_eigen_order
    q_ordered = (q_e, q_mu, q_tau)
    verdict = classify_response_sign(q_ordered)
    return JetHeatSectorResponse(
        sector=sector,
        eigenvalues=tuple(float(value) for value in eigenvalues),  # type: ignore[arg-type]
        q_tau=float(q_tau),
        q_mu=float(q_mu),
        q_e=float(q_e),
        response_condition_q_e_lt_q_mu_lt_q_tau=(verdict == JET_HEAT_STRENGTHENS_HIERARCHY),
        sector_verdict=verdict,
    )


def _sector_to_json(response: JetHeatSectorResponse) -> Dict[str, object]:
    return {
        "eigenvalues": list(response.eigenvalues),
        "q_tau": response.q_tau,
        "q_mu": response.q_mu,
        "q_e": response.q_e,
        "response_condition_q_e_lt_q_mu_lt_q_tau": (
            response.response_condition_q_e_lt_q_mu_lt_q_tau
        ),
        "sector_verdict": response.sector_verdict,
    }


def stack_verdict(sector_verdicts: Iterable[str]) -> str:
    verdicts = tuple(sector_verdicts)
    if not verdicts:
        return STACK_JET_HEAT_OPEN
    if all(verdict == JET_HEAT_STRENGTHENS_HIERARCHY for verdict in verdicts):
        return STACK_JET_HEAT_SUPPORTED
    if all(verdict == JET_HEAT_COMPRESSES_HIERARCHY for verdict in verdicts):
        return STACK_JET_HEAT_REJECTED_AS_PRIMARY
    if any(verdict == JET_HEAT_OPEN for verdict in verdicts):
        return STACK_JET_HEAT_OPEN
    if any(verdict == JET_HEAT_STRENGTHENS_HIERARCHY for verdict in verdicts):
        return STACK_JET_HEAT_PARTIAL
    return STACK_JET_HEAT_MIXED_OR_NEUTRAL


def audit_artifact_from_branch_matrix_artifact(payload: Dict[str, object]) -> Dict[str, object]:
    branch = str(payload["branch"])
    a = float(payload.get("a", berger_a()))
    sectors = payload.get("sectors")
    if not isinstance(sectors, dict):
        raise ValueError("branch artifact is missing sectors")

    responses: Dict[str, Dict[str, object]] = {}
    for sector, row in sectors.items():
        if not isinstance(row, dict) or "K" not in row:
            continue
        response = compute_q_tau_response(
            row["K"],  # type: ignore[arg-type]
            a,
            payload.get("c", [1, 2, 4]),  # type: ignore[arg-type]
            branch,
            sector=str(sector),
        )
        responses[str(sector)] = _sector_to_json(response)

    lepton_verdict = responses.get("lepton", {}).get("sector_verdict", JET_HEAT_OPEN)
    verdict = stack_verdict(
        str(row.get("sector_verdict", JET_HEAT_OPEN)) for row in responses.values()
    )
    if lepton_verdict == JET_HEAT_STRENGTHENS_HIERARCHY:
        oriented_status = "STRUCTURALLY_SUPPORTED_CANDIDATE"
    elif lepton_verdict == JET_HEAT_COMPRESSES_HIERARCHY:
        oriented_status = "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
    elif lepton_verdict == JET_HEAT_OPEN:
        oriented_status = "OPEN"
    else:
        oriented_status = "PARTIAL_OR_MIXED_CANDIDATE"

    return {
        "audit": "oriented_jet_heat_response_audit",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": branch,
        "source_branch_artifact": payload.get("artifact"),
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "observed_masses_used": False,
        "CKM_PMNS_used": False,
        "response_condition": "q_e < q_mu < q_tau",
        "charged_precision_closure": "OPEN",
        "frozen_before_comparison": True,
        "used_target_data": False,
        "a": a,
        "a_formula": "alpha^{-1}/(12*pi^2)",
        "a_inverse_squared": berger_a_inverse_squared(a),
        "jet_heat_operator": oriented_jet_heat_operator(a),
        "sector_responses": responses,
        "lepton_response_verdict": lepton_verdict,
        "stack_verdict": verdict,
        "oriented_jet_heat_response": oriented_status,
        "open_items": [
            "tau remains boundary-derived/open; this response audit is structural only",
            "sigma remains boundary-derived/open; no mass fit is allowed",
            "charged precision closure remains open",
        ],
    }


def load_branch_artifact(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_artifact_from_file(path: Path) -> Dict[str, object]:
    return audit_artifact_from_branch_matrix_artifact(load_branch_artifact(path))
