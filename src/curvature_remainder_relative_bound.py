"""BHSM v2.8 relative-bound audit for the curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_kernel_action import REMAINDER_KERNEL_COMPLEMENT_OPEN, build_curvature_remainder_kernel_action_report


@dataclass(frozen=True)
class CurvatureRemainderRelativeBoundReport:
    title: str
    kernel_action_status: str
    inequality: str
    a_existing: float
    a_remainder: float | None
    b_remainder: float | None
    a_total: float | None
    a_total_less_than_one: bool | None
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_relative_bound_report() -> CurvatureRemainderRelativeBoundReport:
    kernel = build_curvature_remainder_kernel_action_report()
    return CurvatureRemainderRelativeBoundReport(
        title="BHSM v2.8 Curvature Remainder Relative Bound Report",
        kernel_action_status=kernel.status,
        inequality="||R_bundle psi|| <= a_R ||A0 psi|| + b_R ||psi||",
        a_existing=0.0,
        a_remainder=None,
        b_remainder=None,
        a_total=None,
        a_total_less_than_one=None,
        status="REMAINDER_RELATIVE_BOUND_OPEN" if kernel.status == REMAINDER_KERNEL_COMPLEMENT_OPEN else "REMAINDER_RELATIVE_BOUND_CONDITIONAL",
        theorem_complete=False,
        limitations=(
            "No explicit R_bundle operator is available, so no relative-bound constants are derived.",
            "The condition a_total < 1 is not evaluated for the missing remainder.",
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


def export_curvature_remainder_relative_bound_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_relative_bound_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_relative_bound_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_relative_bound_report()
    lines = [
        "# BHSM v2.8 Curvature Remainder Relative Bound Report",
        "",
        f"Kernel action status: `{report.kernel_action_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| inequality | `{report.inequality}` |",
        f"| a_existing | `{report.a_existing}` |",
        f"| a_remainder | `{report.a_remainder}` |",
        f"| b_remainder | `{report.b_remainder}` |",
        f"| a_total | `{report.a_total}` |",
        f"| a_total < 1 | `{report.a_total_less_than_one}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
