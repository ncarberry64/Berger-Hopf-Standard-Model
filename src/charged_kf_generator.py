from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import log
from typing import Dict, Iterable, List, Tuple

import numpy as np

import charged_suppression_operator_kernel as suppression_kernel


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

KAPPA_3 = 3
RHO_CH_BRANCHES: Tuple[int, int, int] = (1, 2, 3)

RULE_A_SINGLE_OPERATOR_TRACE = "RULE_A_SINGLE_OPERATOR_TRACE"
RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE = "RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE"
DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE = RULE_A_SINGLE_OPERATOR_TRACE

BRIDGE_RULE_DIAGONAL_ONLY = "BRIDGE_RULE_DIAGONAL_ONLY"
BRIDGE_RULE_MINIMAL_ANSATZ = "BRIDGE_RULE_MINIMAL_ANSATZ"
BRIDGE_RULE_SYMBOLIC_OPEN = "BRIDGE_RULE_SYMBOLIC_OPEN"
DEFAULT_DIAGNOSTIC_BRIDGE_RULE = BRIDGE_RULE_MINIMAL_ANSATZ

BRIDGE_RULE_STATUS_TABLE = {
    BRIDGE_RULE_DIAGONAL_ONLY: "BASELINE_DIAGNOSTIC",
    BRIDGE_RULE_MINIMAL_ANSATZ: "STRONGLY_SUPPORTED_CANDIDATE",
    BRIDGE_RULE_SYMBOLIC_OPEN: "TOPOLOGY_PRESENT_MAGNITUDES_OPEN",
}

SECTORS: Dict[str, Tuple[int, int]] = {
    "neutrino": (0, +1),
    "lepton": (0, -1),
    "up": (1, +1),
    "down": (1, -1),
}

LEDGERS: Dict[str, Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]] = {
    "neutrino": ((0, 0), (3, 0), (1, 1)),
    "lepton": ((0, 0), (1, 2), (3, 3)),
    "up": ((0, 0), (6, 0), (8, 1)),
    "down": ((0, 0), (0, 3), (4, 2)),
}

CHARGED_SECTORS: Tuple[str, str, str] = ("lepton", "up", "down")

EXPECTED_TANGENTS: Dict[str, Tuple[int, int]] = {
    "neutrino": (-2, 1),
    "lepton": (2, 1),
    "up": (2, 1),
    "down": (4, -1),
}

EXPECTED_OMEGA_EXPRESSIONS = {
    "neutrino": "-q - 2j",
    "lepton": "-q + 2j",
    "up": "q - 2j",
    "down": "q + 4j",
}

PI: Dict[str, Fraction] = {
    "lepton": Fraction(1, 7),
    "up": Fraction(2, 7),
    "down": Fraction(4, 7),
}

CHI: Dict[str, int] = {
    "lepton": 1,
    "up": 2,
    "down": 4,
}

STATUS_TABLE = {
    "Boundary_Graded_Defect_Theorem": "STRONGLY_SUPPORTED_CANDIDATE",
    "sector_target_incidence_product_A": "STRONGLY_SUPPORTED_CANDIDATE",
    "orientation_trace_Gamma_T": "STRONGLY_SUPPORTED_CANDIDATE",
    "unified_Omega_projector_formula": "STRONGLY_SUPPORTED_CANDIDATE",
    "zero_defect_tangent_adjacency": "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
    "charged_suppression_incidence_closure": "STRONGLY_SUPPORTED_CANDIDATE",
    "minimal_charged_Kf_generator": "STRONGLY_SUPPORTED_CANDIDATE",
    "operator_level_threshold_insertion": "STRONGLY_SUPPORTED_CANDIDATE",
    "Mode_Identity_Threshold_Readout_Theorem": "STRONGLY_SUPPORTED_CANDIDATE",
    "Z_virt_u1": "DERIVED_CONDITIONAL",
    "charged_Kf_rule_A_suppression_propagation": "DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL",
    "RULE_A_SINGLE_OPERATOR_TRACE": "DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL",
    "RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE": "CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE",
    "minimal_charged_Kf_generator_eta_rule_A": "DERIVED_CONDITIONAL_DIAGNOSTIC_BRANCH",
    "minimal_charged_Kf_generator_eta_rule_B": "LEGACY_CANDIDATE_BRANCH",
    "independent_phase_response_source": "OPEN_LOCALIZABLE",
    "rho_ch_exact_value": "OPEN_LOCALIZABLE",
    "full_threshold_operator": "OPEN",
    "RG_transport": "OPEN",
    "numerical_closure": "OPEN",
}

FORBIDDEN_DERIVATION_INPUTS = (
    "observed masses",
    "quark mass ratios",
    "charged lepton masses",
    "CKM",
    "PMNS",
    "neutrino data",
    "measured alpha",
    "target ratios",
    "post-comparison residuals",
)


@dataclass(frozen=True)
class SectorRow:
    sector: str
    C: int
    sigma: int
    P_C: Fraction
    P_plus: Fraction
    P_minus: Fraction
    P_d: Fraction
    omega_expression: str
    A: Fraction
    tau: Fraction
    T: Fraction


@dataclass(frozen=True)
class MatrixBranchReport:
    sector: str
    rho_ch: int
    ledger: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]
    diagonal_costs: Tuple[Fraction, Fraction, Fraction]
    eta: Fraction
    beta: Fraction
    kappa: Fraction
    matrix: Tuple[Tuple[Fraction, Fraction, Fraction], ...]
    eigenvalues: Tuple[float, float, float]
    gaps_from_ground: Tuple[float, float, float]


def validate_sector_labels(C: int, sigma: int) -> None:
    if C not in (0, 1):
        raise ValueError("C must be 0 or 1")
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or +1")


def P_C(C: int) -> Fraction:
    if C not in (0, 1):
        raise ValueError("C must be 0 or 1")
    return Fraction(C, 1)


def P_plus(sigma: int) -> Fraction:
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or +1")
    return Fraction(1 + sigma, 2)


def P_minus(sigma: int) -> Fraction:
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or +1")
    return Fraction(1 - sigma, 2)


def P_d(C: int, sigma: int) -> Fraction:
    validate_sector_labels(C, sigma)
    return P_C(C) * P_minus(sigma)


def sector_projectors(C: int, sigma: int) -> Dict[str, Fraction]:
    validate_sector_labels(C, sigma)
    return {
        "P_nu": (1 - P_C(C)) * P_plus(sigma),
        "P_l": (1 - P_C(C)) * P_minus(sigma),
        "P_u": P_C(C) * P_plus(sigma),
        "P_d": P_d(C, sigma),
    }


def omega_coefficients(C: int, sigma: int) -> Tuple[Fraction, Fraction]:
    validate_sector_labels(C, sigma)
    q_coeff = 2 * P_C(C) - 1
    j_coeff = 2 * (-sigma) * (1 + P_d(C, sigma))
    return q_coeff, j_coeff


def omega(C: int, sigma: int, q: int, j: int) -> Fraction:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    return q_coeff * q + j_coeff * j


def omega_expression(C: int, sigma: int) -> str:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    q_part = "q" if q_coeff == 1 else "-q"
    sign = "+" if j_coeff > 0 else "-"
    return f"{q_part} {sign} {abs(j_coeff)}j"


def incidence_A(C: int, sigma: int) -> Fraction:
    validate_sector_labels(C, sigma)
    return KAPPA_3 * (1 + P_C(C)) * (1 + P_d(C, sigma))


def orientation_tau(C: int, sigma: int) -> Fraction:
    validate_sector_labels(C, sigma)
    return P_C(C) - (1 - P_C(C)) * sigma


def target_T(C: int, sigma: int) -> Fraction:
    return orientation_tau(C, sigma) * incidence_A(C, sigma)


def delta_IT(C: int, sigma: int, q: int, j: int) -> Fraction:
    return omega(C, sigma, q, j) - target_T(C, sigma)


def sector_rows() -> Iterable[SectorRow]:
    for sector, (C, sigma) in SECTORS.items():
        yield SectorRow(
            sector=sector,
            C=C,
            sigma=sigma,
            P_C=P_C(C),
            P_plus=P_plus(sigma),
            P_minus=P_minus(sigma),
            P_d=P_d(C, sigma),
            omega_expression=omega_expression(C, sigma),
            A=incidence_A(C, sigma),
            tau=orientation_tau(C, sigma),
            T=target_T(C, sigma),
        )


def is_reference_slot(mode: Tuple[int, int]) -> bool:
    return mode == (0, 0)


def nonzero_ledger_modes(sector: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return LEDGERS[sector][1:]


def tangent_difference(sector: str) -> Tuple[int, int]:
    first, second = nonzero_ledger_modes(sector)
    return second[0] - first[0], second[1] - first[1]


def mode_satisfies_sector_equation(sector: str, mode: Tuple[int, int]) -> bool:
    C, sigma = SECTORS[sector]
    q, j = mode
    return omega(C, sigma, q, j) == target_T(C, sigma)


def charged_norm_N(q: int, j: int, rho_ch: int | Fraction) -> Fraction:
    return q * q + Fraction(rho_ch) * j * j


def diagonal_costs(sector: str, rho_ch: int | Fraction) -> Tuple[Fraction, Fraction, Fraction]:
    if sector not in CHARGED_SECTORS:
        raise ValueError("minimal K_f is defined only for charged sectors")
    return tuple(charged_norm_N(q, j, rho_ch) for q, j in LEDGERS[sector])  # type: ignore[return-value]


def g_ch() -> Fraction:
    return Fraction(1, 21)


def projection_fraction(sector: str) -> Fraction:
    return PI[sector]


def self_screening(sector: str) -> Fraction:
    return 1 - CHI[sector] * g_ch()


def eta(sector: str) -> Fraction:
    return projection_fraction(sector) * g_ch() * self_screening(sector)


def eta_for_rule(sector: str, rule: str = DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE) -> Fraction:
    if rule == RULE_A_SINGLE_OPERATOR_TRACE:
        return suppression_kernel.eta_single_trace(sector)
    if rule == RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE:
        return eta(sector)
    raise ValueError(f"unknown suppression rule: {rule}")


def suppression_rule_status(rule: str) -> str:
    if rule == RULE_A_SINGLE_OPERATOR_TRACE:
        return STATUS_TABLE["RULE_A_SINGLE_OPERATOR_TRACE"]
    if rule == RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE:
        return STATUS_TABLE["RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE"]
    raise ValueError(f"unknown suppression rule: {rule}")


def bridge_rule_status(rule: str) -> str:
    try:
        return BRIDGE_RULE_STATUS_TABLE[rule]
    except KeyError:
        raise ValueError(f"unknown bridge rule: {rule}") from None


def beta(sector: str) -> Fraction:
    return g_ch() * projection_fraction(sector)


def tangent_norm_sq(sector: str, rho_ch: int | Fraction) -> Fraction:
    dq, dj = EXPECTED_TANGENTS[sector]
    return charged_norm_N(dq, dj, rho_ch)


def kappa(sector: str, rho_ch: int | Fraction) -> Fraction:
    return g_ch() / tangent_norm_sq(sector, rho_ch)


def bridge_values(
    sector: str,
    rho_ch: int | Fraction,
    bridge_rule: str = DEFAULT_DIAGNOSTIC_BRIDGE_RULE,
) -> Tuple[Fraction, Fraction]:
    if bridge_rule == BRIDGE_RULE_DIAGONAL_ONLY:
        return Fraction(0), Fraction(0)
    if bridge_rule == BRIDGE_RULE_MINIMAL_ANSATZ:
        return beta(sector), kappa(sector, rho_ch)
    if bridge_rule == BRIDGE_RULE_SYMBOLIC_OPEN:
        raise ValueError("symbolic-open bridge rule has topology but no numeric beta/kappa")
    raise ValueError(f"unknown bridge rule: {bridge_rule}")


def minimal_K_f(sector: str, rho_ch: int | Fraction) -> Tuple[Tuple[Fraction, Fraction, Fraction], ...]:
    costs = diagonal_costs(sector, rho_ch)
    lam0, lam1, lam2 = tuple(eta(sector) * cost for cost in costs)
    b, k = bridge_values(sector, rho_ch, DEFAULT_DIAGNOSTIC_BRIDGE_RULE)
    return (
        (lam0, b, Fraction(0)),
        (b, lam1, k),
        (Fraction(0), k, lam2),
    )


def minimal_K_f_for_rule(
    sector: str,
    rho_ch: int | Fraction,
    rule: str = DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE,
    bridge_rule: str = DEFAULT_DIAGNOSTIC_BRIDGE_RULE,
) -> Tuple[Tuple[Fraction, Fraction, Fraction], ...]:
    costs = diagonal_costs(sector, rho_ch)
    lam0, lam1, lam2 = tuple(eta_for_rule(sector, rule) * cost for cost in costs)
    b, k = bridge_values(sector, rho_ch, bridge_rule)
    return (
        (lam0, b, Fraction(0)),
        (b, lam1, k),
        (Fraction(0), k, lam2),
    )


def threshold_insertions() -> List[Dict[str, object]]:
    return [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "value": "ln 2",
            "source": "Z_virt^{u,2}=1/2 weak-double projection bridge",
            "operator_level": True,
        }
    ]


def dressed_K_u(rho_ch: int | Fraction) -> Tuple[Tuple[float, float, float], ...]:
    matrix = [[float(value) for value in row] for row in minimal_K_f("up", rho_ch)]
    insertion = threshold_insertions()[0]
    matrix[int(insertion["slot"])][int(insertion["slot"])] += log(2.0)
    return tuple(tuple(row) for row in matrix)


def dressed_K_u_for_rule(
    rho_ch: int | Fraction,
    rule: str = DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE,
) -> Tuple[Tuple[float, float, float], ...]:
    matrix = [[float(value) for value in row] for row in minimal_K_f_for_rule("up", rho_ch, rule)]
    insertion = threshold_insertions()[0]
    matrix[int(insertion["slot"])][int(insertion["slot"])] += log(2.0)
    return tuple(tuple(row) for row in matrix)


def eigenvalues(matrix: Tuple[Tuple[Fraction | float, ...], ...]) -> Tuple[float, ...]:
    values = np.linalg.eigvalsh(np.array([[float(value) for value in row] for row in matrix]))
    return tuple(float(value) for value in values)


def gaps_from_ground(matrix: Tuple[Tuple[Fraction | float, ...], ...]) -> Tuple[float, ...]:
    values = eigenvalues(matrix)
    ground = values[0]
    return tuple(value - ground for value in values)


def branch_report(sector: str, rho_ch: int) -> MatrixBranchReport:
    matrix = minimal_K_f(sector, rho_ch)
    return MatrixBranchReport(
        sector=sector,
        rho_ch=rho_ch,
        ledger=LEDGERS[sector],
        diagonal_costs=diagonal_costs(sector, rho_ch),
        eta=eta(sector),
        beta=beta(sector),
        kappa=kappa(sector, rho_ch),
        matrix=matrix,
        eigenvalues=eigenvalues(matrix),
        gaps_from_ground=gaps_from_ground(matrix),
    )


def all_branch_reports() -> Dict[int, Dict[str, MatrixBranchReport]]:
    return {
        rho: {sector: branch_report(sector, rho) for sector in CHARGED_SECTORS}
        for rho in RHO_CH_BRANCHES
    }


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix_to_strings(matrix: Tuple[Tuple[Fraction, Fraction, Fraction], ...]) -> List[List[str]]:
    return [[fraction_string(value) for value in row] for row in matrix]


def report_as_dict() -> Dict[str, object]:
    sectors = [asdict(row) for row in sector_rows()]
    for row in sectors:
        for key in ("P_C", "P_plus", "P_minus", "P_d", "A", "tau", "T"):
            row[key] = fraction_string(row[key])

    branch_rows = []
    for rho, reports in all_branch_reports().items():
        for sector, report in reports.items():
            branch_rows.append(
                {
                    "rho_ch": rho,
                    "sector": sector,
                    "ledger": [list(mode) for mode in report.ledger],
                    "diagonal_costs": [fraction_string(value) for value in report.diagonal_costs],
                    "eta": fraction_string(report.eta),
                    "beta": fraction_string(report.beta),
                    "kappa": fraction_string(report.kappa),
                    "matrix": matrix_to_strings(report.matrix),
                    "eigenvalues": list(report.eigenvalues),
                    "gaps_from_ground": list(report.gaps_from_ground),
                }
            )

    dressed_rows = []
    for rho in RHO_CH_BRANCHES:
        matrix = dressed_K_u(rho)
        dressed_rows.append(
            {
                "rho_ch": rho,
                "sector": "up",
                "threshold_insertions": threshold_insertions(),
                "matrix": [list(row) for row in matrix],
                "eigenvalues": list(eigenvalues(matrix)),
                "gaps_from_ground": list(gaps_from_ground(matrix)),
            }
        )

    return {
        "id": "PO-BH-freeze-protocol-charged-Kf-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "statuses": STATUS_TABLE,
        "sectors": sectors,
        "ledgers": {key: [list(mode) for mode in value] for key, value in LEDGERS.items()},
        "rho_ch_branches": list(RHO_CH_BRANCHES),
        "charged_suppression": {
            "g_ch": fraction_string(g_ch()),
            "Pi_l": fraction_string(PI["lepton"]),
            "Pi_u": fraction_string(PI["up"]),
            "Pi_d": fraction_string(PI["down"]),
            "S_l": fraction_string(self_screening("lepton")),
            "S_u": fraction_string(self_screening("up")),
            "S_d": fraction_string(self_screening("down")),
            "eta_l": fraction_string(eta("lepton")),
            "eta_u": fraction_string(eta("up")),
            "eta_d": fraction_string(eta("down")),
        },
        "branch_reports": branch_rows,
        "up_threshold_reports": dressed_rows,
        "threshold_insertions": threshold_insertions(),
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "claim_boundary": (
            "Candidate freeze/readout machinery only; no empirical comparison input, "
            "frozen prediction change, official prediction change, or numerical closure."
        ),
    }
