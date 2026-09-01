"""BHSM v1.8 self-adjointness closure attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from infinite_basis_domain import build_infinite_basis_domain_report
from uniform_relative_bound import UNIFORM_RELATIVE_BOUND_PROVEN, build_uniform_relative_bound_report


SELF_ADJOINT_DOMAIN_PROVEN = "SELF_ADJOINT_DOMAIN_PROVEN"
ESSENTIALLY_SELF_ADJOINT_ON_CORE = "ESSENTIALLY_SELF_ADJOINT_ON_CORE"
SELF_ADJOINT_DOMAIN_CANDIDATE = "SELF_ADJOINT_DOMAIN_CANDIDATE"
SELF_ADJOINT_DOMAIN_CONDITIONAL = "SELF_ADJOINT_DOMAIN_CONDITIONAL"
SELF_ADJOINT_DOMAIN_OPEN = "SELF_ADJOINT_DOMAIN_OPEN"
FAILS_SELF_ADJOINTNESS = "FAILS_SELF_ADJOINTNESS"


@dataclass(frozen=True)
class SelfAdjointClosureReport:
    """Kato-Rellich/self-adjointness closure report."""

    title: str
    reference_self_adjoint_operator: str
    perturbation_class: str
    relative_bound_constant: float
    relative_bound_below_one: bool
    relative_bound_proven: bool
    domain_equality_conditions: tuple[str, ...]
    essential_self_adjointness_follows: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_self_adjoint_closure_report() -> SelfAdjointClosureReport:
    """Build the self-adjoint closure report."""

    domain = build_infinite_basis_domain_report()
    relative = build_uniform_relative_bound_report()
    relative_proven = relative.status == UNIFORM_RELATIVE_BOUND_PROVEN
    domain_defined = domain.status != "FAILS_INFINITE_DOMAIN"
    essential = relative_proven and domain_defined
    status = ESSENTIALLY_SELF_ADJOINT_ON_CORE if essential else SELF_ADJOINT_DOMAIN_CONDITIONAL
    open_obligations = tuple(
        dict.fromkeys(
            (
                *(item for component in domain.components for item in component.open_obligations),
                *(item for term in relative.terms for item in term.open_obligations),
                "prove the diagonal reference operator is essentially self-adjoint on C_fin",
                "prove perturbations preserve the graph-norm domain",
            )
        )
    )
    return SelfAdjointClosureReport(
        title="BHSM v1.8 Self-Adjointness Closure Attempt",
        reference_self_adjoint_operator="D0^2 on the graph-norm closure of C_fin",
        perturbation_class="V_Hopf + V_boundary + V_chi + K_sector + P_perp_lift + PSD_profile",
        relative_bound_constant=relative.total_relative_a_upper,
        relative_bound_below_one=relative.all_a_below_one,
        relative_bound_proven=relative_proven,
        domain_equality_conditions=(
            "D(D_FK^2) = D(D0^2) as graph-norm domains",
            "finite core C_fin is a core for D0^2 and D_FK^2",
            "formal kernel/complement projectors preserve or reduce the domain",
        ),
        essential_self_adjointness_follows=essential,
        status=status,
        theorem_complete=essential,
        open_obligations=open_obligations,
        limitations=(
            "Kato-Rellich-style closure is conditional because the uniform relative-bound proof is not fully proven.",
            "Finite Hermiticity and relative-bound scans are not sufficient by themselves.",
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


def export_self_adjoint_closure_json(path: str | Path) -> None:
    """Export the self-adjoint closure report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_self_adjoint_closure_report()), indent=2, sort_keys=True) + "\n")


def export_self_adjoint_closure_markdown(path: str | Path) -> None:
    """Export the self-adjoint closure report as Markdown."""

    report = build_self_adjoint_closure_report()
    lines = [
        "# BHSM v1.8 Self-Adjointness Closure Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Relative-bound constant: `{report.relative_bound_constant}`",
        f"Relative bound below one: `{report.relative_bound_below_one}`",
        f"Relative bound proven: `{report.relative_bound_proven}`",
        f"Essential self-adjointness follows: `{report.essential_self_adjointness_follows}`",
        "",
        "## Domain Equality Conditions",
        "",
    ]
    lines.extend(f"- {item}" for item in report.domain_equality_conditions)
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

