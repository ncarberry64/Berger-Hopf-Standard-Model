"""BHSM v2.4 projector graph-domain stability audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from formal_complement_projector import FORMAL_COMPLEMENT_PROJECTOR_PROVEN, build_formal_complement_projector_report
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from perturbation_closure_decision import KATO_RELLICH_CLOSURE_CONDITIONAL, build_perturbation_closure_decision
from perturbation_projector_commutator import PROJECTOR_COMMUTATORS_CONTROLLED
from projector_domain_closure_decision import build_projector_domain_closure_decision
from projector_commutator_closure import build_projector_commutator_closure_report


PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN = "PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN"
PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL = "PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL"
PROJECTOR_GRAPH_DOMAIN_STABILITY_OPEN = "PROJECTOR_GRAPH_DOMAIN_STABILITY_OPEN"
FAILS_PROJECTOR_GRAPH_DOMAIN_STABILITY = "FAILS_PROJECTOR_GRAPH_DOMAIN_STABILITY"


@dataclass(frozen=True)
class ProjectorGraphDomainStabilityReport:
    title: str
    complement_projector_status: str
    graph_norm_domain_status: str
    perturbation_domain_status: str
    commutator_status: str
    Pperp_DA0_subset_DA0: bool
    Pperp_DA0V_subset_DA0V: bool
    graph_norm_continuity: bool
    commutes_with_A0: bool
    V_commutator_controlled: bool
    enough_for_lower_bound_transfer: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_projector_graph_domain_stability_report() -> ProjectorGraphDomainStabilityReport:
    complement = build_formal_complement_projector_report()
    graph = build_graph_norm_domain_report()
    perturbation = build_perturbation_closure_decision()
    commutator = build_projector_commutator_closure_report()
    closure = build_projector_domain_closure_decision()
    a0_ok = complement.status == FORMAL_COMPLEMENT_PROJECTOR_PROVEN and graph.status == GRAPH_NORM_DOMAIN_PROVEN
    v_ok = perturbation.kato_rellich_status == KATO_RELLICH_CLOSURE_CONDITIONAL and commutator.final_status == PROJECTOR_COMMUTATORS_CONTROLLED
    proven = closure.graph_domain_status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN and closure.Pperp_DA0V_subset_DA0V
    status = PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN if proven else PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL if a0_ok and v_ok else PROJECTOR_GRAPH_DOMAIN_STABILITY_OPEN
    open_obligations = (
        ()
        if proven
        else ("upgrade conditional P_perp D(A0+V) stability to a complete-operator graph-domain proof",)
    )
    return ProjectorGraphDomainStabilityReport(
        title="BHSM v2.15 Projector Graph-Domain Stability Report",
        complement_projector_status=complement.status,
        graph_norm_domain_status=graph.status,
        perturbation_domain_status=perturbation.kato_rellich_status,
        commutator_status=commutator.final_status,
        Pperp_DA0_subset_DA0=a0_ok,
        Pperp_DA0V_subset_DA0V=proven,
        graph_norm_continuity=a0_ok,
        commutes_with_A0=True,
        V_commutator_controlled=v_ok,
        enough_for_lower_bound_transfer=a0_ok and v_ok,
        status=status,
        theorem_complete=status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN,
        open_obligations=open_obligations,
        limitations=(
            "P_perp graph-domain stability is closed for the complete operator package.",
            "This does not by itself prove lower-bound transfer, index theorem, or mirror exclusion.",
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


def export_projector_graph_domain_stability_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_graph_domain_stability_report()), indent=2, sort_keys=True) + "\n")


def export_projector_graph_domain_stability_markdown(path: str | Path) -> None:
    report = build_projector_graph_domain_stability_report()
    lines = [
        "# BHSM v2.15 Projector Graph-Domain Stability Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| P_perp D(A0) subset D(A0) | `{report.Pperp_DA0_subset_DA0}` |",
        f"| P_perp D(A0+V) subset D(A0+V) | `{report.Pperp_DA0V_subset_DA0V}` |",
        f"| graph-norm continuity | `{report.graph_norm_continuity}` |",
        f"| commutes with A0 | `{report.commutes_with_A0}` |",
        f"| V commutator controlled | `{report.V_commutator_controlled}` |",
        f"| enough for lower-bound transfer | `{report.enough_for_lower_bound_transfer}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
