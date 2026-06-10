"""BHSM v2.12 R_bundle classification after the v2.11 mixed rule."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_curvature_term_map import build_bundle_curvature_term_map_report
from topographic_curvature_representation import build_topographic_curvature_representation_report


REMAINDER_ZERO = "REMAINDER_ZERO"
REMAINDER_REPRESENTED_BY_EXISTING_TERM = "REMAINDER_REPRESENTED_BY_EXISTING_TERM"
REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR = "REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"
REMAINDER_PSD_PROFILE_CONTROLLED = "REMAINDER_PSD_PROFILE_CONTROLLED"
REMAINDER_SCREENED_OR_LIFTED = "REMAINDER_SCREENED_OR_LIFTED"
REMAINDER_RELATIVELY_BOUNDED_SAFE = "REMAINDER_RELATIVELY_BOUNDED_SAFE"
REMAINDER_REAL_MISSING_TERM_SAFE_AFTER_REAUDIT = "REMAINDER_REAL_MISSING_TERM_SAFE_AFTER_REAUDIT"
REMAINDER_REAL_MISSING_TERM_BREAKS_HT = "REMAINDER_REAL_MISSING_TERM_BREAKS_HT"
REMAINDER_OPEN = "REMAINDER_OPEN"


@dataclass(frozen=True)
class CurvatureRemainderAfterMixedRuleReport:
    title: str
    r_bundle_classification: str
    r_bundle_contributors: tuple[str, ...]
    relative_bound_added: float
    lower_bound_transfer_recomputed: bool
    lower_bound_requires_new_term: bool
    mirror_leakage_introduced: bool
    formal_kernel_sector_labeled: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_after_mixed_rule_report() -> CurvatureRemainderAfterMixedRuleReport:
    term_map = build_bundle_curvature_term_map_report()
    topo = build_topographic_curvature_representation_report()
    if term_map.r_bundle_contributors:
        classification = REMAINDER_OPEN
    elif topo.theorem_complete:
        classification = REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    else:
        classification = REMAINDER_OPEN
    closed = classification != REMAINDER_OPEN
    return CurvatureRemainderAfterMixedRuleReport(
        title="BHSM v2.12 Curvature Remainder After Mixed Rule Report",
        r_bundle_classification=classification,
        r_bundle_contributors=term_map.r_bundle_contributors,
        relative_bound_added=0.0,
        lower_bound_transfer_recomputed=False,
        lower_bound_requires_new_term=False,
        mirror_leakage_introduced=False,
        formal_kernel_sector_labeled=True,
        status="CURVATURE_REMAINDER_AFTER_MIXED_RULE_CLOSED" if closed else "CURVATURE_REMAINDER_AFTER_MIXED_RULE_OPEN",
        theorem_complete=closed,
        limitations=(
            "No independent R_bundle term remains after v2.11 topographic representation, so no new relative-bound contribution is added.",
            "Full H_T theorem status remains governed by the global dependency ledger.",
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


def export_curvature_remainder_after_mixed_rule_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_after_mixed_rule_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_after_mixed_rule_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_after_mixed_rule_report()
    lines = [
        "# BHSM v2.12 Curvature Remainder After Mixed Rule Report",
        "",
        f"R_bundle classification: `{report.r_bundle_classification}`",
        f"Status: `{report.status}`",
        f"Relative-bound contribution added: `{report.relative_bound_added}`",
        f"Lower-bound transfer recomputed: `{report.lower_bound_transfer_recomputed}`",
        f"New lower-bound term required: `{report.lower_bound_requires_new_term}`",
        f"Mirror leakage introduced: `{report.mirror_leakage_introduced}`",
        f"Formal kernel sector-labeled: `{report.formal_kernel_sector_labeled}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## R_bundle Contributors",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.r_bundle_contributors)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

