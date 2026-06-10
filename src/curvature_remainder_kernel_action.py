"""BHSM v2.8 formal-kernel/complement audit for the curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_basis_action import REMAINDER_BASIS_ACTION_OPEN, build_curvature_remainder_basis_action_report


REMAINDER_KERNEL_SAFE = "REMAINDER_KERNEL_SAFE"
REMAINDER_COMPLEMENT_SAFE = "REMAINDER_COMPLEMENT_SAFE"
REMAINDER_KERNEL_COMPLEMENT_CONDITIONAL = "REMAINDER_KERNEL_COMPLEMENT_CONDITIONAL"
REMAINDER_KERNEL_COMPLEMENT_OPEN = "REMAINDER_KERNEL_COMPLEMENT_OPEN"
FAILS_KERNEL_COMPLEMENT_ACTION = "FAILS_KERNEL_COMPLEMENT_ACTION"


@dataclass(frozen=True)
class KernelComplementCheck:
    check_id: str
    status: str
    conclusion: str
    limitation: str


@dataclass(frozen=True)
class CurvatureRemainderKernelActionReport:
    title: str
    basis_action_status: str
    checks: tuple[KernelComplementCheck, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_kernel_action_report() -> CurvatureRemainderKernelActionReport:
    basis = build_curvature_remainder_basis_action_report()
    checks = (
        KernelComplementCheck("R_on_K_formal", "OPEN", "not proven zero on the formal lepton/up/down kernel", "Requires explicit curvature action on protected states."),
        KernelComplementCheck("R_on_H_perp", "OPEN", "not proven lower-bound safe on H_perp", "Requires PSD, relative-bound, or screening proof."),
        KernelComplementCheck("commutator_Pperp_R", "OPEN", "[P_perp,R_bundle] is not computed", "Requires explicit matrix/operator action."),
        KernelComplementCheck("lower_bound_transfer", "OPEN", "lower-bound transfer cannot include R_bundle", "No nonzero bound constants are available."),
        KernelComplementCheck("mirror_channels", "OPEN", "mirror leakage not excluded for R_bundle", "Requires chirality-resolved curvature action."),
    )
    status = REMAINDER_KERNEL_COMPLEMENT_OPEN if basis.status == REMAINDER_BASIS_ACTION_OPEN else REMAINDER_KERNEL_COMPLEMENT_CONDITIONAL
    return CurvatureRemainderKernelActionReport(
        title="BHSM v2.8 Curvature Remainder Kernel/Complement Action Report",
        basis_action_status=basis.status,
        checks=checks,
        status=status,
        theorem_complete=False,
        limitations=(
            "The formal kernel remains lepton/up/down sector-labeled, but R_bundle is not proven to vanish on it.",
            "No lower-bound transfer upgrade is possible while kernel/complement action is open.",
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


def export_curvature_remainder_kernel_action_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_kernel_action_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_kernel_action_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_kernel_action_report()
    lines = [
        "# BHSM v2.8 Curvature Remainder Kernel/Complement Action Report",
        "",
        f"Basis-action status: `{report.basis_action_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Check | Status | Conclusion | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.checks:
        lines.append(f"| `{row.check_id}` | `{row.status}` | {row.conclusion} | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
