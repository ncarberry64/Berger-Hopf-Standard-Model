"""Final BHSM closure campaign ledger."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from action_dependency_closure import build_action_dependency_closure_report
from full_ht_theorem import build_full_ht_theorem_report
from qcd_precision_closure import build_qcd_precision_closure_report
from virtual_dressing_theorem import build_virtual_dressing_theorem_report
from fifth_force_exclusion import build_scalar_screening_proof_report


FROZEN = "FROZEN"
PROVEN = "PROVEN"
THEOREM_CANDIDATE = "THEOREM_CANDIDATE"
STRONG_SCAFFOLD = "STRONG_SCAFFOLD"
CONDITIONAL = "CONDITIONAL"
OPEN = "OPEN"
FORBIDDEN = "FORBIDDEN"

FULL_BHSM_COMPLETE = "FULL_BHSM_COMPLETE"
BHSM_STRONG_SCAFFOLD = "BHSM_STRONG_SCAFFOLD"
BHSM_PARTIAL = "BHSM_PARTIAL"
BHSM_FAILED = "BHSM_FAILED"


@dataclass(frozen=True)
class FinalTheoremLedgerRow:
    """One final theorem ledger row."""

    id: str
    title: str
    status: str
    gate_status: str
    closed: bool
    open_obligations: tuple[str, ...]
    forbidden_upgrade: str


@dataclass(frozen=True)
class FinalClosureReport:
    """Final closure campaign report."""

    title: str
    gates_completed: tuple[str, ...]
    theorem_ledger: tuple[FinalTheoremLedgerRow, ...]
    full_bhsm_complete: bool
    full_theorem_package_complete: bool
    better_rubric_than_sm_ledger_candidate: bool
    final_status: str
    frozen_outputs_changed: bool
    theorem_complete: bool
    correct_final_claim: str
    remaining_open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_final_theorem_ledger() -> tuple[FinalTheoremLedgerRow, ...]:
    """Build final theorem ledger rows."""

    ht = build_full_ht_theorem_report()
    vd = build_virtual_dressing_theorem_report()
    qcd = build_qcd_precision_closure_report()
    scalar = build_scalar_screening_proof_report()
    action = build_action_dependency_closure_report()
    return (
        FinalTheoremLedgerRow("frozen_predictions", "BHSM v1 frozen prediction branches", FROZEN, "FROZEN", True, (), "Do not claim all model outputs are final confirmed predictions."),
        FinalTheoremLedgerRow("omega_f", "boundary operators Omega_f", THEOREM_CANDIDATE, "BOUNDARY_FUNCTIONAL_DERIVED", False, ("derive boundary functional from complete action globally",), "Do not claim complete action derivation."),
        FinalTheoremLedgerRow(
            "ht_gap",
            "full H_T no-extra-light theorem",
            STRONG_SCAFFOLD,
            ht.status,
            False,
            (
                "Compute or prove the full twisted Dirac / H_T spectrum in the complete operator.",
                *ht.remaining_open_nodes,
            ),
            "Do not claim FULL_HT_THEOREM_PROVEN.",
        ),
        FinalTheoremLedgerRow("scalar_topographic", "scalar/topographic screening and decoupling", STRONG_SCAFFOLD, scalar.status, False, ("prove global scalar/topographic action decoupling",), "Do not claim full scalar-screening theorem."),
        FinalTheoremLedgerRow("virtual_dressing", "Z_virt^{u,2}=1/2 dressed candidate", THEOREM_CANDIDATE, vd.status, False, vd.open_obligations, "Do not claim dressed branch canonical."),
        FinalTheoremLedgerRow("qcd_rg", "precision QCD/RG comparison", OPEN, qcd.status, False, qcd.open_obligations, "Do not claim precision QCD matching complete."),
        FinalTheoremLedgerRow("unified_action", "unified action dependency graph", STRONG_SCAFFOLD, action.status, False, tuple(action.open_nodes), "Do not claim FULL_ACTION_CLOSED."),
        FinalTheoremLedgerRow("forbidden_claims", "forbidden overclaims", FORBIDDEN, "ACTIVE", True, (), "Do not claim pure first-principles SM derivation, H_T theorem proof, precision QCD closure, or final dressed adoption."),
    )


def build_final_closure_report() -> FinalClosureReport:
    """Build the final BHSM closure campaign report."""

    ledger = build_final_theorem_ledger()
    open_obligations = tuple(
        dict.fromkeys(item for row in ledger for item in row.open_obligations)
    )
    full_complete = all(row.closed for row in ledger if row.status != FORBIDDEN)
    failed = any(row.status == "FAIL" for row in ledger)
    final_status = FULL_BHSM_COMPLETE if full_complete else BHSM_FAILED if failed else BHSM_STRONG_SCAFFOLD
    return FinalClosureReport(
        title="BHSM Final Closure Campaign Report",
        gates_completed=(
            "Gate 1: full H_T theorem closure attempt",
            "Gate 2: virtual dressing closure attempt",
            "Gate 3: precision QCD/RG closure attempt",
            "Gate 4: unified action dependency closure",
            "Gate 5: final theorem ledger and open obligations",
        ),
        theorem_ledger=ledger,
        full_bhsm_complete=full_complete,
        full_theorem_package_complete=full_complete,
        better_rubric_than_sm_ledger_candidate=True,
        final_status=final_status,
        frozen_outputs_changed=False,
        theorem_complete=full_complete,
        correct_final_claim=(
            "BHSM is a strong no-retuning geometric Standard Model reinterpretation framework "
            "with frozen predictions and multiple theorem scaffolds, but not a fully closed "
            "first-principles theorem package."
        ),
        remaining_open_obligations=open_obligations,
        limitations=(
            "No theorem node is marked complete unless implemented and dependency-clean.",
            "Frozen predictions and tolerance bands are unchanged.",
            "Open obligations are explicit rather than hidden.",
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


def export_final_closure_json(path: str | Path) -> None:
    """Export final closure report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_final_closure_report()), indent=2, sort_keys=True) + "\n")


def export_final_theorem_ledger_json(path: str | Path) -> None:
    """Export final theorem ledger as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_final_theorem_ledger()), indent=2, sort_keys=True) + "\n")


def export_final_closure_markdown(path: str | Path) -> None:
    """Export final closure report as Markdown."""

    report = build_final_closure_report()
    lines = [
        "# BHSM Final Closure Campaign Report",
        "",
        f"Final status: `{report.final_status}`",
        f"Full BHSM complete: `{report.full_bhsm_complete}`",
        f"Full theorem package complete: `{report.full_theorem_package_complete}`",
        f"Frozen outputs changed: `{report.frozen_outputs_changed}`",
        "",
        "## Correct Final Claim",
        "",
        report.correct_final_claim,
        "",
        "## Gates Completed",
        "",
    ]
    lines.extend(f"- {item}" for item in report.gates_completed)
    lines.extend(["", "## Theorem Ledger", "", "| ID | Status | Gate status | Closed | Open obligations |", "| --- | --- | --- | --- | --- |"])
    for row in report.theorem_ledger:
        lines.append(f"| `{row.id}` | `{row.status}` | `{row.gate_status}` | `{row.closed}` | {'<br>'.join(row.open_obligations) or 'none'} |")
    lines.extend(["", "## Remaining Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.remaining_open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_final_theorem_ledger_markdown(path: str | Path) -> None:
    """Export final theorem ledger as Markdown."""

    rows = build_final_theorem_ledger()
    lines = [
        "# BHSM Final Theorem Ledger",
        "",
        "| ID | Title | Status | Gate status | Closed | Forbidden upgrade |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row.id}` | {row.title} | `{row.status}` | `{row.gate_status}` | `{row.closed}` | {row.forbidden_upgrade} |")
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_final_open_obligations_markdown(path: str | Path) -> None:
    """Export final open obligations as Markdown."""

    report = build_final_closure_report()
    lines = ["# BHSM Final Open Obligations", ""]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(report.remaining_open_obligations, start=1))
    lines.append("")
    Path(path).write_text("\n".join(lines))
