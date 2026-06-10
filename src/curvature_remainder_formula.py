"""BHSM v2.8 formula audit for the bundle-curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


REMAINDER_FORMULA_DERIVED = "REMAINDER_FORMULA_DERIVED"
REMAINDER_FORMULA_CONDITIONAL = "REMAINDER_FORMULA_CONDITIONAL"
REMAINDER_FORMULA_OPEN = "REMAINDER_FORMULA_OPEN"
FAILS_REMAINDER_FORMULA = "FAILS_REMAINDER_FORMULA"

REMAINDER_TERM_ID = "lichnerowicz_bundle_curvature_remainder"


@dataclass(frozen=True)
class FormulaComponent:
    component_id: str
    symbolic_term: str
    represented_by: str
    status: str
    limitation: str


@dataclass(frozen=True)
class CurvatureRemainderFormulaReport:
    title: str
    term_id: str
    lichnerowicz_identity: str
    remainder_formula: str
    components: tuple[FormulaComponent, ...]
    status: str
    theorem_complete: bool
    exact_missing_input: str
    limitations: tuple[str, ...]


def formula_components() -> tuple[FormulaComponent, ...]:
    """Return the symbolic formula decomposition currently available."""

    return (
        FormulaComponent("hopf_curvature_contraction", "c(F_Hopf)", "V_Hopf", "REPRESENTED_SYMBOLICALLY", "Coefficient-level contraction in the complete bundle connection is not derived."),
        FormulaComponent("boundary_curvature_contraction", "c(F_boundary)", "V_boundary", "REPRESENTED_SYMBOLICALLY", "Boundary functional curvature is action-linked but not fully action-derived."),
        FormulaComponent("chirality_curvature_contraction", "c(F_chi)", "V_chi", "REPRESENTED_SYMBOLICALLY", "Chirality action is scaffold-controlled, not a full curvature theorem."),
        FormulaComponent("sector_curvature_contraction", "c(F_sector)", "K_sector", "REPRESENTED_SYMBOLICALLY", "Sector off-diagonal curvature coefficients are not derived from the complete connection."),
        FormulaComponent("profile_curvature_contraction", "c(F_profile)", "V_PSD", "CONDITIONAL_PROFILE_REPRESENTATION", "Only safe if the curvature contraction is proven PSD/profile-controlled."),
        FormulaComponent("unresolved_mixed_curvature", "c(F_mixed^BH) - represented contractions", "not represented", "OPEN", "The complete mixed bundle-curvature formula/action is not specified."),
    )


def build_curvature_remainder_formula_report() -> CurvatureRemainderFormulaReport:
    components = formula_components()
    open_components = tuple(row for row in components if row.status == "OPEN")
    status = REMAINDER_FORMULA_OPEN if open_components else REMAINDER_FORMULA_CONDITIONAL
    return CurvatureRemainderFormulaReport(
        title="BHSM v2.8 Curvature Remainder Formula Report",
        term_id=REMAINDER_TERM_ID,
        lichnerowicz_identity="D_BH^2 = nabla_BH^* nabla_BH + scal_BH/4 + c(F_BH)",
        remainder_formula="R_bundle = c(F_BH) - (V_Hopf + V_boundary + V_chi + K_sector + V_PSD represented curvature contractions)",
        components=components,
        status=status,
        theorem_complete=False,
        exact_missing_input="COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP",
        limitations=(
            "The Lichnerowicz structure is formalized but the complete mixed curvature contraction is not derived.",
            "No harmless classification follows until the missing connection-curvature formula is supplied.",
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


def export_curvature_remainder_formula_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_formula_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_formula_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_formula_report()
    lines = [
        "# BHSM v2.8 Curvature Remainder Formula Report",
        "",
        f"Term: `{report.term_id}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        f"Lichnerowicz identity: `{report.lichnerowicz_identity}`",
        f"Remainder formula: `{report.remainder_formula}`",
        f"Exact missing input: `{report.exact_missing_input}`",
        "",
        "| Component | Symbolic term | Represented by | Status | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.components:
        lines.append(f"| `{row.component_id}` | `{row.symbolic_term}` | `{row.represented_by}` | `{row.status}` | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
