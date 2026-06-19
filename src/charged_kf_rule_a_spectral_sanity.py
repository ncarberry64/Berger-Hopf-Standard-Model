from __future__ import annotations

from fractions import Fraction
from math import exp
from typing import Dict, Tuple

import charged_kf_generator as kf


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _matrix_to_strings(matrix: Tuple[Tuple[Fraction, ...], ...]) -> list[list[str]]:
    return [[fraction_string(value) for value in row] for row in matrix]


def _float_matrix(matrix: Tuple[Tuple[float, ...], ...]) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix]


def spectral_factors_from_gaps(gaps: Tuple[float, ...]) -> Tuple[float, ...]:
    return tuple(exp(-gap) for gap in gaps)


def branch_row(
    sector: str,
    rho_ch: int,
    rule: str = kf.DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE,
) -> Dict[str, object]:
    matrix = kf.minimal_K_f_for_rule(sector, rho_ch, rule)
    gaps = kf.gaps_from_ground(matrix)
    return {
        "sector": sector,
        "rho_ch": rho_ch,
        "suppression_rule": rule,
        "rule_status": kf.suppression_rule_status(rule),
        "eta": fraction_string(kf.eta_for_rule(sector, rule)),
        "diagonal_costs": [fraction_string(value) for value in kf.diagonal_costs(sector, rho_ch)],
        "diagonal_entries": [fraction_string(matrix[i][i]) for i in range(3)],
        "beta_f": fraction_string(kf.beta(sector)),
        "kappa_f": fraction_string(kf.kappa(sector, rho_ch)),
        "bridge_ansatz_status": "UNCHANGED_BRIDGE_ANSATZ_NOT_SUPPRESSION_DERIVED",
        "matrix": _matrix_to_strings(matrix),
        "eigenvalues": list(kf.eigenvalues(matrix)),
        "gaps_from_ground": list(gaps),
        "spectral_factors_exp_minus_gap": list(spectral_factors_from_gaps(gaps)),
        "branch_ordering_note": (
            "Eigenvalues are sorted numerically; no empirical mass comparison is performed."
        ),
    }


def up_threshold_row(
    rho_ch: int,
    rule: str = kf.DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE,
) -> Dict[str, object]:
    matrix = kf.dressed_K_u_for_rule(rho_ch, rule)
    gaps = kf.gaps_from_ground(matrix)
    return {
        "sector": "up",
        "rho_ch": rho_ch,
        "suppression_rule": rule,
        "threshold_insertions": kf.threshold_insertions(),
        "only_threshold_is_up_middle_ln2": True,
        "matrix": _float_matrix(matrix),
        "eigenvalues": list(kf.eigenvalues(matrix)),
        "gaps_from_ground": list(gaps),
        "spectral_factors_exp_minus_gap": list(spectral_factors_from_gaps(gaps)),
        "branch_ordering_note": (
            "Operator-level ln2 insertion is applied only to the up-sector (6,0) slot."
        ),
    }


def report_as_dict() -> Dict[str, object]:
    rule_a_rows = [
        branch_row(sector, rho, kf.RULE_A_SINGLE_OPERATOR_TRACE)
        for rho in kf.RHO_CH_BRANCHES
        for sector in kf.CHARGED_SECTORS
    ]
    rule_b_rows = [
        branch_row(sector, rho, kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE)
        for rho in kf.RHO_CH_BRANCHES
        for sector in kf.CHARGED_SECTORS
    ]
    return {
        "id": "PO-BH-charged-Kf-rule-A-suppression-v1",
        "title": "Charged Kf Rule-A Suppression Propagation and Branch Spectral Sanity v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "default_diagnostic_suppression_rule": kf.DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE,
        "statuses": {
            "charged_Kf_rule_A_suppression_propagation": kf.STATUS_TABLE[
                "charged_Kf_rule_A_suppression_propagation"
            ],
            "RULE_A_SINGLE_OPERATOR_TRACE": kf.STATUS_TABLE["RULE_A_SINGLE_OPERATOR_TRACE"],
            "RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE": kf.STATUS_TABLE[
                "RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE"
            ],
            "minimal_charged_Kf_generator_eta_rule_A": kf.STATUS_TABLE[
                "minimal_charged_Kf_generator_eta_rule_A"
            ],
            "minimal_charged_Kf_generator_eta_rule_B": kf.STATUS_TABLE[
                "minimal_charged_Kf_generator_eta_rule_B"
            ],
            "independent_phase_response_source": kf.STATUS_TABLE[
                "independent_phase_response_source"
            ],
            "numerical_closure": kf.STATUS_TABLE["numerical_closure"],
        },
        "eta_values": {
            "RULE_A_SINGLE_OPERATOR_TRACE": {
                sector: fraction_string(kf.eta_for_rule(sector, kf.RULE_A_SINGLE_OPERATOR_TRACE))
                for sector in kf.CHARGED_SECTORS
            },
            "RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE": {
                sector: fraction_string(
                    kf.eta_for_rule(sector, kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE)
                )
                for sector in kf.CHARGED_SECTORS
            },
        },
        "rule_a_branch_rows": rule_a_rows,
        "rule_b_comparison_rows": rule_b_rows,
        "rule_a_up_threshold_rows": [
            up_threshold_row(rho, kf.RULE_A_SINGLE_OPERATOR_TRACE) for rho in kf.RHO_CH_BRANCHES
        ],
        "threshold_policy": {
            "insertions": kf.threshold_insertions(),
            "no_other_threshold_dressings_added": True,
        },
        "bridge_policy": (
            "beta_f and kappa_f remain the existing bridge ansatz layer; Rule A changes "
            "suppression diagonals only."
        ),
        "claim_boundary": (
            "Rule A propagation is a diagnostic charged K_f branch; no empirical comparison, "
            "official prediction update, frozen output change, or numerical closure is claimed."
        ),
    }
