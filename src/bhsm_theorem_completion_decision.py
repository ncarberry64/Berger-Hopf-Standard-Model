"""Final BHSM theorem-completion decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_bhsm_theorem import (
    FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
    BHSM_THEOREM_PACKAGE_INCOMPLETE,
    FullBHSMTheoremReport,
    build_full_bhsm_theorem_report,
)


BHSM_THEOREM_CANDIDATE_WITH_OPEN_ASSUMPTIONS = "BHSM_THEOREM_CANDIDATE_WITH_OPEN_ASSUMPTIONS"
BHSM_STRONG_SCAFFOLD_REMAINS = "BHSM_STRONG_SCAFFOLD_REMAINS"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class BHSMTheoremCompletionDecision:
    """Final theorem-completion decision row."""

    theorem_report: FullBHSMTheoremReport
    final_status: str
    final_paper_allowed: bool
    zenodo_release_allowed: bool
    exact_next_action: str
    rationale: tuple[str, ...]
    limitations: tuple[str, ...]


def build_bhsm_theorem_completion_decision() -> BHSMTheoremCompletionDecision:
    """Build the final theorem-completion decision."""

    report = build_full_bhsm_theorem_report()
    hard_failure = any("FAIL" in node.gate_status for node in report.nodes)
    if report.status == FULL_BHSM_THEOREM_PACKAGE_COMPLETE:
        final_status = FULL_BHSM_THEOREM_PACKAGE_COMPLETE
    elif hard_failure:
        final_status = BHSM_THEOREM_FAILURE
    elif report.status == BHSM_THEOREM_PACKAGE_INCOMPLETE and report.open_obligations:
        final_status = BHSM_THEOREM_CANDIDATE_WITH_OPEN_ASSUMPTIONS
    else:
        final_status = BHSM_STRONG_SCAFFOLD_REMAINS
    final_paper_allowed = final_status == FULL_BHSM_THEOREM_PACKAGE_COMPLETE
    return BHSMTheoremCompletionDecision(
        theorem_report=report,
        final_status=final_status,
        final_paper_allowed=final_paper_allowed,
        zenodo_release_allowed=final_paper_allowed,
        exact_next_action=(
            "Do not prepare final paper/Zenodo release; attack the full operator domain, "
            "topological index, mirror exclusion, and infinite-basis H_T complement proof obligations."
            if not final_paper_allowed
            else "Proceed to final paper packaging."
        ),
        rationale=(
            "The frozen prediction package remains intact.",
            "The theorem graph is coherent and dependency-clean at scaffold level.",
            "Named theorem obligations remain open, so full theorem completion is not honest yet.",
        ),
        limitations=(
            "This decision does not alter BHSM_BARE_V1 or BHSM_DRESSED_V1_CANDIDATE.",
            "This decision does not claim first-principles theorem closure.",
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


def export_bhsm_theorem_completion_decision_json(path: str | Path) -> None:
    """Export the completion decision as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_bhsm_theorem_completion_decision()), indent=2, sort_keys=True) + "\n")


def export_bhsm_theorem_completion_decision_markdown(path: str | Path) -> None:
    """Export the completion decision as Markdown."""

    decision = build_bhsm_theorem_completion_decision()
    report = decision.theorem_report
    lines = [
        "# BHSM Theorem Completion Decision",
        "",
        f"Final status: `{decision.final_status}`",
        f"Full theorem package status: `{report.status}`",
        f"Final paper allowed: `{decision.final_paper_allowed}`",
        f"Zenodo release allowed: `{decision.zenodo_release_allowed}`",
        "",
        "## Rationale",
        "",
        *[f"- {item}" for item in decision.rationale],
        "",
        "## Exact Next Action",
        "",
        decision.exact_next_action,
        "",
        "## Open Obligations",
        "",
        *[f"- {item}" for item in report.open_obligations],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in decision.limitations],
        "",
    ]
    Path(path).write_text("\n".join(lines))

