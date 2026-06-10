"""BHSM v2.5 full theorem package completion decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_ht_theorem_closure import (
    BHSM_THEOREM_FAILURE,
    FULL_HT_THEOREM_PROVEN,
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_full_ht_theorem_closure_report,
)


FULL_BHSM_THEOREM_PACKAGE_COMPLETE = "FULL_BHSM_THEOREM_PACKAGE_COMPLETE"


@dataclass(frozen=True)
class FullBHSMTheoremCompletionReport:
    title: str
    final_result: str
    full_ht_result: str
    final_paper_allowed: bool
    theorem_complete: bool
    single_named_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    exact_obstruction: str
    limitations: tuple[str, ...]


def build_full_bhsm_theorem_completion_report() -> FullBHSMTheoremCompletionReport:
    ht = build_full_ht_theorem_closure_report()
    if ht.final_result == FULL_HT_THEOREM_PROVEN:
        result = FULL_BHSM_THEOREM_PACKAGE_COMPLETE
    elif ht.final_result == BHSM_THEOREM_FAILURE:
        result = BHSM_THEOREM_FAILURE
    else:
        result = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    return FullBHSMTheoremCompletionReport(
        title="BHSM v2.5 Full BHSM Theorem Completion Decision",
        final_result=result,
        full_ht_result=ht.final_result,
        final_paper_allowed=result == FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
        theorem_complete=result == FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
        single_named_gap=ht.single_named_gap,
        recommended_next_branch=ht.recommended_next_branch,
        recommended_target_theorem=ht.recommended_target_theorem,
        exact_obstruction=ht.exact_obstruction,
        limitations=(
            "Final paper is not prepared unless the full theorem package is complete.",
            "This decision is limited to theorem status and does not alter frozen predictions.",
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


def export_full_bhsm_theorem_completion_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_full_bhsm_theorem_completion_report()), indent=2, sort_keys=True) + "\n")


def export_full_bhsm_theorem_completion_markdown(path: str | Path) -> None:
    report = build_full_bhsm_theorem_completion_report()
    lines = [
        "# BHSM v2.5 Full BHSM Theorem Completion Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Full H_T result: `{report.full_ht_result}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Single Named Gap",
        "",
        f"`{report.single_named_gap}`",
        "",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
        "",
        "## Exact Obstruction",
        "",
        report.exact_obstruction,
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
