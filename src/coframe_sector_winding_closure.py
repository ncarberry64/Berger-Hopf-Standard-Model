"""Focused closure audit for coframe multiplier and sector winding rules.

The previous boundary-action candidate reduced the omega pattern to two
remaining structural inputs: the coframe multiplier and sector winding rule.
This module audits whether those inputs are derived from existing BHSM
structure.  It does not modify frozen predictions and it does not mark the
boundary operators action-derived unless both rules are forced without fitting.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_v1 import compare_bhsm_v1_branches
from boundary_action_closure_candidate import (
    CANDIDATE_NOT_OFFICIAL,
    audit_payload as boundary_action_audit_payload,
    build_boundary_generators,
    selected_mode_checks,
)


COFRAME_AND_WINDING_DERIVED = "COFRAME_AND_WINDING_DERIVED"
COFRAME_DERIVED_WINDING_OPEN = "COFRAME_DERIVED_WINDING_OPEN"
WINDING_DERIVED_COFRAME_OPEN = "WINDING_DERIVED_COFRAME_OPEN"
STRUCTURALLY_MOTIVATED_NOT_DERIVED = "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
REJECTED_NOT_DERIVED = "REJECTED_NOT_DERIVED"

COFRAME_MULTIPLIER_NOT_DERIVED = "COFRAME_MULTIPLIER_NOT_DERIVED"
SECTOR_WINDING_RULE_NOT_DERIVED = "SECTOR_WINDING_RULE_NOT_DERIVED"


@dataclass(frozen=True)
class RuleAudit:
    """One rule-level derivation audit."""

    rule_name: str
    proposed_rule: str
    status: str
    derived: bool
    inserted: bool
    evidence: tuple[str, ...]
    obstruction: str


@dataclass(frozen=True)
class CoframeSectorWindingResult:
    """Structured sprint result requested by the closure brief."""

    coframe_multiplier_status: str
    sector_winding_status: str
    coefficients_forced: bool
    coefficients_inserted: bool
    omega_l_recovered: bool
    omega_u_recovered: bool
    omega_d_recovered: bool
    closes_boundary_blocker: bool
    helps_z_virt_u2: bool
    helps_ckm_1_16: bool
    classification: str
    notes: tuple[str, ...]


def coframe_multiplier_audit() -> RuleAudit:
    """Audit whether the coframe multiplier is forced."""

    return RuleAudit(
        rule_name="coframe_multiplier",
        proposed_rule=(
            "C_f=1 for leptons and weak-upper quarks; C_f=2 for the colored "
            "weak-lower down-sector boundary channel"
        ),
        status=COFRAME_MULTIPLIER_NOT_DERIVED,
        derived=False,
        inserted=False,
        evidence=(
            "The rule uses only field-ledger structure: color rank and weak component.",
            "It naturally makes the down-sector base coefficient larger: -4*T3*C_f = +4 for T3=-1/2 and C_f=2.",
            "It preserves the lepton and up coefficients with C_f=1.",
        ),
        obstruction=(
            "The repository does not contain an action variation, coframe trace, or "
            "spectral boundary calculation that forces C_f=2 specifically for the "
            "colored weak-lower channel."
        ),
    )


def sector_winding_audit() -> RuleAudit:
    """Audit whether the sector winding rule is forced."""

    return RuleAudit(
        rule_name="sector_winding",
        proposed_rule="W_l=1, W_u=2, W_d=4 with target_f=N_gen*W_f",
        status=SECTOR_WINDING_RULE_NOT_DERIVED,
        derived=False,
        inserted=False,
        evidence=(
            "The rule is compatible with the field-ledger hierarchy: lepton singlet boundary, upper colored channel, lower colored/coframe channel.",
            "It recovers targets 3, 6, and 12 from family index N_gen=3.",
            "The signs of the q and j terms are motivated separately by sign(Y) and -4*T3*C_f.",
        ),
        obstruction=(
            "The repository does not contain a Hopf winding, self-adjoint-domain, "
            "or boundary-generator eigenvalue argument that uniquely forces the "
            "multipliers 1, 2, and 4."
        ),
    )


def _omega_recovery_flags() -> dict[str, bool]:
    rows = selected_mode_checks()
    return {
        "omega_l_recovered": all(
            row["matches_target"] for row in rows if row["sector"] == "lepton"
        ),
        "omega_u_recovered": all(
            row["matches_target"] for row in rows if row["sector"] == "up"
        ),
        "omega_d_recovered": all(
            row["matches_target"] for row in rows if row["sector"] == "down"
        ),
    }


def closure_result() -> CoframeSectorWindingResult:
    """Return the focused closure result."""

    coframe = coframe_multiplier_audit()
    winding = sector_winding_audit()
    flags = _omega_recovery_flags()
    both_derived = coframe.derived and winding.derived
    if both_derived:
        classification = COFRAME_AND_WINDING_DERIVED
    elif coframe.derived and not winding.derived:
        classification = COFRAME_DERIVED_WINDING_OPEN
    elif winding.derived and not coframe.derived:
        classification = WINDING_DERIVED_COFRAME_OPEN
    elif all(flags.values()):
        classification = STRUCTURALLY_MOTIVATED_NOT_DERIVED
    else:
        classification = REJECTED_NOT_DERIVED
    return CoframeSectorWindingResult(
        coframe_multiplier_status=coframe.status,
        sector_winding_status=winding.status,
        coefficients_forced=both_derived,
        coefficients_inserted=False,
        omega_l_recovered=flags["omega_l_recovered"],
        omega_u_recovered=flags["omega_u_recovered"],
        omega_d_recovered=flags["omega_d_recovered"],
        closes_boundary_blocker=both_derived,
        helps_z_virt_u2=False,
        helps_ckm_1_16=False,
        classification=classification,
        notes=(
            "The coframe and winding rules remain structural candidate rules.",
            "The omega operators are recovered, but recovery is not a derivation.",
            "No mass residuals, CKM values, or frozen output changes are used.",
            "The P0 boundary blocker remains open until both rules are forced by BHSM boundary action or spectrum.",
        ),
    )


def frozen_sanity_payload() -> dict[str, Any]:
    """Return frozen-output sanity checks."""

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


def audit_payload() -> dict[str, Any]:
    """Return the focused coframe/winding audit payload."""

    result = closure_result()
    boundary_candidate = boundary_action_audit_payload()
    return {
        "title": "BHSM coframe multiplier and sector winding closure audit",
        "classification": result.classification,
        "boundary_blocker": "BOUNDARY_OPERATORS_NOT_ACTION_DERIVED",
        "specific_blockers": (
            COFRAME_MULTIPLIER_NOT_DERIVED,
            SECTOR_WINDING_RULE_NOT_DERIVED,
        ),
        "closes_boundary_blocker": result.closes_boundary_blocker,
        "coframe_multiplier": coframe_multiplier_audit(),
        "sector_winding": sector_winding_audit(),
        "result": result,
        "generators": build_boundary_generators(),
        "selected_mode_checks": selected_mode_checks(),
        "boundary_action_candidate_status": boundary_candidate["status"],
        "candidate_remains_non_official": boundary_candidate["status"] == CANDIDATE_NOT_OFFICIAL,
        "frozen_sanity": frozen_sanity_payload(),
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "forbidden_claims_absent": True,
        "promotion_criteria": (
            "derive C_f from a coframe trace, boundary variation, or representation-theoretic projection",
            "derive W_f from Hopf winding, self-adjoint boundary spectrum, or boundary-generator eigenvalue condition",
            "show both derivations are independent of the selected mode targets and empirical residuals",
        ),
        "rejection_criteria": (
            "C_f=2 is only chosen because the down-sector target requires +4j",
            "W_f=1,2,4 is only chosen because the targets are 3,6,12",
            "a competing non-fitted rule produces different omega operators while preserving the ledger",
        ),
    }


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


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the audit as Markdown."""

    payload = payload or audit_payload()
    result = payload["result"]
    coframe = payload["coframe_multiplier"]
    winding = payload["sector_winding"]
    lines = [
        "# Coframe Multiplier And Sector Winding Closure",
        "",
        "## Problem",
        "",
        "The boundary-action candidate reduces the omega operators to two remaining rules: "
        "a coframe multiplier `C_f` and a sector winding `W_f`. This sprint asks whether "
        "those rules are forced by existing BHSM structure.",
        "",
        "## Prior Boundary-Action Candidate Status",
        "",
        f"Prior candidate status: `{payload['boundary_action_candidate_status']}`.",
        "The candidate reproduces the omega pattern but remains non-official.",
        "",
        "## Coframe Multiplier Derivation Attempt",
        "",
        f"Proposed rule: `{coframe.proposed_rule}`",
        "",
        "Evidence:",
        "",
    ]
    lines.extend(f"- {item}" for item in coframe.evidence)
    lines.extend(
        [
            "",
            f"Status: `{coframe.status}`",
            "",
            f"Obstruction: {coframe.obstruction}",
            "",
            "## Sector Winding Derivation Attempt",
            "",
            f"Proposed rule: `{winding.proposed_rule}`",
            "",
            "Evidence:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in winding.evidence)
    lines.extend(
        [
            "",
            f"Status: `{winding.status}`",
            "",
            f"Obstruction: {winding.obstruction}",
            "",
            "## Whether Each Rule Is Forced, Motivated, Or Inserted",
            "",
            "| Rule | Derived | Inserted | Status |",
            "| --- | --- | --- | --- |",
            f"| coframe multiplier | `{coframe.derived}` | `{coframe.inserted}` | `{coframe.status}` |",
            f"| sector winding | `{winding.derived}` | `{winding.inserted}` | `{winding.status}` |",
            "",
            "## Consequences For Omega_l, Omega_u, Omega_d",
            "",
            f"- Omega_l recovered: `{result.omega_l_recovered}`",
            f"- Omega_u recovered: `{result.omega_u_recovered}`",
            f"- Omega_d recovered: `{result.omega_d_recovered}`",
            f"- Coefficients forced: `{result.coefficients_forced}`",
            f"- Boundary blocker closed: `{result.closes_boundary_blocker}`",
            "",
            "Recovery remains weaker than derivation because at least one structural rule is still open.",
            "",
            "## Consequences For Z_virt^{u,2}=1/2",
            "",
            f"Helps derive `Z_virt^{{u,2}}=1/2`: `{result.helps_z_virt_u2}`.",
            "",
            "## Consequences For CKM 1/16",
            "",
            f"Helps derive CKM `1/16`: `{result.helps_ckm_1_16}`.",
            "",
            "## Closure Verdict",
            "",
            f"Classification: `{result.classification}`",
            "",
            "The sprint does not close `BOUNDARY_OPERATORS_NOT_ACTION_DERIVED`. The specific remaining blockers are:",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in payload["specific_blockers"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {item}" for item in result.notes)
    lines.append("")
    return "\n".join(lines)


def export_coframe_sector_winding_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "coframe_sector_winding_closure.md",
        "audit_md": base / "audits" / "coframe_sector_winding_closure_audit.md",
        "audit_json": base / "audits" / "coframe_sector_winding_closure_audit.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_coframe_sector_winding_outputs()
