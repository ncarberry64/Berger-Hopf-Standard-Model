"""BHSM v2.5 full H_T theorem closure attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_identification_closure import COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP, build_complete_operator_identification_closure_report
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
from index_theorem_final_proof import build_index_theorem_final_proof_report
from lower_bound_transfer_closure import build_lower_bound_transfer_closure_report
from mirror_exclusion_final_proof import build_mirror_exclusion_final_proof_report
from perturbation_projector_commutator import PROJECTOR_COMMUTATORS_CONTROLLED
from projector_commutator_closure import build_projector_commutator_closure_report
from projector_graph_domain_closure import build_projector_graph_domain_closure_report
from projector_graph_domain_stability import PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN


FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class FullHTTheoremClosureReport:
    title: str
    complete_operator_status: str
    commutator_status: str
    projector_graph_domain_status: str
    lower_bound_transfer_status: str
    index_status: str
    mirror_status: str
    final_result: str
    theorem_complete: bool
    single_named_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    exact_obstruction: str
    limitations: tuple[str, ...]


def build_full_ht_theorem_closure_report() -> FullHTTheoremClosureReport:
    operator = build_complete_operator_identification_closure_report()
    comm = build_projector_commutator_closure_report()
    projector = build_projector_graph_domain_closure_report()
    lower = build_lower_bound_transfer_closure_report()
    index = build_index_theorem_final_proof_report()
    mirror = build_mirror_exclusion_final_proof_report()
    all_closed = (
        operator.final_status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        and comm.final_status == PROJECTOR_COMMUTATORS_CONTROLLED
        and projector.final_status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
        and lower.theorem_complete
        and index.theorem_complete
        and mirror.theorem_complete
    )
    if all_closed:
        result = FULL_HT_THEOREM_PROVEN
        gap = ""
        obstruction = "No obstruction."
    else:
        result = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        gap = COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP
        obstruction = operator.exact_obstruction
    return FullHTTheoremClosureReport(
        title="BHSM v2.5 Full H_T Theorem Closure Attempt",
        complete_operator_status=operator.final_status,
        commutator_status=comm.final_status,
        projector_graph_domain_status=projector.final_status,
        lower_bound_transfer_status=lower.final_status,
        index_status=index.final_status,
        mirror_status=mirror.final_status,
        final_result=result,
        theorem_complete=result == FULL_HT_THEOREM_PROVEN,
        single_named_gap=gap,
        recommended_next_branch=operator.next_branch if gap else "",
        recommended_target_theorem=operator.next_target_theorem if gap else "",
        exact_obstruction=obstruction,
        limitations=(
            "The closure attempt does not stop at a generic scaffold label; it names the first theorem gap blocking downstream upgrades.",
            "No H_T theorem is marked proven while any blocker remains conditional.",
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


def export_full_ht_theorem_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_full_ht_theorem_closure_report()), indent=2, sort_keys=True) + "\n")


def export_full_ht_theorem_closure_markdown(path: str | Path) -> None:
    report = build_full_ht_theorem_closure_report()
    lines = [
        "# BHSM v2.5 Full H_T Theorem Closure Attempt",
        "",
        f"Final result: `{report.final_result}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Blocker | Status |",
        "| --- | --- |",
        f"| complete operator | `{report.complete_operator_status}` |",
        f"| commutator control | `{report.commutator_status}` |",
        f"| projector graph-domain | `{report.projector_graph_domain_status}` |",
        f"| lower-bound transfer | `{report.lower_bound_transfer_status}` |",
        f"| index theorem | `{report.index_status}` |",
        f"| mirror exclusion | `{report.mirror_status}` |",
        "",
        "## Single Named Gap",
        "",
        f"`{report.single_named_gap}`",
        "",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
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
