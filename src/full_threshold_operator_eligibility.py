from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple

import charged_kf_generator as kf


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STATUS_TABLE = {
    "full_threshold_operator_eligibility_v1": "COMPLETED_ELIGIBILITY_AUDIT",
    "threshold_rank_projection_rule": "DERIVED_CONDITIONAL_ON_VIRTUAL_DOOR_PROJECTOR_DATA",
    "up_6_0_Zvirt_threshold": "DERIVED_CONDITIONAL",
    "up_8_1_threshold_source": "NO_THRESHOLD_SOURCE_FOUND",
    "lepton_1_2_threshold_source": "NO_THRESHOLD_SOURCE_FOUND",
    "lepton_3_3_threshold_source": "NO_THRESHOLD_SOURCE_FOUND",
    "down_0_3_threshold_source": "NO_THRESHOLD_SOURCE_FOUND",
    "down_4_2_threshold_source": "NO_THRESHOLD_SOURCE_FOUND",
    "reference_slot_threshold_source": "REFERENCE_SLOT_NOT_THRESHOLD_TARGET",
    "full_threshold_operator": "OPEN",
    "numerical_closure": "OPEN",
}

FORBIDDEN_DERIVATION_INPUTS = (
    "observed masses",
    "charged-lepton masses",
    "quark masses",
    "CKM",
    "PMNS",
    "neutrino data",
    "measured alpha",
    "empirical target ratios",
    "post-comparison residuals",
)


@dataclass(frozen=True)
class VirtualDoorEvidence:
    sector: str
    slot: int
    mode: Tuple[int, int]
    virtual_door_subspace: str
    subspace_dimension: int
    projector: str
    projector_rank: int
    source: str
    status: str


@dataclass(frozen=True)
class ThresholdFactor:
    sector: str
    slot: int
    mode: Tuple[int, int]
    D_fi: Fraction | None
    formula: str
    status: str
    source: str


@dataclass(frozen=True)
class OperatorInsertion:
    sector: str
    slot: int
    mode: Tuple[int, int]
    insertion: str | None
    formula: str
    status: str
    operator_level: bool


@dataclass(frozen=True)
class ThresholdEligibilityRecord:
    sector: str
    slot: int
    mode: Tuple[int, int]
    is_reference_slot: bool
    threshold_status: str
    has_virtual_door_subspace: bool
    has_sector_projector: bool
    threshold_factor: Fraction | None
    operator_insertion: str | None
    notes: str


@dataclass(frozen=True)
class FullThresholdOperatorVerdict:
    threshold_eligibility_verdict: str
    full_threshold_operator_status: str
    known_derived_insertions: int
    open_or_no_source_slots: int
    numerical_closure: str
    theorem_complete: bool


def fraction_string(value: Fraction | None) -> str | None:
    if value is None:
        return None
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


def charged_ledger_slots() -> Dict[str, Tuple[Tuple[int, int], ...]]:
    return {sector: kf.LEDGERS[sector] for sector in kf.CHARGED_SECTORS}


def rank_projection_threshold_factor(projector_rank: int, subspace_dimension: int) -> Fraction:
    if subspace_dimension <= 0:
        raise ValueError("subspace_dimension must be positive")
    if projector_rank < 0 or projector_rank > subspace_dimension:
        raise ValueError("projector_rank must lie between 0 and subspace_dimension")
    return Fraction(projector_rank, subspace_dimension)


def operator_insertion_from_factor(factor: Fraction) -> str:
    if factor <= 0:
        raise ValueError("threshold factor must be positive")
    if factor == Fraction(1, 2):
        return "ln 2"
    if factor == 1:
        return "0"
    return f"-ln({fraction_string(factor)})"


def known_virtual_door_evidence() -> Tuple[VirtualDoorEvidence, ...]:
    return (
        VirtualDoorEvidence(
            sector="up",
            slot=1,
            mode=(6, 0),
            virtual_door_subspace="V_weak=span{door_upper,door_lower}",
            subspace_dimension=2,
            projector="P_u=diag(1,0)",
            projector_rank=1,
            source="weak-double projection bridge",
            status=STATUS_TABLE["up_6_0_Zvirt_threshold"],
        ),
    )


def evidence_for_slot(sector: str, slot: int, mode: Tuple[int, int]) -> VirtualDoorEvidence | None:
    for evidence in known_virtual_door_evidence():
        if evidence.sector == sector and evidence.slot == slot and evidence.mode == mode:
            return evidence
    return None


def threshold_factor_for_slot(sector: str, slot: int, mode: Tuple[int, int]) -> ThresholdFactor:
    evidence = evidence_for_slot(sector, slot, mode)
    if evidence is None:
        return ThresholdFactor(
            sector=sector,
            slot=slot,
            mode=mode,
            D_fi=None,
            formula="D_fi=rank(P_fi|V_fi)/dim(V_fi)",
            status=slot_threshold_status(sector, slot, mode),
            source="no virtual-door/projector source found",
        )
    factor = rank_projection_threshold_factor(evidence.projector_rank, evidence.subspace_dimension)
    return ThresholdFactor(
        sector=sector,
        slot=slot,
        mode=mode,
        D_fi=factor,
        formula="D_fi=rank(P_fi|V_fi)/dim(V_fi)",
        status=evidence.status,
        source=evidence.source,
    )


def operator_insertion_for_slot(sector: str, slot: int, mode: Tuple[int, int]) -> OperatorInsertion:
    factor = threshold_factor_for_slot(sector, slot, mode)
    insertion = operator_insertion_from_factor(factor.D_fi) if factor.D_fi is not None else None
    return OperatorInsertion(
        sector=sector,
        slot=slot,
        mode=mode,
        insertion=insertion,
        formula="K_f -> K_f + [-ln(D_fi)] |i_f><i_f|",
        status=factor.status,
        operator_level=insertion is not None,
    )


def slot_threshold_status(sector: str, slot: int, mode: Tuple[int, int]) -> str:
    if slot == 0 or mode == (0, 0):
        return STATUS_TABLE["reference_slot_threshold_source"]
    if sector == "up" and mode == (6, 0):
        return STATUS_TABLE["up_6_0_Zvirt_threshold"]
    key = f"{sector}_{mode[0]}_{mode[1]}_threshold_source"
    return STATUS_TABLE.get(key, "NO_THRESHOLD_SOURCE_FOUND")


def threshold_eligibility_records() -> Tuple[ThresholdEligibilityRecord, ...]:
    rows = []
    for sector, ledger in charged_ledger_slots().items():
        for slot, mode in enumerate(ledger):
            evidence = evidence_for_slot(sector, slot, mode)
            factor = threshold_factor_for_slot(sector, slot, mode)
            insertion = operator_insertion_for_slot(sector, slot, mode)
            is_reference = slot == 0 or mode == (0, 0)
            rows.append(
                ThresholdEligibilityRecord(
                    sector=sector,
                    slot=slot,
                    mode=mode,
                    is_reference_slot=is_reference,
                    threshold_status=slot_threshold_status(sector, slot, mode),
                    has_virtual_door_subspace=evidence is not None,
                    has_sector_projector=evidence is not None,
                    threshold_factor=factor.D_fi,
                    operator_insertion=insertion.insertion,
                    notes=(
                        "reference anchor, not an ordinary threshold target"
                        if is_reference
                        else (
                            "weak-double projection gives D=1/2"
                            if evidence is not None
                            else "no virtual-door/projector source found"
                        )
                    ),
                )
            )
    return tuple(rows)


def derived_operator_insertions() -> Tuple[OperatorInsertion, ...]:
    return tuple(
        operator_insertion_for_slot(record.sector, record.slot, record.mode)
        for record in threshold_eligibility_records()
        if record.operator_insertion is not None
    )


def generator_threshold_insertions(rule: str = kf.THRESHOLD_RULE_DERIVED_ONLY):
    return kf.threshold_insertions(rule)


def verdict() -> FullThresholdOperatorVerdict:
    rows = threshold_eligibility_records()
    derived = [row for row in rows if row.threshold_status == "DERIVED_CONDITIONAL"]
    open_rows = [
        row
        for row in rows
        if row.threshold_status in {"NO_THRESHOLD_SOURCE_FOUND", "OPEN_LOCALIZABLE"}
    ]
    return FullThresholdOperatorVerdict(
        threshold_eligibility_verdict="ONLY_UP_6_0_THRESHOLD_DERIVED_CONDITIONAL",
        full_threshold_operator_status=STATUS_TABLE["full_threshold_operator"],
        known_derived_insertions=len(derived),
        open_or_no_source_slots=len(open_rows),
        numerical_closure=STATUS_TABLE["numerical_closure"],
        theorem_complete=False,
    )


def _dataclass_rows(rows):
    out = []
    for row in rows:
        item = asdict(row)
        out.append({key: _convert(value) for key, value in item.items()})
    return out


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-full-threshold-operator-eligibility-v1",
        "title": "Full Threshold Operator Eligibility Kernel v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "threshold_principle": {
            "factor": "D_fi=rank(P_fi|V_fi)/dim(V_fi)",
            "operator_insertion": "K_f -> K_f + [-ln(D_fi)] |i_f><i_f|",
            "status": STATUS_TABLE["threshold_rank_projection_rule"],
        },
        "charged_ledgers": {
            sector: [list(mode) for mode in ledger] for sector, ledger in charged_ledger_slots().items()
        },
        "virtual_door_evidence": _dataclass_rows(known_virtual_door_evidence()),
        "eligibility_records": _dataclass_rows(threshold_eligibility_records()),
        "derived_operator_insertions": _dataclass_rows(derived_operator_insertions()),
        "generator_threshold_rules": {
            "none": {
                "name": kf.THRESHOLD_RULE_NONE,
                "status": kf.threshold_rule_status(kf.THRESHOLD_RULE_NONE),
                "insertions": kf.threshold_insertions(kf.THRESHOLD_RULE_NONE),
            },
            "derived_only": {
                "name": kf.THRESHOLD_RULE_DERIVED_ONLY,
                "status": kf.threshold_rule_status(kf.THRESHOLD_RULE_DERIVED_ONLY),
                "insertions": kf.threshold_insertions(kf.THRESHOLD_RULE_DERIVED_ONLY),
            },
            "symbolic_open": {
                "name": kf.THRESHOLD_RULE_SYMBOLIC_OPEN,
                "status": kf.threshold_rule_status(kf.THRESHOLD_RULE_SYMBOLIC_OPEN),
                "insertions": "eligibility table only; no extra numeric insertions",
            },
        },
        "statuses": STATUS_TABLE,
        "verdict": {key: _convert(value) for key, value in asdict(verdict()).items()},
        "claim_boundary": (
            "The current eligibility kernel derives only the up (6,0) threshold conditionally; "
            "all other charged non-reference slots have no threshold source in this audit."
        ),
    }
