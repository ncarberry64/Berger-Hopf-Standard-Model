"""BHSM v2.10 mixed Hopf/base/boundary/coframe coefficient audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mixed_coefficient_rule import (
    MIXED_COEFFICIENT_RULE_OPEN,
    build_mixed_coefficient_rule_report,
)


MIXED_COEFFICIENT_DERIVED = "MIXED_COEFFICIENT_DERIVED"
MIXED_COEFFICIENT_CONDITIONAL = "MIXED_COEFFICIENT_CONDITIONAL"
MIXED_COEFFICIENT_OPEN = "MIXED_COEFFICIENT_OPEN"
FAILS_MIXED_COEFFICIENT = "FAILS_MIXED_COEFFICIENT"


@dataclass(frozen=True)
class MixedConnectionCoefficient:
    coefficient_id: str
    source_terms: tuple[str, ...]
    symbolic_form: str
    status: str
    acts_on: tuple[str, ...]
    limitation: str


@dataclass(frozen=True)
class MixedConnectionCoefficientReport:
    title: str
    coefficients: tuple[MixedConnectionCoefficient, ...]
    all_coefficients_classified: bool
    open_coefficients: tuple[str, ...]
    exact_missing_rule: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def mixed_connection_coefficients() -> tuple[MixedConnectionCoefficient, ...]:
    rule = build_mixed_coefficient_rule_report()
    if rule.rule_status != MIXED_COEFFICIENT_RULE_OPEN:
        return tuple(
            MixedConnectionCoefficient(
                row.slot,
                (row.geometric_source, row.representation_target),
                row.value_or_rule,
                MIXED_COEFFICIENT_CONDITIONAL,
                (row.representation_target, "H_perp"),
                row.limitation,
            )
            for row in rule.rows
        )
    return (
        MixedConnectionCoefficient("hopf_fiber_base_cross", ("Hopf fiber", "base/S2"), "C_HB(q,j) [nabla_H,nabla_B]", MIXED_COEFFICIENT_OPEN, ("Hopf/base/fiber modes", "H_perp"), "The coefficient rule C_HB(q,j) is not derived from the full connection."),
        MixedConnectionCoefficient("base_boundary_cross", ("base/S2", "boundary functional"), "C_Bbd(j,Omega_f) [nabla_B,nabla_boundary]", MIXED_COEFFICIENT_OPEN, ("lepton", "up", "down", "boundary functional"), "The coefficient rule tying base nodes to boundary functional phases is not derived."),
        MixedConnectionCoefficient("boundary_coframe_cross", ("boundary functional", "coframe"), "C_bdC(Omega_f,cof) [nabla_boundary,nabla_cof]", MIXED_COEFFICIENT_OPEN, ("up", "down", "coframe channels"), "The coframe participation coefficient in the mixed connection is not fixed."),
        MixedConnectionCoefficient("hopf_boundary_coframe_mixed", ("Hopf fiber", "boundary functional", "coframe"), "C_HbdC(q,Omega_f,cof) mixed triple contraction", MIXED_COEFFICIENT_OPEN, ("charged sectors", "mirror channels", "formal kernel"), "The triple mixed coefficient is the exact missing geometric rule."),
        MixedConnectionCoefficient("chirality_dependence", ("chirality projector", "mixed connection"), "C_chi(chi) mixed chirality sign", MIXED_COEFFICIENT_OPEN, ("chirality", "mirror channels"), "The chirality-resolved mixed coefficient is not derived."),
        MixedConnectionCoefficient("sector_dependence", ("lepton/up/down sector labels", "mixed connection"), "C_sector(f) mixed sector weight", MIXED_COEFFICIENT_OPEN, ("lepton", "up", "down"), "The sector weights of the mixed connection are not derived."),
    )


def build_mixed_connection_coefficients_report() -> MixedConnectionCoefficientReport:
    coefficients = mixed_connection_coefficients()
    open_ids = tuple(row.coefficient_id for row in coefficients if row.status == MIXED_COEFFICIENT_OPEN)
    rule = build_mixed_coefficient_rule_report()
    return MixedConnectionCoefficientReport(
        title="BHSM v2.10 Mixed Connection Coefficients Report",
        coefficients=coefficients,
        all_coefficients_classified=all(row.status for row in coefficients),
        open_coefficients=open_ids,
        exact_missing_rule="" if not open_ids else "MIXED_HOPF_BASE_BOUNDARY_COFRAME_COEFFICIENT_RULE",
        status=MIXED_COEFFICIENT_OPEN if open_ids else MIXED_COEFFICIENT_CONDITIONAL,
        theorem_complete=not open_ids,
        limitations=(
            "The mixed coefficient slots are represented through the v2.11 bundle-separation/topographic-representation rule.",
            f"Rule status: {rule.rule_status}.",
            "No numerical or residual fit is used to choose coefficients.",
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


def export_mixed_connection_coefficients_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_connection_coefficients_report()), indent=2, sort_keys=True) + "\n")


def export_mixed_connection_coefficients_markdown(path: str | Path) -> None:
    report = build_mixed_connection_coefficients_report()
    lines = [
        "# BHSM v2.10 Mixed Connection Coefficients Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Exact missing rule: `{report.exact_missing_rule}`",
        "",
        "| Coefficient | Sources | Symbolic form | Status | Acts on | Limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.coefficients:
        lines.append(f"| `{row.coefficient_id}` | `{row.source_terms}` | `{row.symbolic_form}` | `{row.status}` | `{row.acts_on}` | {row.limitation} |")
    lines.extend(["", "## Open Coefficients", ""])
    lines.extend(f"- `{item}`" for item in report.open_coefficients)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
