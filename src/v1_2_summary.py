"""BHSM v1.2 action-origin development summary exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from action_minimality import build_minimality_audit
from action_uniqueness import build_uniqueness_audit
from boundary_functional_derivation import build_parent_action_derivation_report
from omega_derivation import build_omega_action_origin_report


OMEGA_EQUATIONS = {
    "lepton": "Omega_ell = -q + 2j = 3",
    "up": "Omega_u = q - 2j = 6",
    "down": "Omega_d = q + 4j = 12",
}

MAIN_RESULT = (
    "The charged-sector boundary operators are derived from an explicit symbolic sector "
    "boundary functional, and that functional is reduced from a symbolic parent "
    "internal-action scaffold. Minimality and tested-variant uniqueness audits find "
    "the scaffold unique under current BHSM axioms."
)


def build_v1_2_action_origin_summary() -> dict[str, Any]:
    """Build the BHSM v1.2 action-origin summary."""

    omega = build_omega_action_origin_report()
    parent = build_parent_action_derivation_report()
    minimality = build_minimality_audit()
    uniqueness = build_uniqueness_audit()
    return {
        "title": "BHSM v1.2 Action-Origin Development Summary",
        "branch": "bhsm-v1.2-action-origin",
        "main_result": MAIN_RESULT,
        "omega_equations": OMEGA_EQUATIONS,
        "omega_coefficient_status": omega.coefficient_status_table,
        "parent_action_reduction_status": parent.status.value,
        "minimality_status": minimality.status,
        "uniqueness_status": uniqueness.status,
        "theorem_complete": False,
        "minimality_table": [
            {
                "removed_term": criterion.removed_term,
                "required_for": criterion.required_for,
                "passes": criterion.passes,
            }
            for criterion in minimality.criteria
        ],
        "uniqueness_variant_table": [
            {
                "variant": criterion.variant_id,
                "status": criterion.status.value,
                "recovers_mode_ledger": criterion.recovers_mode_ledger,
                "frozen_outputs_would_change_if_adopted": criterion.frozen_outputs_would_change_if_adopted,
            }
            for criterion in uniqueness.criteria
        ],
        "frozen_outputs_changed": False,
        "limitations": (
            "Does not prove global uniqueness of the complete Berger-Hopf internal action.",
            "Does not compute the full twisted Dirac/bundle spectrum.",
            "Does not alter frozen v1.0/v1.1 predictions.",
            "Does not retune any mass or CKM output.",
        ),
        "correct_claim": (
            "BHSM v1.2C audits whether the parent-action scaffold is minimal and unique "
            "under the current BHSM axioms. It does not claim full uniqueness of the "
            "complete internal action unless competing variants are excluded by explicit tests."
        ),
    }


def export_v1_2_summary_json(path: str | Path) -> None:
    """Export the v1.2 summary as JSON."""

    Path(path).write_text(json.dumps(build_v1_2_action_origin_summary(), indent=2, sort_keys=True) + "\n")


def export_v1_2_summary_markdown(path: str | Path) -> None:
    """Export the v1.2 summary as Markdown."""

    summary = build_v1_2_action_origin_summary()
    lines = [
        "# BHSM v1.2 Action-Origin Development Summary",
        "",
        f"Branch: `{summary['branch']}`",
        "",
        "## Main Result",
        "",
        summary["main_result"],
        "",
        "## Boundary Operators",
        "",
        "```text",
        summary["omega_equations"]["lepton"],
        summary["omega_equations"]["up"],
        summary["omega_equations"]["down"],
        "```",
        "",
        "## Status",
        "",
        f"- Parent-action reduction status: `{summary['parent_action_reduction_status']}`.",
        f"- Minimality status: `{summary['minimality_status']}`.",
        f"- Uniqueness status: `{summary['uniqueness_status']}`.",
        f"- Theorem complete: `{summary['theorem_complete']}`.",
        "",
        "## Minimality Table",
        "",
        "| Term | Required for | Passes |",
        "| --- | --- | --- |",
    ]
    for row in summary["minimality_table"]:
        lines.append(f"| `{row['removed_term']}` | {row['required_for']} | `{row['passes']}` |")
    lines.extend(
        [
            "",
            "## Uniqueness Variant Table",
            "",
            "| Variant | Status | Recovers ledger | Would change frozen outputs if adopted |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in summary["uniqueness_variant_table"]:
        lines.append(
            f"| `{row['variant']}` | `{row['status']}` | `{row['recovers_mode_ledger']}` | `{row['frozen_outputs_would_change_if_adopted']}` |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in summary["limitations"]],
            "",
            "## Correct Claim",
            "",
            summary["correct_claim"],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
