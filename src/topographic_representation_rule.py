"""BHSM v2.11 representation audit for mixed Hopf/base/boundary/coframe terms."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_separation_axiom import BUNDLE_SEPARATION_AXIOM_FORMALIZED, build_bundle_separation_axiom_report


REPRESENTED_BY_V_BOUNDARY = "REPRESENTED_BY_V_BOUNDARY"
REPRESENTED_BY_V_PSD_PROFILE = "REPRESENTED_BY_V_PSD_PROFILE"
REPRESENTED_BY_SCALAR_TOPOGRAPHIC_SCREENED_SECTOR = "REPRESENTED_BY_SCALAR_TOPOGRAPHIC_SCREENED_SECTOR"
REPRESENTED_BY_P_PERP_LIFT = "REPRESENTED_BY_P_PERP_LIFT"
ZERO_BY_COMPATIBILITY = "ZERO_BY_COMPATIBILITY"
RELATIVELY_BOUNDED_SAFE = "RELATIVELY_BOUNDED_SAFE"
REAL_MISSING_TERM = "REAL_MISSING_TERM"
TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED = "TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED"
TOPOGRAPHIC_REPRESENTATION_RULE_OPEN = "TOPOGRAPHIC_REPRESENTATION_RULE_OPEN"


@dataclass(frozen=True)
class TopographicRepresentationRow:
    slot: str
    representation: str
    mapped_operator_term: str
    independent_bundle_curvature_forbidden: bool
    contributes_to_r_bundle: bool
    classification: str
    limitation: str


@dataclass(frozen=True)
class TopographicRepresentationRuleReport:
    title: str
    axiom_status: str
    rows: tuple[TopographicRepresentationRow, ...]
    all_slots_represented_or_zero: bool
    real_missing_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def topographic_representation_rows() -> tuple[TopographicRepresentationRow, ...]:
    return (
        TopographicRepresentationRow("hopf_fiber_base_cross", "zero/cancelled by vertical-horizontal compatibility", "A0 + V_Hopf bookkeeping only", True, False, ZERO_BY_COMPATIBILITY, "No independent bundle curvature coefficient is introduced."),
        TopographicRepresentationRow("base_boundary_cross", "represented by boundary functional sector", "V_boundary", True, False, REPRESENTED_BY_V_BOUNDARY, "The boundary action remains the place where base-node phase enters."),
        TopographicRepresentationRow("boundary_coframe_cross", "represented by profile/coframe topographic sector", "V_PSD/profile", True, False, REPRESENTED_BY_V_PSD_PROFILE, "Full scalar/topographic proof remains separate from this coefficient rule."),
        TopographicRepresentationRow("hopf_boundary_coframe_mixed", "represented by scalar/topographic screened sector", "scalar/topographic screened sector", True, False, REPRESENTED_BY_SCALAR_TOPOGRAPHIC_SCREENED_SECTOR, "This classifies the mixed channel as represented rather than free."),
        TopographicRepresentationRow("chirality_dependence", "represented by chiral projector and lift package", "V_chi + P_perp_lift", True, False, REPRESENTED_BY_P_PERP_LIFT, "Mirror exclusion remains a separate dependency in the full theorem chain."),
        TopographicRepresentationRow("sector_dependence", "represented by sector boundary functional", "V_boundary + K_sector", True, False, REPRESENTED_BY_V_BOUNDARY, "Sector dependence is not a fitted coefficient; it follows the formal sector-labeled boundary functional."),
    )


def build_topographic_representation_rule_report() -> TopographicRepresentationRuleReport:
    axiom = build_bundle_separation_axiom_report()
    rows = topographic_representation_rows()
    missing = tuple(row.slot for row in rows if row.classification == REAL_MISSING_TERM)
    status = (
        TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED
        if axiom.status == BUNDLE_SEPARATION_AXIOM_FORMALIZED and not missing
        else TOPOGRAPHIC_REPRESENTATION_RULE_OPEN
    )
    return TopographicRepresentationRuleReport(
        title="BHSM v2.11 Topographic Representation Rule Report",
        axiom_status=axiom.status,
        rows=rows,
        all_slots_represented_or_zero=not missing,
        real_missing_terms=missing,
        status=status,
        theorem_complete=status == TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED,
        limitations=(
            "Representation of the mixed coefficient rule does not by itself prove scalar/topographic decoupling or the full H_T theorem.",
            "The rule forbids independent fitted mixed coefficients.",
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


def export_topographic_representation_rule_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_topographic_representation_rule_report()), indent=2, sort_keys=True) + "\n")


def export_topographic_representation_rule_markdown(path: str | Path) -> None:
    report = build_topographic_representation_rule_report()
    lines = [
        "# BHSM v2.11 Topographic Representation Rule Report",
        "",
        f"Axiom status: `{report.axiom_status}`",
        f"Status: `{report.status}`",
        f"All slots represented or zero: `{report.all_slots_represented_or_zero}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Slot | Representation | Mapped operator term | Free coefficient forbidden | Contributes to R_bundle | Classification | Limitation |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.slot}` | {row.representation} | `{row.mapped_operator_term}` | `{row.independent_bundle_curvature_forbidden}` | `{row.contributes_to_r_bundle}` | `{row.classification}` | {row.limitation} |")
    lines.extend(["", "## Real Missing Terms", ""])
    lines.extend(f"- `{item}`" for item in report.real_missing_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

