from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import log
from typing import Dict


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STATUS_TABLE = {
    "CKM_structural_source": "STRONGLY_SUPPORTED_CANDIDATE",
    "CKM_real_mixing_source": "DOWN_NEAR_DEGENERACY_VS_UP_THRESHOLD_GAP",
    "CKM_numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class CKMStructuralDiagnostic:
    down_N_d1: int
    down_N_d2: int
    down_cost_difference: int
    down_rule_A_diagonal_gap: Fraction
    up_N_u1: int
    up_N_u2: int
    up_lambda_u1_without_ln2: Fraction
    up_lambda_u1_thresholded_label: str
    up_lambda_u2: Fraction
    up_threshold_gap_label: str
    theta_12_u_label: str
    theta_12_d: Fraction
    source_status: str


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def up_threshold_gap_numeric() -> float:
    return float(Fraction(1178, 147)) - log(2.0)


def theta_12_u_numeric() -> float:
    return float(Fraction(16, 1323)) / up_threshold_gap_numeric()


def diagnostic() -> CKMStructuralDiagnostic:
    return CKMStructuralDiagnostic(
        down_N_d1=27,
        down_N_d2=28,
        down_cost_difference=1,
        down_rule_A_diagonal_gap=Fraction(68, 147),
        up_N_u1=36,
        up_N_u2=67,
        up_lambda_u1_without_ln2=Fraction(456, 49),
        up_lambda_u1_thresholded_label="456/49 + ln2",
        up_lambda_u2=Fraction(2546, 147),
        up_threshold_gap_label="1178/147 - ln2",
        theta_12_u_label="(16/1323)/(1178/147 - ln2)",
        theta_12_d=Fraction(28, 2907),
        source_status=STATUS_TABLE["CKM_real_mixing_source"],
    )


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    return value


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-CKM-structural-source-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "diagnostic": {key: _convert(value) for key, value in asdict(diagnostic()).items()},
        "theta_12_u_numeric_diagnostic": theta_12_u_numeric(),
        "statuses": STATUS_TABLE,
        "claim_boundary": "CKM structural source is candidate only; CKM numerical closure remains open.",
    }
