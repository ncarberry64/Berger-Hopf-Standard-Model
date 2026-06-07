"""Minimality audit for the BHSM v1.2 parent-action scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from action_reduction import reduce_parent_action_to_boundary_functional, reduced_coefficients
from parent_internal_action import ParentActionTerm, ParentReductionStatus, parent_action_terms


@dataclass(frozen=True)
class ActionVariant:
    """A controlled parent-action variant used in minimality/uniqueness audits."""

    id: str
    description: str
    removed_terms: tuple[str, ...] = ()
    overrides: dict[str, dict[str, int | None | str]] | None = None
    expected_effect: str = ""
    status: str = "AUDIT_VARIANT"


@dataclass(frozen=True)
class ReductionOutcome:
    """Outcome for one sector under one action variant."""

    variant_id: str
    sector: str
    parent_status: str
    fiber_value: int | None
    fiber_status: str
    base_value: int | None
    base_status: str
    target_value: int | None
    target_status: str
    open_reasons: tuple[str, ...]
    recovered_expected_modes: bool | None = None


@dataclass(frozen=True)
class MinimalityCriterion:
    """Minimality criterion for a required parent-action term."""

    id: str
    removed_term: str
    required_for: str
    passes: bool
    evidence: tuple[ReductionOutcome, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ActionAuditReport:
    """Minimality/uniqueness report container."""

    title: str
    status: str
    theorem_complete: bool
    variants: tuple[ActionVariant, ...]
    outcomes: tuple[ReductionOutcome, ...]
    criteria: tuple[MinimalityCriterion, ...]
    limitations: tuple[str, ...]


def terms_without(term_id: str, terms: tuple[ParentActionTerm, ...] | None = None) -> tuple[ParentActionTerm, ...]:
    """Return parent action terms with one term removed."""

    terms = parent_action_terms() if terms is None else terms
    return tuple(term for term in terms if term.id != term_id)


def minimality_variants() -> tuple[ActionVariant, ...]:
    """Return the parent-action term-removal variants."""

    expected = {
        "I_HOPF": "fiber_q opens",
        "I_U1": "fiber_q opens",
        "I_BASE": "base_j opens",
        "I_WEAK": "base_j opens",
        "I_COF": "base_j opens",
        "I_BDY": "target opens",
    }
    return tuple(
        ActionVariant(
            id=f"remove_{term}",
            description=f"Remove parent action term {term}.",
            removed_terms=(term,),
            expected_effect=effect,
        )
        for term, effect in expected.items()
    )


def evaluate_minimality_variant(variant: ActionVariant) -> tuple[ReductionOutcome, ...]:
    """Evaluate one term-removal variant over all charged sectors."""

    terms = parent_action_terms()
    for term in variant.removed_terms:
        terms = terms_without(term, terms)
    outcomes = []
    for sector in ("lepton", "up", "down"):
        reduction = reduce_parent_action_to_boundary_functional(sector, terms)
        coefficients = reduced_coefficients(reduction)
        open_reasons = tuple(
            reason
            for coefficient in coefficients.values()
            for reason in (coefficient.open_reason,)
            if reason
        )
        outcomes.append(
            ReductionOutcome(
                variant_id=variant.id,
                sector=sector,
                parent_status=reduction.parent_action_status.value,
                fiber_value=coefficients["fiber_q"].value,
                fiber_status=coefficients["fiber_q"].status.value,
                base_value=coefficients["base_j"].value,
                base_status=coefficients["base_j"].status.value,
                target_value=coefficients["target"].value,
                target_status=coefficients["target"].status.value,
                open_reasons=open_reasons,
            )
        )
    return tuple(outcomes)


def _criterion_passes(term: str, outcomes: tuple[ReductionOutcome, ...]) -> bool:
    if term in {"I_HOPF", "I_U1"}:
        return all(outcome.fiber_status == "OPEN" and outcome.fiber_value is None for outcome in outcomes)
    if term in {"I_BASE", "I_WEAK", "I_COF"}:
        return all(outcome.base_status == "OPEN" and outcome.base_value is None for outcome in outcomes)
    if term == "I_BDY":
        return all(outcome.target_status == "OPEN" and outcome.target_value is None for outcome in outcomes)
    raise ValueError(f"unknown term: {term}")


def build_minimality_audit() -> ActionAuditReport:
    """Build the parent-action minimality audit."""

    variants = minimality_variants()
    outcomes = tuple(outcome for variant in variants for outcome in evaluate_minimality_variant(variant))
    criteria = []
    for variant in variants:
        term = variant.removed_terms[0]
        evidence = tuple(outcome for outcome in outcomes if outcome.variant_id == variant.id)
        criteria.append(
            MinimalityCriterion(
                id=f"minimal_{term}",
                removed_term=term,
                required_for=variant.expected_effect,
                passes=_criterion_passes(term, evidence),
                evidence=evidence,
                limitations=(
                    "Minimality is tested inside the symbolic parent-action scaffold.",
                    "This does not prove global minimality of the complete internal action.",
                ),
            )
        )
    return ActionAuditReport(
        title="BHSM v1.2C Parent-Action Minimality Audit",
        status="MINIMAL_UNDER_TESTED_PARENT_TERMS" if all(criterion.passes for criterion in criteria) else "MINIMALITY_FAILURE",
        theorem_complete=False,
        variants=variants,
        outcomes=outcomes,
        criteria=tuple(criteria),
        limitations=(
            "Term-removal minimality is local to the v1.2B symbolic parent-action scaffold.",
            "No empirical flavor or residual data are used.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_minimality_audit_json(path: str | Path) -> None:
    """Export parent-action minimality audit as JSON."""

    report = build_minimality_audit()
    Path(path).write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")


def export_minimality_audit_markdown(path: str | Path) -> None:
    """Export parent-action minimality audit as Markdown."""

    report = build_minimality_audit()
    lines = [
        "# BHSM v1.2C Parent-Action Minimality Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Removed term | Required for | Passes | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for criterion in report.criteria:
        sectors = ", ".join(
            f"{outcome.sector}:{outcome.parent_status}" for outcome in criterion.evidence
        )
        lines.append(
            f"| `{criterion.removed_term}` | {criterion.required_for} | `{criterion.passes}` | {sectors} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
