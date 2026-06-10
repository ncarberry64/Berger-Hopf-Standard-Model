"""BHSM v2.0 Kato-Rellich perturbation closure."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from essential_self_adjointness import DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN, build_essential_self_adjointness_report
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from lower_bound_preservation import build_lower_bound_preservation_report
from perturbation_domain_inclusion import PERTURBATION_DOMAIN_INCLUSION_PROVEN, build_perturbation_domain_inclusion_report
from perturbation_symmetry import PERTURBATION_SYMMETRY_PROVEN, build_perturbation_symmetry_report
from relative_bound_closure import RELATIVE_BOUND_PROVEN, build_relative_bound_closure_report


KATO_RELLICH_CLOSURE_PROVEN = "KATO_RELLICH_CLOSURE_PROVEN"
KATO_RELLICH_CLOSURE_CANDIDATE = "KATO_RELLICH_CLOSURE_CANDIDATE"
KATO_RELLICH_CLOSURE_CONDITIONAL = "KATO_RELLICH_CLOSURE_CONDITIONAL"
KATO_RELLICH_CLOSURE_OPEN = "KATO_RELLICH_CLOSURE_OPEN"
FAILS_KATO_RELLICH_CLOSURE = "FAILS_KATO_RELLICH_CLOSURE"


@dataclass(frozen=True)
class KatoRellichClosureReport:
    title: str
    reference_self_adjoint_status: str
    graph_domain_status: str
    perturbation_symmetry_status: str
    perturbation_domain_status: str
    relative_bound_status: str
    lower_bound_status: str
    can_apply_kato_rellich: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_kato_rellich_closure_report() -> KatoRellichClosureReport:
    esa = build_essential_self_adjointness_report()
    graph = build_graph_norm_domain_report()
    symmetry = build_perturbation_symmetry_report()
    domain = build_perturbation_domain_inclusion_report()
    relative = build_relative_bound_closure_report()
    lower = build_lower_bound_preservation_report()
    can_apply = (
        esa.status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
        and graph.status == GRAPH_NORM_DOMAIN_PROVEN
        and symmetry.status == PERTURBATION_SYMMETRY_PROVEN
        and domain.status == PERTURBATION_DOMAIN_INCLUSION_PROVEN
        and relative.status == RELATIVE_BOUND_PROVEN
    )
    candidate = (
        esa.status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
        and graph.status == GRAPH_NORM_DOMAIN_PROVEN
        and relative.a_less_than_one
    )
    status = KATO_RELLICH_CLOSURE_PROVEN if can_apply else KATO_RELLICH_CLOSURE_CONDITIONAL if candidate else KATO_RELLICH_CLOSURE_OPEN
    open_obligations = tuple(
        dict.fromkeys(
            (
                *(item for row in symmetry.term_statuses for item in row["open_obligations"]),
                *(item for row in domain.term_statuses for item in row["open_obligations"]),
                *(item for row in relative.term_bounds for item in row["open_obligations"]),
                *lower.open_obligations,
                "prove perturbation domain inclusion for the complete operator on D(A0)",
            )
        )
    )
    return KatoRellichClosureReport(
        title="BHSM v2.0 Kato-Rellich Perturbation Closure Report",
        reference_self_adjoint_status=esa.status,
        graph_domain_status=graph.status,
        perturbation_symmetry_status=symmetry.status,
        perturbation_domain_status=domain.status,
        relative_bound_status=relative.status,
        lower_bound_status=lower.status,
        can_apply_kato_rellich=can_apply,
        status=status,
        theorem_complete=status == KATO_RELLICH_CLOSURE_PROVEN,
        open_obligations=open_obligations,
        limitations=(
            "The reference operator is closed, but perturbation symmetry/domain inclusion and full relative-bound closure remain conditional.",
            "Kato-Rellich closure is therefore not complete.",
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


def export_kato_rellich_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_kato_rellich_closure_report()), indent=2, sort_keys=True) + "\n")


def export_kato_rellich_closure_markdown(path: str | Path) -> None:
    report = build_kato_rellich_closure_report()
    lines = [
        "# BHSM v2.0 Kato-Rellich Perturbation Closure Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Can apply Kato-Rellich: `{report.can_apply_kato_rellich}`",
        "",
        "| Precondition | Status |",
        "| --- | --- |",
        f"| reference self-adjointness | `{report.reference_self_adjoint_status}` |",
        f"| graph domain | `{report.graph_domain_status}` |",
        f"| perturbation symmetry | `{report.perturbation_symmetry_status}` |",
        f"| perturbation domain | `{report.perturbation_domain_status}` |",
        f"| relative bound | `{report.relative_bound_status}` |",
        f"| lower bound | `{report.lower_bound_status}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
