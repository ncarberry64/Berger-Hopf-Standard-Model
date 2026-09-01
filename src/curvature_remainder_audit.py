"""BHSM v2.7 classification audit for the bundle-curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_connection_curvature import build_bundle_connection_curvature_report
from curvature_remainder_after_mixed_rule import build_curvature_remainder_after_mixed_rule_report
from lichnerowicz_bundle_curvature import REMAINDER_TERM_ID, build_lichnerowicz_bundle_curvature_report


REMAINDER_ZERO = "REMAINDER_ZERO"
REMAINDER_REPRESENTED_BY_EXISTING_TERM = "REMAINDER_REPRESENTED_BY_EXISTING_TERM"
REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR = "REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"
REMAINDER_PSD_PROFILE_CONTROLLED = "REMAINDER_PSD_PROFILE_CONTROLLED"
REMAINDER_SCREENED_OR_LIFTED = "REMAINDER_SCREENED_OR_LIFTED"
REMAINDER_RELATIVELY_BOUNDED_SAFE = "REMAINDER_RELATIVELY_BOUNDED_SAFE"
REMAINDER_REAL_MISSING_TERM = "REMAINDER_REAL_MISSING_TERM"
REMAINDER_OPEN = "REMAINDER_OPEN"

FINAL_REMAINDER_CLASSIFICATIONS = {
    REMAINDER_ZERO,
    REMAINDER_REPRESENTED_BY_EXISTING_TERM,
    REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
    REMAINDER_PSD_PROFILE_CONTROLLED,
    REMAINDER_SCREENED_OR_LIFTED,
    REMAINDER_RELATIVELY_BOUNDED_SAFE,
    REMAINDER_REAL_MISSING_TERM,
    REMAINDER_OPEN,
}

SAFE_REMAINDER_CLASSIFICATIONS = {
    REMAINDER_ZERO,
    REMAINDER_REPRESENTED_BY_EXISTING_TERM,
    REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
    REMAINDER_PSD_PROFILE_CONTROLLED,
    REMAINDER_SCREENED_OR_LIFTED,
    REMAINDER_RELATIVELY_BOUNDED_SAFE,
}


@dataclass(frozen=True)
class RemainderDispositionCheck:
    disposition: str
    passes: bool
    evidence: str
    limitation: str


@dataclass(frozen=True)
class CurvatureRemainderAuditReport:
    title: str
    term_id: str
    checks: tuple[RemainderDispositionCheck, ...]
    final_classification: str
    exact_remaining_gap: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_audit_report() -> CurvatureRemainderAuditReport:
    """Classify the Lichnerowicz/bundle-curvature remainder exactly once."""

    lich = build_lichnerowicz_bundle_curvature_report()
    connection = build_bundle_connection_curvature_report()
    after_mixed = build_curvature_remainder_after_mixed_rule_report()
    represented = after_mixed.r_bundle_classification == REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    checks = (
        RemainderDispositionCheck(REMAINDER_ZERO, False, "No cancellation/trace/projection proof is implemented.", "Cannot claim zero from connection-source inventory alone."),
        RemainderDispositionCheck(REMAINDER_REPRESENTED_BY_EXISTING_TERM, False, "Connection-level sources map to existing terms, but v2.12 uses the more specific topographic-sector classification.", "Representation is recorded in the topographic-sector row."),
        RemainderDispositionCheck(REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, represented, "v2.11/v2.12 maps the mixed contribution to existing boundary/profile/topographic/screening/lift sectors.", "This closes R_bundle for the mixed contribution but does not prove the full H_T theorem."),
        RemainderDispositionCheck(REMAINDER_PSD_PROFILE_CONTROLLED, False, "No symmetry and PSD proof for R_bundle is present.", "The PSD/profile package cannot absorb an unidentified sign-indefinite curvature contraction."),
        RemainderDispositionCheck(REMAINDER_SCREENED_OR_LIFTED, False, "No proof excludes R_bundle from H_perp or lifts it above threshold.", "Screening/lifting remains unavailable without its sector/chirality action."),
        RemainderDispositionCheck(REMAINDER_RELATIVELY_BOUNDED_SAFE, False, "No constants a_R,b_R have been derived for ||R_bundle psi|| <= a_R ||A0 psi|| + b_R ||psi||.", "Relative-bound closure requires an explicit operator formula or norm estimate."),
        RemainderDispositionCheck(REMAINDER_REAL_MISSING_TERM, False, "The term is not proven nonzero or uncontrolled; only unresolved.", "Failure would require showing the term breaks lower-bound transfer."),
        RemainderDispositionCheck(REMAINDER_OPEN, not represented, f"{lich.remainder.term_id} has no complete formula/action; {len(connection.unresolved_components)} connection sources retain curvature-remainder risk.", "This is an honest theorem gap, not an H_T theorem failure."),
    )
    passing = tuple(row.disposition for row in checks if row.passes)
    final = passing[0] if len(passing) == 1 else REMAINDER_OPEN
    return CurvatureRemainderAuditReport(
        title="BHSM v2.7 Curvature Remainder Audit",
        term_id=REMAINDER_TERM_ID,
        checks=checks,
        final_classification=final,
        exact_remaining_gap="" if final in SAFE_REMAINDER_CLASSIFICATIONS else "BUNDLE_CURVATURE_REMAINDER_FORMULA_AND_BOUND_GAP",
        theorem_complete=final in SAFE_REMAINDER_CLASSIFICATIONS,
        limitations=(
            "The audit classifies the remainder exactly once.",
            "The v2.12 classification is topographic representation when the mixed contribution contributes no independent R_bundle term.",
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


def export_curvature_remainder_audit_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_audit_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_audit_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_audit_report()
    lines = [
        "# BHSM v2.7 Curvature Remainder Audit",
        "",
        f"Term: `{report.term_id}`",
        f"Final classification: `{report.final_classification}`",
        f"Exact remaining gap: `{report.exact_remaining_gap}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Disposition | Passes | Evidence | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.checks:
        lines.append(f"| `{row.disposition}` | `{row.passes}` | {row.evidence} | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
