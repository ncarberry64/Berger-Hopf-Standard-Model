"""BHSM v2.1 lift/projector domain behavior scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


LIFT_PROJECTOR_DOMAIN_PROVEN = "LIFT_PROJECTOR_DOMAIN_PROVEN"
LIFT_PROJECTOR_DOMAIN_CONDITIONAL = "LIFT_PROJECTOR_DOMAIN_CONDITIONAL"
LIFT_PROJECTOR_DOMAIN_OPEN = "LIFT_PROJECTOR_DOMAIN_OPEN"
FAILS_LIFT_PROJECTOR_DOMAIN = "FAILS_LIFT_PROJECTOR_DOMAIN"


@dataclass(frozen=True)
class LiftProjectorTerm:
    term_id: str
    operator_role: str
    bounded: bool
    psd: bool
    preserves_DA0: bool
    symmetric_on_DA0: bool
    relative_a: float
    relative_b: float
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class LiftProjectorDomainReport:
    title: str
    terms: tuple[LiftProjectorTerm, ...]
    projector_commutes_with_formal_kernel_scaffold: bool
    all_preserve_DA0: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def lift_projector_terms() -> tuple[LiftProjectorTerm, ...]:
    return (
        LiftProjectorTerm(
            term_id="P_perp_lift",
            operator_role="bounded formal-complement heat-lift projector",
            bounded=True,
            psd=True,
            preserves_DA0=True,
            symmetric_on_DA0=True,
            relative_a=0.0,
            relative_b=0.0,
            assumptions=("the formal complement projector has a bounded infinite-basis limit preserving D(A0)",),
            limitations=("Formal complement stability remains a later theorem obligation.",),
        ),
        LiftProjectorTerm(
            term_id="PSD_profile",
            operator_role="positive semidefinite topographic/profile contribution",
            bounded=True,
            psd=True,
            preserves_DA0=True,
            symmetric_on_DA0=True,
            relative_a=0.0,
            relative_b=0.0,
            assumptions=("the profile contribution is nonnegative on the formal complement",),
            limitations=("The full scalar/topographic action proof is separate from this perturbation bridge.",),
        ),
    )


def build_lift_projector_domain_report() -> LiftProjectorDomainReport:
    terms = lift_projector_terms()
    all_preserve = all(term.preserves_DA0 and term.symmetric_on_DA0 for term in terms)
    return LiftProjectorDomainReport(
        title="BHSM v2.1 Lift/Projector Domain Report",
        terms=terms,
        projector_commutes_with_formal_kernel_scaffold=True,
        all_preserve_DA0=all_preserve,
        status=LIFT_PROJECTOR_DOMAIN_CONDITIONAL if all_preserve else LIFT_PROJECTOR_DOMAIN_OPEN,
        theorem_complete=False,
        open_obligations=(
            "prove the formal complement projector and its infinite-basis limit preserve D(A0)",
            "prove profile positivity from the complete topographic action",
        ),
        limitations=(
            "The domain behavior is controlled under the formal-kernel scaffold.",
            "This does not close the final formal complement stability theorem.",
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


def export_lift_projector_domain_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_lift_projector_domain_report()), indent=2, sort_keys=True) + "\n")


def export_lift_projector_domain_markdown(path: str | Path) -> None:
    report = build_lift_projector_domain_report()
    lines = [
        "# BHSM v2.1 Lift/Projector Domain Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All preserve D(A0): `{report.all_preserve_DA0}`",
        f"Projector commutes with formal-kernel scaffold: `{report.projector_commutes_with_formal_kernel_scaffold}`",
        "",
        "| Term | Bounded | PSD | Preserves D(A0) | Symmetric on D(A0) | Assumptions |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for term in report.terms:
        lines.append(f"| `{term.term_id}` | `{term.bounded}` | `{term.psd}` | `{term.preserves_DA0}` | `{term.symmetric_on_DA0}` | {'<br>'.join(term.assumptions)} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
