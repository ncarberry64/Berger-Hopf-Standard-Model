"""BHSM v2.4 complete-operator domain-stability bridge."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_bound_transfer import HT_LOWER_BOUND_TRANSFER_CONDITIONAL, build_complete_operator_bound_transfer_report
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL, build_complete_twisted_dirac_operator_report
from perturbation_closure_decision import KATO_RELLICH_CLOSURE_CONDITIONAL, build_perturbation_closure_decision
from perturbation_projector_commutator import PROJECTOR_COMMUTATORS_CONDITIONAL, build_perturbation_projector_commutator_report
from projector_graph_domain_stability import PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL, build_projector_graph_domain_stability_report


PERTURBATION_DOMAIN_STABILITY_PROVEN = "PERTURBATION_DOMAIN_STABILITY_PROVEN"
PERTURBATION_DOMAIN_STABILITY_CONDITIONAL = "PERTURBATION_DOMAIN_STABILITY_CONDITIONAL"
PERTURBATION_DOMAIN_STABILITY_OPEN = "PERTURBATION_DOMAIN_STABILITY_OPEN"
FAILS_PERTURBATION_DOMAIN_STABILITY = "FAILS_PERTURBATION_DOMAIN_STABILITY"

HT_DOMAIN_STABILITY_BRIDGE_PROVEN = "HT_DOMAIN_STABILITY_BRIDGE_PROVEN"
HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG = "HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG"
HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY = "HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY"
HT_THEOREM_BLOCKED_BY_COMPLETE_OPERATOR_IDENTIFICATION = "HT_THEOREM_BLOCKED_BY_COMPLETE_OPERATOR_IDENTIFICATION"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class PerturbationDomainTerm:
    term_id: str
    maps_DA0_to_H: bool
    preserves_common_domain: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class CompleteOperatorDomainStabilityReport:
    title: str
    complete_operator_identification_status: str
    perturbation_domain_stability_status: str
    projector_graph_domain_stability_status: str
    commutator_control_status: str
    lower_bound_transfer_status: str
    perturbation_terms: tuple[PerturbationDomainTerm, ...]
    all_termwise_checks_pass: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def perturbation_domain_terms() -> tuple[PerturbationDomainTerm, ...]:
    conditional = "PERTURBATION_TERM_DOMAIN_CONDITIONAL"
    common_assumption = ("v2.1 common-domain and relative-bound scaffold applies to D(A0)",)
    return (
        PerturbationDomainTerm("V_Hopf", True, True, conditional, common_assumption, ("complete Hopf covariant derivative domain proof remains conditional",)),
        PerturbationDomainTerm("V_boundary", True, True, conditional, common_assumption, ("complete boundary functional domain proof remains conditional",)),
        PerturbationDomainTerm("V_chi", True, True, conditional, common_assumption, ("chirality projector is controlled, but complete action domain linkage remains conditional",)),
        PerturbationDomainTerm("K_sector", True, True, conditional, common_assumption, ("sector-coupling complete operator identification remains conditional",)),
        PerturbationDomainTerm("P_perp_lift", True, True, conditional, common_assumption, ("projector/domain stability is handled by the v2.4 graph-domain bridge",)),
        PerturbationDomainTerm("PSD_profile", True, True, conditional, common_assumption, ("profile positivity/domain invariance remains scalar-action conditional",)),
    )


def build_complete_operator_domain_stability_report() -> CompleteOperatorDomainStabilityReport:
    operator = build_complete_twisted_dirac_operator_report()
    perturbation = build_perturbation_closure_decision()
    projector = build_projector_graph_domain_stability_report()
    commutator = build_perturbation_projector_commutator_report()
    transfer = build_complete_operator_bound_transfer_report()
    terms = perturbation_domain_terms()
    termwise = all(row.maps_DA0_to_H and row.preserves_common_domain for row in terms)
    perturbation_status = PERTURBATION_DOMAIN_STABILITY_CONDITIONAL if perturbation.kato_rellich_status == KATO_RELLICH_CLOSURE_CONDITIONAL and termwise else PERTURBATION_DOMAIN_STABILITY_OPEN
    if operator.status != COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL:
        status = HT_THEOREM_BLOCKED_BY_COMPLETE_OPERATOR_IDENTIFICATION
    elif perturbation_status != PERTURBATION_DOMAIN_STABILITY_CONDITIONAL or projector.status != PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL:
        status = HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY
    elif commutator.status == PROJECTOR_COMMUTATORS_CONDITIONAL and transfer.status == HT_LOWER_BOUND_TRANSFER_CONDITIONAL:
        status = HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    else:
        status = HT_THEOREM_BLOCKED_BY_DOMAIN_STABILITY
    return CompleteOperatorDomainStabilityReport(
        title="BHSM v2.4 Complete-Operator Domain-Stability Report",
        complete_operator_identification_status=operator.status,
        perturbation_domain_stability_status=perturbation_status,
        projector_graph_domain_stability_status=projector.status,
        commutator_control_status=commutator.status,
        lower_bound_transfer_status=transfer.status,
        perturbation_terms=terms,
        all_termwise_checks_pass=termwise,
        status=status,
        theorem_complete=status == FULL_HT_THEOREM_PROVEN,
        open_obligations=(
            *operator.open_obligations,
            *projector.open_obligations,
            *commutator.open_obligations,
            *transfer.open_obligations,
        ),
        limitations=(
            "v2.4 strengthens the domain-stability bridge to explicit termwise conditional control.",
            "It does not mark the bridge proven because complete-operator identification and commutator proofs remain conditional.",
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


def export_complete_operator_domain_stability_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_operator_domain_stability_report()), indent=2, sort_keys=True) + "\n")


def export_complete_operator_domain_stability_markdown(path: str | Path) -> None:
    report = build_complete_operator_domain_stability_report()
    lines = [
        "# BHSM v2.4 Complete-Operator Domain-Stability Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| complete-operator identification | `{report.complete_operator_identification_status}` |",
        f"| perturbation domain stability | `{report.perturbation_domain_stability_status}` |",
        f"| projector graph-domain stability | `{report.projector_graph_domain_stability_status}` |",
        f"| commutator control | `{report.commutator_control_status}` |",
        f"| lower-bound transfer | `{report.lower_bound_transfer_status}` |",
        "",
        "## Perturbation Terms",
        "",
        "| Term | Maps D(A0) to H | Preserves common domain | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.perturbation_terms:
        lines.append(f"| `{row.term_id}` | `{row.maps_DA0_to_H}` | `{row.preserves_common_domain}` | `{row.status}` |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in dict.fromkeys(report.open_obligations))
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
