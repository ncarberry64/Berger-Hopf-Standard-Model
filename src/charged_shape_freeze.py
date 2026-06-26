from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import log, sqrt
from typing import Dict, Tuple

import numpy as np

import charged_effective_bridge_balance as balance
import charged_kf_generator as kf


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STATUS_TABLE = {
    "charged_shape_freeze_candidate": "STRONGLY_SUPPORTED_CANDIDATE",
    "charged_symbolic_shape_vector": "STRONGLY_SUPPORTED_CANDIDATE",
    "charged_full_numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class ChargedShapeRecord:
    sector: str
    matrix: Tuple[Tuple[float, float, float], ...]
    eigenvalues: Tuple[float, float, float]
    gaps_from_ground: Tuple[float, float, float]
    shape_ratio: float
    status: str


def rule_a_eta(sector: str) -> Fraction:
    return kf.eta_for_rule(sector, kf.RULE_A_SINGLE_OPERATOR_TRACE)


def charged_matrix(sector: str) -> Tuple[Tuple[float, float, float], ...]:
    costs = kf.diagonal_costs(sector, balance.RHO_CH_CANDIDATE)
    diag = [float(rule_a_eta(sector) * cost) for cost in costs]
    beta = float(balance.beta_f(sector))
    kappa = float(balance.kappa_f(sector))
    matrix = [
        [diag[0], beta, 0.0],
        [beta, diag[1], kappa],
        [0.0, kappa, diag[2]],
    ]
    if sector == "up":
        matrix[1][1] += log(2.0)
    return tuple(tuple(row) for row in matrix)


def eigenvalues(sector: str) -> Tuple[float, float, float]:
    values = np.linalg.eigvalsh(np.array(charged_matrix(sector), dtype=float))
    return tuple(float(value) for value in values)


def gaps_from_ground(sector: str) -> Tuple[float, float, float]:
    values = eigenvalues(sector)
    return tuple(value - values[0] for value in values)


def shape_ratio(sector: str) -> float:
    gaps = gaps_from_ground(sector)
    return gaps[2] / gaps[1]


def shape_record(sector: str) -> ChargedShapeRecord:
    return ChargedShapeRecord(
        sector=sector,
        matrix=charged_matrix(sector),
        eigenvalues=eigenvalues(sector),
        gaps_from_ground=gaps_from_ground(sector),
        shape_ratio=shape_ratio(sector),
        status=STATUS_TABLE["charged_shape_freeze_candidate"],
    )


def shape_records() -> Tuple[ChargedShapeRecord, ...]:
    return tuple(shape_record(sector) for sector in kf.CHARGED_SECTORS)


def tri_sector_residual() -> float:
    return shape_ratio("lepton") - shape_ratio("down") - shape_ratio("up")


def symbolic_shape_targets() -> Dict[str, float]:
    return {
        "down": 28.0 / 27.0,
        "up": sqrt(3.0),
        "lepton": sqrt(3.0) + 28.0 / 27.0,
    }


def symbolic_shape_deltas() -> Dict[str, float]:
    targets = symbolic_shape_targets()
    return {sector: shape_ratio(sector) - targets[sector] for sector in targets}


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-charged-shape-freeze-candidate-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "rho_ch_candidate": "3",
        "g_bridge": "16/189",
        "rule": "Rule-A suppression with derived-only up ln2 threshold",
        "records": [asdict(row) for row in shape_records()],
        "tri_sector_residual": tri_sector_residual(),
        "symbolic_shape_targets": symbolic_shape_targets(),
        "symbolic_shape_deltas": symbolic_shape_deltas(),
        "statuses": STATUS_TABLE,
        "claim_boundary": (
            "Shape ratios are internal eigen-gap diagnostics, not direct empirical "
            "mass predictions or final numerical closure."
        ),
    }
