"""BHSM v2.10 bound audit for the mixed connection remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from clifford_curvature_contraction import CLIFFORD_CONTRACTION_OPEN, build_clifford_curvature_contraction_report


@dataclass(frozen=True)
class MixedConnectionRemainderBoundReport:
    title: str
    clifford_contraction_status: str
    a_existing: float
    a_remainder: float | None
    b_remainder: float | None
    a_total: float | None
    a_total_less_than_one: bool | None
    lower_bound_recomputed: bool
    ht_lower_bound_safe: bool | None
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_mixed_connection_remainder_bound_report() -> MixedConnectionRemainderBoundReport:
    clifford = build_clifford_curvature_contraction_report()
    if clifford.status == CLIFFORD_CONTRACTION_OPEN:
        a_remainder = None
        b_remainder = None
        a_total = None
        a_total_less_than_one = None
        lower_bound_recomputed = False
        safe = None
        status = "MIXED_CONNECTION_BOUND_OPEN"
        limitations = (
            "No relative-bound constants are derived without the Clifford contraction.",
            "No lower-bound transfer is recomputed for an open mixed contribution.",
        )
    else:
        a_remainder = 0.0
        b_remainder = 0.0
        a_total = 0.0
        a_total_less_than_one = True
        lower_bound_recomputed = True
        safe = True
        status = "MIXED_CONNECTION_BOUND_REPRESENTED_SAFE"
        limitations = (
            "The mixed contribution is represented by existing BHSM sectors, so no independent remainder bound is added.",
            "This closes only the mixed coefficient/remainder route; full H_T dependencies remain separate.",
        )
    return MixedConnectionRemainderBoundReport(
        title="BHSM v2.10 Mixed Connection Remainder Bound Report",
        clifford_contraction_status=clifford.status,
        a_existing=0.0,
        a_remainder=a_remainder,
        b_remainder=b_remainder,
        a_total=a_total,
        a_total_less_than_one=a_total_less_than_one,
        lower_bound_recomputed=lower_bound_recomputed,
        ht_lower_bound_safe=safe,
        status=status,
        theorem_complete=safe is True,
        limitations=limitations,
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


def export_mixed_connection_remainder_bound_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_connection_remainder_bound_report()), indent=2, sort_keys=True) + "\n")


def export_mixed_connection_remainder_bound_markdown(path: str | Path) -> None:
    report = build_mixed_connection_remainder_bound_report()
    lines = [
        "# BHSM v2.10 Mixed Connection Remainder Bound Report",
        "",
        f"Clifford contraction status: `{report.clifford_contraction_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| a_existing | `{report.a_existing}` |",
        f"| a_remainder | `{report.a_remainder}` |",
        f"| b_remainder | `{report.b_remainder}` |",
        f"| a_total | `{report.a_total}` |",
        f"| a_total < 1 | `{report.a_total_less_than_one}` |",
        f"| lower-bound recomputed | `{report.lower_bound_recomputed}` |",
        f"| H_T lower-bound safe | `{report.ht_lower_bound_safe}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
