"""BHSM v1.3A inventory of Level 2 H_T operator terms.

This module is an audit layer over the existing Level 2 finite-basis
twisted-Dirac scaffold. It classifies the terms already present in
``twisted_dirac.py`` and ``ht_operator.py`` without changing the model,
predictions, constants, or tests. The no-extra-light-state theorem remains
open.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from twisted_dirac import DIRAC_PROXY_LEVEL_2


class HTTermClassification(StrEnum):
    """Analytic-bound status for one Level 2 H_T term."""

    DIAGONAL_EXACT = "DIAGONAL_EXACT"
    PSD_EXACT = "PSD_EXACT"
    SIGN_INDEFINITE_BOUNDED = "SIGN_INDEFINITE_BOUNDED"
    OFF_DIAGONAL_BOUNDED = "OFF_DIAGONAL_BOUNDED"
    FINITE_BASIS_ONLY = "FINITE_BASIS_ONLY"
    OPEN = "OPEN"


@dataclass(frozen=True)
class HTOperatorTerm:
    """One term in the Level 2 twisted Dirac / H_T construction."""

    id: str
    name: str
    source_module: str
    source_symbol: str
    operator_role: str
    matrix_structure: str
    classification: HTTermClassification
    preserves_zero_modes: bool
    can_lower_complement_gap: bool
    lower_bound_method: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class TermBoundClassification:
    """Compact lower-bound classification for a term."""

    term_id: str
    classification: HTTermClassification
    lower_bound_method: str
    can_lower_complement_gap: bool
    analytic_status: str
    upgrade_requirement: str


@dataclass(frozen=True)
class HTBoundInventory:
    """Machine-readable inventory of the Level 2 H_T terms."""

    title: str
    model_level: str
    terms: tuple[HTOperatorTerm, ...]
    classifications: tuple[TermBoundClassification, ...]
    theorem_complete: bool
    limitations: tuple[str, ...]


def level2_ht_operator_terms() -> tuple[HTOperatorTerm, ...]:
    """Return the inventoried Level 2 H_T operator terms.

    The inventory is descriptive: it records the current scaffold structure and
    its available lower-bound methods. It does not alter the Level 2 operator.
    """

    return (
        HTOperatorTerm(
            id="berger_dirac_kinetic",
            name="Berger / Dirac kinetic diagonal contribution",
            source_module="twisted_dirac",
            source_symbol="build_level2_dirac_matrix",
            operator_role="dominant signed diagonal Dirac proxy contribution before squaring",
            matrix_structure="diagonal in the finite Dirac basis before the D^dagger D construction",
            classification=HTTermClassification.DIAGONAL_EXACT,
            preserves_zero_modes=True,
            can_lower_complement_gap=False,
            lower_bound_method="exact diagonal minimum after complement restriction; min-max check after squaring",
            assumptions=(
                "Level 2 matrix uses the existing Berger anisotropy and finite mode basis.",
                "The protected zero-mode rows and columns are projected out by construction.",
            ),
            limitations=(
                "The term is exact only inside DIRAC_PROXY_LEVEL_2.",
                "A closed analytic Berger twisted-Dirac spectrum is not derived here.",
            ),
        ),
        HTOperatorTerm(
            id="hopf_twist",
            name="Hopf twist contribution",
            source_module="twisted_dirac",
            source_symbol="level2_hopf_twist_term",
            operator_role="Hopf-charge dependent diagonal twist",
            matrix_structure="diagonal but sign-indefinite because q can have either sign in general basis choices",
            classification=HTTermClassification.SIGN_INDEFINITE_BOUNDED,
            preserves_zero_modes=True,
            can_lower_complement_gap=True,
            lower_bound_method="Weyl bound with explicit coefficient and finite q range",
            assumptions=(
                "The finite basis has bounded Hopf charges.",
                "The Hopf coefficient is fixed before residual comparison.",
            ),
            limitations=(
                "The current lower bound is finite-basis bounded, not a global analytic q-bound.",
            ),
        ),
        HTOperatorTerm(
            id="boundary_term",
            name="Action-linked boundary residual contribution",
            source_module="twisted_dirac",
            source_symbol="level2_boundary_term",
            operator_role="sector boundary residual term tied to the omega scaffold",
            matrix_structure="diagonal residual term; sign may vary by sector and mode",
            classification=HTTermClassification.SIGN_INDEFINITE_BOUNDED,
            preserves_zero_modes=True,
            can_lower_complement_gap=True,
            lower_bound_method="Weyl bound using the bounded residual range in the finite basis",
            assumptions=(
                "Boundary coefficients are those from the v1.2 action-origin scaffold.",
                "Boundary strength is explicit and nonnegative.",
            ),
            limitations=(
                "The full action-level uniqueness of the complete internal action remains open.",
                "A global analytic residual bound beyond the finite basis is not proven here.",
            ),
        ),
        HTOperatorTerm(
            id="chirality_term",
            name="Chirality splitting contribution",
            source_module="twisted_dirac",
            source_symbol="level2_chirality_term",
            operator_role="left/right chirality dependent diagonal splitting",
            matrix_structure="diagonal sign-indefinite term",
            classification=HTTermClassification.SIGN_INDEFINITE_BOUNDED,
            preserves_zero_modes=True,
            can_lower_complement_gap=True,
            lower_bound_method="Weyl bound from explicit chirality coefficient",
            assumptions=(
                "Chirality labels are explicit finite-basis labels.",
                "The coefficient is not fitted to residuals.",
            ),
            limitations=(
                "The chirality splitting is still a Level 2 proxy term.",
            ),
        ),
        HTOperatorTerm(
            id="sector_coupling",
            name="Sector and boundary off-diagonal coupling",
            source_module="twisted_dirac",
            source_symbol="level2_sector_coupling_term",
            operator_role="symmetric off-diagonal coupling between sectors with matching k, j, chirality",
            matrix_structure="off-diagonal symmetric finite matrix block",
            classification=HTTermClassification.OFF_DIAGONAL_BOUNDED,
            preserves_zero_modes=True,
            can_lower_complement_gap=True,
            lower_bound_method="Gershgorin bound and restricted min-max finite-basis check",
            assumptions=(
                "Off-diagonal strengths are explicit and nonnegative.",
                "Only same-(k,j,chirality) cross-sector couplings are allowed in Level 2.",
            ),
            limitations=(
                "This is the weakest matrix term for analytic upgrade because the present control is finite-basis.",
                "No infinite-basis operator-norm bound is proven here.",
            ),
        ),
        HTOperatorTerm(
            id="heat_lift",
            name="Heat-kernel Hopf lift",
            source_module="ht_operator",
            source_symbol="build_ht_spectrum",
            operator_role="monotone heat lift d + mu_H(1-exp(-d/Lambda^2))",
            matrix_structure="spectral functional of D^dagger D",
            classification=HTTermClassification.PSD_EXACT,
            preserves_zero_modes=True,
            can_lower_complement_gap=False,
            lower_bound_method="PSD nonnegative monotone heat-lift inequality",
            assumptions=(
                "The cutoff Lambda^2 is supplied explicitly and defaults to 1/(4*pi).",
                "Dirac-squared input d is nonnegative.",
            ),
            limitations=(
                "The heat lift inherits any incompleteness in the lower bound for D^dagger D on the complement.",
            ),
        ),
        HTOperatorTerm(
            id="psd_profile",
            name="Positive-semidefinite curvature/profile contribution",
            source_module="ht_operator",
            source_symbol="_profile_values",
            operator_role="optional PSD profile contribution on H_perp",
            matrix_structure="PSD vector or matrix contribution; negative profiles are rejected by default",
            classification=HTTermClassification.PSD_EXACT,
            preserves_zero_modes=True,
            can_lower_complement_gap=False,
            lower_bound_method="PSD nonnegative Weyl contribution",
            assumptions=(
                "Profile operators are PSD unless explicit failure tests opt into negative profiles.",
                "The curvature/profile positivity condition is imposed on the complement.",
            ),
            limitations=(
                "The full curvature/profile operator from the action is not computed here.",
            ),
        ),
        HTOperatorTerm(
            id="zero_complement_projector",
            name="Zero-mode and complement projector",
            source_module="twisted_dirac / positivity",
            source_symbol="zero_mode_subspace / complement_projector",
            operator_role="separates three protected zero modes from H_perp in the finite basis",
            matrix_structure="coordinate projector in the Level 2 finite basis",
            classification=HTTermClassification.FINITE_BASIS_ONLY,
            preserves_zero_modes=True,
            can_lower_complement_gap=False,
            lower_bound_method="min-max restricted complement in finite basis",
            assumptions=(
                "Exactly three protected zero modes are inserted or projected in the Level 2 scaffold.",
                "The complement is taken orthogonal to that finite coordinate subspace.",
            ),
            limitations=(
                "This is the weakest analytic block: dim ker D_twist = 3 is not proven in the full action.",
                "The infinite-dimensional complement separation remains open.",
            ),
        ),
    )


def _classification_for(term: HTOperatorTerm) -> TermBoundClassification:
    if term.classification == HTTermClassification.PSD_EXACT:
        analytic_status = "nonnegative contribution controlled exactly under the PSD assumption"
        upgrade = "derive the profile or heat-lift input from the complete action"
    elif term.classification == HTTermClassification.DIAGONAL_EXACT:
        analytic_status = "exact for the Level 2 finite-basis diagonal block"
        upgrade = "derive a closed Berger twisted-Dirac diagonal lower bound"
    elif term.classification == HTTermClassification.OFF_DIAGONAL_BOUNDED:
        analytic_status = "bounded in finite basis by Gershgorin and restricted min-max estimates"
        upgrade = "prove an infinite-basis operator-norm or relative-bound estimate"
    elif term.classification == HTTermClassification.SIGN_INDEFINITE_BOUNDED:
        analytic_status = "bounded in finite basis by explicit coefficient and mode ranges"
        upgrade = "prove global coefficient-weighted mode bounds on H_perp"
    elif term.classification == HTTermClassification.FINITE_BASIS_ONLY:
        analytic_status = "finite-basis evidence only"
        upgrade = "prove the protected kernel and complement decomposition in the full action"
    else:
        analytic_status = "open"
        upgrade = "supply a lower-bound proof or mark as excluded from the theorem"
    return TermBoundClassification(
        term_id=term.id,
        classification=term.classification,
        lower_bound_method=term.lower_bound_method,
        can_lower_complement_gap=term.can_lower_complement_gap,
        analytic_status=analytic_status,
        upgrade_requirement=upgrade,
    )


def build_ht_bound_inventory() -> HTBoundInventory:
    """Build the Level 2 term inventory and bound classification."""

    terms = level2_ht_operator_terms()
    return HTBoundInventory(
        title="BHSM v1.3A Level 2 H_T Term Inventory",
        model_level=DIRAC_PROXY_LEVEL_2,
        terms=terms,
        classifications=tuple(_classification_for(term) for term in terms),
        theorem_complete=False,
        limitations=(
            "This inventory classifies the current Level 2 finite-basis proxy; it is not the full analytic H_T spectrum.",
            "Frozen v1.0/v1.1 predictions, constants, tolerances, and mode ledgers are not changed.",
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


def export_ht_term_inventory_json(path: str | Path) -> None:
    """Export the Level 2 H_T term inventory as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_ht_bound_inventory()), indent=2, sort_keys=True) + "\n")


def export_ht_term_inventory_markdown(path: str | Path) -> None:
    """Export the Level 2 H_T term inventory as Markdown."""

    inventory = build_ht_bound_inventory()
    lines = [
        "# BHSM v1.3A Level 2 H_T Term Inventory",
        "",
        f"Model level: `{inventory.model_level}`",
        f"Theorem complete: `{inventory.theorem_complete}`",
        "",
        "This inventory records the terms already present in the Level 2 finite-basis H_T scaffold. It does not prove the full no-extra-light-state theorem.",
        "",
        "| Term | Classification | Preserves zero modes | Can lower complement gap | Lower-bound method |",
        "| --- | --- | --- | --- | --- |",
    ]
    for term in inventory.terms:
        lines.append(
            f"| `{term.id}` | `{term.classification.value}` | `{term.preserves_zero_modes}` | `{term.can_lower_complement_gap}` | {term.lower_bound_method} |"
        )
    lines.extend(
        [
            "",
            "## Term Limitations",
            "",
        ]
    )
    for term in inventory.terms:
        limitations = " ".join(term.limitations)
        lines.append(f"- `{term.id}`: {limitations}")
    lines.extend(
        [
            "",
            "## Global Limitations",
            "",
            *[f"- {item}" for item in inventory.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
