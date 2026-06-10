"""BHSM v2.1 common-domain proof scaffold for perturbation terms."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from hopf_boundary_infinite_bound import build_hopf_boundary_infinite_bound_report
from lift_projector_domain import build_lift_projector_domain_report
from sector_coupling_infinite_bound import build_sector_coupling_infinite_bound_report


COMMON_DOMAIN_EQUALS_DA0_PROVEN = "COMMON_DOMAIN_EQUALS_DA0_PROVEN"
COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL = "COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL"
COMMON_DOMAIN_DENSE_CORE_ONLY = "COMMON_DOMAIN_DENSE_CORE_ONLY"
COMMON_DOMAIN_OPEN = "COMMON_DOMAIN_OPEN"
FAILS_COMMON_DOMAIN = "FAILS_COMMON_DOMAIN"


@dataclass(frozen=True)
class DomainTermStatus:
    term_id: str
    preserves_graph_norm_finiteness: bool
    maps_DA0_to_H: bool
    symmetry_relevant: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class PerturbationDomainProofReport:
    title: str
    common_domain_expression: str
    graph_norm_domain_status: str
    finite_core_common_core: bool
    terms: tuple[DomainTermStatus, ...]
    common_domain_equals_DA0: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_perturbation_domain_proof_report() -> PerturbationDomainProofReport:
    graph = build_graph_norm_domain_report()
    hopf = build_hopf_boundary_infinite_bound_report()
    sector = build_sector_coupling_infinite_bound_report()
    lift = build_lift_projector_domain_report()
    rows: list[DomainTermStatus] = []
    for term in hopf.terms:
        rows.append(
            DomainTermStatus(
                term.term_id,
                term.preserves_domain,
                term.preserves_domain,
                True,
                "DA0_DOMAIN_CONDITIONAL",
                term.assumptions,
                term.limitations,
            )
        )
    rows.append(
        DomainTermStatus(
            "K_sector",
            True,
            True,
            True,
            "DA0_DOMAIN_CONDITIONAL",
            sector.pattern.assumptions,
            sector.limitations,
        )
    )
    for term in lift.terms:
        rows.append(
            DomainTermStatus(
                term.term_id,
                term.preserves_DA0,
                term.preserves_DA0,
                True,
                "DA0_DOMAIN_CONDITIONAL",
                term.assumptions,
                term.limitations,
            )
        )
    all_preserve = graph.status == GRAPH_NORM_DOMAIN_PROVEN and all(row.maps_DA0_to_H for row in rows)
    return PerturbationDomainProofReport(
        title="BHSM v2.1 Perturbation Common-Domain Proof Scaffold",
        common_domain_expression="D(A0) cap D(V_Hopf) cap D(V_boundary) cap D(V_chi) cap D(K_sector) cap D(P_perp_lift)",
        graph_norm_domain_status=graph.status,
        finite_core_common_core=True,
        terms=tuple(rows),
        common_domain_equals_DA0=all_preserve,
        status=COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL if all_preserve else COMMON_DOMAIN_OPEN,
        theorem_complete=False,
        open_obligations=(
            "upgrade scaffold termwise D(A0) preservation to the complete twisted Dirac/bundle operator",
            "prove the formal complement projector preserves D(A0) in the infinite-basis limit",
        ),
        limitations=(
            "The common domain equals D(A0) under explicit v2.1 scaffold assumptions.",
            "The equality is not marked proven for the complete operator.",
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


def export_perturbation_domain_proof_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_domain_proof_report()), indent=2, sort_keys=True) + "\n")


def export_perturbation_domain_proof_markdown(path: str | Path) -> None:
    report = build_perturbation_domain_proof_report()
    lines = [
        "# BHSM v2.1 Perturbation Common-Domain Proof Scaffold",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Common domain: `{report.common_domain_expression}`",
        f"Graph-norm domain status: `{report.graph_norm_domain_status}`",
        f"Finite core is common core: `{report.finite_core_common_core}`",
        f"Common domain equals D(A0): `{report.common_domain_equals_DA0}`",
        "",
        "| Term | Preserves graph norm | Maps D(A0) to H | Status | Assumptions |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.terms:
        lines.append(f"| `{row.term_id}` | `{row.preserves_graph_norm_finiteness}` | `{row.maps_DA0_to_H}` | `{row.status}` | {'<br>'.join(row.assumptions)} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
