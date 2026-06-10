"""BHSM v1.8 formal complement stability audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from infinite_basis_domain import FORMAL_KERNEL_STATES


FORMAL_COMPLEMENT_STABLE = "FORMAL_COMPLEMENT_STABLE"
FORMAL_COMPLEMENT_CONDITIONAL = "FORMAL_COMPLEMENT_CONDITIONAL"
FINITE_PROJECTOR_ONLY = "FINITE_PROJECTOR_ONLY"
FORMAL_COMPLEMENT_OPEN = "FORMAL_COMPLEMENT_OPEN"
FAILS_COMPLEMENT_STABILITY = "FAILS_COMPLEMENT_STABILITY"


@dataclass(frozen=True)
class ComplementStabilityCheck:
    """One formal-complement projector check."""

    id: str
    statement: str
    passes: bool
    proof_scope: str
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class FormalComplementStabilityReport:
    """Formal complement projector stability report."""

    title: str
    formal_kernel: tuple[str, ...]
    projector: str
    complement: str
    checks: tuple[ComplementStabilityCheck, ...]
    old_coordinate_first_artifact_reintroduced: bool
    finite_projector_converges_conditionally: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def complement_stability_checks() -> tuple[ComplementStabilityCheck, ...]:
    """Return complement stability checks."""

    return (
        ComplementStabilityCheck("idempotence", "P_perp^2 = P_perp for P_perp = I - P_K.", True, "finite-rank Hilbert-space projection", ()),
        ComplementStabilityCheck("self_adjointness", "P_perp^* = P_perp.", True, "finite-rank orthogonal projection", ()),
        ComplementStabilityCheck("sector_kernel", "K_formal remains one lepton, one up, one down protected state.", True, "coordinate-free formal label", ()),
        ComplementStabilityCheck("no_coordinate_first", "The coordinate-first block (0,1,2) is not used.", True, "explicit rejection", ()),
        ComplementStabilityCheck("operator_invariance", "D_FK maps K_formal and H_perp into controlled blocks.", False, "conditional complete-operator statement", ("prove full operator block invariance or controlled off-block coupling",)),
        ComplementStabilityCheck("finite_projector_limit", "finite formal-kernel projectors converge strongly to P_K.", False, "conditional nested-basis statement", ("prove nested finite projectors converge to the coordinate-free formal projector",)),
    )


def build_formal_complement_stability_report() -> FormalComplementStabilityReport:
    """Build the complement stability report."""

    checks = complement_stability_checks()
    hard_fail = any(not check.passes and not check.open_obligations for check in checks)
    open_items = any(check.open_obligations for check in checks)
    if hard_fail:
        status = FAILS_COMPLEMENT_STABILITY
    elif open_items:
        status = FORMAL_COMPLEMENT_CONDITIONAL
    else:
        status = FORMAL_COMPLEMENT_STABLE
    return FormalComplementStabilityReport(
        title="BHSM v1.8 Formal Complement Stability Report",
        formal_kernel=FORMAL_KERNEL_STATES,
        projector="P_perp = I - P_K_formal",
        complement="H_perp = K_formal^perp",
        checks=checks,
        old_coordinate_first_artifact_reintroduced=False,
        finite_projector_converges_conditionally=True,
        status=status,
        theorem_complete=status == FORMAL_COMPLEMENT_STABLE,
        limitations=(
            "Projection algebra is clean for the finite-rank formal kernel.",
            "Full operator invariance and finite-projector convergence remain conditional.",
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


def export_formal_complement_stability_json(path: str | Path) -> None:
    """Export the complement stability report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_formal_complement_stability_report()), indent=2, sort_keys=True) + "\n")


def export_formal_complement_stability_markdown(path: str | Path) -> None:
    """Export the complement stability report as Markdown."""

    report = build_formal_complement_stability_report()
    lines = [
        "# BHSM v1.8 Formal Complement Stability Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Old coordinate-first artifact reintroduced: `{report.old_coordinate_first_artifact_reintroduced}`",
        "",
        "## Formal Kernel",
        "",
    ]
    lines.extend(f"- `{state}`" for state in report.formal_kernel)
    lines.extend(["", "## Checks", "", "| Check | Passes | Scope | Open obligations |", "| --- | --- | --- | --- |"])
    for check in report.checks:
        lines.append(f"| `{check.id}` | `{check.passes}` | {check.proof_scope} | {'<br>'.join(check.open_obligations) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

