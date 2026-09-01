"""BHSM v2.5 projector graph-domain closure attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from projector_commutator_closure import build_projector_commutator_closure_report
from projector_graph_domain_stability import (
    PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL,
    PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN,
    build_projector_graph_domain_stability_report,
)


@dataclass(frozen=True)
class ProjectorGraphDomainClosureReport:
    title: str
    source_status: str
    commutator_status: str
    final_status: str
    theorem_complete: bool
    exact_obstruction: str
    limitations: tuple[str, ...]


def build_projector_graph_domain_closure_report() -> ProjectorGraphDomainClosureReport:
    report = build_projector_graph_domain_stability_report()
    commutator = build_projector_commutator_closure_report()
    proven = report.status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN and commutator.theorem_complete
    obstruction = (
        "No obstruction: P_perp preserves D(A0) and D(A0+V)."
        if proven
        else "P_perp D(A0) is controlled and commutator control is proven, but P_perp D(A0+V) still needs a standalone graph-domain stability proof."
    )
    return ProjectorGraphDomainClosureReport(
        title="BHSM v2.5 Projector Graph-Domain Closure Attempt",
        source_status=report.status,
        commutator_status=commutator.final_status,
        final_status=PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN if proven else PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL,
        theorem_complete=proven,
        exact_obstruction=obstruction,
        limitations=(
            "Projector graph-domain stability is not marked proven until the full P_perp D(A0+V) graph-domain argument is complete.",
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


def export_projector_graph_domain_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_graph_domain_closure_report()), indent=2, sort_keys=True) + "\n")


def export_projector_graph_domain_closure_markdown(path: str | Path) -> None:
    report = build_projector_graph_domain_closure_report()
    lines = [
        "# BHSM v2.5 Projector Graph-Domain Closure Attempt",
        "",
        f"Source status: `{report.source_status}`",
        f"Commutator status: `{report.commutator_status}`",
        f"Final status: `{report.final_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Exact Obstruction",
        "",
        report.exact_obstruction,
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
