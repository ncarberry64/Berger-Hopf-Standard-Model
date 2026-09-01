"""BHSM v2.11 coframe compatibility rule audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from topographic_representation_rule import build_topographic_representation_rule_report


COFRAME_COMPATIBILITY_CONDITIONAL = "COFRAME_COMPATIBILITY_CONDITIONAL"
COFRAME_COMPATIBILITY_FORMALIZED = "COFRAME_COMPATIBILITY_FORMALIZED"
COFRAME_COMPATIBILITY_OPEN = "COFRAME_COMPATIBILITY_OPEN"
COFRAME_COMPATIBILITY_FAILS = "COFRAME_COMPATIBILITY_FAILS"


@dataclass(frozen=True)
class CoframeCompatibilityRow:
    criterion: str
    bhsm_input: str
    conclusion: str
    status: str
    limitation: str


@dataclass(frozen=True)
class CoframeCompatibilityReport:
    title: str
    rows: tuple[CoframeCompatibilityRow, ...]
    triplet_required: bool
    singlet_variant_fails: bool
    coefficient_rule_fixed: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_coframe_compatibility_rule_report() -> CoframeCompatibilityReport:
    representation = build_topographic_representation_rule_report()
    rows = (
        CoframeCompatibilityRow(
            "triplet_participation",
            "quark coframe triplet from the v1.2 parent-action scaffold",
            "triplet participation is required for the charged-sector boundary functional",
            COFRAME_COMPATIBILITY_CONDITIONAL,
            "This fixes which coframe channel participates, not a new coefficient.",
        ),
        CoframeCompatibilityRow(
            "singlet_variant",
            "replace triplet by singlet coframe participation",
            "variant conflicts with the v1.2C tested-sector ledger",
            COFRAME_COMPATIBILITY_FAILS,
            "Failure of a nearby variant constrains structure but does not tune predictions.",
        ),
        CoframeCompatibilityRow(
            "mixed_connection_coefficient",
            "boundary/coframe cross term C_bdC",
            "independent coefficient is forbidden and represented by V_PSD/profile",
            COFRAME_COMPATIBILITY_FORMALIZED,
            "This closes the free coefficient slot; full scalar/topographic proof remains separate.",
        ),
    )
    fixed = representation.all_slots_represented_or_zero
    return CoframeCompatibilityReport(
        title="BHSM v2.11 Coframe Compatibility Rule Report",
        rows=rows,
        triplet_required=True,
        singlet_variant_fails=True,
        coefficient_rule_fixed=fixed,
        status=COFRAME_COMPATIBILITY_FORMALIZED if fixed else COFRAME_COMPATIBILITY_OPEN,
        theorem_complete=fixed,
        limitations=(
            "The coframe audit closes the free coefficient slot by representation, not by introducing numeric coefficients.",
            "No empirical mass, CKM, PMNS, residual, or prediction-ledger data are used.",
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


def export_coframe_compatibility_rule_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_coframe_compatibility_rule_report()), indent=2, sort_keys=True) + "\n")


def export_coframe_compatibility_rule_markdown(path: str | Path) -> None:
    report = build_coframe_compatibility_rule_report()
    lines = [
        "# BHSM v2.11 Coframe Compatibility Rule Report",
        "",
        f"Status: `{report.status}`",
        f"Triplet required: `{report.triplet_required}`",
        f"Singlet variant fails: `{report.singlet_variant_fails}`",
        f"Coefficient rule fixed: `{report.coefficient_rule_fixed}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Criterion | BHSM input | Conclusion | Status | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.criterion}` | {row.bhsm_input} | {row.conclusion} | `{row.status}` | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

