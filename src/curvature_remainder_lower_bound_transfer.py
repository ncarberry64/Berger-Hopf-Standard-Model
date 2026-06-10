"""BHSM v2.8 lower-bound transfer audit for the curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_relative_bound import build_curvature_remainder_relative_bound_report


@dataclass(frozen=True)
class CurvatureRemainderLowerBoundTransferReport:
    title: str
    relative_bound_status: str
    nonzero_remainder_included: bool
    lower_bound_recomputed: bool
    ht_survives_if_included: bool | None
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_lower_bound_transfer_report() -> CurvatureRemainderLowerBoundTransferReport:
    relative = build_curvature_remainder_relative_bound_report()
    included = relative.a_remainder is not None or relative.b_remainder is not None
    return CurvatureRemainderLowerBoundTransferReport(
        title="BHSM v2.8 Curvature Remainder Lower-Bound Transfer Report",
        relative_bound_status=relative.status,
        nonzero_remainder_included=included,
        lower_bound_recomputed=included,
        ht_survives_if_included=None,
        status="REMAINDER_LOWER_BOUND_TRANSFER_OPEN",
        theorem_complete=False,
        limitations=(
            "A nonzero remainder is not inserted into the operator because its formula/action is not derived.",
            "Renewed lower-bound transfer is deferred until the missing formula and relative-bound constants exist.",
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


def export_curvature_remainder_lower_bound_transfer_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_lower_bound_transfer_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_lower_bound_transfer_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_lower_bound_transfer_report()
    lines = [
        "# BHSM v2.8 Curvature Remainder Lower-Bound Transfer Report",
        "",
        f"Relative-bound status: `{report.relative_bound_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| nonzero remainder included | `{report.nonzero_remainder_included}` |",
        f"| lower-bound recomputed | `{report.lower_bound_recomputed}` |",
        f"| H_T survives if included | `{report.ht_survives_if_included}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
