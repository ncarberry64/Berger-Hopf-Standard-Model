"""Focused P0 sprint audit for BHSM boundary-operator derivation.

This module inspects the repository-supported boundary-operator evidence and
classifies whether the charged-sector operators are actually derived.  It does
not change frozen BHSM outputs and it deliberately keeps the claim below
derivation level unless an action, spectral, or boundary principle forces the
operators.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_v1 import compare_bhsm_v1_branches
from boundary_derivation import (
    DerivationStatus,
    action_link_report,
    boundary_equation,
    compare_to_operational_omega,
    default_boundaries,
)
from mode_selection import EXPECTED_LEDGER, HEAVY_MODE, hopf_charge


ACTION_DERIVED = "ACTION_DERIVED"
SPECTRAL_DERIVED = "SPECTRAL_DERIVED"
BOUNDARY_DERIVED = "BOUNDARY_DERIVED"
STRUCTURALLY_MOTIVATED_NOT_DERIVED = "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
NOT_DERIVED_BLOCKER = "NOT_DERIVED_BLOCKER"


@dataclass(frozen=True)
class BoundarySprintFinding:
    """One sector-level boundary-operator finding."""

    sector: str
    equation: str
    fiber_coefficient_on_q: int
    base_coefficient_on_j: int
    target: int
    derivation_status: str
    heavy_mode: tuple[int, int]
    selected_modes: tuple[tuple[int, int], ...]
    selected_mode_charges: tuple[int, ...]
    selected_modes_satisfy_target: bool
    action_linked_evidence: str
    derivation_gap: str


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def frozen_sanity_payload() -> dict[str, Any]:
    """Return frozen-branch sanity checks without modifying outputs."""

    comparison = compare_bhsm_v1_branches()
    rows = comparison["rows"]
    changed = [row for row in rows if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in rows if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in rows if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def boundary_sprint_findings() -> tuple[BoundarySprintFinding, ...]:
    """Return sector-level findings for the boundary-operator sprint."""

    findings: list[BoundarySprintFinding] = []
    for sector, boundary in default_boundaries().items():
        action_report = action_link_report(sector)
        comparison = compare_to_operational_omega(sector)
        selected_modes = tuple(tuple(mode) for mode in EXPECTED_LEDGER[sector])
        selected_targets = [row["symbolic"] for row in comparison["comparisons"]]
        findings.append(
            BoundarySprintFinding(
                sector=sector,
                equation=boundary_equation(boundary),
                fiber_coefficient_on_q=boundary.fiber_weight,
                base_coefficient_on_j=boundary.base_weight,
                target=boundary.target,
                derivation_status=boundary.derivation_status.value,
                heavy_mode=HEAVY_MODE,
                selected_modes=selected_modes,
                selected_mode_charges=tuple(hopf_charge(*mode) for mode in selected_modes),
                selected_modes_satisfy_target=all(
                    value == boundary.target for value in selected_targets
                ),
                action_linked_evidence=(
                    "Symbolic phase factors reproduce the operational coefficients: "
                    f"{action_report['phase_contributions']}."
                ),
                derivation_gap=(
                    "The phase factors are inputs to the scaffold. The repository does not "
                    "derive them from variation, self-adjoint boundary conditions, or the "
                    "spectrum of the full twisted Dirac/bundle action."
                ),
            )
        )
    return tuple(findings)


def derivation_sprint_payload() -> dict[str, Any]:
    """Return the focused P0 boundary-operator sprint payload."""

    findings = boundary_sprint_findings()
    all_action_linked = all(item.derivation_status == DerivationStatus.ACTION_LINKED for item in findings)
    all_targets_satisfied = all(item.selected_modes_satisfy_target for item in findings)
    actual_derivation_present = any(
        item.derivation_status == DerivationStatus.ACTION_DERIVED for item in findings
    )
    classification = (
        STRUCTURALLY_MOTIVATED_NOT_DERIVED
        if all_action_linked and all_targets_satisfied and not actual_derivation_present
        else NOT_DERIVED_BLOCKER
    )
    return {
        "title": "BHSM focused P0 boundary-operator derivation sprint",
        "p0_blocker": "BOUNDARY_OPERATORS_NOT_ACTION_DERIVED",
        "classification": classification,
        "p0_boundary_blocker_closed": classification
        in {ACTION_DERIVED, SPECTRAL_DERIVED, BOUNDARY_DERIVED},
        "action_derived": False,
        "spectral_derived": False,
        "boundary_derived": False,
        "official_frozen_outputs_changed": False,
        "helps_derive_z_virt_u2_half": False,
        "helps_derive_ckm_exponent_1_16": False,
        "shared_boundary_principle": {
            "answer": (
                "A shared symbolic phase bookkeeping rule exists, but it is not an "
                "action/spectral/boundary derivation."
            ),
            "classification": STRUCTURALLY_MOTIVATED_NOT_DERIVED,
        },
        "coefficient_forcing": {
            "answer": (
                "The coefficients are reproduced from assigned Hopf fiber, chirality, "
                "weak-component, and coframe factors. The repo does not show that those "
                "factors are forced by the complete BHSM action."
            ),
            "forced": False,
        },
        "target_origin": {
            "answer": (
                "The targets equal family index times sector winding multipliers and are "
                "satisfied by the selected modes. This is not, by itself, an independent "
                "derivation of the targets."
            ),
            "selected_modes_only": False,
        },
        "action_spectral_boundary_result": {
            "answer": (
                "No non-fitted action variation, spectral condition, self-adjoint-domain "
                "condition, or boundary condition was found that forces all three formulas."
            ),
            "derivation_found": False,
        },
        "additional_structure_required": (
            "A complete internal action/bundle boundary functional, a variational or "
            "self-adjoint-domain argument that fixes the Hopf/base coefficients, a "
            "derivation of sector winding targets, and a spectral check that no competing "
            "boundary functional recovers the same ledger by post-hoc assignment."
        ),
        "findings": findings,
        "sources_inspected": (
            "theory/boundary_operator_scaffold.md",
            "theory/boundary_operator_action_derivation.md",
            "theory/boundary_operator_completion_attempt.md",
            "theory/proof_gap_report.md",
            "theory/gate_ledger.md",
            "src/boundary_derivation.py",
            "src/mode_selection.py",
            "src/twisted_dirac.py",
            "tests/test_boundary_derivation.py",
            "tests/test_mode_selection.py",
            "tests/test_boundary_operator_closure.py",
        ),
        "frozen_sanity": frozen_sanity_payload(),
        "limitations": (
            "The sprint audits existing BHSM repository evidence only.",
            "It does not introduce a new internal action or new spectral theorem.",
            "It does not alter frozen prediction branches or mode ledgers.",
            "It does not derive Z_virt^{u,2}=1/2 or the CKM 1/16 mixing exponent.",
        ),
    }


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the sprint report as Markdown."""

    payload = payload or derivation_sprint_payload()
    lines = [
        "# Boundary Operator Derivation Sprint",
        "",
        f"P0 blocker: `{payload['p0_blocker']}`",
        f"Classification: `{payload['classification']}`",
        f"P0 boundary blocker closed: `{payload['p0_boundary_blocker_closed']}`",
        "",
        "## Sprint Verdict",
        "",
        (
            "The operational formulas are structurally motivated and internally "
            "consistent with the supplied BHSM mode ledger, but this sprint did not "
            "find a non-fitted action, spectral, or boundary derivation that forces "
            "them. The blocker therefore remains open."
        ),
        "",
        "## Boundary Operators",
        "",
        "| Sector | Equation | Selected modes | Charges | Target satisfied | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in payload["findings"]:
        selected = ", ".join(f"({k},{j})" for k, j in item.selected_modes)
        charges = ", ".join(str(q) for q in item.selected_mode_charges)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                item.sector,
                item.equation,
                selected,
                charges,
                item.selected_modes_satisfy_target,
                item.derivation_status,
            )
        )
    lines.extend(
        [
            "",
            "## Questions Answered",
            "",
            "1. Are these formulas derived from a shared boundary principle?",
            "",
            payload["shared_boundary_principle"]["answer"],
            "",
            "2. Are the coefficients forced by charge, chirality, Hopf fiber/base split, or sector embedding?",
            "",
            payload["coefficient_forcing"]["answer"],
            "",
            "3. Are the targets consequences of the selected modes?",
            "",
            payload["target_origin"]["answer"],
            "",
            "4. Can the formulas be derived from an action variation, spectral condition, boundary condition, or representation constraint?",
            "",
            payload["action_spectral_boundary_result"]["answer"],
            "",
            "5. What additional structure would be required?",
            "",
            payload["additional_structure_required"],
            "",
            "## Impact On Other P0 Items",
            "",
            f"- Helps derive `Z_virt^{{u,2}}=1/2`: `{payload['helps_derive_z_virt_u2_half']}`",
            f"- Helps derive CKM exponent `1/16`: `{payload['helps_derive_ckm_exponent_1_16']}`",
            "",
            "## Frozen Output Discipline",
            "",
            f"- Official frozen outputs changed: `{payload['official_frozen_outputs_changed']}`",
            f"- Frozen sanity: `{payload['frozen_sanity']}`",
            "",
            "## Sources Inspected",
            "",
        ]
    )
    lines.extend(f"- `{source}`" for source in payload["sources_inspected"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in payload["limitations"])
    lines.append("")
    return "\n".join(lines)


def export_boundary_operator_derivation_sprint_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export the sprint report and return the payload."""

    base = Path(root)
    payload = derivation_sprint_payload()
    theory_path = base / "theory" / "boundary_operator_derivation_sprint.md"
    audit_md_path = base / "audits" / "boundary_operator_derivation_sprint_audit.md"
    audit_json_path = base / "audits" / "boundary_operator_derivation_sprint_audit.json"
    theory_path.parent.mkdir(parents=True, exist_ok=True)
    audit_md_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_markdown(payload)
    theory_path.write_text(rendered, encoding="utf-8")
    audit_md_path.write_text(rendered, encoding="utf-8")
    audit_json_path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_boundary_operator_derivation_sprint_outputs()
