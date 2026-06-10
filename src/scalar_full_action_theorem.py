"""Scalar/topographic full action theorem completion wrapper."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from fifth_force_exclusion import ScalarScreeningProofReport, build_scalar_screening_proof_report
from scalar_screening_action import SCREENING_SCAFFOLD_PASSES


SCALAR_FULL_ACTION_THEOREM_PROVEN = "SCALAR_FULL_ACTION_THEOREM_PROVEN"
SCALAR_FULL_ACTION_THEOREM_CANDIDATE = "SCALAR_FULL_ACTION_THEOREM_CANDIDATE"
SCALAR_FULL_ACTION_PROOF_OPEN = "SCALAR_FULL_ACTION_PROOF_OPEN"
OPEN_SCALAR_RISK = "OPEN_SCALAR_RISK"
FAILS_SCALAR_THEOREM = "FAILS_SCALAR_THEOREM"


@dataclass(frozen=True)
class ScalarFullActionTheoremReport:
    """Full scalar/topographic action theorem status."""

    title: str
    screening_report: ScalarScreeningProofReport
    exactly_one_higgs_projection: bool
    open_scalar_risk_count: int
    ordinary_fifth_force_mediators: int
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_scalar_full_action_theorem_report() -> ScalarFullActionTheoremReport:
    """Build the conservative scalar full-action report."""

    screening = build_scalar_screening_proof_report()
    higgs_count = sum(row.higgs_projected_sm_scalar for row in screening.matter_coupling_audit)
    open_risk_count = len(screening.fifth_force_exclusion.open_scalar_risks)
    fifth_force_count = sum(row.ordinary_on_shell_fifth_force_mediator for row in screening.matter_coupling_audit)
    if open_risk_count:
        status = OPEN_SCALAR_RISK
    elif screening.status == SCREENING_SCAFFOLD_PASSES and higgs_count == 1 and fifth_force_count == 0:
        status = SCALAR_FULL_ACTION_PROOF_OPEN
    else:
        status = FAILS_SCALAR_THEOREM
    return ScalarFullActionTheoremReport(
        title="BHSM Scalar/Topographic Full Action Theorem Attempt",
        screening_report=screening,
        exactly_one_higgs_projection=higgs_count == 1,
        open_scalar_risk_count=open_risk_count,
        ordinary_fifth_force_mediators=fifth_force_count,
        status=status,
        theorem_complete=False,
        open_obligations=(
            "derive all scalar/topographic screening channels from the complete action",
            "prove global absence of unscreened direct light scalar matter couplings",
            "connect scalar complement lifting to the full H_T theorem",
        ),
        limitations=(
            "The v1.6 scaffold passes with zero current open scalar risk rows.",
            "This wrapper does not upgrade scaffold screening to a complete action proof.",
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


def export_scalar_full_action_theorem_json(path: str | Path) -> None:
    """Export the scalar full-action theorem report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_scalar_full_action_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_scalar_full_action_theorem_markdown(path: str | Path) -> None:
    """Export the scalar full-action theorem report as Markdown."""

    report = build_scalar_full_action_theorem_report()
    lines = [
        "# BHSM Scalar/Topographic Full Action Theorem Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Scaffold Checks",
        "",
        f"- Screening scaffold status: `{report.screening_report.status}`",
        f"- Exactly one Higgs projection: `{report.exactly_one_higgs_projection}`",
        f"- Open scalar risk rows: `{report.open_scalar_risk_count}`",
        f"- Ordinary fifth-force mediators: `{report.ordinary_fifth_force_mediators}`",
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
    Path(path).write_text("\n".join(lines))

