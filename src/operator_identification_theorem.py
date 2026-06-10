"""BHSM v2.6 complete-operator identification theorem attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_dirac_derivation import build_bundle_dirac_derivation_report
from complete_berger_hopf_operator import build_complete_berger_hopf_operator_report
from curvature_remainder_audit import REMAINDER_RELATIVELY_BOUNDED_SAFE
from curvature_remainder_closure_decision import BUNDLE_CURVATURE_REMAINDER_CLOSED, build_curvature_remainder_closure_decision
from operator_missing_term_audit import build_operator_missing_term_audit_report
from operator_term_inventory import build_operator_term_inventory_report


COMPLETE_OPERATOR_IDENTIFICATION_PROVEN = "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG = "COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG"
COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM = "COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM"
COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_DOMAIN = "COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_DOMAIN"
COMPLETE_OPERATOR_IDENTIFICATION_OPEN = "COMPLETE_OPERATOR_IDENTIFICATION_OPEN"
FAILS_COMPLETE_OPERATOR_IDENTIFICATION = "FAILS_COMPLETE_OPERATOR_IDENTIFICATION"


@dataclass(frozen=True)
class OperatorIdentificationTheoremReport:
    title: str
    proposed_identity: str
    operator_status: str
    derivation_status: str
    inventory_status: str
    missing_term_audit_status: str
    blocking_term: str
    status: str
    theorem_complete: bool
    exact_obstruction: str
    next_branch: str
    next_target_theorem: str
    limitations: tuple[str, ...]


def build_operator_identification_theorem_report() -> OperatorIdentificationTheoremReport:
    operator = build_complete_berger_hopf_operator_report()
    derivation = build_bundle_dirac_derivation_report()
    inventory = build_operator_term_inventory_report()
    missing = build_operator_missing_term_audit_report()
    curvature = build_curvature_remainder_closure_decision()
    all_operator_terms_closed = (
        not missing.blocking_term
        and inventory.theorem_complete
        and derivation.theorem_complete
        and operator.theorem_complete
        and curvature.final_result == BUNDLE_CURVATURE_REMAINDER_CLOSED
    )
    if all_operator_terms_closed:
        status = COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG
    elif missing.blocking_term:
        status = COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM
    else:
        status = COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG
    obstruction = (
        "No obstruction."
        if status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        else "The curvature formula is closed, but the complete operator remains action-uniqueness/perturbation-package conditional rather than proven from the full internal action."
    )
    next_branch = "bhsm-v2.13-complete-operator-action-uniqueness" if status == COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG else curvature.recommended_next_branch
    next_target = "COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP" if status == COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG else curvature.recommended_target_theorem
    return OperatorIdentificationTheoremReport(
        title="BHSM v2.7 Complete Operator Identification Theorem Attempt",
        proposed_identity="D_BH^2 = A0 + V on D(A0), up to terms proven zero, screened, lifted, represented, or axiom-forbidden",
        operator_status=operator.status,
        derivation_status=derivation.status,
        inventory_status=inventory.status,
        missing_term_audit_status=missing.status,
        blocking_term=missing.blocking_term or "",
        status=status,
        theorem_complete=status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
        exact_obstruction=obstruction,
        next_branch=next_branch,
        next_target_theorem=next_target,
        limitations=(
            "The theorem attempt accounts for every listed candidate contribution.",
            "It refuses proven status while complete-operator action uniqueness and perturbation-package closure remain conditional.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_operator_identification_theorem_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_identification_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_operator_identification_theorem_markdown(path: str | Path) -> None:
    report = build_operator_identification_theorem_report()
    lines = [
        "# BHSM v2.7 Complete Operator Identification Theorem Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Identity: `{report.proposed_identity}`",
        f"Blocking term: `{report.blocking_term}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| complete operator | `{report.operator_status}` |",
        f"| bundle derivation | `{report.derivation_status}` |",
        f"| term inventory | `{report.inventory_status}` |",
        f"| missing-term audit | `{report.missing_term_audit_status}` |",
        "",
        "## Exact Obstruction",
        "",
        report.exact_obstruction,
        "",
        f"Recommended next branch: `{report.next_branch}`",
        f"Recommended target theorem: `{report.next_target_theorem}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
