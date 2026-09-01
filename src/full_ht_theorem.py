"""Full H_T theorem closure attempt for the BHSM final campaign."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from infinite_basis_ht_bound import (
    FORMAL_KERNEL_SCAFFOLD_STRONG,
    INFINITE_BASIS_OPEN,
    InfiniteBasisHTBoundReport,
    build_infinite_basis_ht_bound_report,
)
from twisted_dirac_kernel_theorem import (
    INDEX_THEOREM_OPEN,
    KernelTheoremNode,
    formal_kernel_coordinates_kmax4,
    formal_kernel_statement,
    kernel_theorem_nodes,
)


FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"
HT_THEOREM_CANDIDATE = "HT_THEOREM_CANDIDATE"
FAILS_HT_THEOREM = "FAILS_HT_THEOREM"


@dataclass(frozen=True)
class HTTheoremClosureReport:
    """Full H_T theorem closure attempt report."""

    title: str
    formal_kernel: str
    formal_kernel_coordinates: tuple[int, int, int]
    infinite_basis_report: InfiniteBasisHTBoundReport
    kernel_nodes: tuple[KernelTheoremNode, ...]
    heat_lift_and_psd_profile_preserved: bool
    sector_coupling_uniform_relative_bound_status: str
    v1_7_dependency_status: str
    v1_8_domain_bridge_status: str
    remaining_open_nodes: tuple[str, ...]
    status: str
    theorem_complete: bool
    correct_claim: str
    forbidden_claims: tuple[str, ...]


def build_full_ht_theorem_report() -> HTTheoremClosureReport:
    """Attempt to close the full H_T theorem without overclaiming."""

    from ht_domain_bridge import build_ht_domain_bridge_report

    infinite = build_infinite_basis_ht_bound_report()
    bridge = build_ht_domain_bridge_report()
    kernel = kernel_theorem_nodes()
    open_nodes = []
    for node in infinite.nodes:
        open_nodes.extend(node.open_obligations)
    for node in kernel:
        open_nodes.extend(node.open_obligations)
    theorem_complete = False
    if any(node.status == INFINITE_BASIS_OPEN for node in infinite.nodes) or any(
        node.status == INDEX_THEOREM_OPEN for node in kernel
    ):
        status = FORMAL_KERNEL_SCAFFOLD_STRONG
    else:
        status = HT_THEOREM_CANDIDATE
    return HTTheoremClosureReport(
        title="BHSM Full H_T Theorem Closure Attempt",
        formal_kernel=formal_kernel_statement(),
        formal_kernel_coordinates=formal_kernel_coordinates_kmax4(),
        infinite_basis_report=infinite,
        kernel_nodes=kernel,
        heat_lift_and_psd_profile_preserved=True,
        sector_coupling_uniform_relative_bound_status="UNIFORM_BOUND_CANDIDATE",
        v1_7_dependency_status="HT_THEOREM_BLOCKED_BY_DOMAIN",
        v1_8_domain_bridge_status=bridge.domain_bridge_status,
        remaining_open_nodes=tuple(dict.fromkeys(open_nodes)),
        status=status,
        theorem_complete=theorem_complete,
        correct_claim=(
            "The corrected formal-kernel H_T scaffold is strong and clears current finite/semi-analytic thresholds; "
            "the full H_T theorem remains open pending infinite-basis, domain, and index proofs."
        ),
        forbidden_claims=(
            "Do not claim FULL_HT_THEOREM_PROVEN.",
            "Do not claim the no-extra-light-state theorem is proven.",
            "Do not use coordinate-first protected block (0,1,2) as the corrected formal kernel.",
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


def export_full_ht_theorem_json(path: str | Path) -> None:
    """Export full H_T theorem closure report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_full_ht_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_full_ht_theorem_markdown(path: str | Path) -> None:
    """Export full H_T theorem closure report as Markdown."""

    report = build_full_ht_theorem_report()
    lines = [
        "# BHSM Full H_T Theorem Closure Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Corrected Formal Kernel",
        "",
        f"`{report.formal_kernel}`",
        "",
        f"k_max=4 coordinates: `{report.formal_kernel_coordinates}`",
        "",
        "## Bound Summary",
        "",
        "| Bound | Value |",
        "| --- | --- |",
        f"| required Dirac lower bound | `{report.infinite_basis_report.required_dirac_lower_bound}` |",
        f"| structured relative lower bound | `{report.infinite_basis_report.structured_relative_lower_bound}` |",
        f"| exact finite lower bound | `{report.infinite_basis_report.exact_finite_lower_bound}` |",
        f"| heat-lift lower bound | `{report.infinite_basis_report.heat_lift_lower_bound}` |",
        "",
        "## v1.7 Dependency Status",
        "",
        f"`{report.v1_7_dependency_status}`",
        "",
        "The corrected formal-kernel H_T scaffold remains strong, but v1.7 keeps the full theorem blocked by the complete operator-domain/self-adjointness chain before index and mirror closure can upgrade the theorem.",
        "",
        "## v1.8 Domain Bridge Status",
        "",
        f"`{report.v1_8_domain_bridge_status}`",
        "",
        "The v1.8 domain bridge records favorable conditional infinite-basis relative-bound structure, but it does not prove the full H_T theorem.",
        "",
        "## Remaining Open Nodes",
        "",
    ]
    lines.extend(f"- {item}" for item in report.remaining_open_nodes)
    lines.extend(
        [
            "",
            "## Correct Claim",
            "",
            report.correct_claim,
            "",
            "## Forbidden Claims",
            "",
            *[f"- {item}" for item in report.forbidden_claims],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
