"""BHSM v2.14 graph-domain relevance of projector commutator control."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from projector_commutator_relative_bound import PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN, build_projector_commutator_relative_bound_report


PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT = "PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT"
PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_BLOCKED = "PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_BLOCKED"


@dataclass(frozen=True)
class ProjectorCommutatorDomainControlReport:
    title: str
    graph_norm_domain_status: str
    commutator_relative_bound_status: str
    pperp_DA0_subset_DA0: bool
    supports_pperp_DA0V_subset_DA0V: bool
    supports_lower_bound_transfer: bool
    closes_projector_graph_domain: bool
    next_gap_if_not_closed: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_projector_commutator_domain_control_report() -> ProjectorCommutatorDomainControlReport:
    graph = build_graph_norm_domain_report()
    bound = build_projector_commutator_relative_bound_report()
    supported = graph.status == GRAPH_NORM_DOMAIN_PROVEN and bound.status == PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN
    return ProjectorCommutatorDomainControlReport(
        title="BHSM v2.14 Projector Commutator Domain-Control Report",
        graph_norm_domain_status=graph.status,
        commutator_relative_bound_status=bound.status,
        pperp_DA0_subset_DA0=graph.status == GRAPH_NORM_DOMAIN_PROVEN,
        supports_pperp_DA0V_subset_DA0V=supported,
        supports_lower_bound_transfer=supported,
        closes_projector_graph_domain=False,
        next_gap_if_not_closed="PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP",
        status=PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT if supported else PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_BLOCKED,
        theorem_complete=supported,
        limitations=(
            "Commutator control is sufficient input for the next graph-domain proof.",
            "This branch deliberately does not close projector graph-domain stability itself.",
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


def export_projector_commutator_domain_control_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_commutator_domain_control_report()), indent=2, sort_keys=True) + "\n")


def export_projector_commutator_domain_control_markdown(path: str | Path) -> None:
    report = build_projector_commutator_domain_control_report()
    lines = [
        "# BHSM v2.14 Projector Commutator Domain-Control Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"P_perp D(A0) subset D(A0): `{report.pperp_DA0_subset_DA0}`",
        f"Supports P_perp D(A0+V) subset D(A0+V): `{report.supports_pperp_DA0V_subset_DA0V}`",
        f"Supports lower-bound transfer: `{report.supports_lower_bound_transfer}`",
        f"Closes projector graph-domain: `{report.closes_projector_graph_domain}`",
        f"Next gap if not closed: `{report.next_gap_if_not_closed}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
