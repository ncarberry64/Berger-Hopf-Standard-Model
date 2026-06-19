from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Iterable, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

KAPPA_3 = 3

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

EXPECTED_TANGENTS: Dict[str, Tuple[int, int]] = {
    "neutrino": (-2, 1),
    "lepton": (2, 1),
    "up": (2, 1),
    "down": (4, -1),
}

SECTOR_EQUATIONS = {
    "neutrino": "-q - 2j = -3, equivalently q + 2j = 3",
    "lepton": "-q + 2j = 3",
    "up": "q - 2j = 6",
    "down": "q + 4j = 12",
}

STATUS_TABLE = {
    "Boundary_Graded_Defect_Action_Kernel_v1": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "Boundary_Graded_Defect_Theorem": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "D_C_colored_contact_defect": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "D_d_color_lower_overlap_contact_defect": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "Gamma_sigma_weak_orientation_grading": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "Gamma_T_target_orientation_trace": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "E3_universal_rank_three_closure": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "EA_incidence_module_factorization": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "Delta_IT_index_trace_defect": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "S_index_trace_constraint": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "unified_Omega_projector_formula": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "sector_target_incidence_product_A": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "orientation_trace_Gamma_T": "DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL",
    "zero_defect_tangent_adjacency": "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
    "charged_Hessian_from_S_index_trace": "INVALIDATED_DO_NOT_CLAIM",
    "B_supp_universal_suppression_operator": "OPEN_LOCALIZABLE",
    "g_ch_phase_normalized_coupling": "STRONGLY_SUPPORTED_CANDIDATE",
    "rho_ch_exact_value": "OPEN_LOCALIZABLE",
    "full_threshold_operator": "OPEN",
    "RG_transport": "OPEN",
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


@dataclass(frozen=True)
class SectorLabel:
    sector: str
    C: int
    sigma: int


@dataclass(frozen=True)
class ProjectorReadouts:
    C: int
    sigma: int
    P_C: Fraction
    P_plus: Fraction
    P_minus: Fraction
    P_d_overlap: Fraction
    P_nu: Fraction
    P_l: Fraction
    P_u: Fraction
    P_d_sector: Fraction


@dataclass(frozen=True)
class DefectReadout:
    name: str
    activator: Fraction | int
    rank_readout: Fraction
    orientation_readout: Fraction | None
    hopf_multiplier: Fraction | None
    role: str
    status: str


@dataclass(frozen=True)
class IncidenceModule:
    sector: str
    rank_E3: Fraction
    rank_EC: Fraction
    rank_Ed: Fraction
    A: Fraction
    factorization: str
    status: str


@dataclass(frozen=True)
class KernelStatusRecord:
    claim_id: str
    status: str
    evidence_summary: str
    blocking_missing_source: str


@dataclass(frozen=True)
class BoundaryGradedDefectKernel:
    sector: str
    label: SectorLabel
    projectors: ProjectorReadouts
    D_C: DefectReadout
    D_d: DefectReadout
    Gamma_sigma: DefectReadout
    Gamma_T_tau: Fraction
    incidence_module: IncidenceModule
    omega_expression: str
    sector_equation: str
    T: Fraction
    ledger: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]
    tangent: Tuple[int, int]
    status: str


def validate_sector_labels(C: int, sigma: int) -> None:
    if C not in (0, 1):
        raise ValueError("C must be 0 or 1")
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or +1")


def sector_labels() -> Tuple[SectorLabel, ...]:
    return tuple(SectorLabel(sector, C, sigma) for sector, (C, sigma) in SECTORS.items())


def label_for_sector(sector: str) -> SectorLabel:
    C, sigma = SECTORS[sector]
    return SectorLabel(sector, C, sigma)


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


def P_d_overlap(C: int, sigma: int) -> Fraction:
    validate_sector_labels(C, sigma)
    return P_C(C) * P_minus(sigma)


def projectors(C: int, sigma: int) -> ProjectorReadouts:
    validate_sector_labels(C, sigma)
    p_c = P_C(C)
    p_plus = P_plus(sigma)
    p_minus = P_minus(sigma)
    p_d = P_d_overlap(C, sigma)
    return ProjectorReadouts(
        C=C,
        sigma=sigma,
        P_C=p_c,
        P_plus=p_plus,
        P_minus=p_minus,
        P_d_overlap=p_d,
        P_nu=(1 - p_c) * p_plus,
        P_l=(1 - p_c) * p_minus,
        P_u=p_c * p_plus,
        P_d_sector=p_c * p_minus,
    )


def D_C_readout(C: int, sigma: int) -> DefectReadout:
    validate_sector_labels(C, sigma)
    p_c = P_C(C)
    return DefectReadout(
        name="D_C",
        activator=p_c,
        rank_readout=1 + p_c,
        orientation_readout=2 * p_c - 1,
        hopf_multiplier=None,
        role="colored-channel contact defect: quark target doubling and q-orientation flip",
        status=STATUS_TABLE["D_C_colored_contact_defect"],
    )


def D_d_readout(C: int, sigma: int) -> DefectReadout:
    validate_sector_labels(C, sigma)
    p_d = P_d_overlap(C, sigma)
    return DefectReadout(
        name="D_d",
        activator=p_d,
        rank_readout=1 + p_d,
        orientation_readout=None,
        hopf_multiplier=1 + p_d,
        role="color-lower overlap contact defect: down-sector target and Hopf/base multiplier",
        status=STATUS_TABLE["D_d_color_lower_overlap_contact_defect"],
    )


def Gamma_sigma_readout(C: int, sigma: int) -> DefectReadout:
    validate_sector_labels(C, sigma)
    return DefectReadout(
        name="Gamma_sigma",
        activator=sigma,
        rank_readout=Fraction(1, 1),
        orientation_readout=Fraction(-sigma, 1),
        hopf_multiplier=Fraction(-sigma, 1),
        role="weak-orientation grading: Hopf sign and leptonic target sign split",
        status=STATUS_TABLE["Gamma_sigma_weak_orientation_grading"],
    )


def omega_coefficients(C: int, sigma: int) -> Tuple[Fraction, Fraction]:
    d_c = D_C_readout(C, sigma)
    d_d = D_d_readout(C, sigma)
    gamma = Gamma_sigma_readout(C, sigma)
    q_coeff = d_c.orientation_readout
    assert q_coeff is not None
    j_coeff = 2 * gamma.hopf_multiplier * d_d.hopf_multiplier
    assert j_coeff is not None
    return q_coeff, j_coeff


def omega(C: int, sigma: int, q: int, j: int) -> Fraction:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    return q_coeff * q + j_coeff * j


def omega_expression(C: int, sigma: int) -> str:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    q_part = "q" if q_coeff == 1 else "-q"
    sign = "+" if j_coeff > 0 else "-"
    return f"{q_part} {sign} {abs(j_coeff)}j"


def tau(C: int, sigma: int) -> Fraction:
    validate_sector_labels(C, sigma)
    return P_C(C) - (1 - P_C(C)) * sigma


def incidence_module(sector: str) -> IncidenceModule:
    C, sigma = SECTORS[sector]
    d_c = D_C_readout(C, sigma)
    d_d = D_d_readout(C, sigma)
    rank_E3 = Fraction(KAPPA_3, 1)
    rank_EC = d_c.rank_readout
    rank_Ed = d_d.rank_readout
    return IncidenceModule(
        sector=sector,
        rank_E3=rank_E3,
        rank_EC=rank_EC,
        rank_Ed=rank_Ed,
        A=rank_E3 * rank_EC * rank_Ed,
        factorization="E_A(C,sigma)=E3 tensor E_C(C) tensor E_d(C,sigma)",
        status=STATUS_TABLE["EA_incidence_module_factorization"],
    )


def incidence_A(C: int, sigma: int) -> Fraction:
    validate_sector_labels(C, sigma)
    sector = sector_from_labels(C, sigma)
    return incidence_module(sector).A


def target_T(C: int, sigma: int) -> Fraction:
    return tau(C, sigma) * incidence_A(C, sigma)


def delta_IT(C: int, sigma: int, q: int, j: int) -> Fraction:
    return omega(C, sigma, q, j) - target_T(C, sigma)


def S_index_trace(C: int, sigma: int, q: int, j: int, lambda_IT: Fraction | int = 1) -> Fraction:
    return Fraction(lambda_IT) * delta_IT(C, sigma, q, j) ** 2


def S_index_trace_hessian(C: int, sigma: int, lambda_IT: Fraction | int = 1) -> Tuple[Tuple[Fraction, Fraction], Tuple[Fraction, Fraction]]:
    q_coeff, j_coeff = omega_coefficients(C, sigma)
    scale = 2 * Fraction(lambda_IT)
    return (
        (scale * q_coeff * q_coeff, scale * q_coeff * j_coeff),
        (scale * q_coeff * j_coeff, scale * j_coeff * j_coeff),
    )


def S_index_trace_hessian_diagnostic(C: int, sigma: int) -> Dict[str, object]:
    hessian = S_index_trace_hessian(C, sigma)
    off_diagonal = hessian[0][1]
    determinant = hessian[0][0] * hessian[1][1] - hessian[0][1] * hessian[1][0]
    return {
        "hessian": [[fraction_string(value) for value in row] for row in hessian],
        "determinant": fraction_string(determinant),
        "rank": 1 if determinant == 0 and any(value != 0 for row in hessian for value in row) else 0,
        "has_cross_term": off_diagonal != 0,
        "charged_Hessian_from_S_index_trace": STATUS_TABLE["charged_Hessian_from_S_index_trace"],
        "reason": "The Hessian of (Omega-T)^2 is rank-one and generally has qj cross terms; it selects admissible modes but is not the charged hierarchy Hessian.",
    }


def sector_from_labels(C: int, sigma: int) -> str:
    validate_sector_labels(C, sigma)
    for sector, labels in SECTORS.items():
        if labels == (C, sigma):
            return sector
    raise ValueError("unknown sector labels")


def is_reference_slot(mode: Tuple[int, int]) -> bool:
    return mode == (0, 0)


def nonzero_ledger_modes(sector: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return LEDGERS[sector][1:]


def tangent_difference(sector: str) -> Tuple[int, int]:
    first, second = nonzero_ledger_modes(sector)
    return second[0] - first[0], second[1] - first[1]


def build_kernel(sector: str) -> BoundaryGradedDefectKernel:
    label = label_for_sector(sector)
    C, sigma = label.C, label.sigma
    return BoundaryGradedDefectKernel(
        sector=sector,
        label=label,
        projectors=projectors(C, sigma),
        D_C=D_C_readout(C, sigma),
        D_d=D_d_readout(C, sigma),
        Gamma_sigma=Gamma_sigma_readout(C, sigma),
        Gamma_T_tau=tau(C, sigma),
        incidence_module=incidence_module(sector),
        omega_expression=omega_expression(C, sigma),
        sector_equation=SECTOR_EQUATIONS[sector],
        T=target_T(C, sigma),
        ledger=LEDGERS[sector],
        tangent=EXPECTED_TANGENTS[sector],
        status=STATUS_TABLE["Boundary_Graded_Defect_Action_Kernel_v1"],
    )


def build_all_kernels() -> Tuple[BoundaryGradedDefectKernel, ...]:
    return tuple(build_kernel(sector) for sector in SECTORS)


def kernel_status_records() -> Tuple[KernelStatusRecord, ...]:
    blockers = {
        "charged_Hessian_from_S_index_trace": "S_index_trace is rank-one and has cross terms; it is a constraint, not N_ch.",
        "B_supp_universal_suppression_operator": "B_supp action source remains outside this kernel.",
        "g_ch_phase_normalized_coupling": "Phase-response normalization remains outside this kernel.",
        "rho_ch_exact_value": "rho_ch stiffness selection remains outside this kernel.",
        "full_threshold_operator": "Full virtual loop/threshold operator remains outside this kernel.",
        "RG_transport": "RG/scheme transport remains outside this kernel.",
        "numerical_closure": "Numerical closure remains outside this kernel.",
    }
    records = []
    for claim_id, status in STATUS_TABLE.items():
        records.append(
            KernelStatusRecord(
                claim_id=claim_id,
                status=status,
                evidence_summary="Encoded in boundary_graded_defect_action_kernel.py"
                if status.startswith("DERIVED_CONDITIONAL")
                else "Guardrail/open status preserved by the kernel scaffold.",
                blocking_missing_source=blockers.get(
                    claim_id,
                    "Full boundary action derivation remains required before stronger claims.",
                ),
            )
        )
    return tuple(records)


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [_convert(item) for item in value]
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_convert(item) for item in value]
    return value


def kernel_as_dict(kernel: BoundaryGradedDefectKernel) -> Dict[str, object]:
    data = asdict(kernel)
    return _convert(data)


def report_as_dict() -> Dict[str, object]:
    kernels = build_all_kernels()
    return {
        "id": "PO-BH-boundary-graded-defect-action-kernel-v1",
        "title": "Boundary Graded Defect Action Kernel v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "kernels": [kernel_as_dict(kernel) for kernel in kernels],
        "ledgers": {sector: [list(mode) for mode in ledger] for sector, ledger in LEDGERS.items()},
        "tangents": {sector: list(tangent) for sector, tangent in EXPECTED_TANGENTS.items()},
        "statuses": STATUS_TABLE,
        "status_records": [asdict(record) for record in kernel_status_records()],
        "s_index_trace_hessian_diagnostics": {
            sector: S_index_trace_hessian_diagnostic(C, sigma)
            for sector, (C, sigma) in SECTORS.items()
        },
        "claim_boundary": (
            "The sector action kernel is now explicit as a conditional scaffold; "
            "S_index_trace selects admissible modes only, charged Hessian and numerical closure remain open."
        ),
    }
