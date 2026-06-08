"""Unified BHSM action-level dependency scaffold."""

from __future__ import annotations

from dataclasses import dataclass


FULL_ACTION_CLOSED = "FULL_ACTION_CLOSED"
ACTION_DEPENDENCY_GRAPH_COMPLETE = "ACTION_DEPENDENCY_GRAPH_COMPLETE"
ACTION_SCAFFOLD_WITH_OPEN_NODES = "ACTION_SCAFFOLD_WITH_OPEN_NODES"
OPEN = "OPEN"


@dataclass(frozen=True)
class UnifiedActionNode:
    """One node in the unified BHSM action dependency graph."""

    id: str
    statement: str
    status: str
    depends_on: tuple[str, ...]
    open_obligations: tuple[str, ...]


def unified_action_nodes() -> tuple[UnifiedActionNode, ...]:
    """Return the unified BHSM action dependency nodes."""

    return (
        UnifiedActionNode("alpha_geometry", "a=alpha^{-1}/(12*pi^2)", "FROZEN", (), ()),
        UnifiedActionNode("overlap_width", "S=1/(4*pi)", "FROZEN", (), ()),
        UnifiedActionNode("omega_f", "charged-sector boundary operators Omega_f", "BOUNDARY_FUNCTIONAL_DERIVED", (), ("derive boundary functional from complete action globally",)),
        UnifiedActionNode("mode_ledger", "frozen charged-sector mode ledger", "FROZEN", ("omega_f",), ()),
        UnifiedActionNode("ckm_cp", "CKM/CP internal-rule scaffold", "FROZEN_SCREEN", ("mode_ledger", "alpha_geometry", "overlap_width"), ("derive full flavor matrix from complete action",)),
        UnifiedActionNode("formal_kernel", "formal sector-labeled H_T kernel", "STRONG_SCAFFOLD", ("omega_f",), ("prove full topological index theorem",)),
        UnifiedActionNode("ht_gap", "H_T no-extra-light gap", "STRONG_SCAFFOLD", ("formal_kernel",), ("prove infinite-basis complement bound", "prove full operator domain")),
        UnifiedActionNode("scalar_topographic", "scalar/topographic decoupling", "STRONG_SCAFFOLD", ("ht_gap",), ("prove global scalar/topographic action decoupling",)),
        UnifiedActionNode("virtual_dressing", "Z_virt^{u,2}=1/2 candidate branch", "THEOREM_CANDIDATE", (), ("derive full virtual loop/threshold dressing factor",)),
        UnifiedActionNode("qcd_rg", "precision QCD/RG comparison", OPEN, (), ("supply validated precision-QCD inputs",)),
        UnifiedActionNode("state_ontology", "state ontology", "SCAFFOLD", (), ("connect ontology to complete spectral theorem",)),
    )


def action_dependency_edges() -> tuple[tuple[str, str], ...]:
    """Return dependency edges as (source,target)."""

    return tuple((dep, node.id) for node in unified_action_nodes() for dep in node.depends_on)


def hidden_cycle_detected() -> bool:
    """Detect cycles in the unified graph."""

    nodes = {node.id: set(node.depends_on) for node in unified_action_nodes()}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        for dep in nodes.get(node_id, set()):
            if visit(dep):
                return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(node_id) for node_id in nodes)

