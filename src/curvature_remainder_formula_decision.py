"""BHSM v2.8 final decision for curvature remainder formula and bound."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_audit import REMAINDER_OPEN
from curvature_remainder_basis_action import REMAINDER_BASIS_ACTION_OPEN, build_curvature_remainder_basis_action_report
from curvature_remainder_formula import REMAINDER_FORMULA_OPEN, build_curvature_remainder_formula_report
from curvature_remainder_kernel_action import REMAINDER_KERNEL_COMPLEMENT_OPEN, build_curvature_remainder_kernel_action_report
from curvature_remainder_lower_bound_transfer import build_curvature_remainder_lower_bound_transfer_report
from curvature_remainder_relative_bound import build_curvature_remainder_relative_bound_report


CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED = "CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"

FINAL_CLASSIFICATIONS = {
    "REMAINDER_ZERO",
    "REMAINDER_REPRESENTED_BY_EXISTING_TERM",
    "REMAINDER_PSD_PROFILE_CONTROLLED",
    "REMAINDER_SCREENED_OR_LIFTED",
    "REMAINDER_RELATIVELY_BOUNDED_SAFE",
    "REMAINDER_REAL_MISSING_TERM_SAFE_AFTER_REAUDIT",
    "REMAINDER_REAL_MISSING_TERM_BREAKS_HT",
    REMAINDER_OPEN,
}


@dataclass(frozen=True)
class CurvatureRemainderFormulaDecision:
    title: str
    final_result: str
    formula_status: str
    basis_action_status: str
    kernel_action_status: str
    final_classification: str
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    complete_operator_identification_status: str
    final_paper_allowed: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_formula_decision() -> CurvatureRemainderFormulaDecision:
    formula = build_curvature_remainder_formula_report()
    basis = build_curvature_remainder_basis_action_report()
    kernel = build_curvature_remainder_kernel_action_report()
    relative = build_curvature_remainder_relative_bound_report()
    transfer = build_curvature_remainder_lower_bound_transfer_report()
    if formula.status == REMAINDER_FORMULA_OPEN or basis.status == REMAINDER_BASIS_ACTION_OPEN or kernel.status == REMAINDER_KERNEL_COMPLEMENT_OPEN:
        final_classification = REMAINDER_OPEN
        final_result = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_REMAINDER"
    elif transfer.ht_survives_if_included is False:
        final_classification = "REMAINDER_REAL_MISSING_TERM_BREAKS_HT"
        final_result = BHSM_THEOREM_FAILURE
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_FAILS"
    else:
        final_classification = "REMAINDER_RELATIVELY_BOUNDED_SAFE"
        final_result = CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG"
    return CurvatureRemainderFormulaDecision(
        title="BHSM v2.8 Curvature Remainder Formula and Bound Decision",
        final_result=final_result,
        formula_status=formula.status,
        basis_action_status=basis.status,
        kernel_action_status=kernel.status,
        final_classification=final_classification,
        exact_remaining_gap="COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP",
        recommended_next_branch="bhsm-v2.9-complete-bundle-connection-curvature",
        recommended_target_theorem="COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP",
        complete_operator_identification_status=operator_status,
        final_paper_allowed=False,
        theorem_complete=final_result == CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED,
        limitations=(
            "The formal Lichnerowicz expression is written, but the complete BHSM bundle connection curvature formula is not derived.",
            "No zero, represented, PSD, screened, or relatively bounded classification is adopted without the missing formula/action.",
            "Final paper preparation remains blocked.",
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


def export_curvature_remainder_formula_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_formula_decision()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_formula_decision_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_formula_decision()
    lines = [
        "# BHSM v2.8 Curvature Remainder Formula and Bound Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Final classification: `{report.final_classification}`",
        f"Formula status: `{report.formula_status}`",
        f"Basis-action status: `{report.basis_action_status}`",
        f"Kernel-action status: `{report.kernel_action_status}`",
        f"Complete-operator status: `{report.complete_operator_identification_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
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
