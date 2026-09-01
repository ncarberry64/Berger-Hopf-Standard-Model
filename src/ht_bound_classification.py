"""Combined analytic-bound classification report for Level 2 H_T terms."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ht_term_inventory import (
    HTBoundInventory,
    HTTermClassification,
    build_ht_bound_inventory,
)


@dataclass(frozen=True)
class HTInventoryReport:
    """v1.3A report for the current Level 2 H_T lower-bound program."""

    title: str
    inventory: HTBoundInventory
    combined_bound_chain: tuple[str, ...]
    weakest_term: str
    weakest_matrix_term: str
    sector_coupling_bound_status: str
    next_upgrade_target: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def combined_bound_plan(inventory: HTBoundInventory | None = None) -> tuple[str, ...]:
    """Return the best current conservative lower-bound chain."""

    inv = build_ht_bound_inventory() if inventory is None else inventory
    term_ids = {term.id for term in inv.terms}
    required = {
        "berger_dirac_kinetic",
        "hopf_twist",
        "boundary_term",
        "chirality_term",
        "sector_coupling",
        "heat_lift",
        "psd_profile",
        "zero_complement_projector",
    }
    missing = sorted(required - term_ids)
    if missing:
        raise ValueError(f"missing Level 2 terms: {missing}")
    return (
        "Restrict the finite Level 2 Dirac matrix to the complement of the three protected zero modes.",
        "Use the exact finite-basis diagonal contribution and finite q/residual ranges for diagonal sign-indefinite terms.",
        "Control sector off-diagonal blocks with Gershgorin and restricted min-max bounds.",
        "Use the v1.3B sector-coupling operator-norm audit to distinguish norm-certified cases from finite-basis-only passes.",
        "Square the symmetric Level 2 Dirac matrix and take the conservative complement lower bound.",
        "Apply the monotone heat-lift inequality with Lambda^2 = 1/(4*pi).",
        "Add only PSD curvature/profile contributions, so Weyl's lower bound cannot decrease.",
        "Keep theorem_complete=False until the zero-mode/complement split and off-diagonal bounds are proven in the full action.",
    )


def weakest_term(inventory: HTBoundInventory | None = None) -> str:
    """Return the weakest current analytic block in the lower-bound chain."""

    inv = build_ht_bound_inventory() if inventory is None else inventory
    finite_only = [term.id for term in inv.terms if term.classification == HTTermClassification.FINITE_BASIS_ONLY]
    if finite_only:
        return finite_only[0]
    open_terms = [term.id for term in inv.terms if term.classification == HTTermClassification.OPEN]
    if open_terms:
        return open_terms[0]
    offdiag = [term.id for term in inv.terms if term.classification == HTTermClassification.OFF_DIAGONAL_BOUNDED]
    return offdiag[0] if offdiag else inv.terms[-1].id


def weakest_matrix_term(inventory: HTBoundInventory | None = None) -> str:
    """Return the weakest matrix-valued term apart from the projector block."""

    inv = build_ht_bound_inventory() if inventory is None else inventory
    offdiag = [term.id for term in inv.terms if term.classification == HTTermClassification.OFF_DIAGONAL_BOUNDED]
    if offdiag:
        return offdiag[0]
    finite = [term.id for term in inv.terms if term.classification == HTTermClassification.FINITE_BASIS_ONLY]
    return finite[0] if finite else inv.terms[-1].id


def build_ht_inventory_report() -> HTInventoryReport:
    """Build the complete v1.3A H_T term inventory and bound report."""

    inventory = build_ht_bound_inventory()
    return HTInventoryReport(
        title="BHSM v1.3A H_T Analytic-Bound Classification Report",
        inventory=inventory,
        combined_bound_chain=combined_bound_plan(inventory),
        weakest_term=weakest_term(inventory),
        weakest_matrix_term=weakest_matrix_term(inventory),
        sector_coupling_bound_status=(
            "v1.3B adds finite spectral, Frobenius, row-sum, Weyl, and relative-bound estimates. "
            "v1.3C adds structured block and generalized relative-bound diagnostics. "
            "v1.3D tests uniform-in-k_max stability through k_max=32. "
            "v1.3E defines the Hilbert-space/domain assumptions needed to upgrade the scan. "
            "The status remains THEOREM_SCAFFOLD, not proven."
        ),
        next_upgrade_target=(
            "Prove the full-action zero-mode/complement decomposition "
            "dim ker D_twist = 3 and prove assumptions A1-A6 from the complete operator."
        ),
        theorem_complete=False,
        limitations=(
            "The report is an analytic-bound development scaffold over DIRAC_PROXY_LEVEL_2.",
            "It does not prove the full no-extra-light-state theorem.",
            "No frozen v1.0/v1.1 predictions or v1.2 action-origin outputs are changed.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, HTTermClassification):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_ht_bound_classification_json(path: str | Path) -> None:
    """Export the v1.3A H_T bound classification report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_ht_inventory_report()), indent=2, sort_keys=True) + "\n")


def export_ht_bound_classification_markdown(path: str | Path) -> None:
    """Export the v1.3A H_T bound classification report as Markdown."""

    report = build_ht_inventory_report()
    lines = [
        "# BHSM v1.3A H_T Analytic-Bound Classification Report",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Weakest analytic block: `{report.weakest_term}`",
        f"Weakest matrix term: `{report.weakest_matrix_term}`",
        f"Sector-coupling bound status: {report.sector_coupling_bound_status}",
        "",
        "BHSM v1.3A inventories and classifies the Level 2 H_T operator terms for analytic-bound development. It does not prove the full no-extra-light-state theorem.",
        "",
        "## Classification Table",
        "",
        "| Term | Classification | Analytic status | Upgrade requirement |",
        "| --- | --- | --- | --- |",
    ]
    for item in report.inventory.classifications:
        lines.append(
            f"| `{item.term_id}` | `{item.classification.value}` | {item.analytic_status} | {item.upgrade_requirement} |"
        )
    lines.extend(
        [
            "",
            "## Current Best Lower-Bound Chain",
            "",
        ]
    )
    lines.extend(f"{idx}. {step}" for idx, step in enumerate(report.combined_bound_chain, start=1))
    lines.extend(
        [
            "",
            "## Next Upgrade Target",
            "",
            report.next_upgrade_target,
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
