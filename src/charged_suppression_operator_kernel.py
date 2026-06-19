from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

CHARGED_SECTORS: Tuple[str, str, str] = ("lepton", "up", "down")

INCIDENCE_RANKS: Dict[str, int] = {
    "lepton": 3,
    "up": 6,
    "down": 12,
}

SELF_SCREENING_COUNTS: Dict[str, int] = {
    "lepton": 1,
    "up": 2,
    "down": 4,
}

STATUS_TABLE = {
    "B_supp_universal_suppression_operator": "DERIVED_CONDITIONAL_ON_TRACE_NORMALIZED_KERNEL",
    "B_supp_trace_normalization": "DERIVED_CONDITIONAL_ON_TRACE_NORMALIZED_KERNEL",
    "Pi_f_incidence_projection_fractions": "DERIVED_CONDITIONAL_FROM_B_SUPP_TRACE",
    "chi_f_incidence_self_screening_counts": "DERIVED_CONDITIONAL_ON_INCIDENCE_KERNEL",
    "charged_suppression_single_operator_trace_rule": "DERIVED_CONDITIONAL_ON_B_SUPP_KERNEL",
    "charged_suppression_double_normalized_rule": (
        "STRONGLY_SUPPORTED_CANDIDATE_REQUIRES_INDEPENDENT_PHASE_COUPLING"
    ),
    "charged_suppression_local_sector_rule": "STRUCTURALLY_POSSIBLE_NOT_SELECTED",
    "g_ch_independent_phase_response": "OPEN_LOCALIZABLE",
    "charged_suppression_eta_values": "RULE_A_DERIVED_CONDITIONAL_RULE_B_CANDIDATE",
    "minimal_charged_Kf_generator_eta_dependency": "NOT_OVERWRITTEN_REQUIRES_EXPLICIT_RULE_SELECTION",
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
class SectorSuppressionRow:
    sector: str
    rank: int
    projector_trace: Fraction
    diagonal_weight: Fraction
    sector_trace: Fraction
    chi: int
    self_screening: Fraction
    eta_single_trace: Fraction
    eta_double_normalized: Fraction
    eta_local_normalized: Fraction


@dataclass(frozen=True)
class ContractionRule:
    rule_id: str
    formula: str
    status: str
    selected_by_kernel: bool
    requires_independent_phase_coupling: bool
    eta_values: Dict[str, Fraction]
    notes: Tuple[str, ...]


def validate_sector(sector: str) -> None:
    if sector not in CHARGED_SECTORS:
        raise ValueError(f"sector must be one of {CHARGED_SECTORS}")


def total_charged_rank() -> int:
    return sum(INCIDENCE_RANKS.values())


def diagonal_incidence_weight() -> Fraction:
    return Fraction(1, total_charged_rank())


def B_supp_trace() -> Fraction:
    return Fraction(total_charged_rank(), total_charged_rank())


def B_supp_diagonal_weights() -> Tuple[Fraction, ...]:
    return tuple(diagonal_incidence_weight() for _ in range(total_charged_rank()))


def sector_rank(sector: str) -> int:
    validate_sector(sector)
    return INCIDENCE_RANKS[sector]


def sector_trace_contraction(sector: str) -> Fraction:
    return Fraction(sector_rank(sector), total_charged_rank())


def self_screening_count(sector: str) -> int:
    validate_sector(sector)
    return SELF_SCREENING_COUNTS[sector]


def single_operator_g_eff() -> Fraction:
    return diagonal_incidence_weight()


def self_screening_factor(sector: str) -> Fraction:
    return 1 - self_screening_count(sector) * single_operator_g_eff()


def eta_single_trace(sector: str) -> Fraction:
    return sector_trace_contraction(sector) * self_screening_factor(sector)


def independent_phase_response_candidate() -> Fraction:
    return Fraction(1, total_charged_rank())


def eta_double_normalized(sector: str) -> Fraction:
    return (
        sector_trace_contraction(sector)
        * independent_phase_response_candidate()
        * self_screening_factor(sector)
    )


def eta_local_normalized(sector: str) -> Fraction:
    return independent_phase_response_candidate() * self_screening_factor(sector)


def sector_row(sector: str) -> SectorSuppressionRow:
    return SectorSuppressionRow(
        sector=sector,
        rank=sector_rank(sector),
        projector_trace=Fraction(sector_rank(sector), 1),
        diagonal_weight=diagonal_incidence_weight(),
        sector_trace=sector_trace_contraction(sector),
        chi=self_screening_count(sector),
        self_screening=self_screening_factor(sector),
        eta_single_trace=eta_single_trace(sector),
        eta_double_normalized=eta_double_normalized(sector),
        eta_local_normalized=eta_local_normalized(sector),
    )


def sector_rows() -> Tuple[SectorSuppressionRow, ...]:
    return tuple(sector_row(sector) for sector in CHARGED_SECTORS)


def contraction_rules() -> Dict[str, ContractionRule]:
    rule_a = {
        sector: eta_single_trace(sector) for sector in CHARGED_SECTORS
    }
    rule_b = {
        sector: eta_double_normalized(sector) for sector in CHARGED_SECTORS
    }
    rule_c = {
        sector: eta_local_normalized(sector) for sector in CHARGED_SECTORS
    }
    return {
        "RULE_A_SINGLE_OPERATOR_TRACE": ContractionRule(
            rule_id="RULE_A_SINGLE_OPERATOR_TRACE",
            formula="eta_f = Tr(P_f B_supp) * S_f",
            status=STATUS_TABLE["charged_suppression_single_operator_trace_rule"],
            selected_by_kernel=True,
            requires_independent_phase_coupling=False,
            eta_values=rule_a,
            notes=(
                "Direct contraction of the trace-normalized B_supp=I_ch/R_ch kernel.",
                "No separate primitive phase-response coupling is inserted.",
            ),
        ),
        "RULE_B_DOUBLE_NORMALIZED": ContractionRule(
            rule_id="RULE_B_DOUBLE_NORMALIZED",
            formula="eta_f = Tr(P_f B_supp) * g_ch * S_f",
            status=STATUS_TABLE["charged_suppression_double_normalized_rule"],
            selected_by_kernel=False,
            requires_independent_phase_coupling=True,
            eta_values=rule_b,
            notes=(
                "Retains the older eta package as a candidate only.",
                "Promotion requires an independently derived phase-response operator.",
            ),
        ),
        "RULE_C_LOCAL_SECTOR_NORMALIZATION": ContractionRule(
            rule_id="RULE_C_LOCAL_SECTOR_NORMALIZATION",
            formula="eta_f = g_ch * S_f with local Pi_f=1",
            status=STATUS_TABLE["charged_suppression_local_sector_rule"],
            selected_by_kernel=False,
            requires_independent_phase_coupling=True,
            eta_values=rule_c,
            notes=(
                "Structurally possible local-sector normalization.",
                "Not selected by the global trace-normalized E_ch kernel.",
            ),
        ),
    }


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
    return value


def report_as_dict() -> Dict[str, object]:
    rows = []
    for row in sector_rows():
        item = asdict(row)
        rows.append({key: _convert(value) for key, value in item.items()})

    rule_rows = {}
    for rule_id, rule in contraction_rules().items():
        item = asdict(rule)
        rule_rows[rule_id] = {key: _convert(value) for key, value in item.items()}

    return {
        "id": "PO-BH-charged-suppression-operator-kernel-v1",
        "title": "Charged Suppression Operator and Phase-Response Kernel v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "incidence_ranks": dict(INCIDENCE_RANKS),
        "total_charged_rank": total_charged_rank(),
        "B_supp": {
            "definition": "I_ch / R_ch",
            "R_ch": total_charged_rank(),
            "diagonal_weight": fraction_string(diagonal_incidence_weight()),
            "trace": fraction_string(B_supp_trace()),
            "normalization_status": STATUS_TABLE["B_supp_trace_normalization"],
        },
        "sector_rows": rows,
        "contraction_rules": rule_rows,
        "statuses": STATUS_TABLE,
        "selected_kernel_rule": "RULE_A_SINGLE_OPERATOR_TRACE",
        "older_eta_package_status": (
            "DOUBLE_NORMALIZED_CANDIDATE_REQUIRES_INDEPENDENT_PHASE_COUPLING"
        ),
        "minimal_charged_Kf_generator_overwritten": False,
        "final_scientific_interpretation": (
            "The trace-normalized B_supp kernel directly derives the single-operator "
            "trace contraction. The older double-normalized eta package remains a "
            "candidate unless an independent phase-response coupling is derived."
        ),
        "claim_boundary": (
            "B_supp trace normalization is a conditional structural kernel result; "
            "numerical closure and official predictions remain unchanged."
        ),
    }
