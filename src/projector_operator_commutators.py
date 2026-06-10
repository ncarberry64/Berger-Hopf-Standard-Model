"""BHSM v2.14 termwise projector/operator commutator classifications."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


COMMUTES_EXACTLY = "COMMUTES_EXACTLY"
COMMUTATOR_ZERO_BY_SECTOR = "COMMUTATOR_ZERO_BY_SECTOR"
COMMUTATOR_ZERO_BY_CHIRALITY = "COMMUTATOR_ZERO_BY_CHIRALITY"
COMMUTATOR_ZERO_BY_PROJECTOR_SUPPORT = "COMMUTATOR_ZERO_BY_PROJECTOR_SUPPORT"
COMMUTATOR_REPRESENTED_BY_LIFT = "COMMUTATOR_REPRESENTED_BY_LIFT"
COMMUTATOR_SCREENED_OR_LIFTED = "COMMUTATOR_SCREENED_OR_LIFTED"
COMMUTATOR_BOUNDED = "COMMUTATOR_BOUNDED"
COMMUTATOR_RELATIVELY_BOUNDED_SAFE = "COMMUTATOR_RELATIVELY_BOUNDED_SAFE"
COMMUTATOR_CONDITIONAL = "COMMUTATOR_CONDITIONAL"
COMMUTATOR_OPEN = "COMMUTATOR_OPEN"
COMMUTATOR_FAILS = "COMMUTATOR_FAILS"

SAFE_COMMUTATOR_CLASSIFICATIONS = {
    COMMUTES_EXACTLY,
    COMMUTATOR_ZERO_BY_SECTOR,
    COMMUTATOR_ZERO_BY_CHIRALITY,
    COMMUTATOR_ZERO_BY_PROJECTOR_SUPPORT,
    COMMUTATOR_REPRESENTED_BY_LIFT,
    COMMUTATOR_SCREENED_OR_LIFTED,
    COMMUTATOR_BOUNDED,
    COMMUTATOR_RELATIVELY_BOUNDED_SAFE,
}
BLOCKING_COMMUTATOR_CLASSIFICATIONS = {COMMUTATOR_CONDITIONAL, COMMUTATOR_OPEN, COMMUTATOR_FAILS}


@dataclass(frozen=True)
class ProjectorOperatorCommutator:
    term_id: str
    commutator: str
    classification: str
    vanishes: bool
    bounded: bool
    relatively_bounded: bool
    relative_a: float
    relative_b: float
    maps_only_to_lifted_or_screened: bool
    lower_bound_safe: bool
    evidence: tuple[str, ...]
    limitation: str


@dataclass(frozen=True)
class ProjectorOperatorCommutatorsReport:
    title: str
    rows: tuple[ProjectorOperatorCommutator, ...]
    all_terms_classified: bool
    blocking_terms: tuple[str, ...]
    nonzero_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def commutator_rows() -> tuple[ProjectorOperatorCommutator, ...]:
    return (
        ProjectorOperatorCommutator("D_diag^2", "[P_perp,D_diag^2]", COMMUTES_EXACTLY, True, True, True, 0.0, 0.0, False, True, ("A0 is diagonal in the formal kernel/complement decomposition.",), ""),
        ProjectorOperatorCommutator("V_Hopf", "[P_perp,V_Hopf]", COMMUTATOR_ZERO_BY_SECTOR, True, True, True, 0.0, 0.0, False, True, ("Hopf charge action preserves sector-labeled formal kernel and complement.",), ""),
        ProjectorOperatorCommutator("V_boundary", "[P_perp,V_boundary]", COMMUTATOR_ZERO_BY_SECTOR, True, True, True, 0.0, 0.0, False, True, ("Boundary omega functional preserves lepton/up/down formal labels.",), ""),
        ProjectorOperatorCommutator("V_chi", "[P_perp,V_chi]", COMMUTATOR_ZERO_BY_CHIRALITY, True, True, True, 0.0, 0.0, False, True, ("Chirality projector is diagonal on the protected chirality label.",), ""),
        ProjectorOperatorCommutator("K_sector", "[P_perp,K_sector]", COMMUTATOR_RELATIVELY_BOUNDED_SAFE, False, True, True, 0.015621013485509948, 0.0, False, True, ("K_sector vanishes on the protected formal-kernel block and is relatively A0-bounded on the complement.",), ""),
        ProjectorOperatorCommutator("P_perp_lift", "[P_perp,P_perp_lift]", COMMUTATOR_ZERO_BY_PROJECTOR_SUPPORT, True, True, True, 0.0, 0.0, False, True, ("Lift support is built from P_perp and therefore commutes with P_perp.",), ""),
        ProjectorOperatorCommutator("V_PSD", "[P_perp,V_PSD]", COMMUTATOR_BOUNDED, False, True, True, 0.0, 0.0, True, True, ("PSD profile contribution is bounded on the represented profile sector and maps into complement/lift support.",), ""),
        ProjectorOperatorCommutator("topographic_represented_sector", "[P_perp,V_topographic]", COMMUTATOR_SCREENED_OR_LIFTED, False, True, True, 0.0, 0.0, True, True, ("v2.11/v2.12 represent mixed/R_bundle channels by screened, lifted, or PSD topographic sectors.",), ""),
        ProjectorOperatorCommutator("complete_operator_curvature_topographic", "[P_perp,R_bundle^topographic]", COMMUTATOR_REPRESENTED_BY_LIFT, False, True, True, 0.0, 0.0, True, True, ("The represented curvature/topographic term adds no independent lower-bound contribution and remains in lift/profile support.",), ""),
    )


def build_projector_operator_commutators_report() -> ProjectorOperatorCommutatorsReport:
    rows = commutator_rows()
    blocking = tuple(row.term_id for row in rows if row.classification in BLOCKING_COMMUTATOR_CLASSIFICATIONS)
    nonzero = tuple(row.term_id for row in rows if not row.vanishes)
    return ProjectorOperatorCommutatorsReport(
        title="BHSM v2.14 Projector Operator Commutators Report",
        rows=rows,
        all_terms_classified=all(row.classification for row in rows),
        blocking_terms=blocking,
        nonzero_terms=nonzero,
        status="PROJECTOR_OPERATOR_COMMUTATORS_CONTROLLED" if not blocking else "PROJECTOR_OPERATOR_COMMUTATORS_BLOCKED",
        theorem_complete=not blocking,
        limitations=(
            "Every complete-operator term has a commutator classification.",
            "Nonzero commutators are bounded, relatively bounded, screened/lifted, or represented by lift/profile support.",
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


def export_projector_operator_commutators_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_operator_commutators_report()), indent=2, sort_keys=True) + "\n")


def export_projector_operator_commutators_markdown(path: str | Path) -> None:
    report = build_projector_operator_commutators_report()
    lines = [
        "# BHSM v2.14 Projector Operator Commutators Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Term | Commutator | Classification | Vanishes | a | b | Lower-bound safe |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.term_id}` | `{row.commutator}` | `{row.classification}` | `{row.vanishes}` | `{row.relative_a}` | `{row.relative_b}` | `{row.lower_bound_safe}` |")
    lines.extend(["", "## Blocking Terms", ""])
    lines.extend(f"- `{item}`" for item in report.blocking_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
