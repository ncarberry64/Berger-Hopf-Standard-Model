"""BHSM v2.13 parent-action ingredient inventory for operator uniqueness."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


ACTION_DERIVED = "ACTION_DERIVED"
AXIOM_DERIVED = "AXIOM_DERIVED"
REPRESENTED_BY_EXISTING_TERM = "REPRESENTED_BY_EXISTING_TERM"
ZERO_BY_SYMMETRY = "ZERO_BY_SYMMETRY"
SCREENED_OR_LIFTED = "SCREENED_OR_LIFTED"
CONDITIONAL = "CONDITIONAL"
OPEN = "OPEN"
MISSING = "MISSING"

SAFE_INGREDIENT_STATUSES = {
    ACTION_DERIVED,
    AXIOM_DERIVED,
    REPRESENTED_BY_EXISTING_TERM,
    ZERO_BY_SYMMETRY,
    SCREENED_OR_LIFTED,
}
BLOCKING_INGREDIENT_STATUSES = {CONDITIONAL, OPEN, MISSING}


@dataclass(frozen=True)
class ActionIngredient:
    ingredient_id: str
    role: str
    forced_operator_terms: tuple[str, ...]
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class OperatorActionUniquenessReport:
    title: str
    ingredients: tuple[ActionIngredient, ...]
    all_ingredients_classified: bool
    blocking_ingredients: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def action_ingredients() -> tuple[ActionIngredient, ...]:
    return (
        ActionIngredient(
            "berger_hopf_geometry",
            "Berger diagonal/Hopf geometric core",
            ("A0", "V_Hopf"),
            ACTION_DERIVED,
            ("Berger diagonal reference operator and Hopf twist are already represented in the complete-operator package.",),
            ("This is an action-origin uniqueness input, not a new prediction.",),
        ),
        ActionIngredient(
            "sector_boundary_functional",
            "charged-sector boundary functional",
            ("V_boundary",),
            ACTION_DERIVED,
            ("v1.2/v1.2B/v1.2C derive the omega functional from the symbolic parent boundary scaffold under BHSM axioms.",),
            ("Global uniqueness of arbitrary actions is not claimed beyond the listed BHSM axioms.",),
        ),
        ActionIngredient(
            "chirality_projection",
            "weak chirality projector and mirror guard",
            ("V_chi",),
            ACTION_DERIVED,
            ("Chiral projector channel excludes generated mirror candidates in the scaffold chain.",),
            ("Full H_T still depends on separate mirror/index closure.",),
        ),
        ActionIngredient(
            "sector_lepton_up_down_structure",
            "lepton/up/down sector structure",
            ("K_sector",),
            ACTION_DERIVED,
            ("Sector-labeled formal kernel and sector-coupling block are the only allowed lepton/up/down mixing package.",),
            ("Sector coupling commutator control remains a downstream H_T dependency.",),
        ),
        ActionIngredient(
            "formal_kernel_complement_projector",
            "formal kernel and complement projector",
            ("P_perp_lift",),
            ACTION_DERIVED,
            ("Formal kernel coordinates are sector-labeled and not coordinate-first.",),
            ("Projector graph-domain stability remains downstream.",),
        ),
        ActionIngredient(
            "lift_profile_psd_sector",
            "heat lift and positive semidefinite profile sector",
            ("P_perp_lift", "V_PSD"),
            REPRESENTED_BY_EXISTING_TERM,
            ("PSD/profile and lift terms are represented by existing operator package terms.",),
            ("Scalar/topographic decoupling remains separately audited.",),
        ),
        ActionIngredient(
            "topographic_representation",
            "topographic representation of mixed connection and R_bundle",
            ("topographic represented sector",),
            AXIOM_DERIVED,
            ("v2.11/v2.12 close mixed coefficient and bundle-curvature formula gaps with BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION.",),
            ("This is a BHSM axiom-level uniqueness input, not empirical fitting.",),
        ),
        ActionIngredient(
            "local_sm_bundle_separation",
            "local Standard Model bundle dynamics remain locally unchanged",
            ("forbid independent free mixed operator terms",),
            AXIOM_DERIVED,
            ("Free mixed coefficients are forbidden because they would alter local SM bundle dynamics.",),
            ("Uniqueness is under the BHSM local-separation axiom.",),
        ),
        ActionIngredient(
            "no_mirror_leakage",
            "mirror leakage guard",
            ("forbid mirror-opening perturbations",),
            AXIOM_DERIVED,
            ("Alternative terms that open mirror leakage are theorem-failing rather than allowed deformations.",),
            ("Full mirror theorem is downstream; this uniqueness audit only forbids adding mirror-opening terms.",),
        ),
        ActionIngredient(
            "coordinate_first_kernel_exclusion",
            "exclude coordinate-first kernel artifact",
            ("force sector-labeled formal kernel",),
            ZERO_BY_SYMMETRY,
            ("The old coordinate-first protected block is excluded by formal sector-label alignment.",),
            ("This prevents an artifact from selecting the operator package.",),
        ),
    )


def build_operator_action_uniqueness_report() -> OperatorActionUniquenessReport:
    ingredients = action_ingredients()
    all_classified = all(row.status for row in ingredients)
    blocking = tuple(row.ingredient_id for row in ingredients if row.status in BLOCKING_INGREDIENT_STATUSES)
    status = "OPERATOR_ACTION_INGREDIENTS_CLOSED" if not blocking else "OPERATOR_ACTION_INGREDIENTS_BLOCKED"
    return OperatorActionUniquenessReport(
        title="BHSM v2.13 Operator Action Ingredient Inventory",
        ingredients=ingredients,
        all_ingredients_classified=all_classified,
        blocking_ingredients=blocking,
        status=status,
        theorem_complete=not blocking,
        limitations=(
            "The inventory closes the action-origin ingredient list under current BHSM axioms.",
            "It does not by itself prove the full H_T theorem or authorize final paper preparation.",
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


def export_operator_action_uniqueness_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_action_uniqueness_report()), indent=2, sort_keys=True) + "\n")


def export_operator_action_uniqueness_markdown(path: str | Path) -> None:
    report = build_operator_action_uniqueness_report()
    lines = [
        "# BHSM v2.13 Operator Action Ingredient Inventory",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All ingredients classified: `{report.all_ingredients_classified}`",
        "",
        "| Ingredient | Status | Forced terms | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.ingredients:
        lines.append(f"| `{row.ingredient_id}` | `{row.status}` | `{', '.join(row.forced_operator_terms)}` | {'<br>'.join(row.evidence)} |")
    lines.extend(["", "## Blocking Ingredients", ""])
    lines.extend(f"- `{item}`" for item in report.blocking_ingredients)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
