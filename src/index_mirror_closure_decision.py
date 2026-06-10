"""BHSM v2.3 index/mirror closure decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complement_lower_bound_bridge import COMPLEMENT_LOWER_BOUND_CONDITIONAL, build_complement_lower_bound_bridge_report
from full_mirror_exclusion import MIRROR_EXCLUSION_CONDITIONAL, build_full_mirror_exclusion_report
from twisted_dirac_index_closure import INDEX_THEOREM_CONDITIONAL, build_twisted_dirac_index_closure_report


HT_INDEX_MIRROR_BRIDGE_PROVEN = "HT_INDEX_MIRROR_BRIDGE_PROVEN"
HT_THEOREM_CANDIDATE_STRENGTHENED = "HT_THEOREM_CANDIDATE_STRENGTHENED"
HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY = "HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY"
HT_THEOREM_BLOCKED_BY_INDEX = "HT_THEOREM_BLOCKED_BY_INDEX"
HT_THEOREM_BLOCKED_BY_MIRROR = "HT_THEOREM_BLOCKED_BY_MIRROR"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class IndexMirrorClosureDecision:
    title: str
    index_theorem_status: str
    mirror_exclusion_status: str
    complement_lower_bound_status: str
    ht_dependency_status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_index_mirror_closure_decision() -> IndexMirrorClosureDecision:
    index = build_twisted_dirac_index_closure_report()
    mirror = build_full_mirror_exclusion_report()
    lower = build_complement_lower_bound_bridge_report()
    if index.status != INDEX_THEOREM_CONDITIONAL:
        ht_status = HT_THEOREM_BLOCKED_BY_INDEX
    elif mirror.status != MIRROR_EXCLUSION_CONDITIONAL:
        ht_status = HT_THEOREM_BLOCKED_BY_MIRROR
    elif lower.status == COMPLEMENT_LOWER_BOUND_CONDITIONAL:
        ht_status = HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY
    else:
        ht_status = HT_THEOREM_CANDIDATE_STRENGTHENED
    return IndexMirrorClosureDecision(
        title="BHSM v2.3 Index/Mirror Closure Decision",
        index_theorem_status=index.status,
        mirror_exclusion_status=mirror.status,
        complement_lower_bound_status=lower.status,
        ht_dependency_status=ht_status,
        theorem_complete=False,
        open_obligations=(
            *index.open_obligations,
            *mirror.open_obligations,
            "upgrade perturbation/projector domain stability from conditional scaffold control to complete-operator proof",
        ),
        limitations=(
            "Index and mirror channels are conditionally closed inside the current scaffold.",
            "Full H_T theorem remains blocked by complete-operator domain stability and full topological proofs.",
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


def export_index_mirror_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_index_mirror_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_index_mirror_closure_decision_markdown(path: str | Path) -> None:
    report = build_index_mirror_closure_decision()
    lines = [
        "# BHSM v2.3 Index/Mirror Closure Decision",
        "",
        f"H_T dependency status: `{report.ht_dependency_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| index theorem | `{report.index_theorem_status}` |",
        f"| mirror exclusion | `{report.mirror_exclusion_status}` |",
        f"| complement lower bound | `{report.complement_lower_bound_status}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
