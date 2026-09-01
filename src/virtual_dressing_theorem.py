"""Virtual dressing theorem closure attempt for BHSM final campaign."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_model import build_bhsm_model
from virtual_environment import (
    ADOPTION_CANDIDATE,
    pure_fiber_middle_up_rule,
    compare_bare_vs_dressed_model,
)
from weak_projection_dressing import WeakProjectionDressingStep, weak_projection_dressing_steps


VIRTUAL_DRESSING_DERIVED = "VIRTUAL_DRESSING_DERIVED"
VIRTUAL_DRESSING_ADOPTION_CANDIDATE = "VIRTUAL_DRESSING_ADOPTION_CANDIDATE"
VIRTUAL_DRESSING_REJECTED = "VIRTUAL_DRESSING_REJECTED"
OPEN = "OPEN"


@dataclass(frozen=True)
class VirtualDressingTheoremReport:
    """Virtual dressing theorem closure report."""

    title: str
    rule_factor: float
    rule_status: str
    weak_projection_steps: tuple[WeakProjectionDressingStep, ...]
    changed_outputs: tuple[str, ...]
    unrelated_sectors_changed: tuple[str, ...]
    preserves_u_over_t: bool
    preserves_ckm_sin_theta_13: bool
    threshold_rg_compatible_scaffold: bool
    derived_without_empirical_residuals: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_virtual_dressing_theorem_report() -> VirtualDressingTheoremReport:
    """Attempt to close the virtual dressing rule without overclaiming."""

    model = build_bhsm_model()
    rule = pure_fiber_middle_up_rule()
    comparison = compare_bare_vs_dressed_model(model, (rule,))
    bare, dressed = comparison["variants"]
    steps = weak_projection_dressing_steps()
    structural_pass = all(step.passes for step in steps)
    preserves_u = bare["ratios"]["up_quarks"]["light"] == dressed["ratios"]["up_quarks"]["light"]
    preserves_ckm13 = bare["ckm"]["sin_theta_13"] == dressed["ckm"]["sin_theta_13"]
    full_loop_derived = False
    if structural_pass and rule.status in {ADOPTION_CANDIDATE, "VIRTUAL_ENV_LINKED"}:
        status = VIRTUAL_DRESSING_ADOPTION_CANDIDATE
    else:
        status = OPEN
    return VirtualDressingTheoremReport(
        title="BHSM Virtual Dressing Theorem Closure Attempt",
        rule_factor=rule.factor,
        rule_status=rule.status,
        weak_projection_steps=steps,
        changed_outputs=tuple(comparison["changed_outputs"]),
        unrelated_sectors_changed=tuple(comparison["unrelated_sectors_changed"]),
        preserves_u_over_t=preserves_u,
        preserves_ckm_sin_theta_13=preserves_ckm13,
        threshold_rg_compatible_scaffold=True,
        derived_without_empirical_residuals=True,
        status=status,
        theorem_complete=False,
        open_obligations=(
            "Derive the virtual-environment dressing factor from the full loop/threshold action.",
            "Prove that weak-doublet projection uniquely yields Z_virt^{u,2}=1/2 in the complete theory.",
            "Keep BHSM_DRESSED_V1_CANDIDATE noncanonical until the loop derivation is complete.",
        ),
        limitations=(
            "The rule is structurally linked and candidate-level, not canonically adopted.",
            "No empirical residual is used to set the factor.",
            "Frozen bare and dressed branches are not changed.",
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


def export_virtual_dressing_theorem_json(path: str | Path) -> None:
    """Export virtual dressing theorem report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_virtual_dressing_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_virtual_dressing_theorem_markdown(path: str | Path) -> None:
    """Export virtual dressing theorem report as Markdown."""

    report = build_virtual_dressing_theorem_report()
    lines = [
        "# BHSM Virtual Dressing Theorem Closure Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Rule factor: `{report.rule_factor}`",
        f"Rule status from existing audit: `{report.rule_status}`",
        "",
        "## Weak-Projection Steps",
        "",
        "| Step | Passes | Evidence | Limitations |",
        "| --- | --- | --- | --- |",
    ]
    for step in report.weak_projection_steps:
        lines.append(f"| `{step.id}` | `{step.passes}` | {'<br>'.join(step.evidence)} | {'<br>'.join(step.limitations)} |")
    lines.extend(
        [
            "",
            "## Output Scope",
            "",
            f"- Changed outputs: `{report.changed_outputs}`",
            f"- Unrelated sectors changed: `{report.unrelated_sectors_changed}`",
            f"- Preserves u/t: `{report.preserves_u_over_t}`",
            f"- Preserves CKM sin(theta_13): `{report.preserves_ckm_sin_theta_13}`",
            "",
            "## Open Obligations",
            "",
            *[f"- {item}" for item in report.open_obligations],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))

