from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple

import rho_ch_branch_pressure_test as pressure


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STIFFNESS_ACTION_FORM = "S_stiffness,ch = k_q q^2 + k_j j^2"
RHO_DEFINITION = "rho_ch = k_j/k_q"

STATUS_TABLE = {
    "charged_stiffness_action_selector_v1": "COMPLETED_SELECTOR_AUDIT",
    "rho_ch_1_isotropic_action_selector": "STRUCTURALLY_SUPPORTED_CANDIDATE",
    "rho_ch_2_weak_involution_action_selector": "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
    "rho_ch_3_rank_three_action_selector": "STRUCTURALLY_INTERESTING_BRANCH",
    "rho_ch_exact_value": "OPEN_LOCALIZABLE",
    "charged_Hessian_from_S_index_trace": "INVALIDATED_DO_NOT_CLAIM",
    "charged_stiffness_action_source": "OPEN_LOCALIZABLE",
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
class ChargedStiffnessSelector:
    selector_id: str
    rho_ch: Fraction
    k_q: Fraction
    k_j: Fraction
    meaning: str
    claimed_action_source: str
    evidence_summary: str
    status: str
    selected: bool
    reason_not_selected: str


@dataclass(frozen=True)
class RhoBranchActionEvidence:
    rho_ch: Fraction
    pressure_test_status: str
    action_selector_status: str
    uses_empirical_input: bool
    direct_action_coupling_found: bool
    notes: Tuple[str, ...]


@dataclass(frozen=True)
class StiffnessSelectorVerdict:
    selected_rho_ch: Fraction | None
    rho_ch_exact_value_status: str
    verdict: str
    theorem_complete: bool
    explanation: str


def stiffness_action(q: int, j: int, k_q: Fraction, k_j: Fraction) -> Fraction:
    return k_q * q * q + k_j * j * j


def rho_from_stiffness(k_q: Fraction, k_j: Fraction) -> Fraction:
    if k_q == 0:
        raise ValueError("k_q must be nonzero")
    return k_j / k_q


def has_cross_term() -> bool:
    return False


def selector_candidates() -> Tuple[ChargedStiffnessSelector, ...]:
    return (
        ChargedStiffnessSelector(
            selector_id="A_ISOTROPIC_PRIMITIVE_STIFFNESS",
            rho_ch=Fraction(1, 1),
            k_q=Fraction(1, 1),
            k_j=Fraction(1, 1),
            meaning="channel winding and Hopf/fiber winding carry equal primitive charged stiffness",
            claimed_action_source="primitive isotropic charged stiffness form",
            evidence_summary=(
                "The diagonal form q^2+j^2 is structurally simple and compatible with the "
                "charged stiffness ansatz, but the current action does not force isotropy."
            ),
            status=STATUS_TABLE["rho_ch_1_isotropic_action_selector"],
            selected=False,
            reason_not_selected="No action theorem explicitly enforces k_q=k_j.",
        ),
        ChargedStiffnessSelector(
            selector_id="B_WEAK_INVOLUTION_WEIGHTED_STIFFNESS",
            rho_ch=Fraction(2, 1),
            k_q=Fraction(1, 1),
            k_j=Fraction(2, 1),
            meaning="Hopf/fiber stiffness receives the weak-involution orientation dimension weight",
            claimed_action_source="rank or dimension of weak orientation/involution layer equals 2",
            evidence_summary=(
                "The weak orientation layer supplies a structural two-state motive, but the "
                "current action does not explicitly couple j-stiffness to that layer."
            ),
            status=STATUS_TABLE["rho_ch_2_weak_involution_action_selector"],
            selected=False,
            reason_not_selected="No charged action coupling maps weak two-state structure to k_j/k_q.",
        ),
        ChargedStiffnessSelector(
            selector_id="C_RANK_THREE_CLOSURE_WEIGHTED_STIFFNESS",
            rho_ch=Fraction(3, 1),
            k_q=Fraction(1, 1),
            k_j=Fraction(3, 1),
            meaning="Hopf/fiber stiffness receives the universal rank-three closure weight E3",
            claimed_action_source="rank(E3)=3",
            evidence_summary=(
                "The rank-three closure module supplies a structural three-weight motive, and "
                "rho_ch=3 is interesting in the pressure test, but the current action does not "
                "explicitly couple E3 to j-stiffness."
            ),
            status=STATUS_TABLE["rho_ch_3_rank_three_action_selector"],
            selected=False,
            reason_not_selected="Down near-degeneracy and rank(E3)=3 are not an action selection theorem.",
        ),
    )


def action_evidence_records() -> Tuple[RhoBranchActionEvidence, ...]:
    pressure_status = pressure.report_as_dict()["branch_classifications"]
    records = []
    for selector in selector_candidates():
        records.append(
            RhoBranchActionEvidence(
                rho_ch=selector.rho_ch,
                pressure_test_status=pressure_status[str(selector.rho_ch.numerator)],
                action_selector_status=selector.status,
                uses_empirical_input=False,
                direct_action_coupling_found=False,
                notes=(
                    selector.evidence_summary,
                    selector.reason_not_selected,
                ),
            )
        )
    return tuple(records)


def selector_verdict() -> StiffnessSelectorVerdict:
    selected = [candidate for candidate in selector_candidates() if candidate.selected]
    if selected:
        chosen = selected[0]
        return StiffnessSelectorVerdict(
            selected_rho_ch=chosen.rho_ch,
            rho_ch_exact_value_status="DERIVED_CONDITIONAL_ON_CHARGED_STIFFNESS_ACTION",
            verdict="UNIQUE_SELECTOR_FOUND",
            theorem_complete=False,
            explanation="A selector was marked selected by direct action evidence.",
        )
    return StiffnessSelectorVerdict(
        selected_rho_ch=None,
        rho_ch_exact_value_status=STATUS_TABLE["rho_ch_exact_value"],
        verdict="NO_UNIQUE_ACTION_SELECTOR_FOUND",
        theorem_complete=False,
        explanation=(
            "The current action layer supplies structural motives for rho_ch=1,2,3 but no "
            "explicit charged stiffness coupling that uniquely fixes k_j/k_q."
        ),
    )


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


def report_as_dict() -> Dict[str, object]:
    candidates = []
    for candidate in selector_candidates():
        item = asdict(candidate)
        candidates.append({key: _convert(value) for key, value in item.items()})
    evidence = []
    for record in action_evidence_records():
        item = asdict(record)
        evidence.append({key: _convert(value) for key, value in item.items()})
    verdict = asdict(selector_verdict())
    verdict = {key: _convert(value) for key, value in verdict.items()}
    return {
        "id": "PO-BH-charged-stiffness-action-selector-v1",
        "title": "Charged Stiffness Action Selector v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "stiffness_action_form": STIFFNESS_ACTION_FORM,
        "rho_definition": RHO_DEFINITION,
        "charged_stiffness_has_qj_cross_term": has_cross_term(),
        "S_index_trace_hessian_source_status": STATUS_TABLE[
            "charged_Hessian_from_S_index_trace"
        ],
        "selector_candidates": candidates,
        "action_evidence_records": evidence,
        "verdict": verdict,
        "rho_ch_exact_value_status": STATUS_TABLE["rho_ch_exact_value"],
        "statuses": STATUS_TABLE,
        "pressure_test_classifications_preserved": pressure.report_as_dict()[
            "branch_classifications"
        ],
        "no_empirical_comparison_performed": True,
        "claim_boundary": (
            "The selector audit finds no unique action-level rho_ch selection; "
            "rho_ch_exact_value remains open-localizable."
        ),
    }
