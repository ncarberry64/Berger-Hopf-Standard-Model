from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

UNIFIED_RULE = "g_sector = overlap_amplitude^2 / incidence_trace"

NEUTRAL_STATUS = "DERIVED_CONDITIONAL_ON_NEUTRAL_INCIDENT_TRACE_3_AND_UNIT_OVERLAP"
CHARGED_STATUS = "DERIVED_CONDITIONAL_ON_INCIDENT_TRACE_21_AND_OVERLAP_4_OVER_3"
CHARGED_OVERLAP_ACTION_SOURCE = "OPEN_LOCALIZABLE"

STATUS_TABLE = {
    "incidence_normalized_overlap_bridge_rule": "PARTIALLY_LOCALIZED",
    "charged_bridge_seed_16_over_189": CHARGED_STATUS,
    "neutral_bridge_seed_1_over_3": NEUTRAL_STATUS,
    "charged_overlap_4_over_3_action_source": CHARGED_OVERLAP_ACTION_SOURCE,
    "full_numerical_closure": "OPEN",
}


@dataclass(frozen=True)
class BridgeSourceDiagnostic:
    sector: str
    incidence_trace: Fraction
    overlap_amplitude: Fraction
    bridge_seed: Fraction
    status: str
    notes: str
    open_blockers: Tuple[str, ...]


@dataclass(frozen=True)
class ChargedOverlapMetadata:
    charged_overlap_factor: Fraction
    motivation: str
    action_source_status: str


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def bridge_seed(incidence_trace: Fraction, overlap_amplitude: Fraction) -> Fraction:
    if incidence_trace == 0:
        raise ValueError("incidence_trace must be nonzero")
    return overlap_amplitude**2 / incidence_trace


def neutral_bridge_source() -> BridgeSourceDiagnostic:
    incidence_trace = Fraction(3)
    overlap_amplitude = Fraction(1)
    return BridgeSourceDiagnostic(
        sector="neutral",
        incidence_trace=incidence_trace,
        overlap_amplitude=overlap_amplitude,
        bridge_seed=bridge_seed(incidence_trace, overlap_amplitude),
        status=NEUTRAL_STATUS,
        notes="Neutral primitive incidence rank 3 with unit overlap.",
        open_blockers=(
            "neutral eta/beta/kappa final action derivation",
            "neutral numerical closure",
        ),
    )


def charged_overlap_metadata() -> ChargedOverlapMetadata:
    return ChargedOverlapMetadata(
        charged_overlap_factor=Fraction(4, 3),
        motivation="down Hopf multiplier 4 divided by rank-three closure 3",
        action_source_status=CHARGED_OVERLAP_ACTION_SOURCE,
    )


def charged_bridge_source() -> BridgeSourceDiagnostic:
    incidence_trace = Fraction(21)
    overlap_amplitude = charged_overlap_metadata().charged_overlap_factor
    return BridgeSourceDiagnostic(
        sector="charged",
        incidence_trace=incidence_trace,
        overlap_amplitude=overlap_amplitude,
        bridge_seed=bridge_seed(incidence_trace, overlap_amplitude),
        status=CHARGED_STATUS,
        notes=(
            "Charged total incidence trace 21 with overlap-renormalization "
            "candidate 4/3."
        ),
        open_blockers=(
            "exact action derivation of charged overlap factor 4/3",
            "final bridge action theorem",
            "numerical closure",
        ),
    )


def bridge_sources() -> Tuple[BridgeSourceDiagnostic, BridgeSourceDiagnostic]:
    return (neutral_bridge_source(), charged_bridge_source())


def bridge_ratio_charged_to_neutral() -> Fraction:
    return charged_bridge_source().bridge_seed / neutral_bridge_source().bridge_seed


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [_convert(item) for item in value]
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    return value


def _row(row) -> Dict[str, object]:
    return {key: _convert(value) for key, value in asdict(row).items()}


def report_as_dict() -> Dict[str, object]:
    charged_meta = charged_overlap_metadata()
    return {
        "id": "PO-BH-incidence-normalized-overlap-bridge-source-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "unified_rule": UNIFIED_RULE,
        "neutral": _row(neutral_bridge_source()),
        "charged": {
            **_row(charged_bridge_source()),
            "overlap_action_source": charged_meta.action_source_status,
        },
        "charged_overlap_metadata": _row(charged_meta),
        "bridge_ratio_charged_to_neutral": fraction_string(bridge_ratio_charged_to_neutral()),
        "g_ch_factorization": "(1/21)(4/3)^2",
        "g_ch_factorization_value": fraction_string(
            Fraction(1, 21) * Fraction(4, 3) ** 2
        ),
        "statuses": STATUS_TABLE,
        "numerical_closure": "OPEN",
        "claim_boundary": (
            "The incidence-normalized overlap rule localizes a shared bridge-seed "
            "pattern, but the charged overlap factor 4/3 and full numerical closure "
            "remain open."
        ),
    }
