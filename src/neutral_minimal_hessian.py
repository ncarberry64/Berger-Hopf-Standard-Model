from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

H_NU: Tuple[Tuple[int, int], Tuple[int, int]] = ((1, 1), (1, 2))
NEUTRAL_LEDGER = ((0, 0), (3, 0), (1, 1))
V_NU = (-2, 1)

STATUS_TABLE = {
    "neutral_Hessian_N2": "STRONGLY_SUPPORTED_CANDIDATE_BY_MINIMAL_UNIMODULAR_MIXING",
    "neutral_numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class NeutralHessianDiagnostic:
    matrix: Tuple[Tuple[int, int], Tuple[int, int]]
    determinant: int
    positive_definite: bool
    cost_3_0: int
    cost_1_1: int
    tangent: Tuple[int, int]
    tangent_norm: int
    status: str


def determinant() -> int:
    return H_NU[0][0] * H_NU[1][1] - H_NU[0][1] * H_NU[1][0]


def is_positive_definite() -> bool:
    return H_NU[0][0] > 0 and determinant() > 0


def neutral_cost(q: int, j: int) -> int:
    return q * q + 2 * q * j + 2 * j * j


def tangent_norm() -> int:
    q, j = V_NU
    return neutral_cost(q, j)


def diagnostic() -> NeutralHessianDiagnostic:
    return NeutralHessianDiagnostic(
        matrix=H_NU,
        determinant=determinant(),
        positive_definite=is_positive_definite(),
        cost_3_0=neutral_cost(3, 0),
        cost_1_1=neutral_cost(1, 1),
        tangent=V_NU,
        tangent_norm=tangent_norm(),
        status=STATUS_TABLE["neutral_Hessian_N2"],
    )


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-neutral-minimal-hessian-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "ledger": [list(mode) for mode in NEUTRAL_LEDGER],
        "diagnostic": asdict(diagnostic()),
        "statuses": STATUS_TABLE,
        "claim_boundary": "Neutral Hessian N2 is a structural candidate, not final neutral numerical closure.",
    }
