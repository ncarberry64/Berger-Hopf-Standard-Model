from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Iterable, List, Tuple


SECTORS: Dict[str, Tuple[int, int]] = {
    "neutrino": (0, +1),
    "lepton": (0, -1),
    "up": (1, +1),
    "down": (1, -1),
}

EXPECTED_OMEGA = {
    "neutrino": "-q - 2j",
    "lepton": "-q + 2j",
    "up": "q - 2j",
    "down": "q + 4j",
}

TARGET_AMPLITUDES = {
    "neutrino": 3,
    "lepton": 3,
    "up": 6,
    "down": 12,
}

CHARGED_LEDGER: Dict[str, List[Tuple[int, int]]] = {
    "lepton": [(0, 0), (1, 2), (3, 3)],
    "up": [(0, 0), (6, 0), (8, 1)],
    "down": [(0, 0), (0, 3), (4, 2)],
}

ISOTROPIC_COSTS = {
    "lepton": [0, 5, 18],
    "up": [0, 36, 65],
    "down": [0, 9, 20],
}

CYCLIC_ANISOTROPY_COSTS = {
    "lepton": [0, 13, 36],
    "up": [0, 36, 67],
    "down": [0, 27, 28],
}


@dataclass(frozen=True)
class SectorProjectors:
    sector: str
    C: int
    sigma: int
    P_nu: Fraction
    P_l: Fraction
    P_u: Fraction
    P_d: Fraction
    M: Fraction


def validate_sector_labels(C: int, sigma: int) -> None:
    if C not in (0, 1):
        raise ValueError("C must be 0 or 1")
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or +1")


def sector_projectors(C: int, sigma: int, sector: str = "") -> SectorProjectors:
    validate_sector_labels(C, sigma)
    P_nu = Fraction((1 - C) * (1 + sigma), 2)
    P_l = Fraction((1 - C) * (1 - sigma), 2)
    P_u = Fraction(C * (1 + sigma), 2)
    P_d = Fraction(C * (1 - sigma), 2)
    return SectorProjectors(
        sector=sector,
        C=C,
        sigma=sigma,
        P_nu=P_nu,
        P_l=P_l,
        P_u=P_u,
        P_d=P_d,
        M=1 + P_d,
    )


def down_sector_incidence(C: int, sigma: int) -> Fraction:
    return sector_projectors(C, sigma).M


def omega_coefficients(C: int, sigma: int) -> Tuple[int, int]:
    validate_sector_labels(C, sigma)
    fiber_q = 2 * C - 1
    base_j = -2 * sigma * int(1 + Fraction(C * (1 - sigma), 2))
    return fiber_q, base_j


def omega_value(C: int, sigma: int, q: int, j: int) -> int:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    return q_coeff * q + j_coeff * j


def omega_expression(C: int, sigma: int) -> str:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    q_part = "q" if q_coeff == 1 else "-q"
    if j_coeff == 0:
        return q_part
    sign = "+" if j_coeff > 0 else "-"
    mag = abs(j_coeff)
    return f"{q_part} {sign} {mag}j"


def target_amplitude(C: int, sigma: int) -> int:
    validate_sector_labels(C, sigma)
    return int(3 * (2**C) * (1 + Fraction(C * (1 - sigma), 2)))


def charged_hessian_cost(q: int, j: int, rho_ch: Fraction | int | float) -> Fraction | float:
    if isinstance(rho_ch, Fraction):
        return q * q + rho_ch * j * j
    return q * q + rho_ch * j * j


def ledger_costs(sector: str, rho_ch: Fraction | int | float) -> List[Fraction | float]:
    return [charged_hessian_cost(q, j, rho_ch) for q, j in CHARGED_LEDGER[sector]]


def ledger_order_preserved(sector: str, rho_ch: Fraction | int | float) -> bool:
    costs = ledger_costs(sector, rho_ch)
    return all(left < right for left, right in zip(costs, costs[1:]))


def all_charged_ledgers_preserved(rho_ch: Fraction | int | float) -> bool:
    return all(ledger_order_preserved(sector, rho_ch) for sector in CHARGED_LEDGER)


def down_ordering_constraint_holds(rho_ch: Fraction | int | float) -> bool:
    return 0 < rho_ch < Fraction(16, 5)


def membership_constraint_holds(rho_ch: Fraction | int | float) -> bool:
    return 0 < rho_ch < 8


def audit_statuses() -> Dict[str, str]:
    return {
        "unified_Omega_projector_formula": "STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE",
        "base_cyclic_factor_3": "STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE",
        "color_factor_2_power_C": "STRUCTURALLY_MOTIVATED_CANDIDATE",
        "down_multiplicity_M": "STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE",
        "sector_target_amplitude_A": "STRUCTURALLY_MOTIVATED_CANDIDATE",
        "three_state_ladder_structure": "STRONGLY_SUPPORTED_CANDIDATE",
        "charged_cross_term_s_ch": "FORBIDDEN_CONDITIONAL",
        "neutral_cross_term_s_neutral": "OPEN_ALLOWED",
        "neutral_topographic_metric_mixing": "OPEN_LOCALIZABLE",
        "charged_Hessian_anisotropy_rho_ch": "OPEN_LOCALIZABLE",
        "isotropic_metric_rho_1": "MINIMAL_ISOTROPIC_CANDIDATE",
        "cyclic_anisotropy_rho_3": "CYCLIC_ANISOTROPY_CANDIDATE",
        "exact_old_costs_0_5_18_etc": "CONDITIONAL_ON_RHO_CH_EQUALS_1",
        "cyclic_candidate_costs_0_13_36_etc": "CONDITIONAL_ON_RHO_CH_EQUALS_3",
        "eta_l_8_over_9_trace_route": "DOWNGRADED_NUMERICAL_COINCIDENCE",
        "eta_l_projection_structure": "VALIDATED_CANDIDATE",
        "Pi_l_value": "OPEN_LOCALIZABLE",
        "alpha_geom_internal_derivation": "OPEN_LOCALIZABLE",
        "eta_l_self_screening_factor": "STRUCTURALLY_SUPPORTED_CANDIDATE",
        "eta_l_exact_value": "OPEN",
        "eta_l_fit": "FORBIDDEN_AS_DERIVATION",
        "Z_virt_u2_dimension_ratio": "STRONG_DERIVATION_CANDIDATE",
        "down_extra_boundary_incidence": "STRONGLY_SUPPORTED_CANDIDATE",
    }


def sector_rows() -> Iterable[Tuple[str, int, int]]:
    for sector, (C, sigma) in SECTORS.items():
        yield sector, C, sigma
