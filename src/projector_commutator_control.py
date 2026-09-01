"""BHSM v2.14 formal projector definition audit for commutator control."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_action_uniqueness_decision import COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED, build_complete_operator_action_uniqueness_decision
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_complete_twisted_dirac_operator_report
from formal_complement_projector import FORMAL_COMPLEMENT_PROJECTOR_PROVEN, build_formal_complement_projector_report
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, FORMAL_KERNEL_PROJECTOR_PROVEN, formal_kernel_basis_vectors, build_formal_kernel_projector_report


PROJECTOR_DEFINITION_PROVEN = "PROJECTOR_DEFINITION_PROVEN"
PROJECTOR_DEFINITION_CONDITIONAL = "PROJECTOR_DEFINITION_CONDITIONAL"
PROJECTOR_DEFINITION_OPEN = "PROJECTOR_DEFINITION_OPEN"
PROJECTOR_DEFINITION_FAILS = "PROJECTOR_DEFINITION_FAILS"


@dataclass(frozen=True)
class ProjectorDefinitionAuditReport:
    title: str
    formal_kernel_coordinates: tuple[int, int, int]
    old_coordinate_first_kernel_used: bool
    kernel_sectors: tuple[str, ...]
    complement_projector_status: str
    complete_operator_status: str
    action_uniqueness_status: str
    compatible_with_complete_operator_package: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_projector_definition_audit_report() -> ProjectorDefinitionAuditReport:
    kernel = build_formal_kernel_projector_report()
    complement = build_formal_complement_projector_report()
    operator = build_complete_twisted_dirac_operator_report()
    action = build_complete_operator_action_uniqueness_decision()
    basis = formal_kernel_basis_vectors()
    sectors = tuple(row.sector for row in basis)
    old_used = kernel.old_coordinate_first_kernel_used or DEFAULT_FORMAL_COORDINATES == OLD_COORDINATE_FIRST_KERNEL
    compatible = (
        kernel.status == FORMAL_KERNEL_PROJECTOR_PROVEN
        and complement.status == FORMAL_COMPLEMENT_PROJECTOR_PROVEN
        and operator.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        and action.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
        and sectors == ("lepton", "up", "down")
        and not old_used
    )
    return ProjectorDefinitionAuditReport(
        title="BHSM v2.14 Projector Definition Audit",
        formal_kernel_coordinates=DEFAULT_FORMAL_COORDINATES,
        old_coordinate_first_kernel_used=old_used,
        kernel_sectors=sectors,
        complement_projector_status=complement.status,
        complete_operator_status=operator.status,
        action_uniqueness_status=action.final_result,
        compatible_with_complete_operator_package=compatible,
        status=PROJECTOR_DEFINITION_PROVEN if compatible else PROJECTOR_DEFINITION_FAILS,
        theorem_complete=compatible,
        limitations=(
            "This proves the formal complement projector definition used for commutator control.",
            "Graph-domain invariance remains a downstream theorem gate.",
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


def export_projector_commutator_control_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_definition_audit_report()), indent=2, sort_keys=True) + "\n")


def export_projector_commutator_control_markdown(path: str | Path) -> None:
    report = build_projector_definition_audit_report()
    lines = [
        "# BHSM v2.14 Projector Definition Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Formal kernel coordinates: `{report.formal_kernel_coordinates}`",
        f"Old coordinate-first kernel used: `{report.old_coordinate_first_kernel_used}`",
        f"Kernel sectors: `{report.kernel_sectors}`",
        f"Compatible with complete operator package: `{report.compatible_with_complete_operator_package}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
