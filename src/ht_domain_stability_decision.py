"""BHSM v2.4 H_T domain-stability dependency decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_bound_transfer import HT_LOWER_BOUND_TRANSFER_CONDITIONAL, HT_LOWER_BOUND_TRANSFER_PROVEN, build_complete_operator_bound_transfer_report
from complete_operator_domain_stability import HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG, HT_DOMAIN_STABILITY_BRIDGE_PROVEN, HT_THEOREM_BLOCKED_BY_COMPLETE_OPERATOR_IDENTIFICATION, build_complete_operator_domain_stability_report
from full_mirror_exclusion import MIRROR_EXCLUSION_CONDITIONAL, MIRROR_EXCLUSION_PROVEN, build_full_mirror_exclusion_report
from twisted_dirac_index_closure import INDEX_THEOREM_CONDITIONAL, INDEX_THEOREM_PROVEN, build_twisted_dirac_index_closure_report


HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR = "HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR"
HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY = "HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class HTDomainStabilityDecision:
    title: str
    domain_stability_status: str
    lower_bound_transfer_status: str
    index_status: str
    mirror_status: str
    ht_dependency_status: str
    theorem_complete: bool
    final_paper_allowed: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_ht_domain_stability_decision() -> HTDomainStabilityDecision:
    domain = build_complete_operator_domain_stability_report()
    transfer = build_complete_operator_bound_transfer_report()
    index = build_twisted_dirac_index_closure_report()
    mirror = build_full_mirror_exclusion_report()
    if domain.status == HT_THEOREM_BLOCKED_BY_COMPLETE_OPERATOR_IDENTIFICATION:
        ht_status = HT_THEOREM_BLOCKED_BY_COMPLETE_OPERATOR_IDENTIFICATION
    elif domain.status == HT_DOMAIN_STABILITY_BRIDGE_PROVEN and transfer.status == HT_LOWER_BOUND_TRANSFER_PROVEN and index.status == INDEX_THEOREM_PROVEN and mirror.status == MIRROR_EXCLUSION_PROVEN:
        ht_status = FULL_HT_THEOREM_PROVEN
    elif domain.status == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG and transfer.status == HT_LOWER_BOUND_TRANSFER_CONDITIONAL:
        ht_status = HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    elif index.status == INDEX_THEOREM_CONDITIONAL or mirror.status == MIRROR_EXCLUSION_CONDITIONAL:
        ht_status = HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR
    else:
        ht_status = HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY
    return HTDomainStabilityDecision(
        title="BHSM v2.4 H_T Domain-Stability Decision",
        domain_stability_status=domain.status,
        lower_bound_transfer_status=transfer.status,
        index_status=index.status,
        mirror_status=mirror.status,
        ht_dependency_status=ht_status,
        theorem_complete=ht_status == FULL_HT_THEOREM_PROVEN,
        final_paper_allowed=ht_status == FULL_HT_THEOREM_PROVEN,
        open_obligations=tuple(dict.fromkeys((*domain.open_obligations, *transfer.open_obligations, *index.open_obligations, *mirror.open_obligations))),
        limitations=(
            "v2.4 does not prepare a final paper.",
            "The H_T theorem is not proven while complete-operator domain stability, index, and mirror channels remain conditional.",
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


def export_ht_domain_stability_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_ht_domain_stability_decision()), indent=2, sort_keys=True) + "\n")


def export_ht_domain_stability_decision_markdown(path: str | Path) -> None:
    report = build_ht_domain_stability_decision()
    lines = [
        "# BHSM v2.4 H_T Domain-Stability Decision",
        "",
        f"H_T dependency status: `{report.ht_dependency_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| domain stability | `{report.domain_stability_status}` |",
        f"| lower-bound transfer | `{report.lower_bound_transfer_status}` |",
        f"| index | `{report.index_status}` |",
        f"| mirror | `{report.mirror_status}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
