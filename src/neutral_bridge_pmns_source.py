from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple

import neutral_minimal_hessian as hessian


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

ETA_NU = Fraction(1, 3)
G_NU = Fraction(1, 3)
BETA_NU = Fraction(1, 3)
KAPPA_NU = Fraction(1, 6)

STATUS_TABLE = {
    "neutral_bridge_seed_1_over_3": "STRONGLY_SUPPORTED_CANDIDATE",
    "neutral_tangent_bridge_1_over_6": "STRONGLY_SUPPORTED_CANDIDATE",
    "PMNS_structural_source": "STRONGLY_SUPPORTED_CANDIDATE",
    "PMNS_numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class NeutralBridgeDiagnostic:
    eta_nu: Fraction
    g_nu: Fraction
    beta_nu: Fraction
    kappa_nu: Fraction
    K_nu: Tuple[Tuple[Fraction, Fraction, Fraction], ...]
    cost_3_0: int
    cost_1_1: int
    excitation_inversion: bool
    tangent_norm: int
    theta_01: Fraction
    theta_12: Fraction
    theta_02: Fraction
    theta_l_01: Fraction
    theta_l_12: Fraction


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def neutral_operator() -> Tuple[Tuple[Fraction, Fraction, Fraction], ...]:
    return (
        (Fraction(0), BETA_NU, Fraction(0)),
        (BETA_NU, Fraction(3), KAPPA_NU),
        (Fraction(0), KAPPA_NU, Fraction(5, 3)),
    )


def diagnostic() -> NeutralBridgeDiagnostic:
    return NeutralBridgeDiagnostic(
        eta_nu=ETA_NU,
        g_nu=G_NU,
        beta_nu=BETA_NU,
        kappa_nu=KAPPA_NU,
        K_nu=neutral_operator(),
        cost_3_0=hessian.neutral_cost(3, 0),
        cost_1_1=hessian.neutral_cost(1, 1),
        excitation_inversion=hessian.neutral_cost(3, 0) > hessian.neutral_cost(1, 1),
        tangent_norm=hessian.tangent_norm(),
        theta_01=Fraction(1, 9),
        theta_12=Fraction(1, 8),
        theta_02=Fraction(1, 90),
        theta_l_01=Fraction(4, 585),
        theta_l_12=Fraction(4, 1035),
    )


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [_convert(item) for item in value]
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    return value


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-neutral-bridge-PMNS-source-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "diagnostic": {key: _convert(value) for key, value in asdict(diagnostic()).items()},
        "statuses": STATUS_TABLE,
        "claim_boundary": "PMNS structural source is candidate only; PMNS numerical closure remains open.",
    }
