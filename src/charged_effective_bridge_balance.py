from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple

import charged_kf_generator as kf


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

RHO_CH_CANDIDATE = Fraction(3)
G_BRIDGE = Fraction(16, 189)
UP_THRESHOLD_PROJECTION = Fraction(1, 2)

STATUS_TABLE = {
    "rho_ch_3_effective_bridge_balance": (
        "DERIVED_CONDITIONAL_ON_COLORLESS_LEPTON_BALANCE_AND_UP_THRESHOLD_PROJECTION"
    ),
    "down_bridge_bottleneck_76_over_7": "STRUCTURALLY_SUPPORTED_CANDIDATE",
    "rho_ch_exact_value": "OPEN_LOCALIZABLE",
    "charged_full_numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class BridgeBalanceRecord:
    sector: str
    Pi_f: Fraction
    tangent: Tuple[int, int]
    tangent_norm_sq: Fraction
    beta_f: Fraction
    kappa_f: Fraction
    beta_over_kappa: Fraction
    threshold_projection: Fraction
    effective_balance: Fraction
    status: str


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def g_bridge() -> Fraction:
    return G_BRIDGE


def g_bridge_factorization() -> Fraction:
    return Fraction(1, 21) * Fraction(4, 3) ** 2


def pi_f(sector: str) -> Fraction:
    return kf.projection_fraction(sector)


def tangent_norm_sq(sector: str, rho_ch: Fraction = RHO_CH_CANDIDATE) -> Fraction:
    return kf.tangent_norm_sq(sector, rho_ch)


def beta_f(sector: str) -> Fraction:
    return G_BRIDGE * pi_f(sector)


def kappa_f(sector: str, rho_ch: Fraction = RHO_CH_CANDIDATE) -> Fraction:
    return G_BRIDGE / tangent_norm_sq(sector, rho_ch)


def threshold_projection(sector: str) -> Fraction:
    if sector == "up":
        return UP_THRESHOLD_PROJECTION
    return Fraction(1)


def bridge_balance_record(sector: str) -> BridgeBalanceRecord:
    beta = beta_f(sector)
    kappa = kappa_f(sector)
    raw = beta / kappa
    threshold = threshold_projection(sector)
    status = (
        STATUS_TABLE["down_bridge_bottleneck_76_over_7"]
        if sector == "down"
        else STATUS_TABLE["rho_ch_3_effective_bridge_balance"]
    )
    return BridgeBalanceRecord(
        sector=sector,
        Pi_f=pi_f(sector),
        tangent=kf.EXPECTED_TANGENTS[sector],
        tangent_norm_sq=tangent_norm_sq(sector),
        beta_f=beta,
        kappa_f=kappa,
        beta_over_kappa=raw,
        threshold_projection=threshold,
        effective_balance=threshold * raw,
        status=status,
    )


def bridge_balance_records() -> Tuple[BridgeBalanceRecord, ...]:
    return tuple(bridge_balance_record(sector) for sector in kf.CHARGED_SECTORS)


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [_convert(item) for item in value]
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    return value


def _rows(rows):
    return [{key: _convert(value) for key, value in asdict(row).items()} for row in rows]


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-charged-effective-bridge-balance-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "rho_ch_candidate": fraction_string(RHO_CH_CANDIDATE),
        "g_bridge": fraction_string(G_BRIDGE),
        "g_bridge_factorization": "(1/21)(4/3)^2",
        "g_bridge_factorization_value": fraction_string(g_bridge_factorization()),
        "records": _rows(bridge_balance_records()),
        "statuses": STATUS_TABLE,
        "claim_boundary": (
            "Bridge balance is a structural candidate diagnostic; rho_ch exact value "
            "and full charged numerical closure remain open."
        ),
    }
