"""BHSM v1.8 bridge from domain results to the H_T theorem status."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from formal_complement_stability import FORMAL_COMPLEMENT_STABLE, build_formal_complement_stability_report
from self_adjoint_closure import SELF_ADJOINT_DOMAIN_PROVEN, build_self_adjoint_closure_report
from twisted_dirac_index_theorem import INDEX_THEOREM_PROVEN, build_twisted_dirac_index_theorem_report
from uniform_relative_bound import UNIFORM_RELATIVE_BOUND_PROVEN, build_uniform_relative_bound_report


HT_THEOREM_DOMAIN_BRIDGE_PROVEN = "HT_THEOREM_DOMAIN_BRIDGE_PROVEN"
HT_THEOREM_CANDIDATE_STRENGTHENED = "HT_THEOREM_CANDIDATE_STRENGTHENED"
HT_THEOREM_CONDITIONAL_ON_INDEX = "HT_THEOREM_CONDITIONAL_ON_INDEX"
HT_THEOREM_BLOCKED_BY_DOMAIN = "HT_THEOREM_BLOCKED_BY_DOMAIN"
HT_THEOREM_BLOCKED_BY_COMPLEMENT = "HT_THEOREM_BLOCKED_BY_COMPLEMENT"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class HTDomainBridgeReport:
    """H_T dependency status after v1.8 domain work."""

    title: str
    uniform_relative_bound_status: str
    self_adjointness_status: str
    formal_complement_status: str
    index_status: str
    domain_bridge_status: str
    full_ht_theorem_status_improved: bool
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_ht_domain_bridge_report() -> HTDomainBridgeReport:
    """Build the v1.8 H_T domain bridge report."""

    relative = build_uniform_relative_bound_report()
    self_adjoint = build_self_adjoint_closure_report()
    complement = build_formal_complement_stability_report()
    index = build_twisted_dirac_index_theorem_report()
    relative_proven = relative.status == UNIFORM_RELATIVE_BOUND_PROVEN
    self_adjoint_proven = self_adjoint.status == SELF_ADJOINT_DOMAIN_PROVEN
    complement_stable = complement.status == FORMAL_COMPLEMENT_STABLE
    index_proven = index.status == INDEX_THEOREM_PROVEN
    if relative_proven and self_adjoint_proven and complement_stable and index_proven:
        status = FULL_HT_THEOREM_PROVEN
    elif relative.all_a_below_one and self_adjoint.relative_bound_below_one and complement.status != "FAILS_COMPLEMENT_STABILITY":
        status = HT_THEOREM_CANDIDATE_STRENGTHENED
    elif not complement_stable:
        status = HT_THEOREM_BLOCKED_BY_COMPLEMENT
    else:
        status = HT_THEOREM_BLOCKED_BY_DOMAIN
    open_obligations = tuple(
        dict.fromkeys(
            (
                *(item for term in relative.terms for item in term.open_obligations),
                *self_adjoint.open_obligations,
                *(item for check in complement.checks for item in check.open_obligations),
                *index.open_obligations,
            )
        )
    )
    return HTDomainBridgeReport(
        title="BHSM v1.8 H_T Domain Bridge Report",
        uniform_relative_bound_status=relative.status,
        self_adjointness_status=self_adjoint.status,
        formal_complement_status=complement.status,
        index_status=index.status,
        domain_bridge_status=status,
        full_ht_theorem_status_improved=status == HT_THEOREM_CANDIDATE_STRENGTHENED,
        theorem_complete=status == FULL_HT_THEOREM_PROVEN,
        open_obligations=open_obligations,
        limitations=(
            "The H_T theorem is strengthened from a domain blocker to a candidate bridge only conditionally.",
            "Full H_T theorem proof still requires proven self-adjointness, complement stability, index, and mirror closure.",
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


def export_ht_domain_bridge_json(path: str | Path) -> None:
    """Export the H_T domain bridge report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_ht_domain_bridge_report()), indent=2, sort_keys=True) + "\n")


def export_ht_domain_bridge_markdown(path: str | Path) -> None:
    """Export the H_T domain bridge report as Markdown."""

    report = build_ht_domain_bridge_report()
    lines = [
        "# BHSM v1.8 H_T Domain Bridge Report",
        "",
        f"Domain bridge status: `{report.domain_bridge_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Full H_T theorem status improved: `{report.full_ht_theorem_status_improved}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| Uniform relative bound | `{report.uniform_relative_bound_status}` |",
        f"| Self-adjointness | `{report.self_adjointness_status}` |",
        f"| Formal complement | `{report.formal_complement_status}` |",
        f"| Index | `{report.index_status}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

