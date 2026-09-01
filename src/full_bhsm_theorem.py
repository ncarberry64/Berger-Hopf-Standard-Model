"""Full BHSM theorem package completion decision graph."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from action_dependency_closure import build_action_dependency_closure_report
from full_ht_theorem import build_full_ht_theorem_report
from full_operator_domain import build_full_operator_domain_report
from mirror_exclusion_theorem import build_mirror_exclusion_theorem_report
from qcd_precision_closure import build_qcd_precision_closure_report
from scalar_full_action_theorem import build_scalar_full_action_theorem_report
from twisted_dirac_index_theorem import build_twisted_dirac_index_theorem_report
from virtual_dressing_theorem import build_virtual_dressing_theorem_report


ACTION_DERIVED = "ACTION_DERIVED"
THEOREM_PROVEN = "THEOREM_PROVEN"
THEOREM_CANDIDATE = "THEOREM_CANDIDATE"
STRONG_SCAFFOLD = "STRONG_SCAFFOLD"
CONDITIONAL = "CONDITIONAL"
OPEN = "OPEN"
FORBIDDEN = "FORBIDDEN"

FULL_BHSM_THEOREM_PACKAGE_COMPLETE = "FULL_BHSM_THEOREM_PACKAGE_COMPLETE"
BHSM_THEOREM_PACKAGE_INCOMPLETE = "BHSM_THEOREM_PACKAGE_INCOMPLETE"


@dataclass(frozen=True)
class FullBHSMTheoremNode:
    """One full-theorem package dependency node."""

    id: str
    title: str
    status: str
    gate_status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class FullBHSMTheoremReport:
    """Full BHSM theorem package status report."""

    title: str
    nodes: tuple[FullBHSMTheoremNode, ...]
    status: str
    theorem_complete: bool
    frozen_outputs_changed: bool
    open_obligations: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    final_paper_allowed: bool


def build_full_bhsm_theorem_nodes() -> tuple[FullBHSMTheoremNode, ...]:
    """Build theorem-package nodes from existing checked reports."""

    domain = build_full_operator_domain_report()
    ht = build_full_ht_theorem_report()
    index = build_twisted_dirac_index_theorem_report()
    mirror = build_mirror_exclusion_theorem_report()
    scalar = build_scalar_full_action_theorem_report()
    virtual = build_virtual_dressing_theorem_report()
    qcd = build_qcd_precision_closure_report()
    action = build_action_dependency_closure_report()
    return (
        FullBHSMTheoremNode(
            "canonical_constants",
            "alpha-anchored geometry and universal overlap width",
            ACTION_DERIVED,
            "FROZEN",
            True,
            (),
            ("Frozen constants are not retuned in this branch.",),
        ),
        FullBHSMTheoremNode(
            "operator_domain",
            "full operator domain and self-adjointness",
            OPEN,
            domain.status,
            domain.theorem_complete,
            domain.open_obligations,
            ("Domain proof is required before H_T theorem closure.",),
        ),
        FullBHSMTheoremNode(
            "ht_gap",
            "full twisted Dirac / H_T no-extra-light theorem",
            STRONG_SCAFFOLD,
            ht.status,
            ht.theorem_complete,
            ht.remaining_open_nodes,
            ht.forbidden_claims,
        ),
        FullBHSMTheoremNode(
            "index",
            "topological index dim ker D_twist = 3",
            OPEN,
            index.status,
            index.theorem_complete,
            index.open_obligations,
            index.limitations,
        ),
        FullBHSMTheoremNode(
            "mirror_exclusion",
            "full mirror-mode exclusion",
            OPEN,
            mirror.status,
            mirror.theorem_complete,
            mirror.open_obligations,
            mirror.limitations,
        ),
        FullBHSMTheoremNode(
            "scalar_topographic",
            "scalar/topographic full action decoupling",
            STRONG_SCAFFOLD,
            scalar.status,
            scalar.theorem_complete,
            scalar.open_obligations,
            scalar.limitations,
        ),
        FullBHSMTheoremNode(
            "virtual_dressing",
            "virtual dressing Z_virt^{u,2}=1/2",
            THEOREM_CANDIDATE,
            virtual.status,
            virtual.theorem_complete,
            virtual.open_obligations,
            virtual.limitations,
        ),
        FullBHSMTheoremNode(
            "qcd_rg",
            "precision QCD/RG comparison",
            OPEN,
            qcd.status,
            qcd.theorem_complete,
            qcd.open_obligations,
            qcd.limitations,
        ),
        FullBHSMTheoremNode(
            "unified_action",
            "unified action dependency closure",
            STRONG_SCAFFOLD,
            action.status,
            action.theorem_complete,
            tuple(action.open_nodes),
            action.limitations,
        ),
        FullBHSMTheoremNode(
            "forbidden_claims",
            "forbidden overclaim guard",
            FORBIDDEN,
            "ACTIVE",
            True,
            (),
            ("Forbidden claims remain forbidden unless proofs are implemented and checked.",),
        ),
    )


def build_full_bhsm_theorem_report() -> FullBHSMTheoremReport:
    """Build the full BHSM theorem package report."""

    nodes = build_full_bhsm_theorem_nodes()
    required_nodes = tuple(node for node in nodes if node.status != FORBIDDEN)
    theorem_complete = all(node.theorem_complete for node in required_nodes)
    open_obligations = tuple(
        dict.fromkeys(item for node in required_nodes for item in node.open_obligations)
    )
    return FullBHSMTheoremReport(
        title="BHSM Full Theorem Package Completion Attempt",
        nodes=nodes,
        status=FULL_BHSM_THEOREM_PACKAGE_COMPLETE if theorem_complete else BHSM_THEOREM_PACKAGE_INCOMPLETE,
        theorem_complete=theorem_complete,
        frozen_outputs_changed=False,
        open_obligations=open_obligations,
        forbidden_claims=(
            "Do not claim the full BHSM theorem package is complete while any node remains open.",
            "Do not prepare final paper/Zenodo release unless status is FULL_BHSM_THEOREM_PACKAGE_COMPLETE.",
        ),
        final_paper_allowed=theorem_complete,
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


def export_full_bhsm_theorem_json(path: str | Path) -> None:
    """Export the full theorem package report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_full_bhsm_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_full_bhsm_theorem_markdown(path: str | Path) -> None:
    """Export the full theorem package report as Markdown."""

    report = build_full_bhsm_theorem_report()
    lines = [
        "# BHSM Full Theorem Package Completion Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Frozen outputs changed: `{report.frozen_outputs_changed}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Theorem Nodes",
        "",
        "| Node | Status | Gate status | Complete | Open obligations |",
        "| --- | --- | --- | --- | --- |",
    ]
    for node in report.nodes:
        lines.append(f"| `{node.id}` | `{node.status}` | `{node.gate_status}` | `{node.theorem_complete}` | {'<br>'.join(node.open_obligations) or 'none'} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Forbidden Claims", ""])
    lines.extend(f"- {item}" for item in report.forbidden_claims)
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_full_bhsm_theorem_obligations_markdown(path: str | Path) -> None:
    """Export only the remaining theorem obligations."""

    report = build_full_bhsm_theorem_report()
    lines = ["# BHSM Full Theorem Open Obligations", ""]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(report.open_obligations, start=1))
    lines.append("")
    Path(path).write_text("\n".join(lines))

