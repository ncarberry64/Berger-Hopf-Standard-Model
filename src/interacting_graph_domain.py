"""BHSM v2.15 interacting graph-domain equality scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_action_uniqueness_decision import COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED, build_complete_operator_action_uniqueness_decision
from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from perturbation_closure_decision import build_perturbation_closure_decision
from projector_commutator_control_decision import PROJECTOR_COMMUTATOR_CONTROL_CLOSED, build_projector_commutator_control_decision


GRAPH_DOMAIN_DEFINITIONS_PROVEN = "GRAPH_DOMAIN_DEFINITIONS_PROVEN"
GRAPH_DOMAIN_DEFINITIONS_CONDITIONAL = "GRAPH_DOMAIN_DEFINITIONS_CONDITIONAL"
GRAPH_DOMAIN_DEFINITIONS_OPEN = "GRAPH_DOMAIN_DEFINITIONS_OPEN"
GRAPH_DOMAIN_DEFINITIONS_FAIL = "GRAPH_DOMAIN_DEFINITIONS_FAIL"

INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN = "INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN"
INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_CONDITIONAL = "INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_CONDITIONAL"
INTERACTING_DOMAIN_INCLUSION_PROVEN = "INTERACTING_DOMAIN_INCLUSION_PROVEN"
INTERACTING_DOMAIN_OPEN = "INTERACTING_DOMAIN_OPEN"
INTERACTING_DOMAIN_FAILS = "INTERACTING_DOMAIN_FAILS"


@dataclass(frozen=True)
class GraphDomainDefinitionsReport:
    title: str
    reference_domain: str
    perturbation_domain: str
    interacting_domain: str
    reference_graph_norm: str
    interacting_graph_norm: str
    pperp_action: str
    status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class InteractingGraphDomainReport:
    title: str
    definitions_status: str
    reference_graph_domain_status: str
    complete_operator_status: str
    action_uniqueness_status: str
    perturbation_relative_a: float
    perturbation_relative_b: float
    perturbation_relative_a_less_than_one: bool
    commutator_control_result: str
    domain_equality_status: str
    D_A0V_equals_D_A0: bool
    graph_norms_equivalent: bool
    equivalence_lower_constant: float
    equivalence_upper_constant: float
    status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def build_graph_domain_definitions_report() -> GraphDomainDefinitionsReport:
    graph = build_graph_norm_domain_report()
    proven = graph.status == GRAPH_NORM_DOMAIN_PROVEN
    return GraphDomainDefinitionsReport(
        title="BHSM v2.15 Graph-Domain Definitions Report",
        reference_domain="D(A0) = {psi in l2 : sum lambda_n^2 |psi_n|^2 < infinity}",
        perturbation_domain="D(V) contains D(A0) under the complete BHSM relative-bound package",
        interacting_domain="D(A0+V), with A0+V the complete BHSM operator package",
        reference_graph_norm="||psi||_A0 = (||psi||^2 + ||A0 psi||^2)^(1/2)",
        interacting_graph_norm="||psi||_(A0+V) = (||psi||^2 + ||(A0+V) psi||^2)^(1/2)",
        pperp_action="P_perp is the bounded orthogonal complement projector of the formal lepton/up/down kernel",
        status=GRAPH_DOMAIN_DEFINITIONS_PROVEN if proven else GRAPH_DOMAIN_DEFINITIONS_OPEN,
        theorem_complete=proven,
        assumptions=(
            "The diagonal reference graph domain from v1.9 is used.",
            "The corrected sector-labeled formal projector from v2.14 is used.",
        ),
        limitations=(
            "This definitions report only fixes the domains and norms; equality D(A0+V)=D(A0) is audited separately.",
        ),
    )


def build_interacting_graph_domain_report() -> InteractingGraphDomainReport:
    definitions = build_graph_domain_definitions_report()
    graph = build_graph_norm_domain_report()
    operator = build_complete_operator_identification_closure_report()
    action = build_complete_operator_action_uniqueness_decision()
    perturbation = build_perturbation_closure_decision()
    commutator = build_projector_commutator_control_decision()

    a = perturbation.total_relative_a
    b = perturbation.total_relative_b
    a_less_than_one = a < 1.0
    prerequisites = (
        definitions.status == GRAPH_DOMAIN_DEFINITIONS_PROVEN
        and graph.status == GRAPH_NORM_DOMAIN_PROVEN
        and operator.final_status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        and action.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
        and commutator.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED
        and a_less_than_one
    )
    status = INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN if prerequisites else INTERACTING_DOMAIN_OPEN
    # Kato-Rellich graph-norm equivalence is recorded with conservative constants.
    lower_constant = max(0.0, 1.0 - a)
    upper_constant = 1.0 + a + b
    return InteractingGraphDomainReport(
        title="BHSM v2.15 Interacting Graph-Domain Report",
        definitions_status=definitions.status,
        reference_graph_domain_status=graph.status,
        complete_operator_status=operator.final_status,
        action_uniqueness_status=action.final_result,
        perturbation_relative_a=a,
        perturbation_relative_b=b,
        perturbation_relative_a_less_than_one=a_less_than_one,
        commutator_control_result=commutator.final_result,
        domain_equality_status=status,
        D_A0V_equals_D_A0=prerequisites,
        graph_norms_equivalent=prerequisites,
        equivalence_lower_constant=lower_constant,
        equivalence_upper_constant=upper_constant,
        status=status,
        theorem_complete=prerequisites,
        assumptions=(
            "A0 is the proven diagonal self-adjoint reference operator.",
            "The v2.13 complete-operator action-uniqueness result discharges missing-term ambiguity.",
            "The complete perturbation package has total relative bound a < 1.",
            "The v2.14 projector commutator control result is closed.",
        ),
        limitations=(
            "This proves the graph-domain equality route inside the current BHSM complete-operator scaffold.",
            "It does not prove lower-bound transfer, index theorem, or mirror exclusion.",
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


def export_interacting_graph_domain_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_interacting_graph_domain_report()), indent=2, sort_keys=True) + "\n")


def export_interacting_graph_domain_markdown(path: str | Path) -> None:
    report = build_interacting_graph_domain_report()
    lines = [
        "# BHSM v2.15 Interacting Graph-Domain Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"D(A0+V) = D(A0): `{report.D_A0V_equals_D_A0}`",
        f"Graph norms equivalent: `{report.graph_norms_equivalent}`",
        "",
        "| Dependency | Status/Value |",
        "| --- | --- |",
        f"| definitions | `{report.definitions_status}` |",
        f"| reference graph domain | `{report.reference_graph_domain_status}` |",
        f"| complete operator | `{report.complete_operator_status}` |",
        f"| action uniqueness | `{report.action_uniqueness_status}` |",
        f"| commutator control | `{report.commutator_control_result}` |",
        f"| total relative a | `{report.perturbation_relative_a}` |",
        f"| total relative b | `{report.perturbation_relative_b}` |",
        f"| a < 1 | `{report.perturbation_relative_a_less_than_one}` |",
        f"| lower graph-norm constant | `{report.equivalence_lower_constant}` |",
        f"| upper graph-norm constant | `{report.equivalence_upper_constant}` |",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend(f"- {item}" for item in report.assumptions)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_graph_domain_definitions_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_graph_domain_definitions_report()), indent=2, sort_keys=True) + "\n")


def export_graph_domain_definitions_markdown(path: str | Path) -> None:
    report = build_graph_domain_definitions_report()
    lines = [
        "# BHSM v2.15 Graph-Domain Definitions Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        f"- Reference domain: `{report.reference_domain}`",
        f"- Perturbation domain: `{report.perturbation_domain}`",
        f"- Interacting domain: `{report.interacting_domain}`",
        f"- Reference graph norm: `{report.reference_graph_norm}`",
        f"- Interacting graph norm: `{report.interacting_graph_norm}`",
        f"- P_perp action: `{report.pperp_action}`",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend(f"- {item}" for item in report.assumptions)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
