"""Unified BHSM action dependency closure report."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_ht_theorem import build_full_ht_theorem_report
from qcd_precision_closure import build_qcd_precision_closure_report
from virtual_dressing_theorem import build_virtual_dressing_theorem_report
from fifth_force_exclusion import build_scalar_screening_proof_report
from unified_bhsm_action import (
    ACTION_SCAFFOLD_WITH_OPEN_NODES,
    FULL_ACTION_CLOSED,
    UnifiedActionNode,
    action_dependency_edges,
    hidden_cycle_detected,
    unified_action_nodes,
)


@dataclass(frozen=True)
class ActionDependencyClosureReport:
    """Unified action dependency closure report."""

    title: str
    nodes: tuple[UnifiedActionNode, ...]
    edges: tuple[tuple[str, str], ...]
    hidden_circularity_detected: bool
    empirical_residual_dependency_detected: bool
    open_nodes: tuple[str, ...]
    gate_statuses: dict[str, str]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def theorem_module_sources() -> tuple[str, ...]:
    """Return theorem/closure source files scanned for forbidden dependencies."""

    return (
        "full_ht_theorem.py",
        "infinite_basis_ht_bound.py",
        "twisted_dirac_kernel_theorem.py",
        "virtual_dressing_theorem.py",
        "weak_projection_dressing.py",
        "qcd_precision_closure.py",
        "rg_threshold_uncertainty.py",
        "scalar_screening_action.py",
        "fifth_force_exclusion.py",
        "unified_bhsm_action.py",
    )


def empirical_residual_dependency_detected(root: str | Path = "src") -> bool:
    """Return whether closure theorem modules import residual/prediction machinery."""

    base = Path(root)
    forbidden = (
        "from prediction_ledger",
        "import prediction_ledger",
        "from residual_audit",
        "import residual_audit",
        "build_prediction_ledger(",
        "build_residual_audit(",
        ".best_fit(",
        ".minimize(",
    )
    text = "\n".join(base.joinpath(name).read_text() for name in theorem_module_sources())
    return any(token in text for token in forbidden)


def build_action_dependency_closure_report() -> ActionDependencyClosureReport:
    """Build the unified action dependency closure report."""

    nodes = unified_action_nodes()
    open_nodes = tuple(node.id for node in nodes if node.open_obligations or node.status == "OPEN")
    gate_statuses = {
        "ht_gap": build_full_ht_theorem_report().status,
        "virtual_dressing": build_virtual_dressing_theorem_report().status,
        "qcd_rg": build_qcd_precision_closure_report().status,
        "scalar_topographic": build_scalar_screening_proof_report().status,
    }
    theorem_complete = not open_nodes and not hidden_cycle_detected() and not empirical_residual_dependency_detected()
    return ActionDependencyClosureReport(
        title="BHSM Unified Action Dependency Closure Report",
        nodes=nodes,
        edges=action_dependency_edges(),
        hidden_circularity_detected=hidden_cycle_detected(),
        empirical_residual_dependency_detected=empirical_residual_dependency_detected(),
        open_nodes=open_nodes,
        gate_statuses=gate_statuses,
        status=FULL_ACTION_CLOSED if theorem_complete else ACTION_SCAFFOLD_WITH_OPEN_NODES,
        theorem_complete=theorem_complete,
        limitations=(
            "The unified graph is dependency-clean but has open theorem nodes.",
            "Frozen predictions are not retuned or changed.",
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


def export_action_dependency_closure_json(path: str | Path) -> None:
    """Export action dependency closure report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_action_dependency_closure_report()), indent=2, sort_keys=True) + "\n")


def export_action_dependency_closure_markdown(path: str | Path) -> None:
    """Export action dependency closure report as Markdown."""

    report = build_action_dependency_closure_report()
    lines = [
        "# BHSM Unified Action Dependency Closure Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Hidden circularity detected: `{report.hidden_circularity_detected}`",
        f"Empirical residual dependency detected: `{report.empirical_residual_dependency_detected}`",
        "",
        "## Nodes",
        "",
        "| Node | Status | Depends on | Open obligations |",
        "| --- | --- | --- | --- |",
    ]
    for node in report.nodes:
        lines.append(f"| `{node.id}` | `{node.status}` | `{node.depends_on}` | {'<br>'.join(node.open_obligations) or 'none'} |")
    lines.extend(["", "## Gate Statuses", ""])
    lines.extend(f"- `{key}`: `{value}`" for key, value in report.gate_statuses.items())
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_unified_action_markdown(path: str | Path) -> None:
    """Export a compact unified action report."""

    export_action_dependency_closure_markdown(path)


def export_unified_action_json(path: str | Path) -> None:
    """Export a compact unified action report as JSON."""

    export_action_dependency_closure_json(path)
