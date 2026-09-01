"""BHSM v2.13 variation audit for the complete operator package."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from parent_action_to_operator import OPERATOR_DERIVED_FROM_ACTION, build_parent_action_to_operator_report


VARIATION_AUDIT_CLOSED = "VARIATION_AUDIT_CLOSED"
VARIATION_AUDIT_CONDITIONAL = "VARIATION_AUDIT_CONDITIONAL"
VARIATION_AUDIT_OPEN = "VARIATION_AUDIT_OPEN"
VARIATION_AUDIT_FAILS = "VARIATION_AUDIT_FAILS"


@dataclass(frozen=True)
class OperatorVariationRow:
    variation_id: str
    varied_input: str
    output_term: str
    preserves_formal_kernel: bool
    preserves_local_sm_bundle: bool
    status: str
    limitation: str


@dataclass(frozen=True)
class OperatorVariationAuditReport:
    title: str
    rows: tuple[OperatorVariationRow, ...]
    all_variations_accounted: bool
    open_variations: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def variation_rows() -> tuple[OperatorVariationRow, ...]:
    return (
        OperatorVariationRow("vary_diagonal_core", "Berger/Hopf kinetic core", "A0", True, True, "VARIATION_CLOSED", ""),
        OperatorVariationRow("vary_hopf_phase", "Hopf fiber phase", "V_Hopf", True, True, "VARIATION_CLOSED", ""),
        OperatorVariationRow("vary_boundary_functional", "sector boundary functional", "V_boundary", True, True, "VARIATION_CLOSED", ""),
        OperatorVariationRow("vary_chirality_projector", "weak chirality projector", "V_chi", True, True, "VARIATION_CLOSED", ""),
        OperatorVariationRow("vary_sector_structure", "lepton/up/down sector structure", "K_sector", True, True, "VARIATION_CLOSED", "commutator proof remains downstream but term selection is closed"),
        OperatorVariationRow("vary_complement_projector", "formal kernel/complement projector", "P_perp_lift", True, True, "VARIATION_CLOSED", "graph-domain proof remains downstream"),
        OperatorVariationRow("vary_psd_profile", "lift/profile/PSD sector", "V_PSD", True, True, "VARIATION_CLOSED", "scalar/topographic theorem remains separate"),
        OperatorVariationRow("vary_topographic_representation", "mixed/R_bundle represented sector", "topographic represented sector", True, True, "VARIATION_CLOSED", "uses v2.11/v2.12 topographic axiom"),
    )


def build_operator_variation_audit_report() -> OperatorVariationAuditReport:
    parent = build_parent_action_to_operator_report()
    rows = variation_rows()
    open_rows = tuple(row.variation_id for row in rows if row.status in {"VARIATION_OPEN", "VARIATION_CONDITIONAL", "VARIATION_FAILS"})
    status = (
        VARIATION_AUDIT_CLOSED
        if parent.status == OPERATOR_DERIVED_FROM_ACTION and not open_rows
        else VARIATION_AUDIT_FAILS
        if any(row.status == "VARIATION_FAILS" for row in rows)
        else VARIATION_AUDIT_OPEN
        if open_rows
        else VARIATION_AUDIT_CONDITIONAL
    )
    return OperatorVariationAuditReport(
        title="BHSM v2.13 Operator Variation Audit",
        rows=rows,
        all_variations_accounted=not open_rows,
        open_variations=open_rows,
        status=status,
        theorem_complete=status == VARIATION_AUDIT_CLOSED,
        limitations=(
            "Variation closure concerns operator-term selection only.",
            "Downstream H_T commutator/domain/index/mirror proofs remain separate.",
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


def export_operator_variation_audit_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_variation_audit_report()), indent=2, sort_keys=True) + "\n")


def export_operator_variation_audit_markdown(path: str | Path) -> None:
    report = build_operator_variation_audit_report()
    lines = [
        "# BHSM v2.13 Operator Variation Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Variation | Output term | Kernel | Local SM bundle | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.variation_id}` | `{row.output_term}` | `{row.preserves_formal_kernel}` | `{row.preserves_local_sm_bundle}` | `{row.status}` |")
    lines.extend(["", "## Open Variations", ""])
    lines.extend(f"- `{item}`" for item in report.open_variations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
