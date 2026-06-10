"""BHSM v2.6 symbolic bundle-Dirac derivation audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_term_inventory import OPEN, build_operator_term_inventory_report


@dataclass(frozen=True)
class BundleDiracDerivationStep:
    step_id: str
    statement: str
    output_term: str
    status: str
    limitation: str


@dataclass(frozen=True)
class BundleDiracDerivationReport:
    title: str
    steps: tuple[BundleDiracDerivationStep, ...]
    unresolved_step: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_bundle_dirac_derivation_report() -> BundleDiracDerivationReport:
    inventory = build_operator_term_inventory_report()
    term_status = {term.term_id: term.classification for term in inventory.terms}
    steps = (
        BundleDiracDerivationStep("square_diagonal_berger_core", "Square the diagonal Berger core.", "berger_diagonal_kinetic", term_status["berger_diagonal_kinetic"], ""),
        BundleDiracDerivationStep("include_hopf_boundary_chirality", "Include Hopf, boundary, and chirality contributions.", "hopf/boundary/chirality package", "DERIVED_AND_INCLUDED", ""),
        BundleDiracDerivationStep("include_sector_and_lift_profile", "Include sector coupling, complement lift, heat lift, and PSD profile.", "K_sector + P_perp_lift + V_PSD", "REPRESENTED_BY_EXISTING_TERM", ""),
        BundleDiracDerivationStep("resolve_lichnerowicz_remainder", "Resolve the bundle-curvature remainder in the squared complete twisted Dirac operator.", "lichnerowicz_bundle_curvature_remainder", term_status["lichnerowicz_bundle_curvature_remainder"], "No proof currently shows this term vanishes, is represented, or is screened/lifted."),
    )
    unresolved = next((step.step_id for step in steps if step.status == OPEN), "")
    return BundleDiracDerivationReport(
        title="BHSM v2.7 Bundle Dirac Derivation Report",
        steps=steps,
        unresolved_step=unresolved,
        status="BUNDLE_DIRAC_DERIVATION_BLOCKED_BY_REMAINDER" if unresolved else "BUNDLE_DIRAC_DERIVATION_COMPLETE",
        theorem_complete=not unresolved,
        limitations=("The derivation remains symbolic until complete-operator action uniqueness is proven.",),
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


def export_bundle_dirac_derivation_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_dirac_derivation_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_dirac_derivation_markdown(path: str | Path) -> None:
    report = build_bundle_dirac_derivation_report()
    lines = [
        "# BHSM v2.7 Bundle Dirac Derivation Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Unresolved step: `{report.unresolved_step}`",
        "",
        "| Step | Output | Status | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for step in report.steps:
        lines.append(f"| `{step.step_id}` | `{step.output_term}` | `{step.status}` | {step.limitation or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
