"""BHSM v2.5 lower-bound transfer closure attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_bound_transfer import (
    HT_LOWER_BOUND_TRANSFER_CONDITIONAL,
    HT_LOWER_BOUND_TRANSFER_PROVEN,
    build_complete_operator_bound_transfer_report,
)
from projector_graph_domain_closure import build_projector_graph_domain_closure_report


@dataclass(frozen=True)
class LowerBoundTransferClosureReport:
    title: str
    source_status: str
    projector_graph_domain_status: str
    final_status: str
    theorem_complete: bool
    clears_required_threshold: bool
    exact_obstruction: str
    limitations: tuple[str, ...]


def build_lower_bound_transfer_closure_report() -> LowerBoundTransferClosureReport:
    report = build_complete_operator_bound_transfer_report()
    projector = build_projector_graph_domain_closure_report()
    proven = report.status == HT_LOWER_BOUND_TRANSFER_PROVEN and projector.theorem_complete
    obstruction = (
        "No obstruction: lower bound transfers to H_perp."
        if proven
        else "The numeric lower bound clears the required threshold, but transfer to H_perp remains conditional on projector graph-domain and index/mirror proof closure."
    )
    return LowerBoundTransferClosureReport(
        title="BHSM v2.5 Lower-Bound Transfer Closure Attempt",
        source_status=report.status,
        projector_graph_domain_status=projector.final_status,
        final_status=HT_LOWER_BOUND_TRANSFER_PROVEN if proven else HT_LOWER_BOUND_TRANSFER_CONDITIONAL,
        theorem_complete=proven,
        clears_required_threshold=report.clears_required_threshold,
        exact_obstruction=obstruction,
        limitations=(
            "Lower-bound transfer is not marked proven while projector/domain and index/mirror inputs remain conditional.",
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


def export_lower_bound_transfer_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_lower_bound_transfer_closure_report()), indent=2, sort_keys=True) + "\n")


def export_lower_bound_transfer_closure_markdown(path: str | Path) -> None:
    report = build_lower_bound_transfer_closure_report()
    lines = [
        "# BHSM v2.5 Lower-Bound Transfer Closure Attempt",
        "",
        f"Source status: `{report.source_status}`",
        f"Projector graph-domain status: `{report.projector_graph_domain_status}`",
        f"Final status: `{report.final_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Clears required threshold: `{report.clears_required_threshold}`",
        "",
        "## Exact Obstruction",
        "",
        report.exact_obstruction,
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
