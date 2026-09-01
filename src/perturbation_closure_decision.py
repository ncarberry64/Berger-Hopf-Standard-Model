"""BHSM v2.1 perturbation closure decision layer."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from essential_self_adjointness import DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN, build_essential_self_adjointness_report
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from hopf_boundary_infinite_bound import HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL, build_hopf_boundary_infinite_bound_report
from lift_projector_domain import LIFT_PROJECTOR_DOMAIN_CONDITIONAL, build_lift_projector_domain_report
from perturbation_domain_proof import COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL, build_perturbation_domain_proof_report
from perturbation_symmetry_closure import PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL, build_perturbation_symmetry_closure_report
from sector_coupling_infinite_bound import SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL, build_sector_coupling_infinite_bound_report


RELATIVE_BOUND_PROVEN = "RELATIVE_BOUND_PROVEN"
RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS = "RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS"
RELATIVE_BOUND_FINITE_SCAN_ONLY = "RELATIVE_BOUND_FINITE_SCAN_ONLY"
RELATIVE_BOUND_OPEN = "RELATIVE_BOUND_OPEN"
FAILS_RELATIVE_BOUND = "FAILS_RELATIVE_BOUND"

KATO_RELLICH_CLOSURE_PROVEN = "KATO_RELLICH_CLOSURE_PROVEN"
KATO_RELLICH_CLOSURE_CONDITIONAL = "KATO_RELLICH_CLOSURE_CONDITIONAL"
KATO_RELLICH_BLOCKED_BY_SYMMETRY = "KATO_RELLICH_BLOCKED_BY_SYMMETRY"
KATO_RELLICH_BLOCKED_BY_DOMAIN = "KATO_RELLICH_BLOCKED_BY_DOMAIN"
KATO_RELLICH_BLOCKED_BY_SECTOR_BOUND = "KATO_RELLICH_BLOCKED_BY_SECTOR_BOUND"
FAILS_KATO_RELLICH_CLOSURE = "FAILS_KATO_RELLICH_CLOSURE"

LOWER_BOUND_PRESERVED_PROVEN = "LOWER_BOUND_PRESERVED_PROVEN"
LOWER_BOUND_PRESERVED_CONDITIONAL = "LOWER_BOUND_PRESERVED_CONDITIONAL"
LOWER_BOUND_BLOCKED_BY_COMPLEMENT = "LOWER_BOUND_BLOCKED_BY_COMPLEMENT"
LOWER_BOUND_OPEN = "LOWER_BOUND_OPEN"
FAILS_LOWER_BOUND = "FAILS_LOWER_BOUND"

HT_PERTURBATION_BRIDGE_PROVEN = "HT_PERTURBATION_BRIDGE_PROVEN"
HT_THEOREM_CANDIDATE_STRENGTHENED = "HT_THEOREM_CANDIDATE_STRENGTHENED"
HT_THEOREM_CONDITIONAL_ON_COMPLEMENT = "HT_THEOREM_CONDITIONAL_ON_COMPLEMENT"
HT_THEOREM_BLOCKED_BY_PERTURBATION = "HT_THEOREM_BLOCKED_BY_PERTURBATION"
HT_THEOREM_BLOCKED_BY_SECTOR_BOUND = "HT_THEOREM_BLOCKED_BY_SECTOR_BOUND"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class PerturbationClosureDecisionReport:
    title: str
    reference_self_adjoint_status: str
    graph_domain_status: str
    common_domain_status: str
    perturbation_symmetry_status: str
    sector_coupling_status: str
    hopf_boundary_chi_status: str
    lift_projector_domain_status: str
    total_relative_a: float
    total_relative_b: float
    a_less_than_one: bool
    relative_bound_status: str
    kato_rellich_status: str
    unperturbed_lower_bound: float
    degradation_estimate: float
    preserved_lower_bound: float
    required_dirac_lower_bound: float
    lower_bound_status: str
    ht_dependency_status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_perturbation_closure_decision() -> PerturbationClosureDecisionReport:
    esa = build_essential_self_adjointness_report()
    graph = build_graph_norm_domain_report()
    domain = build_perturbation_domain_proof_report()
    symmetry = build_perturbation_symmetry_closure_report()
    sector = build_sector_coupling_infinite_bound_report()
    hopf = build_hopf_boundary_infinite_bound_report()
    lift = build_lift_projector_domain_report()

    total_a = sector.relative_a + hopf.total_relative_a + sum(term.relative_a for term in lift.terms)
    total_b = sector.relative_b + hopf.total_relative_b + sum(term.relative_b for term in lift.terms)
    a_less_than_one = total_a < 1.0
    all_term_bounds_conditional = (
        sector.status == SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL
        and hopf.status == HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL
        and lift.status == LIFT_PROJECTOR_DOMAIN_CONDITIONAL
    )
    relative_status = (
        RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS
        if a_less_than_one and all_term_bounds_conditional
        else FAILS_RELATIVE_BOUND
        if not a_less_than_one
        else RELATIVE_BOUND_OPEN
    )
    kato_status = KATO_RELLICH_CLOSURE_CONDITIONAL
    if symmetry.status != PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL:
        kato_status = KATO_RELLICH_BLOCKED_BY_SYMMETRY
    elif domain.status != COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL:
        kato_status = KATO_RELLICH_BLOCKED_BY_DOMAIN
    elif sector.status != SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL:
        kato_status = KATO_RELLICH_BLOCKED_BY_SECTOR_BOUND

    unperturbed = 6.8171156827281205
    degradation = total_a * unperturbed
    preserved = unperturbed - degradation
    required = 0.8038064161349437
    clears = preserved >= required
    lower_status = LOWER_BOUND_BLOCKED_BY_COMPLEMENT if clears else FAILS_LOWER_BOUND
    ht_status = HT_THEOREM_CONDITIONAL_ON_COMPLEMENT if clears and kato_status == KATO_RELLICH_CLOSURE_CONDITIONAL else HT_THEOREM_BLOCKED_BY_PERTURBATION

    return PerturbationClosureDecisionReport(
        title="BHSM v2.1 Perturbation Closure Decision",
        reference_self_adjoint_status=esa.status,
        graph_domain_status=graph.status,
        common_domain_status=domain.status,
        perturbation_symmetry_status=symmetry.status,
        sector_coupling_status=sector.status,
        hopf_boundary_chi_status=hopf.status,
        lift_projector_domain_status=lift.status,
        total_relative_a=total_a,
        total_relative_b=total_b,
        a_less_than_one=a_less_than_one,
        relative_bound_status=relative_status,
        kato_rellich_status=kato_status,
        unperturbed_lower_bound=unperturbed,
        degradation_estimate=degradation,
        preserved_lower_bound=preserved,
        required_dirac_lower_bound=required,
        lower_bound_status=lower_status,
        ht_dependency_status=ht_status,
        theorem_complete=False,
        open_obligations=(
            "prove scaffold domain and symmetry assumptions for the complete twisted Dirac/bundle operator",
            "derive the sector-coupling sparse bound from the complete infinite-basis action",
            "prove formal complement stability before using the lower bound as a final H_T theorem",
            "combine with final index and mirror closure before any full theorem claim",
        ),
        limitations=(
            "v2.1 strengthens the perturbation bridge from finite-scan evidence to explicit conditional infinite-basis bounds.",
            "The full H_T theorem remains conditional on complement stability and complete-operator identification.",
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


def export_perturbation_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_perturbation_closure_decision_markdown(path: str | Path) -> None:
    report = build_perturbation_closure_decision()
    lines = [
        "# BHSM v2.1 Perturbation Closure Decision",
        "",
        f"H_T dependency status: `{report.ht_dependency_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| reference self-adjointness | `{report.reference_self_adjoint_status}` |",
        f"| graph-norm domain | `{report.graph_domain_status}` |",
        f"| common domain | `{report.common_domain_status}` |",
        f"| perturbation symmetry | `{report.perturbation_symmetry_status}` |",
        f"| sector coupling | `{report.sector_coupling_status}` |",
        f"| Hopf/boundary/chirality | `{report.hopf_boundary_chi_status}` |",
        f"| lift/projector domain | `{report.lift_projector_domain_status}` |",
        f"| relative-bound closure | `{report.relative_bound_status}` |",
        f"| Kato-Rellich closure | `{report.kato_rellich_status}` |",
        f"| lower-bound preservation | `{report.lower_bound_status}` |",
        "",
        "| Bound quantity | Value |",
        "| --- | --- |",
        f"| total a | `{report.total_relative_a}` |",
        f"| total b | `{report.total_relative_b}` |",
        f"| a < 1 | `{report.a_less_than_one}` |",
        f"| unperturbed lower bound | `{report.unperturbed_lower_bound}` |",
        f"| degradation estimate | `{report.degradation_estimate}` |",
        f"| preserved lower bound | `{report.preserved_lower_bound}` |",
        f"| required Dirac lower bound | `{report.required_dirac_lower_bound}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
