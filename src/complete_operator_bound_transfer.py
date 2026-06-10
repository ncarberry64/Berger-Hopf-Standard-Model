"""BHSM v2.4 lower-bound transfer audit for H_T on H_perp."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complement_lower_bound_bridge import COMPLEMENT_LOWER_BOUND_CONDITIONAL, build_complement_lower_bound_bridge_report
from full_mirror_exclusion import MIRROR_EXCLUSION_CONDITIONAL, MIRROR_EXCLUSION_PROVEN, build_full_mirror_exclusion_report
from projector_graph_domain_stability import PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL, PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN, build_projector_graph_domain_stability_report
from twisted_dirac_index_closure import INDEX_THEOREM_CONDITIONAL, INDEX_THEOREM_PROVEN, build_twisted_dirac_index_closure_report


HT_LOWER_BOUND_TRANSFER_PROVEN = "HT_LOWER_BOUND_TRANSFER_PROVEN"
HT_LOWER_BOUND_TRANSFER_CONDITIONAL = "HT_LOWER_BOUND_TRANSFER_CONDITIONAL"
HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_DOMAIN = "HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_DOMAIN"
HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR = "HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR"
FAILS_HT_LOWER_BOUND_TRANSFER = "FAILS_HT_LOWER_BOUND_TRANSFER"


@dataclass(frozen=True)
class CompleteOperatorBoundTransferReport:
    title: str
    complement_lower_bound_status: str
    projector_graph_domain_status: str
    index_status: str
    mirror_status: str
    preserved_lower_bound: float
    required_dirac_lower_bound: float
    clears_required_threshold: bool
    applies_to_H_perp: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_complete_operator_bound_transfer_report() -> CompleteOperatorBoundTransferReport:
    lower = build_complement_lower_bound_bridge_report()
    domain = build_projector_graph_domain_stability_report()
    index = build_twisted_dirac_index_closure_report()
    mirror = build_full_mirror_exclusion_report()
    clears = lower.clears_required_threshold and lower.applies_to_H_perp
    domain_ok = domain.status in {PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN, PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL}
    index_mirror_proven = index.status == INDEX_THEOREM_PROVEN and mirror.status == MIRROR_EXCLUSION_PROVEN
    index_mirror_conditional = index.status == INDEX_THEOREM_CONDITIONAL and mirror.status == MIRROR_EXCLUSION_CONDITIONAL
    if not domain_ok:
        status = HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_DOMAIN
    elif not clears:
        status = FAILS_HT_LOWER_BOUND_TRANSFER
    elif index_mirror_proven and domain.status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN:
        status = HT_LOWER_BOUND_TRANSFER_PROVEN
    elif index_mirror_conditional:
        status = HT_LOWER_BOUND_TRANSFER_CONDITIONAL
    else:
        status = HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR
    return CompleteOperatorBoundTransferReport(
        title="BHSM v2.4 Complete Operator Lower-Bound Transfer Report",
        complement_lower_bound_status=lower.status,
        projector_graph_domain_status=domain.status,
        index_status=index.status,
        mirror_status=mirror.status,
        preserved_lower_bound=lower.preserved_lower_bound,
        required_dirac_lower_bound=lower.required_dirac_lower_bound,
        clears_required_threshold=clears,
        applies_to_H_perp=clears and domain_ok,
        status=status,
        theorem_complete=status == HT_LOWER_BOUND_TRANSFER_PROVEN,
        open_obligations=(
            "upgrade projector graph-domain stability from conditional to proven",
            "upgrade topological index and mirror exclusion from conditional to proven before claiming final H_T transfer",
        ),
        limitations=(
            "The lower bound transfers to H_perp only conditionally in v2.4.",
            "It is not a final H_T theorem because index/mirror and complete-domain hypotheses remain conditional.",
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


def export_complete_operator_bound_transfer_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_operator_bound_transfer_report()), indent=2, sort_keys=True) + "\n")


def export_complete_operator_bound_transfer_markdown(path: str | Path) -> None:
    report = build_complete_operator_bound_transfer_report()
    lines = [
        "# BHSM v2.4 Complete Operator Lower-Bound Transfer Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Applies to H_perp: `{report.applies_to_H_perp}`",
        "",
        "| Dependency | Status/Value |",
        "| --- | --- |",
        f"| complement lower-bound bridge | `{report.complement_lower_bound_status}` |",
        f"| projector graph-domain stability | `{report.projector_graph_domain_status}` |",
        f"| index | `{report.index_status}` |",
        f"| mirror | `{report.mirror_status}` |",
        f"| preserved lower bound | `{report.preserved_lower_bound}` |",
        f"| required Dirac lower bound | `{report.required_dirac_lower_bound}` |",
        f"| clears threshold | `{report.clears_required_threshold}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
