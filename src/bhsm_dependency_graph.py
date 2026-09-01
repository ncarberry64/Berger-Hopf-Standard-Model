"""Integrated BHSM dependency graph for the completion campaign."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FROZEN_PREDICTION = "FROZEN_PREDICTION"
ACTION_DERIVED = "ACTION_DERIVED"
BOUNDARY_FUNCTIONAL_DERIVED = "BOUNDARY_FUNCTIONAL_DERIVED"
PARENT_ACTION_REDUCED = "PARENT_ACTION_REDUCED"
BASIS_REALIZED = "BASIS_REALIZED"
SEMI_ANALYTIC_SCAFFOLD = "SEMI_ANALYTIC_SCAFFOLD"
FINITE_BASIS_SCAFFOLD = "FINITE_BASIS_SCAFFOLD"
ADOPTION_CANDIDATE = "ADOPTION_CANDIDATE"
OPEN = "OPEN"
FORBIDDEN = "FORBIDDEN"


@dataclass(frozen=True)
class DependencyNode:
    """One BHSM theorem/output dependency node."""

    id: str
    title: str
    status: str
    depends_on: tuple[str, ...]
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class DependencyEdge:
    """Directed dependency edge."""

    source: str
    target: str
    relation: str


@dataclass(frozen=True)
class DependencyGraphReport:
    """Complete integrated dependency graph report."""

    title: str
    nodes: tuple[DependencyNode, ...]
    edges: tuple[DependencyEdge, ...]
    hidden_circularity_detected: bool
    empirical_residual_dependency_detected: bool
    open_obligations: tuple[str, ...]
    theorem_complete: bool
    limitations: tuple[str, ...]


def bhsm_dependency_nodes() -> tuple[DependencyNode, ...]:
    """Return the integrated BHSM dependency nodes."""

    return (
        DependencyNode("alpha_geometry", "a = alpha^{-1}/(12*pi^2)", FROZEN_PREDICTION, (), ("Canonical alpha-anchored geometry frozen in v1.",), ("Not chosen by residual minimization.",)),
        DependencyNode("overlap_width", "S = 1/(4*pi)", FROZEN_PREDICTION, (), ("Universal overlap width frozen in v1.",), ("No retuning allowed.",)),
        DependencyNode("mode_ledger", "charged-sector mode ledger", FROZEN_PREDICTION, ("omega_f",), ("Mode ledger is frozen for v1 branches.",), ("Full action derivation of all mode-selection rules remains linked to omega_f.",)),
        DependencyNode("omega_f", "boundary operators Omega_f", BOUNDARY_FUNCTIONAL_DERIVED, ("parent_action_scaffold",), ("v1.2 derives coefficients from symbolic sector boundary functional.",), ("Full unique derivation from the complete internal action remains open.",)),
        DependencyNode("parent_action_scaffold", "parent internal-action scaffold", PARENT_ACTION_REDUCED, (), ("v1.2B reduces symbolic parent action to sector boundary functional.",), ("Global uniqueness of complete Berger-Hopf action remains open.",)),
        DependencyNode("formal_kernel", "formal sector-labeled kernel", BASIS_REALIZED, ("omega_f", "state_ontology"), ("v1.3O coordinate-free K_formal realized as (0,18,36) at k_max=4.",), ("Full topological index theorem remains open.",)),
        DependencyNode("ht_gap", "H_T no-extra-light gap", SEMI_ANALYTIC_SCAFFOLD, ("formal_kernel", "scalar_decoupling"), ("Corrected formal-kernel lower-bound scaffold clears finite Level 2 threshold.",), ("Full twisted Dirac / H_T theorem remains open.",)),
        DependencyNode("scalar_decoupling", "scalar/topographic decoupling", FINITE_BASIS_SCAFFOLD, ("state_ontology",), ("v1.5 action-level scaffold distinguishes the Higgs projection from heavy, screened, virtual, and forbidden scalar/topographic modes.", "v1.6 derives/constrains derivative-screening and curvature-screening channels as sufficient scaffold conditions.", "H_T-linked complement lifting uses the corrected DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL scaffold as evidence, not a closed theorem dependency.", "Current inventory has one Higgs projection and no current forbidden/open scalar risks."), ("Full scalar/topographic decoupling from the complete action remains open.",)),
        DependencyNode("virtual_dressing", "Z_virt^{u,2}=1/2 dressed branch", ADOPTION_CANDIDATE, ("state_ontology",), ("Dressed candidate changes only c/t.",), ("Candidate branch, not final canonical adoption.",)),
        DependencyNode("qcd_rg_matching", "QCD/RG matching", OPEN, (), ("v1.4 adds approximate and placeholder reference-set architecture.",), ("Precision QCD threshold matching remains open.",)),
        DependencyNode("ckm_cp", "CKM/CP internal-rule screen", FROZEN_PREDICTION, ("mode_ledger", "alpha_geometry", "overlap_width"), ("Frozen v1 prediction ledger includes CKM/CP outputs.",), ("Full action derivation of flavor matrices remains open.",)),
        DependencyNode("pmns_effective", "PMNS effective extension", FROZEN_PREDICTION, ("alpha_geometry",), ("Effective-extension PMNS screen is frozen as a screen.",), ("Not a minimal Standard Model neutrino-mass prediction.",)),
        DependencyNode("state_ontology", "state ontology", FINITE_BASIS_SCAFFOLD, (), ("v1.3F separates internal modes, virtual contributions, and observable states.",), ("Ontology is not a spectral proof.",)),
        DependencyNode("forbidden_extra_light", "extra unscreened light states", FORBIDDEN, ("ht_gap", "scalar_decoupling"), ("Unscreened light direct-coupled extra states are falsifiers.",), ("Requires full spectrum to certify absence globally.",)),
    )


def bhsm_dependency_edges() -> tuple[DependencyEdge, ...]:
    """Return graph edges from node dependencies."""

    edges = []
    for node in bhsm_dependency_nodes():
        for dep in node.depends_on:
            edges.append(DependencyEdge(dep, node.id, "supports"))
    return tuple(edges)


def _detect_cycle(nodes: tuple[DependencyNode, ...]) -> bool:
    graph = {node.id: set(node.depends_on) for node in nodes}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        for dep in graph.get(node_id, set()):
            if visit(dep):
                return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(node.id) for node in nodes)


def _detect_empirical_residual_dependency(nodes: tuple[DependencyNode, ...]) -> bool:
    forbidden = ("residual", "empirical fit", "best fit", "minimization")
    text = "\n".join(
        f"{node.id} {' '.join(node.depends_on)}"
        for node in nodes
    ).lower()
    return any(token in text for token in forbidden)


def smallest_open_obligations() -> tuple[str, ...]:
    """Return ranked remaining proof obligations."""

    return (
        "Prove the full twisted Dirac / H_T spectrum and infinite-basis complement bound.",
        "Prove Index(D_twist)=3 and complete mirror-mode exclusion from the full operator.",
        "Prove scalar/topographic decoupling from the full internal action beyond the v1.5 action scaffold and v1.6 screening scaffold.",
        "Complete precision QCD/RG threshold matching for quark mass comparisons.",
        "Derive full flavor matrices from the complete action rather than internal-rule screens.",
    )


def build_dependency_graph_report() -> DependencyGraphReport:
    """Build the integrated dependency graph report."""

    nodes = bhsm_dependency_nodes()
    return DependencyGraphReport(
        title="BHSM v2.0 Integrated Dependency Graph",
        nodes=nodes,
        edges=bhsm_dependency_edges(),
        hidden_circularity_detected=_detect_cycle(nodes),
        empirical_residual_dependency_detected=_detect_empirical_residual_dependency(nodes),
        open_obligations=smallest_open_obligations(),
        theorem_complete=False,
        limitations=(
            "This graph is a theorem/status ledger, not a completed derivation.",
            "Frozen predictions remain frozen and are not selected by graph residuals.",
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


def export_dependency_graph_json(path: str | Path) -> None:
    """Export dependency graph report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_dependency_graph_report()), indent=2, sort_keys=True) + "\n")


def export_dependency_graph_markdown(path: str | Path) -> None:
    """Export dependency graph report as Markdown."""

    report = build_dependency_graph_report()
    lines = [
        "# BHSM v2.0 Integrated Dependency Graph",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Hidden circularity detected: `{report.hidden_circularity_detected}`",
        f"Empirical residual dependency detected: `{report.empirical_residual_dependency_detected}`",
        "",
        "## Nodes",
        "",
        "| Node | Status | Depends on |",
        "| --- | --- | --- |",
    ]
    for node in report.nodes:
        lines.append(f"| `{node.id}` | `{node.status}` | `{node.depends_on}` |")
    lines.extend(
        [
            "",
            "## Edges",
            "",
            "| Source | Target | Relation |",
            "| --- | --- | --- |",
        ]
    )
    for edge in report.edges:
        lines.append(f"| `{edge.source}` | `{edge.target}` | `{edge.relation}` |")
    lines.extend(
        [
            "",
            "## Smallest Remaining Open Obligations",
            "",
            *[f"{idx}. {item}" for idx, item in enumerate(report.open_obligations, start=1)],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
