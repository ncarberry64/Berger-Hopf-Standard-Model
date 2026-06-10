"""BHSM v2.4 complete twisted-Dirac operator identification audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from diagonal_reference_operator import DIAGONAL_REFERENCE_OPERATOR_PROVEN, build_diagonal_reference_operator_report
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, build_formal_kernel_projector_report
from perturbation_closure_decision import RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS, build_perturbation_closure_decision


COMPLETE_OPERATOR_IDENTIFICATION_PROVEN = "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL = "COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL"
COMPLETE_OPERATOR_IDENTIFICATION_OPEN = "COMPLETE_OPERATOR_IDENTIFICATION_OPEN"
FAILS_COMPLETE_OPERATOR_IDENTIFICATION = "FAILS_COMPLETE_OPERATOR_IDENTIFICATION"


@dataclass(frozen=True)
class CompleteOperatorComponent:
    component_id: str
    role: str
    source_status: str
    identified_with_complete_operator: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class CompleteTwistedDiracOperatorReport:
    title: str
    diagonal_reference_status: str
    perturbation_bridge_status: str
    formal_kernel_coordinates: tuple[int, int, int]
    old_coordinate_first_kernel_used: bool
    components: tuple[CompleteOperatorComponent, ...]
    exact_complete_operator: bool
    theorem_candidate_model: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_complete_twisted_dirac_operator_report() -> CompleteTwistedDiracOperatorReport:
    diagonal = build_diagonal_reference_operator_report()
    perturbation = build_perturbation_closure_decision()
    kernel = build_formal_kernel_projector_report()
    components = (
        CompleteOperatorComponent(
            "A0",
            "diagonal reference operator D_diag^2",
            diagonal.status,
            diagonal.status == DIAGONAL_REFERENCE_OPERATOR_PROVEN,
            "COMPONENT_IDENTIFIED",
            ("diagonal l2 reference operator is the chosen complete-operator core scaffold",),
            ("does not identify all non-diagonal twisted Dirac/bundle terms",),
        ),
        CompleteOperatorComponent(
            "V",
            "Hopf, boundary, chirality, sector-coupling perturbation package",
            perturbation.relative_bound_status,
            perturbation.relative_bound_status == RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS,
            "COMPONENT_CONDITIONAL",
            ("v2.1 termwise relative bounds and common-domain assumptions hold",),
            ("the perturbation package is not derived as the unique complete twisted Dirac/bundle operator",),
        ),
        CompleteOperatorComponent(
            "K_formal",
            "corrected sector-labeled formal kernel",
            kernel.status,
            kernel.old_coordinate_first_kernel_used is False,
            "COMPONENT_IDENTIFIED",
            ("formal kernel is coordinate-independent and sector-labeled",),
            ("topological index theorem remains separate from coordinate realization",),
        ),
        CompleteOperatorComponent(
            "heat_lift_profile",
            "heat-lift and PSD profile contribution",
            perturbation.lift_projector_domain_status,
            True,
            "COMPONENT_CONDITIONAL",
            ("PSD/lift terms preserve the scaffold D(A0) domain conditionally",),
            ("full profile positivity belongs to scalar/topographic action closure",),
        ),
    )
    exact = all(row.status == "COMPONENT_IDENTIFIED" for row in components)
    candidate = all(row.identified_with_complete_operator for row in components)
    status = (
        COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        if exact
        else COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL
        if candidate
        else COMPLETE_OPERATOR_IDENTIFICATION_OPEN
    )
    return CompleteTwistedDiracOperatorReport(
        title="BHSM v2.4 Complete Twisted Dirac Operator Identification Report",
        diagonal_reference_status=diagonal.status,
        perturbation_bridge_status=perturbation.relative_bound_status,
        formal_kernel_coordinates=DEFAULT_FORMAL_COORDINATES,
        old_coordinate_first_kernel_used=kernel.old_coordinate_first_kernel_used or DEFAULT_FORMAL_COORDINATES == OLD_COORDINATE_FIRST_KERNEL,
        components=components,
        exact_complete_operator=exact,
        theorem_candidate_model=candidate,
        status=status,
        theorem_complete=status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
        open_obligations=(
            "derive the perturbation package from the complete Berger-Hopf twisted Dirac/bundle action",
            "prove the theorem-candidate operator is the exact complete operator, not only a controlled scaffold representation",
        ),
        limitations=(
            "This audit identifies the complete-operator candidate chain without changing frozen predictions.",
            "It deliberately refuses COMPLETE_OPERATOR_IDENTIFICATION_PROVEN while V remains action-scaffold conditional.",
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


def export_complete_twisted_dirac_operator_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_twisted_dirac_operator_report()), indent=2, sort_keys=True) + "\n")


def export_complete_twisted_dirac_operator_markdown(path: str | Path) -> None:
    report = build_complete_twisted_dirac_operator_report()
    lines = [
        "# BHSM v2.4 Complete Twisted Dirac Operator Identification Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Exact complete operator: `{report.exact_complete_operator}`",
        f"Theorem-candidate model: `{report.theorem_candidate_model}`",
        f"Formal kernel coordinates: `{report.formal_kernel_coordinates}`",
        f"Old coordinate-first kernel used: `{report.old_coordinate_first_kernel_used}`",
        "",
        "| Component | Role | Source status | Status | Limitations |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.components:
        lines.append(f"| `{row.component_id}` | {row.role} | `{row.source_status}` | `{row.status}` | {'<br>'.join(row.limitations)} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
