"""BHSM v2.0 perturbation domain-inclusion audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from perturbation_operator import perturbation_terms


PERTURBATION_DOMAIN_INCLUSION_PROVEN = "PERTURBATION_DOMAIN_INCLUSION_PROVEN"
PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL = "PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL"
PERTURBATION_DOMAIN_INCLUSION_OPEN = "PERTURBATION_DOMAIN_INCLUSION_OPEN"
FAILS_DOMAIN_INCLUSION = "FAILS_DOMAIN_INCLUSION"


@dataclass(frozen=True)
class PerturbationDomainInclusionReport:
    title: str
    graph_domain_status: str
    term_statuses: tuple[dict[str, object], ...]
    all_terms_include_DA0: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_perturbation_domain_inclusion_report() -> PerturbationDomainInclusionReport:
    graph = build_graph_norm_domain_report()
    rows = []
    for term in perturbation_terms():
        included = term.domain_status == "DOMAIN_INCLUDED"
        rows.append(
            {
                "term_id": term.term_id,
                "domain_status": term.domain_status,
                "D_A0_included": included,
                "open_obligations": term.open_obligations,
            }
        )
    all_included = graph.status == GRAPH_NORM_DOMAIN_PROVEN and all(row["D_A0_included"] for row in rows)
    conditional = graph.status == GRAPH_NORM_DOMAIN_PROVEN and not all_included
    return PerturbationDomainInclusionReport(
        title="BHSM v2.0 Perturbation Domain Inclusion Report",
        graph_domain_status=graph.status,
        term_statuses=tuple(rows),
        all_terms_include_DA0=all_included,
        status=PERTURBATION_DOMAIN_INCLUSION_PROVEN if all_included else PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL if conditional else PERTURBATION_DOMAIN_INCLUSION_OPEN,
        theorem_complete=all_included,
        limitations=("D(A0) is proven, but not every perturbation has proven D(A0) inclusion.",),
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


def export_perturbation_domain_inclusion_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_domain_inclusion_report()), indent=2, sort_keys=True) + "\n")


def export_perturbation_domain_inclusion_markdown(path: str | Path) -> None:
    report = build_perturbation_domain_inclusion_report()
    lines = [
        "# BHSM v2.0 Perturbation Domain Inclusion Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Graph domain status: `{report.graph_domain_status}`",
        "",
        "| Term | D(A0) included | Open obligations |",
        "| --- | --- | --- |",
    ]
    for row in report.term_statuses:
        lines.append(f"| `{row['term_id']}` | `{row['D_A0_included']}` | {'<br>'.join(row['open_obligations']) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

