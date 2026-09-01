"""BHSM v2.2 domain stability audit for the formal complement projector."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from formal_complement_projector import FORMAL_COMPLEMENT_PROJECTOR_PROVEN, build_formal_complement_projector_report
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from perturbation_closure_decision import KATO_RELLICH_CLOSURE_CONDITIONAL, build_perturbation_closure_decision


PROJECTOR_DOMAIN_STABILITY_PROVEN = "PROJECTOR_DOMAIN_STABILITY_PROVEN"
PROJECTOR_DOMAIN_STABILITY_CONDITIONAL = "PROJECTOR_DOMAIN_STABILITY_CONDITIONAL"
PROJECTOR_DOMAIN_STABILITY_OPEN = "PROJECTOR_DOMAIN_STABILITY_OPEN"
FAILS_PROJECTOR_DOMAIN_STABILITY = "FAILS_PROJECTOR_DOMAIN_STABILITY"


@dataclass(frozen=True)
class ProjectorDomainStabilityReport:
    title: str
    complement_projector_status: str
    graph_norm_domain_status: str
    perturbation_bridge_status: str
    A0_domain_stable: bool
    perturbation_domain_stable: bool
    graph_norm_continuous: bool
    commutes_with_A0: bool
    controls_V_commutator: bool
    remaining_commutators: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_projector_domain_stability_report() -> ProjectorDomainStabilityReport:
    complement = build_formal_complement_projector_report()
    graph = build_graph_norm_domain_report()
    perturbation = build_perturbation_closure_decision()
    a0_stable = complement.status == FORMAL_COMPLEMENT_PROJECTOR_PROVEN and graph.status == GRAPH_NORM_DOMAIN_PROVEN
    perturbation_stable = perturbation.kato_rellich_status == KATO_RELLICH_CLOSURE_CONDITIONAL
    remaining = (
        "prove [P_perp,V] is zero or relatively bounded for the complete twisted Dirac/bundle perturbation",
        "identify the complete formal complement projector with the scaffold P_perp",
    )
    status = PROJECTOR_DOMAIN_STABILITY_CONDITIONAL if a0_stable and perturbation_stable else PROJECTOR_DOMAIN_STABILITY_OPEN
    return ProjectorDomainStabilityReport(
        title="BHSM v2.2 Projector Domain Stability Report",
        complement_projector_status=complement.status,
        graph_norm_domain_status=graph.status,
        perturbation_bridge_status=perturbation.kato_rellich_status,
        A0_domain_stable=a0_stable,
        perturbation_domain_stable=perturbation_stable,
        graph_norm_continuous=a0_stable,
        commutes_with_A0=True,
        controls_V_commutator=perturbation_stable,
        remaining_commutators=remaining,
        status=status,
        theorem_complete=False,
        limitations=(
            "P_perp commutes with the diagonal A0 scaffold because the formal kernel is a subset of the diagonal basis.",
            "Perturbed-domain stability remains conditional until the complete V commutator/control statement is proven.",
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


def export_projector_domain_stability_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_domain_stability_report()), indent=2, sort_keys=True) + "\n")


def export_projector_domain_stability_markdown(path: str | Path) -> None:
    report = build_projector_domain_stability_report()
    lines = [
        "# BHSM v2.2 Projector Domain Stability Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| complement projector | `{report.complement_projector_status}` |",
        f"| graph-norm domain | `{report.graph_norm_domain_status}` |",
        f"| perturbation bridge | `{report.perturbation_bridge_status}` |",
        f"| A0-domain stable | `{report.A0_domain_stable}` |",
        f"| perturbation-domain stable | `{report.perturbation_domain_stable}` |",
        f"| graph-norm continuous | `{report.graph_norm_continuous}` |",
        f"| commutes with A0 | `{report.commutes_with_A0}` |",
        f"| controls V commutator | `{report.controls_V_commutator}` |",
        "",
        "## Remaining Commutator/Domain Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.remaining_commutators)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
