"""Combined offline report for the three theorem-closure attempts."""

from __future__ import annotations

from pathlib import Path

from .common import TheoremClosureReport, TheoremClosureResult
from .cp_o_int import evaluate_cp_o_int_candidate
from .neutrino_basis_scale import evaluate_neutrino_basis_scale_candidate
from .x_ch import evaluate_x_ch_candidate


def evaluate_theorem(theorem_key: str, repository: str | Path | None = None) -> TheoremClosureResult:
    evaluators = {
        "X_ch": evaluate_x_ch_candidate,
        "neutrino_basis_scale": evaluate_neutrino_basis_scale_candidate,
        "cp_o_int": evaluate_cp_o_int_candidate,
    }
    try:
        evaluator = evaluators[theorem_key]
    except KeyError as exc:
        raise KeyError(f"unknown theorem key: {theorem_key}") from exc
    return evaluator(repository=repository)


def build_theorem_closure_report(repository: str | Path | None = None) -> TheoremClosureReport:
    return TheoremClosureReport(tuple(evaluate_theorem(key, repository) for key in ("X_ch", "neutrino_basis_scale", "cp_o_int")))


def theorem_closure_report_to_markdown(report: TheoremClosureReport) -> str:
    lines = [
        "# BHSM Theorem Closure Sprint A",
        "",
        "Theorem closure requires executable artifact-backed support; narrative plausibility is not enough.",
        "",
        "| Theorem | Status | Promotion | Missing object |",
        "| --- | --- | --- | --- |",
    ]
    for result in report.results:
        missing = "; ".join(result.missing_objects) or "none"
        lines.append(f"| `{result.theorem_key}` | `{result.closure_status}` | `{str(result.promotion_allowed).lower()}` | {missing} |")
    lines.extend([
        "",
        "Reference values, including PDG values, are comparison inputs only and are never theorem inputs.",
        "",
        "Runtime-disabled software gates remain disabled until live external validation passes.",
    ])
    return "\n".join(lines) + "\n"
