"""BHSM v2.2 bridge applying the v2.1 lower bound to H_perp."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from finite_projector_convergence import FINITE_PROJECTOR_CONVERGENCE_PROVEN, build_finite_projector_convergence_report
from formal_complement_projector import FORMAL_COMPLEMENT_PROJECTOR_PROVEN, build_formal_complement_projector_report
from perturbation_closure_decision import LOWER_BOUND_BLOCKED_BY_COMPLEMENT, build_perturbation_closure_decision
from projector_domain_stability import PROJECTOR_DOMAIN_STABILITY_CONDITIONAL, build_projector_domain_stability_report


COMPLEMENT_LOWER_BOUND_APPLIES = "COMPLEMENT_LOWER_BOUND_APPLIES"
COMPLEMENT_LOWER_BOUND_CONDITIONAL = "COMPLEMENT_LOWER_BOUND_CONDITIONAL"
COMPLEMENT_LOWER_BOUND_BLOCKED_BY_PROJECTOR = "COMPLEMENT_LOWER_BOUND_BLOCKED_BY_PROJECTOR"
COMPLEMENT_LOWER_BOUND_BLOCKED_BY_DOMAIN = "COMPLEMENT_LOWER_BOUND_BLOCKED_BY_DOMAIN"
FAILS_COMPLEMENT_LOWER_BOUND = "FAILS_COMPLEMENT_LOWER_BOUND"


@dataclass(frozen=True)
class ComplementLowerBoundBridgeReport:
    title: str
    complement_projector_status: str
    domain_stability_status: str
    finite_projector_convergence_status: str
    v2_1_lower_bound_status: str
    preserved_lower_bound: float
    required_dirac_lower_bound: float
    clears_required_threshold: bool
    applies_to_H_perp: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_complement_lower_bound_bridge_report() -> ComplementLowerBoundBridgeReport:
    complement = build_formal_complement_projector_report()
    domain = build_projector_domain_stability_report()
    convergence = build_finite_projector_convergence_report()
    perturbation = build_perturbation_closure_decision()
    clears = perturbation.preserved_lower_bound >= perturbation.required_dirac_lower_bound
    projector_ok = complement.status == FORMAL_COMPLEMENT_PROJECTOR_PROVEN and convergence.status == FINITE_PROJECTOR_CONVERGENCE_PROVEN
    domain_ok = domain.status == PROJECTOR_DOMAIN_STABILITY_CONDITIONAL
    if not projector_ok:
        status = COMPLEMENT_LOWER_BOUND_BLOCKED_BY_PROJECTOR
        applies = False
    elif not domain_ok:
        status = COMPLEMENT_LOWER_BOUND_BLOCKED_BY_DOMAIN
        applies = False
    elif not clears:
        status = FAILS_COMPLEMENT_LOWER_BOUND
        applies = False
    else:
        status = COMPLEMENT_LOWER_BOUND_CONDITIONAL
        applies = True
    return ComplementLowerBoundBridgeReport(
        title="BHSM v2.2 Complement Lower-Bound Bridge Report",
        complement_projector_status=complement.status,
        domain_stability_status=domain.status,
        finite_projector_convergence_status=convergence.status,
        v2_1_lower_bound_status=perturbation.lower_bound_status,
        preserved_lower_bound=perturbation.preserved_lower_bound,
        required_dirac_lower_bound=perturbation.required_dirac_lower_bound,
        clears_required_threshold=clears,
        applies_to_H_perp=applies,
        status=status,
        theorem_complete=False,
        open_obligations=(
            "upgrade perturbation-domain stability from conditional scaffold control to the complete operator",
            "prove topological index and mirror exclusion before claiming the full H_T theorem",
        ),
        limitations=(
            "The lower bound applies to H_perp conditionally under the v2.2 projector/domain scaffold.",
            "This does not complete the index or mirror-mode portions of the theorem.",
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


def export_complement_lower_bound_bridge_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complement_lower_bound_bridge_report()), indent=2, sort_keys=True) + "\n")


def export_complement_lower_bound_bridge_markdown(path: str | Path) -> None:
    report = build_complement_lower_bound_bridge_report()
    lines = [
        "# BHSM v2.2 Complement Lower-Bound Bridge Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Applies to H_perp: `{report.applies_to_H_perp}`",
        "",
        "| Dependency | Status/Value |",
        "| --- | --- |",
        f"| complement projector | `{report.complement_projector_status}` |",
        f"| domain stability | `{report.domain_stability_status}` |",
        f"| finite-projector convergence | `{report.finite_projector_convergence_status}` |",
        f"| v2.1 lower-bound status | `{report.v2_1_lower_bound_status}` |",
        f"| preserved lower bound | `{report.preserved_lower_bound}` |",
        f"| required Dirac lower bound | `{report.required_dirac_lower_bound}` |",
        f"| clears threshold | `{report.clears_required_threshold}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
