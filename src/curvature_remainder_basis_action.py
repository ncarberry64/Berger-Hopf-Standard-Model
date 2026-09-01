"""BHSM v2.8 basis-action audit for the curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_formula import REMAINDER_FORMULA_OPEN, build_curvature_remainder_formula_report


REMAINDER_BASIS_ACTION_DERIVED = "REMAINDER_BASIS_ACTION_DERIVED"
REMAINDER_BASIS_ACTION_CONDITIONAL = "REMAINDER_BASIS_ACTION_CONDITIONAL"
REMAINDER_BASIS_ACTION_OPEN = "REMAINDER_BASIS_ACTION_OPEN"
FAILS_REMAINDER_BASIS_ACTION = "FAILS_REMAINDER_BASIS_ACTION"


@dataclass(frozen=True)
class BasisActionFeature:
    feature: str
    status: str
    conclusion: str
    limitation: str


@dataclass(frozen=True)
class CurvatureRemainderBasisActionReport:
    title: str
    formula_status: str
    features: tuple[BasisActionFeature, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_basis_action_report() -> CurvatureRemainderBasisActionReport:
    formula = build_curvature_remainder_formula_report()
    features = (
        BasisActionFeature("diagonal_or_off_diagonal", "OPEN", "not computable without complete curvature coefficients", "Could be diagonal, off-diagonal, or mixed."),
        BasisActionFeature("sector_mixing", "OPEN", "not computable without sector curvature contraction", "Sector representation inputs alone do not determine the curvature action."),
        BasisActionFeature("chirality_mixing", "OPEN", "not computable without Clifford/chirality contraction", "Mirror leakage cannot be ruled out from formula scaffold alone."),
        BasisActionFeature("base_fiber_dependence", "OPEN", "not computable without Hopf/base mixed curvature formula", "Existing Hopf/base terms are represented, but the mixed remainder is not."),
        BasisActionFeature("boundedness_behavior", "OPEN", "no growth law or norm estimate is available", "Relative-bound constants cannot be derived."),
        BasisActionFeature("formal_kernel_action", "OPEN", "not proven to vanish on formal kernel", "Kernel safety requires explicit action."),
        BasisActionFeature("h_perp_preservation", "OPEN", "not proven to preserve H_perp", "Commutator with the complement projector cannot be closed."),
        BasisActionFeature("mirror_leakage", "OPEN", "not proven absent", "Mirror-channel safety remains conditional."),
    )
    status = REMAINDER_BASIS_ACTION_OPEN if formula.status == REMAINDER_FORMULA_OPEN else REMAINDER_BASIS_ACTION_CONDITIONAL
    return CurvatureRemainderBasisActionReport(
        title="BHSM v2.8 Curvature Remainder Basis Action Report",
        formula_status=formula.status,
        features=features,
        status=status,
        theorem_complete=False,
        limitations=(
            "The basis action cannot be derived more strongly than the formula.",
            "No finite-basis or analytic action matrix is introduced for an unidentified curvature term.",
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


def export_curvature_remainder_basis_action_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_basis_action_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_basis_action_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_basis_action_report()
    lines = [
        "# BHSM v2.8 Curvature Remainder Basis Action Report",
        "",
        f"Formula status: `{report.formula_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Feature | Status | Conclusion | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.features:
        lines.append(f"| `{row.feature}` | `{row.status}` | {row.conclusion} | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
