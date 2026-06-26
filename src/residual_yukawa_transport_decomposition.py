from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import same_sector_rg_gauge_cancellation as gauge


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

IDENTITY_CANCELLATION_STATUS = (
    "DERIVED_CONDITIONAL_ON_SHARED_SECTOR_BRANCH_SPACE"
)
DECOMPOSITION_STATUS = "PARTIALLY_LOCALIZED"
K_F_CANDIDATE_STATUS = "STRUCTURALLY_MOTIVATED_CANDIDATE"
K_F_COEFFICIENT_STATUS = "OPEN_LOCALIZABLE"
BRANCH_DIFFERENTIAL_OPEN = "OPEN_LOCALIZABLE"
SECTOR_UNIVERSAL_CANCELED = "CANCELED_BY_SAME_SECTOR_BRANCH_SPACE"
SECTOR_UNIVERSAL_NOT_APPLICABLE = "NOT_APPLICABLE"
RESIDUAL_STAGE = "RG_TRANSPORT_RESIDUAL_LOCALIZED"

FORBIDDEN_DERIVATION_INPUTS = (
    "observed charged masses",
    "observed neutrino masses",
    "neutrino mass splittings",
    "CKM data",
    "PMNS data",
    "measured fine-structure alpha",
    "measured gauge couplings",
    "measured Yukawa couplings",
    "empirical target ratios",
)


@dataclass(frozen=True)
class ResidualTransportDecomposition:
    sector: str
    operator: str
    gauge_identity_component: str
    sector_universal_residual_component: str
    traceless_branch_differential_component: str
    decomposition: str


@dataclass(frozen=True)
class BranchSpaceIdentityCancellation:
    sector: str
    identity_operator: str
    status: str
    cancellation_statement: str


@dataclass(frozen=True)
class TracelessResidualOperator:
    sector: str
    operator_id: str
    trace_condition: str
    status: str
    remaining_obstruction: str


@dataclass(frozen=True)
class SameSectorResidualTransportRecord:
    ratio_id: str
    sector: str
    branch_pair: Tuple[str, str]
    same_sector: bool
    gauge_component: str
    sector_universal_residual_component: str
    branch_differential_residual_component: str
    transport_stage: str
    comparison_ready: bool
    status: str
    notes: str


@dataclass(frozen=True)
class CrossSectorResidualTransportRecord:
    ratio_id: str
    sectors: Tuple[str, str]
    same_sector: bool
    same_sector_identity_cancellation: str
    comparison_ready: bool
    status: str


@dataclass(frozen=True)
class KfAlignedResidualCandidate:
    candidate_id: str
    formula: str
    status: str
    coefficient_status: str
    uses_empirical_inputs: bool
    notes: str


@dataclass(frozen=True)
class ResidualTransportVerdict:
    theorem_id: str
    same_sector_residual_identity_cancellation: str
    residual_Yukawa_transport_decomposition: str
    charged_branch_differential_residual_transport: str
    Kf_aligned_residual_transport_candidate: str
    Kf_residual_transport_coefficient: str
    applies_to: Tuple[str, ...]
    does_not_apply_to: Tuple[str, ...]
    theorem_complete: bool
    public_status: str


def residual_decomposition(sector: str) -> ResidualTransportDecomposition:
    if sector not in gauge.SECTOR_REPRESENTATION_IDS:
        raise ValueError(f"unknown sector: {sector}")
    return ResidualTransportDecomposition(
        sector=sector,
        operator=f"Gamma_{sector}",
        gauge_identity_component=f"gamma_gauge,{sector} I_{sector}",
        sector_universal_residual_component=f"gamma_universal,{sector} I_{sector}",
        traceless_branch_differential_component=f"tilde_Gamma_{sector}",
        decomposition=(
            f"Gamma_{sector} = gamma_gauge,{sector} I_{sector} + "
            f"gamma_universal,{sector} I_{sector} + tilde_Gamma_{sector}"
        ),
    )


def identity_cancellation(sector: str) -> BranchSpaceIdentityCancellation:
    if sector not in gauge.SECTOR_REPRESENTATION_IDS:
        raise ValueError(f"unknown sector: {sector}")
    return BranchSpaceIdentityCancellation(
        sector=sector,
        identity_operator=f"I_{sector}",
        status=IDENTITY_CANCELLATION_STATUS,
        cancellation_statement=(
            f"<a|I_{sector}|a> - <b|I_{sector}|b> = 0 for normalized "
            "branches in the shared same-sector branch space"
        ),
    )


def traceless_residual_operator(sector: str) -> TracelessResidualOperator:
    if sector not in gauge.SECTOR_REPRESENTATION_IDS:
        raise ValueError(f"unknown sector: {sector}")
    return TracelessResidualOperator(
        sector=sector,
        operator_id=f"tilde_Gamma_{sector}",
        trace_condition=f"Tr(tilde_Gamma_{sector}) = 0",
        status=BRANCH_DIFFERENTIAL_OPEN,
        remaining_obstruction=(
            "branch-differential residual transport operator not action-derived"
        ),
    )


def classify_same_sector_record(
    record: gauge.RGGaugeCancellationRecord,
) -> SameSectorResidualTransportRecord:
    if not record.same_sector:
        raise ValueError("same-sector residual record requires same_sector=True")
    return SameSectorResidualTransportRecord(
        ratio_id=record.ratio_id,
        sector=record.numerator_sector,
        branch_pair=(record.numerator, record.denominator),
        same_sector=True,
        gauge_component=record.gauge_transport_component,
        sector_universal_residual_component=SECTOR_UNIVERSAL_CANCELED,
        branch_differential_residual_component=BRANCH_DIFFERENTIAL_OPEN,
        transport_stage=RESIDUAL_STAGE,
        comparison_ready=False,
        status=IDENTITY_CANCELLATION_STATUS,
        notes=(
            "Gauge and sector-universal identity components cancel; remaining "
            "transport is the traceless branch-differential residual operator."
        ),
    )


def charged_same_sector_records() -> Tuple[SameSectorResidualTransportRecord, ...]:
    return tuple(
        classify_same_sector_record(record)
        for record in gauge.charged_same_sector_records()
    )


def cross_sector_records() -> Tuple[CrossSectorResidualTransportRecord, ...]:
    return tuple(
        CrossSectorResidualTransportRecord(
            ratio_id=record.ratio_id,
            sectors=(record.numerator_sector, record.denominator_sector),
            same_sector=False,
            same_sector_identity_cancellation=SECTOR_UNIVERSAL_NOT_APPLICABLE,
            comparison_ready=False,
            status="CROSS_SECTOR_OPEN",
        )
        for record in gauge.cross_sector_records()
    )


def kf_aligned_residual_candidate() -> KfAlignedResidualCandidate:
    return KfAlignedResidualCandidate(
        candidate_id="Kf_aligned_residual_transport_candidate",
        formula="tilde_Gamma_f proportional_to K_f - (Tr K_f / 3) I_f",
        status=K_F_CANDIDATE_STATUS,
        coefficient_status=K_F_COEFFICIENT_STATUS,
        uses_empirical_inputs=False,
        notes=(
            "Structural candidate only: the proportionality/source coefficient "
            "is not derived and no numerical prediction is emitted."
        ),
    )


def residual_blockers() -> Tuple[str, ...]:
    return (
        "action source for tilde_Gamma_f",
        "K_f residual transport coefficient",
        "threshold matching",
        "scheme alignment",
        "common-scale comparison",
    )


def theorem_verdict() -> ResidualTransportVerdict:
    return ResidualTransportVerdict(
        theorem_id="residual_Yukawa_transport_decomposition",
        same_sector_residual_identity_cancellation=IDENTITY_CANCELLATION_STATUS,
        residual_Yukawa_transport_decomposition=DECOMPOSITION_STATUS,
        charged_branch_differential_residual_transport=BRANCH_DIFFERENTIAL_OPEN,
        Kf_aligned_residual_transport_candidate=K_F_CANDIDATE_STATUS,
        Kf_residual_transport_coefficient=K_F_COEFFICIENT_STATUS,
        applies_to=tuple(record.ratio_id for record in charged_same_sector_records()),
        does_not_apply_to=tuple(record.ratio_id for record in cross_sector_records()),
        theorem_complete=False,
        public_status=PUBLIC_STATUS,
    )


def _rows(rows):
    return [asdict(row) for row in rows]


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-residual-yukawa-transport-decomposition-v1",
        "title": "Residual Yukawa Transport Decomposition Theorem v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "theorem_statement": (
            "For same-sector branches, gauge and sector-universal identity "
            "components cancel; the remaining transport is the traceless "
            "branch-differential residual operator."
        ),
        "assumptions": [
            "Both branches are in the same BHSM sector.",
            "Same-sector branches share a normalized branch space.",
            "Only identity-sector residual components are canceled.",
            "The traceless residual operator is not yet action-derived.",
        ],
        "anomalous_dimension_decompositions": _rows(
            residual_decomposition(sector)
            for sector in ("charged_lepton", "up", "down")
        ),
        "identity_cancellations": _rows(
            identity_cancellation(sector)
            for sector in ("charged_lepton", "up", "down")
        ),
        "traceless_residual_operators": _rows(
            traceless_residual_operator(sector)
            for sector in ("charged_lepton", "up", "down")
        ),
        "same_sector_ratio_classifications": _rows(charged_same_sector_records()),
        "cross_sector_diagnostic_classifications": _rows(cross_sector_records()),
        "Kf_aligned_residual_candidate": asdict(kf_aligned_residual_candidate()),
        "residual_blockers": list(residual_blockers()),
        "status_verdict": asdict(theorem_verdict()),
        "claim_boundary": (
            "Residual identity cancellation is conditional; the traceless "
            "branch-differential residual operator, scheme alignment, and "
            "numerical closure remain open."
        ),
    }
