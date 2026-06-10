"""BHSM v2.7 lower-bound audit for the bundle-curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_audit import (
    REMAINDER_RELATIVELY_BOUNDED_SAFE,
    REMAINDER_PSD_PROFILE_CONTROLLED,
    SAFE_REMAINDER_CLASSIFICATIONS,
    build_curvature_remainder_audit_report,
)


@dataclass(frozen=True)
class CurvatureRemainderBoundReport:
    title: str
    remainder_classification: str
    symmetric: bool | None
    psd_or_lower_bounded: bool | None
    a_existing: float
    a_remainder: float | None
    b_remainder: float | None
    a_total: float | None
    a_total_less_than_one: bool | None
    lower_bound_recomputed: bool
    lower_bound_safe: bool
    no_new_low_energy_state: bool | None
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_bound_report() -> CurvatureRemainderBoundReport:
    """Return bound status for the audited remainder without inventing constants."""

    audit = build_curvature_remainder_audit_report()
    safe = audit.final_classification in SAFE_REMAINDER_CLASSIFICATIONS
    bounded_safe = audit.final_classification in {REMAINDER_RELATIVELY_BOUNDED_SAFE, REMAINDER_PSD_PROFILE_CONTROLLED}
    return CurvatureRemainderBoundReport(
        title="BHSM v2.7 Curvature Remainder Bound Report",
        remainder_classification=audit.final_classification,
        symmetric=None,
        psd_or_lower_bounded=None,
        a_existing=0.0,
        a_remainder=None,
        b_remainder=None,
        a_total=None,
        a_total_less_than_one=None,
        lower_bound_recomputed=bounded_safe,
        lower_bound_safe=safe and bounded_safe,
        no_new_low_energy_state=None,
        theorem_complete=safe,
        limitations=(
            "No a_R,b_R constants are supplied because the operator formula is not derived.",
            "Lower-bound transfer is not recomputed for an OPEN remainder.",
            "A future branch must derive a formula or prove PSD/screening/representation before marking this safe.",
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


def export_curvature_remainder_bound_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_bound_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_bound_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_bound_report()
    lines = [
        "# BHSM v2.7 Curvature Remainder Bound Report",
        "",
        f"Remainder classification: `{report.remainder_classification}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| symmetric | `{report.symmetric}` |",
        f"| PSD or lower bounded | `{report.psd_or_lower_bounded}` |",
        f"| a_existing | `{report.a_existing}` |",
        f"| a_remainder | `{report.a_remainder}` |",
        f"| b_remainder | `{report.b_remainder}` |",
        f"| a_total | `{report.a_total}` |",
        f"| a_total < 1 | `{report.a_total_less_than_one}` |",
        f"| lower-bound recomputed | `{report.lower_bound_recomputed}` |",
        f"| lower-bound safe | `{report.lower_bound_safe}` |",
        f"| no new low-energy state | `{report.no_new_low_energy_state}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
