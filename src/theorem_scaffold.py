"""Formal sufficient theorem scaffold for the H_T no-extra-light audit.

This module separates assumptions, conditional implication steps, proxy
evidence, and remaining proof obligations. It does not prove the assumptions
and never marks the theorem complete.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path


class AssumptionStatus(StrEnum):
    """Conservative status labels for theorem-scaffold assumptions."""

    ASSUMED = "ASSUMED"
    VERIFIED_PROXY = "VERIFIED_PROXY"
    PROVEN_CONDITIONAL = "PROVEN_CONDITIONAL"
    OPEN = "OPEN"


@dataclass(frozen=True)
class Assumption:
    """One explicit hypothesis or proof obligation in the theorem scaffold."""

    id: str
    statement: str
    status: AssumptionStatus
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class TheoremStep:
    """One conditional implication in the sufficient theorem scaffold."""

    id: str
    statement: str
    depends_on: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True)
class TheoremScaffold:
    """Machine-readable scaffold for a conditional theorem statement."""

    title: str
    assumptions: tuple[Assumption, ...]
    steps: tuple[TheoremStep, ...]
    conclusion: str
    theorem_complete: bool


def build_ht_no_extra_light_theorem_scaffold() -> TheoremScaffold:
    """Return the Gate 32D sufficient theorem scaffold for H_T."""

    assumptions = (
        Assumption(
            id="A1",
            statement="dim ker D_twist = 3.",
            status=AssumptionStatus.VERIFIED_PROXY,
            evidence=(
                "Level 2 finite-basis proxy inserts and audits three protected zero modes.",
                "Gate 32C convergence scan kept zero_mode_count = 3 across requested bases.",
            ),
            limitations=(
                "The full twisted Dirac kernel has not been computed in the complete internal action.",
            ),
        ),
        Assumption(
            id="A2",
            statement="No opposite-chirality mirror zero modes.",
            status=AssumptionStatus.OPEN,
            evidence=(
                "Current finite-basis scaffolds track chirality labels.",
            ),
            limitations=(
                "Absence of mirror zero modes has not been proven for the full twisted Dirac spectrum.",
            ),
        ),
        Assumption(
            id="A3",
            statement="The physical light subspace is exactly ker D_twist.",
            status=AssumptionStatus.ASSUMED,
            evidence=(
                "The audit projects a protected kernel before testing H_perp.",
            ),
            limitations=(
                "Identification of the physical light subspace remains an action-level assumption.",
            ),
        ),
        Assumption(
            id="A4",
            statement="The complement satisfies d_lower >= 0.8038064161349437 for Lambda^2 = 1/(4 pi).",
            status=AssumptionStatus.VERIFIED_PROXY,
            evidence=(
                "Gate 32B computed the required finite-basis Dirac lower bound at natural cutoff.",
                "Gate 32C found worst direct margin 1.4628370793070644 and worst Gershgorin margin 1.4366234871740744 in the requested convergence scan.",
            ),
            limitations=(
                "This is finite-basis proxy evidence, not a complete Hilbert-space lower bound.",
            ),
        ),
        Assumption(
            id="A5",
            statement="V_profile restricted to H_perp is positive semidefinite: V_profile|H_perp >= 0.",
            status=AssumptionStatus.VERIFIED_PROXY,
            evidence=(
                "Gate 28D and positivity tests verify PSD profile terms preserve proxy complement gaps.",
            ),
            limitations=(
                "The full curvature/profile operator has not been derived and proven PSD on H_perp.",
            ),
        ),
        Assumption(
            id="A6",
            statement="The trace U(1) is topological/nondynamical.",
            status=AssumptionStatus.OPEN,
            evidence=(
                "Tracked as an open claim in the claims ledger.",
            ),
            limitations=(
                "No independent topological proof is implemented.",
            ),
        ),
        Assumption(
            id="A7",
            statement="Scalar orthogonal modes are lifted or screened separately.",
            status=AssumptionStatus.VERIFIED_PROXY,
            evidence=(
                "Gate 30B scalar/topographic decoupling scaffold audits one light Higgs projection and no dangerous light direct-coupled scalar in the proxy inventory.",
            ),
            limitations=(
                "Full action-level scalar/topographic decoupling remains open.",
            ),
        ),
    )

    steps = (
        TheoremStep(
            id="S1",
            statement="Heat-lift inequality: d + mu_H(1 - exp(-d/Lambda^2)) + V_min >= mu_H.",
            depends_on=("A4", "A5"),
            conclusion="A sufficient dimensionless H_T lower bound follows from the Dirac lower bound and nonnegative profile term.",
        ),
        TheoremStep(
            id="S2",
            statement="If A4 and A5 hold, then H_T|H_perp >= mu_H.",
            depends_on=("A4", "A5", "S1"),
            conclusion="The complement clears the dimensionless Hopf-gap target.",
        ),
        TheoremStep(
            id="S3",
            statement="Since mu_H = (4 pi^2 v)^2 r_int^2 in dimensionless units, complement modes are heavier than 4 pi^2 v.",
            depends_on=("S2",),
            conclusion="The complement lies above the Hopf lift scale under the stated unit matching.",
        ),
        TheoremStep(
            id="S4",
            statement="A1-A3 leave exactly three protected chiral families light.",
            depends_on=("A1", "A2", "A3"),
            conclusion="The protected light fermion family count is three if the kernel assumptions are proven.",
        ),
        TheoremStep(
            id="S5",
            statement="A6-A7 remove extra gauge/scalar light states.",
            depends_on=("A6", "A7"),
            conclusion="No additional trace-U(1) or scalar/topographic light state remains under those assumptions.",
        ),
    )

    return TheoremScaffold(
        title="Conditional H_T No-Extra-Light-State Theorem Scaffold",
        assumptions=assumptions,
        steps=steps,
        conclusion=(
            "If A1-A7 are proven in the full internal action, then the "
            "no-extra-light-state theorem follows."
        ),
        theorem_complete=False,
    )


def validate_theorem_scaffold(scaffold: TheoremScaffold) -> bool:
    """Validate scaffold completeness and conservative status discipline."""

    assumption_ids = {assumption.id for assumption in scaffold.assumptions}
    step_ids = {step.id for step in scaffold.steps}
    required_assumptions = {f"A{idx}" for idx in range(1, 8)}
    required_steps = {f"S{idx}" for idx in range(1, 6)}
    if assumption_ids != required_assumptions:
        return False
    if step_ids != required_steps:
        return False
    if scaffold.theorem_complete:
        return False
    for assumption in scaffold.assumptions:
        if not assumption.statement or not assumption.evidence or not assumption.limitations:
            return False
        if assumption.status == AssumptionStatus.PROVEN_CONDITIONAL and any(
            "proxy" in item.lower() for item in assumption.evidence
        ):
            return False
    for step in scaffold.steps:
        if not step.statement or not step.depends_on or not step.conclusion:
            return False
        if not set(step.depends_on).issubset(assumption_ids | step_ids):
            return False
    return bool(scaffold.conclusion)


def _to_jsonable(scaffold: TheoremScaffold) -> dict[str, object]:
    data = asdict(scaffold)
    for assumption in data["assumptions"]:
        assumption["status"] = str(assumption["status"])
    return data


def export_theorem_scaffold_markdown(path: str | Path) -> None:
    """Export the H_T theorem scaffold as Markdown."""

    scaffold = build_ht_no_extra_light_theorem_scaffold()
    if not validate_theorem_scaffold(scaffold):
        raise ValueError("invalid theorem scaffold")
    lines = [
        "# H_T No-Extra-Light-State Theorem Scaffold",
        "",
        "Gate 32D: formal sufficient theorem scaffold added. The theorem is not complete; it lists the exact assumptions A1-A7 that must be proven in the full internal action.",
        "",
        f"Title: {scaffold.title}",
        f"Theorem complete: `{scaffold.theorem_complete}`",
        "",
        "## Assumptions",
        "",
        "| ID | Status | Statement | Evidence | Limitations |",
        "| --- | --- | --- | --- | --- |",
    ]
    for assumption in scaffold.assumptions:
        lines.append(
            "| `{}` | `{}` | {} | {} | {} |".format(
                assumption.id,
                assumption.status.value,
                assumption.statement,
                "<br>".join(assumption.evidence),
                "<br>".join(assumption.limitations),
            )
        )
    lines.extend(
        [
            "",
            "## Implication Steps",
            "",
            "| ID | Depends On | Statement | Conclusion |",
            "| --- | --- | --- | --- |",
        ]
    )
    for step in scaffold.steps:
        lines.append(
            "| `{}` | {} | {} | {} |".format(
                step.id,
                ", ".join(step.depends_on),
                step.statement,
                step.conclusion,
            )
        )
    lines.extend(
        [
            "",
            "## Required Equations",
            "",
            "```text",
            "d + mu_H(1 - exp(-d/Lambda^2)) + V_min >= mu_H",
            "H_T|H_perp >= mu_H",
            "mu_H = (4 pi^2 v)^2 r_int^2",
            "m_complement >= 4 pi^2 v",
            "```",
            "",
            "## Conclusion",
            "",
            scaffold.conclusion,
            "",
            "This is a sufficient theorem scaffold only. It does not prove A1-A7.",
        ]
    )
    Path(path).write_text("\n".join(lines) + "\n")


def export_theorem_scaffold_json(path: str | Path) -> None:
    """Export the H_T theorem scaffold as JSON."""

    scaffold = build_ht_no_extra_light_theorem_scaffold()
    if not validate_theorem_scaffold(scaffold):
        raise ValueError("invalid theorem scaffold")
    Path(path).write_text(json.dumps(_to_jsonable(scaffold), indent=2, sort_keys=True) + "\n")
