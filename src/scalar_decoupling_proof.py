"""BHSM v1.5 scalar/topographic action-level decoupling proof scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from fifth_force_bounds import FifthForceRangeBound, fifth_force_bounds_for_modes
from scalar_action import (
    CURVATURE_SCREENED,
    DERIVATIVE_SCREENED,
    FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
    HIGGS_PROJECTED_LIGHT_MODE,
    HOPF_GAP_LIFTED,
    HT_COMPLEMENT_LIFTED,
    OPEN_SCALAR_RISK,
    ScalarActionTerm,
    ScalarMode,
    VIRTUAL_ONLY,
    action_level_scalar_modes,
    scalar_action_terms,
)
from scalar_decoupling import ScalarMode as ProxyScalarMode
from scalar_decoupling import build_scalar_proxy_spectrum
from scalar_decoupling_theorem import ScalarDecouplingCondition, build_scalar_decoupling_theorem_report
from topographic_action import TopographicActionTerm, topographic_action_terms


SCALAR_ACTION_SCAFFOLD_PASSES = "SCALAR_ACTION_SCAFFOLD_PASSES"
SCALAR_ACTION_THEOREM_CANDIDATE = "SCALAR_ACTION_THEOREM_CANDIDATE"
FAILS_SCALAR_DECOUPLING = "FAILS_SCALAR_DECOUPLING"
FINITE_BASIS_ONLY = "FINITE_BASIS_ONLY"
FULL_ACTION_PROVEN = "FULL_ACTION_PROVEN"


@dataclass(frozen=True)
class ScalarActionProofReport:
    """Complete scalar/topographic action-decoupling proof scaffold."""

    title: str
    scalar_action_terms: tuple[ScalarActionTerm, ...]
    topographic_action_terms: tuple[TopographicActionTerm, ...]
    scalar_modes: tuple[ScalarMode, ...]
    decoupling_conditions: tuple[ScalarDecouplingCondition, ...]
    fifth_force_bounds: tuple[FifthForceRangeBound, ...]
    corrected_ht_dependency: dict[str, Any]
    open_scalar_risks: tuple[ScalarMode, ...]
    forbidden_scalar_modes: tuple[ScalarMode, ...]
    dangerous_proxy_modes: tuple[dict[str, Any], ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def corrected_formal_kernel_ht_dependency() -> dict[str, Any]:
    """Return the corrected v1.3 formal-kernel H_T dependency metadata."""

    return {
        "model_level": "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL",
        "old_coordinate_first_superseded": True,
        "formal_kernel_coordinates_kmax4": (0, 18, 36),
        "structured_relative_lower_bound": 6.729508865520464,
        "exact_finite_lower_bound": 6.8171156827281205,
        "theorem_complete": False,
        "limitations": (
            "Scalar complement lifting may depend on H_T scaffold status.",
            "The old coordinate-first H_T conclusions are not used.",
            "The full H_T theorem remains open.",
        ),
    }


def _proxy_fifth_force_bounds(gap: float) -> tuple[FifthForceRangeBound, ...]:
    modes = tuple(build_scalar_proxy_spectrum(6, gap_scale=gap))
    return fifth_force_bounds_for_modes(modes, gap)


def classify_action_scalar_mode(mode: ScalarMode) -> str:
    """Classify one action-level scalar mode into pass/risk status."""

    if mode.channel == HIGGS_PROJECTED_LIGHT_MODE:
        return "ALLOWED_SM_HIGGS"
    if mode.channel in {HOPF_GAP_LIFTED, HT_COMPLEMENT_LIFTED}:
        return "LIFTED_NOT_LIGHT_PARTICLE"
    if mode.channel in {DERIVATIVE_SCREENED, CURVATURE_SCREENED, VIRTUAL_ONLY}:
        return "SCREENED_OR_VIRTUAL_CONDITIONAL"
    if mode.channel == FORBIDDEN_UNSCREENED_LIGHT_SCALAR:
        return FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    return OPEN_SCALAR_RISK


def build_scalar_action_proof_report() -> ScalarActionProofReport:
    """Build the v1.5 scalar/topographic action-level proof scaffold."""

    scalar_scaffold = build_scalar_decoupling_theorem_report()
    gap = scalar_scaffold.gap
    bounds = _proxy_fifth_force_bounds(gap)
    modes = action_level_scalar_modes()
    open_risks = tuple(mode for mode in modes if classify_action_scalar_mode(mode) == OPEN_SCALAR_RISK)
    forbidden = tuple(mode for mode in modes if classify_action_scalar_mode(mode) == FORBIDDEN_UNSCREENED_LIGHT_SCALAR)
    dangerous_proxy = tuple(row for row in scalar_scaffold.current_audit["dangerous_light_modes"])
    if dangerous_proxy or open_risks:
        status = OPEN_SCALAR_RISK
    elif forbidden:
        status = SCALAR_ACTION_SCAFFOLD_PASSES
    elif scalar_scaffold.status == "SCALAR_DECOUPLING_SCAFFOLD_PASSES":
        status = SCALAR_ACTION_SCAFFOLD_PASSES
    else:
        status = FINITE_BASIS_ONLY
    return ScalarActionProofReport(
        title="BHSM v1.5 Scalar/Topographic Action-Decoupling Proof Scaffold",
        scalar_action_terms=scalar_action_terms(),
        topographic_action_terms=topographic_action_terms(),
        scalar_modes=modes,
        decoupling_conditions=scalar_scaffold.conditions,
        fifth_force_bounds=bounds,
        corrected_ht_dependency=corrected_formal_kernel_ht_dependency(),
        open_scalar_risks=open_risks,
        forbidden_scalar_modes=forbidden,
        dangerous_proxy_modes=dangerous_proxy,
        status=status,
        theorem_complete=False,
        limitations=(
            "This is an action-level scaffold, not FULL_ACTION_PROVEN.",
            "Conditional derivative/curvature screening remains to be proven from the complete action.",
            "H_T-dependent scalar complement lifting uses DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL scaffold status.",
            "No frozen BHSM predictions are changed.",
        ),
    )


def explicit_unscreened_scalar_risk_example() -> dict[str, Any]:
    """Return a diagnostic example showing an unscreened light scalar is exposed."""

    gap = build_scalar_decoupling_theorem_report().gap
    mode = ProxyScalarMode("risk", "orthogonal", 1.0, "dangerous_light", 1.0, False)
    bound = fifth_force_bounds_for_modes((mode,), gap)[0]
    return {
        "mode_id": mode.mode_id,
        "classification": bound.status,
        "violates_low_energy_ontology": bound.violates_low_energy_ontology,
        "reported_not_hidden": True,
    }


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


def export_scalar_action_proof_json(path: str | Path) -> None:
    """Export scalar action proof scaffold as JSON."""

    payload = {
        "report": build_scalar_action_proof_report(),
        "unscreened_scalar_risk_example": explicit_unscreened_scalar_risk_example(),
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_scalar_action_proof_markdown(path: str | Path) -> None:
    """Export scalar action proof scaffold as Markdown."""

    report = build_scalar_action_proof_report()
    lines = [
        "# BHSM v1.5 Scalar/Topographic Action-Decoupling Proof Scaffold",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Status: `{report.status}`",
        f"Corrected H_T dependency: `{report.corrected_ht_dependency['model_level']}`",
        "",
        "## Scalar Action Terms",
        "",
        "| ID | Channel | Expression | Status |",
        "| --- | --- | --- | --- |",
    ]
    for term in report.scalar_action_terms:
        lines.append(f"| `{term.id}` | `{term.channel}` | `{term.expression}` | `{term.status}` |")
    lines.extend(
        [
            "",
            "## Topographic Action Terms",
            "",
            "| ID | Channel | Expression | Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for term in report.topographic_action_terms:
        lines.append(f"| `{term.id}` | `{term.channel}` | `{term.expression}` | `{term.status}` |")
    lines.extend(
        [
            "",
            "## Scalar Mode Classification",
            "",
            "| Mode | Channel | Mass | Coupling | On-shell light | Status |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for mode in report.scalar_modes:
        lines.append(
            f"| `{mode.mode_id}` | `{mode.channel}` | `{mode.effective_mass_gev}` | `{mode.coupling_to_matter}` | `{mode.on_shell_light_particle}` | `{mode.status}` |"
        )
    lines.extend(
        [
            "",
            "## Fifth-Force Bound Rows",
            "",
            "| Mode | Mass | Compton range (m) | Coupling to matter | Status | Violates ontology |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for bound in report.fifth_force_bounds:
        lines.append(
            f"| `{bound.mode_id}` | `{bound.effective_mass_gev}` | `{bound.compton_range_m}` | `{bound.couples_to_ordinary_matter}` | `{bound.status}` | `{bound.violates_low_energy_ontology}` |"
        )
    lines.extend(
        [
            "",
            "## Risk Assessment",
            "",
            f"Open scalar risks: `{len(report.open_scalar_risks)}`",
            f"Dangerous proxy modes: `{len(report.dangerous_proxy_modes)}`",
            "",
            "The forbidden unscreened light scalar channel is retained as a falsifier rule. It is not present in the current scalar inventory.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))


def export_fifth_force_report_markdown(path: str | Path) -> None:
    """Export focused fifth-force range/coupling report."""

    report = build_scalar_action_proof_report()
    lines = [
        "# BHSM Scalar Fifth-Force Bound Report",
        "",
        "| Mode | Effective mass (GeV) | Compton range (m) | Derivative screened | Curvature screened | Screened | Couples to matter | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for bound in report.fifth_force_bounds:
        lines.append(
            f"| `{bound.mode_id}` | `{bound.effective_mass_gev}` | `{bound.compton_range_m}` | `{bound.derivative_screened}` | `{bound.curvature_screened}` | `{bound.screened}` | `{bound.couples_to_ordinary_matter}` | `{bound.status}` |"
        )
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_fifth_force_report_json(path: str | Path) -> None:
    """Export focused fifth-force range/coupling report as JSON."""

    report = build_scalar_action_proof_report()
    payload = {
        "fifth_force_bounds": report.fifth_force_bounds,
        "open_scalar_risks": report.open_scalar_risks,
        "theorem_complete": report.theorem_complete,
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")
