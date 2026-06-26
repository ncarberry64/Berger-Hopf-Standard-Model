from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

THEOREM_STATUS = "DERIVED_CONDITIONAL_ON_SHARED_SECTOR_REPRESENTATION"
GAUGE_CANCELED = "CANCELED_BY_SAME_SECTOR_THEOREM"
GAUGE_NOT_CANCELED = "NOT_CANCELED_BY_SAME_SECTOR_THEOREM"
RESIDUAL_OPEN = "OPEN_LOCALIZABLE"
COMPARISON_NOT_READY = "COMPARISON_NOT_READY"

FORBIDDEN_DERIVATION_INPUTS = (
    "observed charged masses",
    "observed neutrino masses",
    "neutrino mass splittings",
    "CKM data",
    "PMNS data",
    "measured fine-structure alpha",
    "measured gauge couplings",
    "empirical target ratios",
)


@dataclass(frozen=True)
class AnomalousDimensionDecomposition:
    sector: str
    gauge_component: str
    residual_component: str
    decomposition: str


@dataclass(frozen=True)
class RGGaugeCancellationRecord:
    ratio_id: str
    numerator: str
    denominator: str
    numerator_sector: str
    denominator_sector: str
    same_sector: bool
    shared_sector_representation: bool
    transport_equation: str
    gauge_transport_component: str
    residual_transport: str
    transport_stage: str
    comparison_ready: bool
    status: str
    notes: str


@dataclass(frozen=True)
class SameSectorRatioTransportRecord:
    ratio_id: str
    sector: str
    branch_pair: Tuple[str, str]
    gauge_transport_component: str
    residual_transport: str
    comparison_ready: bool
    status: str


@dataclass(frozen=True)
class CrossSectorTransportRecord:
    ratio_id: str
    sectors: Tuple[str, str]
    gauge_transport_component: str
    comparison_ready: bool
    status: str


@dataclass(frozen=True)
class RGGaugeCancellationVerdict:
    theorem_id: str
    status: str
    applies_to: Tuple[str, ...]
    does_not_apply_to: Tuple[str, ...]
    residual_blockers: Tuple[str, ...]
    theorem_complete: bool
    public_status: str


SECTOR_REPRESENTATION_IDS: Dict[str, str] = {
    "charged_lepton": "BHSM charged lepton sector representation",
    "up": "BHSM up-sector representation",
    "down": "BHSM down-sector representation",
    "neutral": "BHSM neutral-sector representation",
}

CHARGED_SAME_SECTOR_RATIOS: Tuple[Tuple[str, str, str, str], ...] = (
    ("mu_over_tau", "mu", "tau", "charged_lepton"),
    ("e_over_tau", "e", "tau", "charged_lepton"),
    ("c_over_t", "c", "t", "up"),
    ("u_over_t", "u", "t", "up"),
    ("s_over_b", "s", "b", "down"),
    ("d_over_b", "d", "b", "down"),
)

CROSS_SECTOR_DIAGNOSTICS: Tuple[Tuple[str, str, str, str, str], ...] = (
    ("tau_over_t", "tau", "t", "charged_lepton", "up"),
    ("b_over_t", "b", "t", "down", "up"),
    ("nu_over_l", "nu", "ell", "neutral", "charged_lepton"),
)


def anomalous_dimension_decomposition(sector: str) -> AnomalousDimensionDecomposition:
    if sector not in SECTOR_REPRESENTATION_IDS:
        raise ValueError(f"unknown sector: {sector}")
    return AnomalousDimensionDecomposition(
        sector=sector,
        gauge_component=f"gamma_gauge({sector})",
        residual_component=f"gamma_residual,{sector}",
        decomposition=(
            f"gamma_a = gamma_gauge({sector}) + gamma_residual,a; "
            f"gamma_b = gamma_gauge({sector}) + gamma_residual,b"
        ),
    )


def shared_sector_representation(sector_a: str, sector_b: str) -> bool:
    return (
        sector_a == sector_b
        and sector_a in SECTOR_REPRESENTATION_IDS
        and sector_b in SECTOR_REPRESENTATION_IDS
    )


def classify_ratio(
    ratio_id: str,
    numerator: str,
    denominator: str,
    numerator_sector: str,
    denominator_sector: str,
) -> RGGaugeCancellationRecord:
    same_sector = shared_sector_representation(numerator_sector, denominator_sector)
    if same_sector:
        gauge_component = GAUGE_CANCELED
        residual_transport = RESIDUAL_OPEN
        transport_stage = "RG_TRANSPORT_PARTIALLY_LOCALIZED"
        status = THEOREM_STATUS
        notes = (
            "Gauge-universal anomalous-dimension contribution cancels because "
            "both branches share the same BHSM sector representation."
        )
    else:
        gauge_component = GAUGE_NOT_CANCELED
        residual_transport = "OPEN"
        transport_stage = "RG_TRANSPORT_PENDING"
        status = "CROSS_SECTOR_OPEN"
        notes = "Cross-sector ratios are diagnostic only and are not covered by the same-sector theorem."
    return RGGaugeCancellationRecord(
        ratio_id=ratio_id,
        numerator=numerator,
        denominator=denominator,
        numerator_sector=numerator_sector,
        denominator_sector=denominator_sector,
        same_sector=same_sector,
        shared_sector_representation=same_sector,
        transport_equation="d ln(R_ab) / d ln(mu) = gamma_a - gamma_b",
        gauge_transport_component=gauge_component,
        residual_transport=residual_transport,
        transport_stage=transport_stage,
        comparison_ready=False,
        status=status,
        notes=notes,
    )


def charged_same_sector_records() -> Tuple[RGGaugeCancellationRecord, ...]:
    return tuple(
        classify_ratio(ratio_id, numerator, denominator, sector, sector)
        for ratio_id, numerator, denominator, sector in CHARGED_SAME_SECTOR_RATIOS
    )


def cross_sector_records() -> Tuple[RGGaugeCancellationRecord, ...]:
    return tuple(
        classify_ratio(ratio_id, numerator, denominator, sector_a, sector_b)
        for ratio_id, numerator, denominator, sector_a, sector_b in CROSS_SECTOR_DIAGNOSTICS
    )


def same_sector_transport_records() -> Tuple[SameSectorRatioTransportRecord, ...]:
    return tuple(
        SameSectorRatioTransportRecord(
            ratio_id=record.ratio_id,
            sector=record.numerator_sector,
            branch_pair=(record.numerator, record.denominator),
            gauge_transport_component=record.gauge_transport_component,
            residual_transport=record.residual_transport,
            comparison_ready=record.comparison_ready,
            status=record.status,
        )
        for record in charged_same_sector_records()
    )


def cross_sector_transport_records() -> Tuple[CrossSectorTransportRecord, ...]:
    return tuple(
        CrossSectorTransportRecord(
            ratio_id=record.ratio_id,
            sectors=(record.numerator_sector, record.denominator_sector),
            gauge_transport_component=record.gauge_transport_component,
            comparison_ready=record.comparison_ready,
            status=record.status,
        )
        for record in cross_sector_records()
    )


def residual_blockers() -> Tuple[str, ...]:
    return (
        "Yukawa/self transport",
        "threshold matching",
        "scheme alignment",
        "common-scale comparison",
    )


def theorem_verdict() -> RGGaugeCancellationVerdict:
    return RGGaugeCancellationVerdict(
        theorem_id="same_sector_RG_gauge_cancellation",
        status=THEOREM_STATUS,
        applies_to=tuple(record.ratio_id for record in charged_same_sector_records()),
        does_not_apply_to=tuple(record.ratio_id for record in cross_sector_records()),
        residual_blockers=residual_blockers(),
        theorem_complete=False,
        public_status=PUBLIC_STATUS,
    )


def _rows(rows):
    return [asdict(row) for row in rows]


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-same-sector-rg-gauge-cancellation-v1",
        "title": "Same-Sector RG Gauge-Cancellation Theorem v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "theorem_statement": (
            "For two branches in the same BHSM sector, "
            "gamma_gauge(sector_f) cancels in d ln(m_a/m_b)/d ln(mu)."
        ),
        "assumptions": [
            "Both branches are in the same BHSM sector.",
            "Same-sector branches share the same gauge representation.",
            "Only the gauge-universal anomalous-dimension component is being canceled.",
        ],
        "anomalous_dimension_decompositions": _rows(
            anomalous_dimension_decomposition(sector)
            for sector in ("charged_lepton", "up", "down")
        ),
        "charged_ratio_classifications": _rows(charged_same_sector_records()),
        "same_sector_transport_records": _rows(same_sector_transport_records()),
        "cross_sector_diagnostic_classifications": _rows(cross_sector_records()),
        "cross_sector_transport_records": _rows(cross_sector_transport_records()),
        "residual_blockers": list(residual_blockers()),
        "status_verdict": asdict(theorem_verdict()),
        "claim_boundary": (
            "Gauge-universal same-sector transport is conditionally derived; "
            "residual transport, scheme alignment, common-scale comparison, "
            "and numerical closure remain open."
        ),
    }
