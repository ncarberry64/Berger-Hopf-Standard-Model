"""BHSM v2.0 lower-bound preservation audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from relative_bound_closure import build_relative_bound_closure_report


LOWER_BOUND_PRESERVED = "LOWER_BOUND_PRESERVED"
LOWER_BOUND_CONDITIONAL = "LOWER_BOUND_CONDITIONAL"
LOWER_BOUND_OPEN = "LOWER_BOUND_OPEN"
FAILS_LOWER_BOUND = "FAILS_LOWER_BOUND"


@dataclass(frozen=True)
class LowerBoundPreservationReport:
    title: str
    unperturbed_diagonal_lower_bound: float
    perturbation_degradation_estimate: float
    resulting_lower_bound: float
    required_dirac_lower_bound: float
    clears_required_threshold: bool
    applies_to_formal_complement: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_lower_bound_preservation_report() -> LowerBoundPreservationReport:
    rel = build_relative_bound_closure_report()
    unperturbed = 6.8171156827281205
    degradation = rel.total_a * unperturbed + rel.total_b * 0.0
    resulting = unperturbed - degradation
    required = 0.8038064161349437
    clears = resulting >= required
    status = LOWER_BOUND_PRESERVED if clears and rel.theorem_complete else LOWER_BOUND_CONDITIONAL if clears else FAILS_LOWER_BOUND
    return LowerBoundPreservationReport(
        title="BHSM v2.0 Lower-Bound Preservation Report",
        unperturbed_diagonal_lower_bound=unperturbed,
        perturbation_degradation_estimate=degradation,
        resulting_lower_bound=resulting,
        required_dirac_lower_bound=required,
        clears_required_threshold=clears,
        applies_to_formal_complement=False,
        status=status,
        theorem_complete=status == LOWER_BOUND_PRESERVED,
        open_obligations=(
            "prove the relative-bound closure without finite-scan assumptions",
            "prove formal complement stability before applying the bound to H_perp",
            "combine with index and mirror exclusion before claiming full H_T theorem",
        ),
        limitations=("The numerical lower-bound margin remains favorable, but its theorem use is conditional.",),
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


def export_lower_bound_preservation_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_lower_bound_preservation_report()), indent=2, sort_keys=True) + "\n")


def export_lower_bound_preservation_markdown(path: str | Path) -> None:
    report = build_lower_bound_preservation_report()
    lines = [
        "# BHSM v2.0 Lower-Bound Preservation Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Unperturbed lower bound: `{report.unperturbed_diagonal_lower_bound}`",
        f"Perturbation degradation estimate: `{report.perturbation_degradation_estimate}`",
        f"Resulting lower bound: `{report.resulting_lower_bound}`",
        f"Required Dirac lower bound: `{report.required_dirac_lower_bound}`",
        f"Clears threshold: `{report.clears_required_threshold}`",
        f"Applies to formal complement: `{report.applies_to_formal_complement}`",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

