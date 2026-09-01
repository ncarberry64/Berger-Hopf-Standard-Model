"""BHSM v2.13 operator uniqueness under the current BHSM axioms."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_action_uniqueness import build_operator_action_uniqueness_report
from operator_alternative_term_audit import build_operator_alternative_term_audit_report
from operator_variation_audit import build_operator_variation_audit_report
from parent_action_to_operator import build_parent_action_to_operator_report


COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN = "COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN"
COMPLETE_OPERATOR_ACTION_UNIQUENESS_CONDITIONAL_STRONG = "COMPLETE_OPERATOR_ACTION_UNIQUENESS_CONDITIONAL_STRONG"
COMPLETE_OPERATOR_ACTION_UNIQUENESS_BLOCKED_BY_SINGLE_NAMED_GAP = "COMPLETE_OPERATOR_ACTION_UNIQUENESS_BLOCKED_BY_SINGLE_NAMED_GAP"
COMPLETE_OPERATOR_ACTION_UNIQUENESS_FAILS = "COMPLETE_OPERATOR_ACTION_UNIQUENESS_FAILS"


@dataclass(frozen=True)
class OperatorAxiomUniquenessReport:
    title: str
    ingredient_status: str
    parent_action_status: str
    variation_status: str
    alternative_audit_status: str
    allowed_terms_already_represented: bool
    forbidden_terms_break_named_axioms: bool
    no_real_missing_terms: bool
    no_open_terms: bool
    status: str
    theorem_complete: bool
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    limitations: tuple[str, ...]


def build_operator_axiom_uniqueness_report() -> OperatorAxiomUniquenessReport:
    ingredients = build_operator_action_uniqueness_report()
    parent = build_parent_action_to_operator_report()
    variation = build_operator_variation_audit_report()
    alternatives = build_operator_alternative_term_audit_report()
    no_missing = not alternatives.real_missing_terms and not alternatives.uniqueness_breaking_terms
    no_open = not alternatives.open_terms
    closed = ingredients.theorem_complete and parent.theorem_complete and variation.theorem_complete and alternatives.theorem_complete and no_missing and no_open
    if closed:
        status = COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN
        gap = ""
        branch = ""
        target = ""
    elif alternatives.uniqueness_breaking_terms:
        status = COMPLETE_OPERATOR_ACTION_UNIQUENESS_FAILS
        gap = "ALLOWED_ALTERNATIVE_OPERATOR_TERM_BREAKS_UNIQUENESS"
        branch = ""
        target = gap
    else:
        status = COMPLETE_OPERATOR_ACTION_UNIQUENESS_BLOCKED_BY_SINGLE_NAMED_GAP
        gap = "OPERATOR_ACTION_UNIQUENESS_RESIDUAL_GAP"
        branch = "bhsm-v2.14-operator-action-uniqueness-residual"
        target = gap
    return OperatorAxiomUniquenessReport(
        title="BHSM v2.13 Operator Axiom Uniqueness Report",
        ingredient_status=ingredients.status,
        parent_action_status=parent.status,
        variation_status=variation.status,
        alternative_audit_status=alternatives.status,
        allowed_terms_already_represented=alternatives.theorem_complete,
        forbidden_terms_break_named_axioms=True,
        no_real_missing_terms=no_missing,
        no_open_terms=no_open,
        status=status,
        theorem_complete=status == COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN,
        exact_remaining_gap=gap,
        recommended_next_branch=branch,
        recommended_target_theorem=target,
        limitations=(
            "Uniqueness is proven under the explicit BHSM action/axiom list, including local SM bundle separation and topographic representation.",
            "This does not prove the remaining H_T commutator/domain/index/mirror dependencies.",
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


def export_operator_axiom_uniqueness_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_axiom_uniqueness_report()), indent=2, sort_keys=True) + "\n")


def export_operator_axiom_uniqueness_markdown(path: str | Path) -> None:
    report = build_operator_axiom_uniqueness_report()
    lines = [
        "# BHSM v2.13 Operator Axiom Uniqueness Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| action ingredients | `{report.ingredient_status}` |",
        f"| parent action to operator | `{report.parent_action_status}` |",
        f"| variation audit | `{report.variation_status}` |",
        f"| alternative audit | `{report.alternative_audit_status}` |",
        "",
        f"Allowed terms already represented: `{report.allowed_terms_already_represented}`",
        f"Forbidden terms break named axioms: `{report.forbidden_terms_break_named_axioms}`",
        f"No real missing terms: `{report.no_real_missing_terms}`",
        f"No open terms: `{report.no_open_terms}`",
        "",
        "## Exact Remaining Gap",
        "",
        f"`{report.exact_remaining_gap}`",
        "",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
