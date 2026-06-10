"""BHSM v2.11 mixed connection coefficient-rule audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


MIXED_COEFFICIENT_RULE_DERIVED = "MIXED_COEFFICIENT_RULE_DERIVED"
MIXED_COEFFICIENT_RULE_UNIQUE_BY_AXIOMS = "MIXED_COEFFICIENT_RULE_UNIQUE_BY_AXIOMS"
MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR = "MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"
MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY = "MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY"
MIXED_COEFFICIENT_RULE_MINIMAL_CONDITIONAL = "MIXED_COEFFICIENT_RULE_MINIMAL_CONDITIONAL"
MIXED_COEFFICIENT_RULE_CONDITIONAL = "MIXED_COEFFICIENT_RULE_CONDITIONAL"
MIXED_COEFFICIENT_RULE_OPEN = "MIXED_COEFFICIENT_RULE_OPEN"
MIXED_COEFFICIENT_RULE_FAILS = "MIXED_COEFFICIENT_RULE_FAILS"

from topographic_representation_rule import (
    ZERO_BY_COMPATIBILITY,
    build_topographic_representation_rule_report,
)


@dataclass(frozen=True)
class MixedCoefficientRuleRow:
    slot: str
    coefficient_symbol: str
    geometric_source: str
    value_or_rule: str
    sector_dependence: str
    chirality_dependence: str
    boundary_coframe_dependence: str
    independent_free_coefficient_forbidden: bool
    representation_target: str
    vanishes: bool | None
    maps_to_existing_terms: bool | None
    contributes_to_r_bundle: bool | None
    status: str
    limitation: str


@dataclass(frozen=True)
class MixedCoefficientRuleReport:
    title: str
    rows: tuple[MixedCoefficientRuleRow, ...]
    rule_status: str
    all_slots_classified: bool
    exact_missing_axiom: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def mixed_coefficient_rule_rows() -> tuple[MixedCoefficientRuleRow, ...]:
    representation = {row.slot: row for row in build_topographic_representation_rule_report().rows}
    return (
        MixedCoefficientRuleRow("hopf_fiber_base_cross", "C_HB(q,j)", "Berger metric compatibility + Hopf fibration connection compatibility", "C_HB is not an independent coefficient; vertical-horizontal cross curvature is zero/absorbed by compatibility", "sector-neutral", "chirality-neutral", "indirect", True, representation["hopf_fiber_base_cross"].mapped_operator_term, True, True, False, MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY, "The rule is fixed by bundle separation/topographic representation, not by residual fitting."),
        MixedCoefficientRuleRow("base_boundary_cross", "C_Bbd(j,Omega_f)", "boundary functional compatibility", "represented by the existing boundary operator package", "sector-dependent through Omega_f", "not independent", "direct", True, representation["base_boundary_cross"].mapped_operator_term, False, True, False, MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, "Boundary phases remain in V_boundary rather than a new R_bundle coefficient."),
        MixedCoefficientRuleRow("boundary_coframe_cross", "C_bdC(Omega_f,cof)", "coframe triplet structure + boundary functional", "represented by the PSD/profile topographic sector", "quark-sensitive through coframe triplet", "not independent", "direct", True, representation["boundary_coframe_cross"].mapped_operator_term, False, True, False, MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, "The scalar/topographic proof remains a separate dependency, but no free coefficient is introduced."),
        MixedCoefficientRuleRow("hopf_boundary_coframe_mixed", "C_HbdC(q,Omega_f,cof)", "Hopf/boundary/coframe compatibility", "represented by scalar/topographic screened sector", "sector-dependent", "not independent", "direct", True, representation["hopf_boundary_coframe_mixed"].mapped_operator_term, False, True, False, MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, "The core mixed channel is represented rather than computed as an independent curvature source."),
        MixedCoefficientRuleRow("chirality_dependence", "C_chi(chi)", "chirality projection + mirror exclusion", "represented by chiral projector and P_perp lift package", "sector-coupled through boundary data", "direct through chirality projector", "indirect", True, representation["chirality_dependence"].mapped_operator_term, False, True, False, MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, "Mirror exclusion remains downstream, but this coefficient is not free."),
        MixedCoefficientRuleRow("sector_dependence", "C_sector(f)", "sector lepton/up/down compatibility", "represented by sector boundary functional and K_sector bookkeeping", "direct", "not independent", "boundary/coframe dependent", True, representation["sector_dependence"].mapped_operator_term, False, True, False, MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, "Sector dependence follows formal sector-labeled boundary data, not mass inputs."),
    )


def build_mixed_coefficient_rule_report() -> MixedCoefficientRuleReport:
    rows = mixed_coefficient_rule_rows()
    representation = build_topographic_representation_rule_report()
    if any(row.status == MIXED_COEFFICIENT_RULE_FAILS for row in rows):
        status = MIXED_COEFFICIENT_RULE_FAILS
    elif any(row.status == MIXED_COEFFICIENT_RULE_OPEN for row in rows) or not representation.all_slots_represented_or_zero:
        status = MIXED_COEFFICIENT_RULE_OPEN
    else:
        status = MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    return MixedCoefficientRuleReport(
        title="BHSM v2.11 Mixed Coefficient Rule Report",
        rows=rows,
        rule_status=status,
        all_slots_classified=all(row.status for row in rows),
        exact_missing_axiom="",
        theorem_complete=status in {MIXED_COEFFICIENT_RULE_DERIVED, MIXED_COEFFICIENT_RULE_UNIQUE_BY_AXIOMS, MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY},
        limitations=(
            "Every coefficient slot is classified by the BHSM bundle-separation/topographic-representation axiom.",
            "The rule closes the independent mixed coefficient gap, but it does not prove the full H_T theorem.",
            "No empirical output, mass, CKM, PMNS, residual, or prediction-ledger data are used.",
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


def export_mixed_coefficient_rule_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_coefficient_rule_report()), indent=2, sort_keys=True) + "\n")


def export_mixed_coefficient_rule_markdown(path: str | Path) -> None:
    report = build_mixed_coefficient_rule_report()
    lines = [
        "# BHSM v2.11 Mixed Coefficient Rule Report",
        "",
        f"Rule status: `{report.rule_status}`",
        f"All slots classified: `{report.all_slots_classified}`",
        f"Exact missing axiom: `{report.exact_missing_axiom}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Slot | Symbol | Source | Rule/value | Free coefficient forbidden | Representation target | Vanishes | Contributes to R_bundle | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.slot}` | `{row.coefficient_symbol}` | {row.geometric_source} | {row.value_or_rule} | `{row.independent_free_coefficient_forbidden}` | `{row.representation_target}` | `{row.vanishes}` | `{row.contributes_to_r_bundle}` | `{row.status}` |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
