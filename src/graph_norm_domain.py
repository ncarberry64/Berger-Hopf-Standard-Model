"""Graph-norm domain for the diagonal BHSM reference operator."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from essential_self_adjointness import (
    DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN,
    build_essential_self_adjointness_report,
)


GRAPH_NORM_DOMAIN_PROVEN = "GRAPH_NORM_DOMAIN_PROVEN"
GRAPH_NORM_DOMAIN_CANDIDATE = "GRAPH_NORM_DOMAIN_CANDIDATE"
GRAPH_NORM_DOMAIN_CONDITIONAL = "GRAPH_NORM_DOMAIN_CONDITIONAL"
GRAPH_NORM_DOMAIN_OPEN = "GRAPH_NORM_DOMAIN_OPEN"


@dataclass(frozen=True)
class GraphNormDomainReport:
    """Graph-norm domain report."""

    title: str
    graph_norm_formula: str
    graph_domain: str
    finite_core_dense_in_graph_norm: bool
    perturbation_compatibility_status: str
    reference_domain_for_relative_bound_bridge: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_graph_norm_domain_report() -> GraphNormDomainReport:
    """Build graph-norm report."""

    essential = build_essential_self_adjointness_report()
    core_proven = essential.status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
    perturbation_open = (
        "prove Hopf, boundary, sector-coupling, heat-lift, and complement-projector compatibility with the A0 graph domain",
    )
    return GraphNormDomainReport(
        title="BHSM v1.9 Graph-Norm Domain Report",
        graph_norm_formula="||x||_A0^2 = ||x||^2 + ||A0 x||^2",
        graph_domain="D(A0) = {x in l2 : sum lambda_n^2 |x_n|^2 < infinity}",
        finite_core_dense_in_graph_norm=core_proven,
        perturbation_compatibility_status="PERTURBATION_COMPATIBILITY_OPEN",
        reference_domain_for_relative_bound_bridge=core_proven,
        status=GRAPH_NORM_DOMAIN_PROVEN if core_proven else GRAPH_NORM_DOMAIN_OPEN,
        theorem_complete=core_proven,
        open_obligations=perturbation_open,
        limitations=(
            "The graph-norm domain is proven for the diagonal reference operator.",
            "Compatibility of all perturbations with this graph domain remains a Kato-Rellich precondition.",
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


def export_graph_norm_domain_json(path: str | Path) -> None:
    """Export graph-norm report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_graph_norm_domain_report()), indent=2, sort_keys=True) + "\n")


def export_graph_norm_domain_markdown(path: str | Path) -> None:
    """Export graph-norm report as Markdown."""

    report = build_graph_norm_domain_report()
    lines = [
        "# BHSM v1.9 Graph-Norm Domain Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Graph norm: `{report.graph_norm_formula}`",
        f"Graph domain: `{report.graph_domain}`",
        f"Finite core dense in graph norm: `{report.finite_core_dense_in_graph_norm}`",
        f"Reference domain for relative-bound bridge: `{report.reference_domain_for_relative_bound_bridge}`",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

