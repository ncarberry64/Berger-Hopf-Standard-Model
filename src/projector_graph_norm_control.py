"""BHSM v2.15 projector graph-norm control report."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from interacting_graph_domain import INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN, build_interacting_graph_domain_report
from projector_domain_invariance import build_projector_domain_invariance_report


PROJECTOR_GRAPH_NORM_CONTROL_PROVEN = "PROJECTOR_GRAPH_NORM_CONTROL_PROVEN"
PROJECTOR_GRAPH_NORM_CONTROL_CONDITIONAL = "PROJECTOR_GRAPH_NORM_CONTROL_CONDITIONAL"
PROJECTOR_GRAPH_NORM_CONTROL_OPEN = "PROJECTOR_GRAPH_NORM_CONTROL_OPEN"
PROJECTOR_GRAPH_NORM_CONTROL_FAILS = "PROJECTOR_GRAPH_NORM_CONTROL_FAILS"


@dataclass(frozen=True)
class ProjectorGraphNormControlReport:
    title: str
    interacting_domain_status: str
    domain_invariance_status: str
    graph_norm_equivalence: bool
    projector_bounded_on_H: bool
    projector_bounded_on_D_A0: bool
    projector_bounded_on_D_A0V: bool
    control_constant: float
    inequality: str
    status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def build_projector_graph_norm_control_report() -> ProjectorGraphNormControlReport:
    domain = build_interacting_graph_domain_report()
    invariance = build_projector_domain_invariance_report()
    proven = (
        domain.status == INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN
        and invariance.Pperp_DA0V_subset_DA0V
        and domain.graph_norms_equivalent
    )
    # Orthogonal projectors are H-bounded with norm one.  The interacting
    # graph-norm bound uses graph-norm equivalence and the commutator-controlled
    # termwise invariance from v2.14/v2.15.
    constant = domain.equivalence_upper_constant / domain.equivalence_lower_constant if domain.equivalence_lower_constant > 0 else float("inf")
    return ProjectorGraphNormControlReport(
        title="BHSM v2.15 Projector Graph-Norm Control Report",
        interacting_domain_status=domain.status,
        domain_invariance_status=invariance.status,
        graph_norm_equivalence=domain.graph_norms_equivalent,
        projector_bounded_on_H=True,
        projector_bounded_on_D_A0=domain.D_A0V_equals_D_A0,
        projector_bounded_on_D_A0V=proven,
        control_constant=constant,
        inequality="||P_perp psi||_(A0+V) <= C ||psi||_(A0+V)",
        status=PROJECTOR_GRAPH_NORM_CONTROL_PROVEN if proven else PROJECTOR_GRAPH_NORM_CONTROL_OPEN,
        theorem_complete=proven,
        assumptions=(
            "P_perp is an orthogonal bounded projector on the formal sector-labeled Hilbert space.",
            "D(A0+V)=D(A0) and the graph norms are equivalent.",
            "All nonzero commutators are controlled by v2.14.",
        ),
        limitations=(
            "The graph-norm control closes projector-domain stability only.",
            "Lower-bound transfer and index/mirror theorem gates remain separate.",
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


def export_projector_graph_norm_control_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_graph_norm_control_report()), indent=2, sort_keys=True) + "\n")


def export_projector_graph_norm_control_markdown(path: str | Path) -> None:
    report = build_projector_graph_norm_control_report()
    lines = [
        "# BHSM v2.15 Projector Graph-Norm Control Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Inequality: `{report.inequality}`",
        f"Control constant: `{report.control_constant}`",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| interacting domain | `{report.interacting_domain_status}` |",
        f"| domain invariance | `{report.domain_invariance_status}` |",
        f"| graph norm equivalence | `{report.graph_norm_equivalence}` |",
        f"| bounded on H | `{report.projector_bounded_on_H}` |",
        f"| bounded on D(A0) | `{report.projector_bounded_on_D_A0}` |",
        f"| bounded on D(A0+V) | `{report.projector_bounded_on_D_A0V}` |",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend(f"- {item}" for item in report.assumptions)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
