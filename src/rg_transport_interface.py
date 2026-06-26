from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import residual_yukawa_transport_decomposition as residual
import same_sector_rg_gauge_cancellation as same_sector


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

TRANSPORT_STAGES = (
    "BARE_MODE_LEDGER",
    "ACTION_KERNEL_SELECTED",
    "SUPPRESSION_DRESSED",
    "BRIDGE_DRESSED",
    "THRESHOLD_DRESSED",
    "RG_TRANSPORT_PENDING",
    "RG_TRANSPORT_PARTIALLY_LOCALIZED",
    "RG_TRANSPORT_RESIDUAL_LOCALIZED",
    "SCHEME_ALIGNED",
    "COMPARISON_READY",
)

STATUS_TABLE = {
    "RG_transport_interface_v1": "STRUCTURAL_SCAFFOLD",
    "same_sector_RG_gauge_cancellation": (
        "DERIVED_CONDITIONAL_ON_SHARED_SECTOR_REPRESENTATION"
    ),
    "charged_same_sector_RG_gauge_transport": "PARTIALLY_LOCALIZED",
    "same_sector_residual_identity_cancellation": (
        "DERIVED_CONDITIONAL_ON_SHARED_SECTOR_BRANCH_SPACE"
    ),
    "residual_Yukawa_transport_decomposition": "PARTIALLY_LOCALIZED",
    "charged_branch_differential_residual_transport": "OPEN_LOCALIZABLE",
    "Kf_aligned_residual_transport_candidate": "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "Kf_residual_transport_coefficient": "OPEN_LOCALIZABLE",
    "charged_RG_transport": "OPEN_LOCALIZABLE",
    "charged_residual_RG_transport": "OPEN_LOCALIZABLE",
    "cross_sector_RG_transport": "OPEN",
    "neutral_RG_transport": "OPEN_LOCALIZABLE",
    "scheme_transport": "OPEN",
    "scheme_alignment": "OPEN",
    "common_scale_comparison": "OPEN",
    "comparison_ready_predictions": "OPEN",
    "numerical_closure": "OPEN",
}

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
class BHSMBareSpectralOutput:
    sector: str
    source_operator: str
    stage: str
    notes: str


@dataclass(frozen=True)
class BHSMThresholdDressedOutput:
    sector: str
    source_operator: str
    stage: str
    threshold_insertions: Tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class SchemeScalePoint:
    scheme: str
    scale: str
    status: str
    notes: str


@dataclass(frozen=True)
class RGTransportRule:
    rule_id: str
    source_stage: str
    target_stage: str
    status: str
    formula: str
    notes: str


@dataclass(frozen=True)
class TransportedObservable:
    sector: str
    observable_family: str
    current_stage: str
    comparison_ready: bool
    blocker: str


@dataclass(frozen=True)
class ComparisonReadinessRecord:
    sector: str
    source_operator: str
    current_readiness: str
    comparison_readiness: str
    known_thresholds: Tuple[str, ...]
    blocker: str
    gauge_component: str
    residual_component: str
    sector_universal_residual_component: str
    branch_differential_residual_component: str


def validate_stage(stage: str) -> None:
    if stage not in TRANSPORT_STAGES:
        raise ValueError(f"unknown transport stage: {stage}")


def bare_spectral_outputs() -> Tuple[BHSMBareSpectralOutput, ...]:
    return (
        BHSMBareSpectralOutput(
            sector="charged_lepton",
            source_operator="charged K_l",
            stage="BRIDGE_DRESSED",
            notes="charged suppression and bridge topology available; RG pending",
        ),
        BHSMBareSpectralOutput(
            sector="up",
            source_operator="charged K_u",
            stage="BRIDGE_DRESSED",
            notes="charged suppression and bridge topology available before threshold insertion",
        ),
        BHSMBareSpectralOutput(
            sector="down",
            source_operator="charged K_d",
            stage="BRIDGE_DRESSED",
            notes="charged suppression and bridge topology available; RG pending",
        ),
        BHSMBareSpectralOutput(
            sector="neutral",
            source_operator="symbolic K_nu",
            stage="ACTION_KERNEL_SELECTED",
            notes="neutral operator is symbolic/candidate only",
        ),
    )


def threshold_dressed_outputs() -> Tuple[BHSMThresholdDressedOutput, ...]:
    return (
        BHSMThresholdDressedOutput(
            sector="charged_lepton",
            source_operator="charged K_l",
            stage="RG_TRANSPORT_PENDING",
            threshold_insertions=(),
            notes="no charged-lepton threshold is derived; transport pending",
        ),
        BHSMThresholdDressedOutput(
            sector="up",
            source_operator="charged K_u",
            stage="RG_TRANSPORT_PENDING",
            threshold_insertions=("up (6,0): ln 2",),
            notes="up sector includes known threshold-dressed middle slot; transport pending",
        ),
        BHSMThresholdDressedOutput(
            sector="down",
            source_operator="charged K_d",
            stage="RG_TRANSPORT_PENDING",
            threshold_insertions=(),
            notes="no down-sector threshold is derived; transport pending",
        ),
        BHSMThresholdDressedOutput(
            sector="neutral",
            source_operator="symbolic K_nu",
            stage="RG_TRANSPORT_PENDING",
            threshold_insertions=(),
            notes="neutral sector remains symbolic/open before transport",
        ),
    )


def scheme_scale_points() -> Tuple[SchemeScalePoint, ...]:
    return (
        SchemeScalePoint(
            scheme="BHSM_internal_operator_units",
            scale="internal",
            status="STRUCTURAL_SOURCE",
            notes="Native BHSM operator-side output.",
        ),
        SchemeScalePoint(
            scheme="transport_target_scheme",
            scale="OPEN",
            status=STATUS_TABLE["scheme_alignment"],
            notes="Target comparison scheme/scale not selected here.",
        ),
    )


def rg_transport_rules() -> Tuple[RGTransportRule, ...]:
    return (
        RGTransportRule(
            rule_id="same_sector_RG_gauge_cancellation",
            source_stage="RG_TRANSPORT_PENDING",
            target_stage="RG_TRANSPORT_PARTIALLY_LOCALIZED",
            status=STATUS_TABLE["same_sector_RG_gauge_cancellation"],
            formula="Delta gamma_gauge(i,j) = 0 for shared sector representation",
            notes="Gauge-universal component cancels for charged same-sector ratios only.",
        ),
        RGTransportRule(
            rule_id="charged_residual_RG_transport",
            source_stage="RG_TRANSPORT_PARTIALLY_LOCALIZED",
            target_stage="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            status=STATUS_TABLE["residual_Yukawa_transport_decomposition"],
            formula="identity residual cancels; tilde_Gamma_f remains",
            notes="Sector-universal residual/Yukawa identity component cancels for charged same-sector ratios.",
        ),
        RGTransportRule(
            rule_id="charged_branch_differential_residual_transport",
            source_stage="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            target_stage="SCHEME_ALIGNED",
            status=STATUS_TABLE["charged_residual_RG_transport"],
            formula="<a|tilde_Gamma_f|a> - <b|tilde_Gamma_f|b>",
            notes="Traceless branch-differential residual operator remains open-localizable.",
        ),
        RGTransportRule(
            rule_id="Kf_aligned_residual_transport_candidate",
            source_stage="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            target_stage="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            status=STATUS_TABLE["Kf_aligned_residual_transport_candidate"],
            formula="tilde_Gamma_f proportional_to K_f - (Tr K_f / 3) I_f",
            notes="Structural candidate only; proportionality/source coefficient remains open.",
        ),
        RGTransportRule(
            rule_id="cross_sector_RG_transport",
            source_stage="RG_TRANSPORT_PENDING",
            target_stage="SCHEME_ALIGNED",
            status=STATUS_TABLE["cross_sector_RG_transport"],
            formula="OPEN",
            notes="Cross-sector ratios are not canceled by the same-sector theorem.",
        ),
        RGTransportRule(
            rule_id="neutral_RG_transport",
            source_stage="RG_TRANSPORT_PENDING",
            target_stage="SCHEME_ALIGNED",
            status=STATUS_TABLE["neutral_RG_transport"],
            formula="OPEN_LOCALIZABLE",
            notes="Neutral-sector transport rule remains to be derived.",
        ),
        RGTransportRule(
            rule_id="scheme_transport",
            source_stage="SCHEME_ALIGNED",
            target_stage="COMPARISON_READY",
            status=STATUS_TABLE["scheme_transport"],
            formula="OPEN",
            notes="Scheme alignment and comparison map remain open.",
        ),
    )


def comparison_readiness_records() -> Tuple[ComparisonReadinessRecord, ...]:
    return (
        ComparisonReadinessRecord(
            sector="charged_lepton",
            source_operator="charged K_l",
            current_readiness="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            comparison_readiness="NOT_READY",
            known_thresholds=(),
            blocker="charged_branch_differential_residual_transport",
            gauge_component="CANCELED_BY_SAME_SECTOR_THEOREM",
            residual_component="OPEN_LOCALIZABLE",
            sector_universal_residual_component="CANCELED_BY_SAME_SECTOR_BRANCH_SPACE",
            branch_differential_residual_component="OPEN_LOCALIZABLE",
        ),
        ComparisonReadinessRecord(
            sector="up",
            source_operator="charged K_u",
            current_readiness="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            comparison_readiness="NOT_READY",
            known_thresholds=("up (6,0): ln 2",),
            blocker="charged_branch_differential_residual_transport",
            gauge_component="CANCELED_BY_SAME_SECTOR_THEOREM",
            residual_component="OPEN_LOCALIZABLE",
            sector_universal_residual_component="CANCELED_BY_SAME_SECTOR_BRANCH_SPACE",
            branch_differential_residual_component="OPEN_LOCALIZABLE",
        ),
        ComparisonReadinessRecord(
            sector="down",
            source_operator="charged K_d",
            current_readiness="RG_TRANSPORT_RESIDUAL_LOCALIZED",
            comparison_readiness="NOT_READY",
            known_thresholds=(),
            blocker="charged_branch_differential_residual_transport",
            gauge_component="CANCELED_BY_SAME_SECTOR_THEOREM",
            residual_component="OPEN_LOCALIZABLE",
            sector_universal_residual_component="CANCELED_BY_SAME_SECTOR_BRANCH_SPACE",
            branch_differential_residual_component="OPEN_LOCALIZABLE",
        ),
        ComparisonReadinessRecord(
            sector="neutral",
            source_operator="symbolic K_nu",
            current_readiness="RG_TRANSPORT_PENDING",
            comparison_readiness="NOT_READY",
            known_thresholds=(),
            blocker="neutral_RG_transport",
            gauge_component="OPEN",
            residual_component="OPEN",
            sector_universal_residual_component="NOT_APPLICABLE",
            branch_differential_residual_component="OPEN",
        ),
    )


def transported_observables() -> Tuple[TransportedObservable, ...]:
    return tuple(
        TransportedObservable(
            sector=record.sector,
            observable_family=(
                "neutral_mixing" if record.sector == "neutral" else "charged_hierarchy"
            ),
            current_stage=record.current_readiness,
            comparison_ready=False,
            blocker=record.blocker,
        )
        for record in comparison_readiness_records()
    )


def current_max_stage() -> str:
    return "RG_TRANSPORT_RESIDUAL_LOCALIZED"


def _rows(rows):
    return [asdict(row) for row in rows]


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-rg-transport-interface-v1",
        "title": "RG / Scheme Transport Interface v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "transport_stages": list(TRANSPORT_STAGES),
        "current_max_stage": current_max_stage(),
        "bare_spectral_outputs": _rows(bare_spectral_outputs()),
        "threshold_dressed_outputs": _rows(threshold_dressed_outputs()),
        "same_sector_gauge_cancellation": same_sector.report_as_dict(),
        "residual_yukawa_transport_decomposition": residual.report_as_dict(),
        "scheme_scale_points": _rows(scheme_scale_points()),
        "rg_transport_rules": _rows(rg_transport_rules()),
        "transported_observables": _rows(transported_observables()),
        "comparison_readiness": _rows(comparison_readiness_records()),
        "statuses": STATUS_TABLE,
        "claim_boundary": "RG interface is structural; no scheme-aligned or comparison-ready predictions are claimed.",
    }
