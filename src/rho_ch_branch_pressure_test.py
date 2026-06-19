from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import exp
from typing import Dict, Tuple

import numpy as np

import charged_kf_generator as kf


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

BRANCH_MEANINGS = {
    1: "isotropic stiffness",
    2: "weak-involution stiffness",
    3: "rank-three closure stiffness",
}

STATUS_TABLE = {
    "rho_ch_branch_pressure_test_v1": "COMPLETED_INTERNAL_PRESSURE_TEST",
    "rho_ch_1_isotropic_branch": "BRANCH_CANDIDATE",
    "rho_ch_2_weak_involution_branch": "BRANCH_CANDIDATE",
    "rho_ch_3_rank_three_branch": "STRUCTURALLY_INTERESTING_BRANCH",
    "rho_ch_exact_value": "OPEN_LOCALIZABLE",
    "down_near_degeneracy_rho_ch_3": "STRUCTURALLY_INTERESTING_NOT_SELECTION_RULE",
    "up_threshold_branch_reordering": "DIAGNOSTIC_REPORTED_NO_EMPIRICAL_SELECTION",
    "charged_Kf_Rule_A_spectral_sanity": "INTERNALLY_STABLE_DIAGNOSTIC",
    "numerical_closure": "OPEN",
}

FORBIDDEN_DERIVATION_INPUTS = (
    "observed charged-lepton masses",
    "observed quark masses",
    "observed CKM values",
    "observed PMNS values",
    "observed neutrino mass splittings",
    "measured fine-structure alpha",
    "empirical target ratios",
    "post-comparison branch selection",
)

BASIS_LABELS = ("reference", "middle", "light")


@dataclass(frozen=True)
class SpectralDiagnostics:
    eigenvalues: Tuple[float, float, float]
    gaps_from_ground: Tuple[float, float, float]
    spectral_factors: Tuple[float, float, float]
    gap_ratio: float | None
    pair_split: float
    reference_gap_min: float
    branch_order: Tuple[str, str, str]


@dataclass(frozen=True)
class RhoBranchReport:
    rho_ch: int
    branch_meaning: str
    branch_status: str
    violates_internal_consistency: bool
    recommended_scientific_status: str
    lepton: SpectralDiagnostics
    up: SpectralDiagnostics
    up_threshold: SpectralDiagnostics
    down: SpectralDiagnostics
    down_degeneracy_measure: float
    up_threshold_causes_reordering: bool
    notes: Tuple[str, ...]


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _float_matrix(matrix) -> np.ndarray:
    return np.array([[float(value) for value in row] for row in matrix], dtype=float)


def spectral_diagnostics(matrix) -> SpectralDiagnostics:
    values, vectors = np.linalg.eigh(_float_matrix(matrix))
    gaps = values - values[0]
    labels = []
    for column in range(vectors.shape[1]):
        dominant = int(np.argmax(np.abs(vectors[:, column])))
        labels.append(BASIS_LABELS[dominant])
    gap_1 = float(gaps[1])
    gap_2 = float(gaps[2])
    return SpectralDiagnostics(
        eigenvalues=tuple(float(value) for value in values),  # type: ignore[return-value]
        gaps_from_ground=tuple(float(value) for value in gaps),  # type: ignore[return-value]
        spectral_factors=tuple(float(exp(-value)) for value in gaps),  # type: ignore[return-value]
        gap_ratio=float(gap_2 / gap_1) if gap_1 != 0 else None,
        pair_split=float(abs(gap_2 - gap_1)),
        reference_gap_min=float(min(gap_1, gap_2)),
        branch_order=tuple(labels),  # type: ignore[return-value]
    )


def branch_status(rho_ch: int) -> str:
    if rho_ch == 3:
        return STATUS_TABLE["rho_ch_3_rank_three_branch"]
    if rho_ch == 2:
        return STATUS_TABLE["rho_ch_2_weak_involution_branch"]
    if rho_ch == 1:
        return STATUS_TABLE["rho_ch_1_isotropic_branch"]
    raise ValueError("rho_ch must be one of 1, 2, 3")


def branch_report(rho_ch: int) -> RhoBranchReport:
    if rho_ch not in kf.RHO_CH_BRANCHES:
        raise ValueError("rho_ch must be one of the charged Kf branches")
    lepton = spectral_diagnostics(kf.minimal_K_f_for_rule("lepton", rho_ch))
    up = spectral_diagnostics(kf.minimal_K_f_for_rule("up", rho_ch))
    up_threshold = spectral_diagnostics(kf.dressed_K_u_for_rule(rho_ch))
    down = spectral_diagnostics(kf.minimal_K_f_for_rule("down", rho_ch))
    down_degeneracy = abs(down.gaps_from_ground[2] - down.gaps_from_ground[1])
    reorders = up.branch_order != up_threshold.branch_order
    notes = [
        "No empirical comparison is performed.",
        "All branches require action-level rho_ch selection before promotion.",
    ]
    if rho_ch == 3:
        notes.append("rho_ch=3 is structurally interesting because it minimizes the down pair split in this diagnostic.")
    return RhoBranchReport(
        rho_ch=rho_ch,
        branch_meaning=BRANCH_MEANINGS[rho_ch],
        branch_status=branch_status(rho_ch),
        violates_internal_consistency=False,
        recommended_scientific_status="REQUIRES_ACTION_SELECTION",
        lepton=lepton,
        up=up,
        up_threshold=up_threshold,
        down=down,
        down_degeneracy_measure=float(down_degeneracy),
        up_threshold_causes_reordering=reorders,
        notes=tuple(notes),
    )


def all_branch_reports() -> Tuple[RhoBranchReport, ...]:
    return tuple(branch_report(rho) for rho in kf.RHO_CH_BRANCHES)


def _diag_to_dict(diag: SpectralDiagnostics) -> Dict[str, object]:
    return {
        "eigenvalues": list(diag.eigenvalues),
        "gaps_from_ground": list(diag.gaps_from_ground),
        "spectral_factors_exp_minus_gap": list(diag.spectral_factors),
        "gap_ratio": diag.gap_ratio,
        "pair_split": diag.pair_split,
        "reference_gap_min": diag.reference_gap_min,
        "branch_order": list(diag.branch_order),
    }


def _branch_to_dict(report: RhoBranchReport) -> Dict[str, object]:
    return {
        "rho_ch": report.rho_ch,
        "branch_meaning": report.branch_meaning,
        "branch_status": report.branch_status,
        "violates_internal_consistency": report.violates_internal_consistency,
        "recommended_scientific_status": report.recommended_scientific_status,
        "lepton": _diag_to_dict(report.lepton),
        "up": _diag_to_dict(report.up),
        "up_threshold": _diag_to_dict(report.up_threshold),
        "down": _diag_to_dict(report.down),
        "down_degeneracy_measure": report.down_degeneracy_measure,
        "up_threshold_causes_reordering": report.up_threshold_causes_reordering,
        "notes": list(report.notes),
    }


def report_as_dict() -> Dict[str, object]:
    branches = all_branch_reports()
    return {
        "id": "PO-BH-rho-ch-branch-pressure-test-v1",
        "title": "rho_ch Branch Pressure Test and Charged Kf Rule-A Spectral Classification v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "suppression_rule": kf.DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE,
        "rule_a_eta_values": {
            sector: fraction_string(kf.eta_for_rule(sector, kf.RULE_A_SINGLE_OPERATOR_TRACE))
            for sector in kf.CHARGED_SECTORS
        },
        "rule_b_used_as_default": False,
        "rho_ch_exact_value_status": STATUS_TABLE["rho_ch_exact_value"],
        "branch_reports": [_branch_to_dict(report) for report in branches],
        "branch_classifications": {
            str(report.rho_ch): report.branch_status for report in branches
        },
        "winning_branch_selected": False,
        "all_branches_viable": all(
            not report.violates_internal_consistency for report in branches
        ),
        "statuses": STATUS_TABLE,
        "threshold_policy": {
            "insertions": kf.threshold_insertions(),
            "only_up_middle_ln2": True,
            "no_other_threshold_dressings_added": True,
        },
        "conclusion": (
            "All rho_ch branches remain internally viable under the Rule-A Kf diagnostic. "
            "rho_ch=3 is structurally interesting from the down-pair split but is not selected."
        ),
    }
