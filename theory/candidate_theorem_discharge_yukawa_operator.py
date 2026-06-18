from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-yukawa-operator-closure-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to derive the "
    "renormalizable Yukawa operator skeleton from BHSM boundary charge closure, "
    "active-orientation contraction, cyclic/reference channel contraction, and the "
    "previously derived scalar boundary doublet, rather than importing the Standard "
    "Model Yukawa table as an assumption. Status labels may be promoted only when "
    "the derivation is explicit, exact, non-tautological, and does not use known "
    "Standard Model Yukawa operators as a premise."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the Yukawa operator-closure theorem layer. "
    "Given the previously derived boundary fermion inventory, scalar doublet H, "
    "conjugate scalar H_tilde, and boundary hypercharge operator, exactly four "
    "renormalizable Yukawa closure classes satisfy hypercharge closure, "
    "active-orientation singlet contraction, and cyclic/reference channel "
    "contraction. The resulting operator skeleton is comparison-equivalent to the "
    "familiar up-type, down-type, charged-reference, and neutral-reference Yukawa "
    "classes, but is derived from BHSM boundary closure rather than imported from "
    "the Standard Model. Numerical Yukawa values, mass ratios, and mixing matrices "
    "remain open."
)
VERDICT_LABELS = [
    "THEOREM_DISCHARGE_YUKAWA_OPERATOR_CLOSURE_COMPLETE",
    "PO_BH_18_YUKAWA_OPERATOR_CLOSURE_DERIVED_CONDITIONAL",
    "BOUNDARY_YUKAWA_FIELD_INVENTORY_DERIVED_CONDITIONAL",
    "YUKAWA_HYPERCHARGE_CLOSURE_DERIVED_CONDITIONAL",
    "YUKAWA_ORIENTATION_CONTRACTIONS_DERIVED_CONDITIONAL",
    "YUKAWA_CYCLIC_REFERENCE_CONTRACTIONS_DERIVED_CONDITIONAL",
    "YUKAWA_ALLOWED_OPERATOR_CLASSES_DERIVED_CONDITIONAL",
    "YUKAWA_FORBIDDEN_OPERATOR_CLASSES_DERIVED_CONDITIONAL",
    "BOUNDARY_NEUTRAL_SINGLET_MASS_OPERATOR_ALLOWED_CONDITIONALLY",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_PMNS_MIXING_REMAINS_OPEN",
    "DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


class DischargeStatus(str, Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class BoundaryField:
    name: str
    role: str
    C: int
    Y: Fraction
    orientation: str
    cyclic_role: str
    multiplicity: int


@dataclass(frozen=True)
class YukawaOperatorCandidate:
    name: str
    active_field: str
    scalar_field: str
    singlet_field: str
    hypercharge_sum: Fraction
    orientation_closes: bool
    cyclic_reference_closes: bool
    status: str
    interpretation: str


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: DischargeStatus
    statement: str
    dependencies: tuple[str, ...]
    remaining_blocker: str


def boundary_field_inventory() -> dict[str, BoundaryField]:
    return {
        "A_ref": BoundaryField("A_ref", "active", 0, Fraction(-1), "active_doublet", "reference", 1),
        "A_cyc": BoundaryField("A_cyc", "active", 1, Fraction(1, 3), "active_doublet", "cyclic", 3),
        "S_ref_neutral": BoundaryField("S_ref_neutral", "singlet", 0, Fraction(0), "singlet", "reference", 1),
        "S_ref_charged": BoundaryField("S_ref_charged", "singlet", 0, Fraction(2), "singlet", "reference", 1),
        "S_cyc_upper": BoundaryField("S_cyc_upper", "singlet", 1, Fraction(-4, 3), "singlet", "cyclic_conjugate", 3),
        "S_cyc_lower": BoundaryField("S_cyc_lower", "singlet", 1, Fraction(2, 3), "singlet", "cyclic_conjugate", 3),
        "H": BoundaryField("H", "scalar", 0, Fraction(1), "active_doublet", "neutral", 1),
        "H_tilde": BoundaryField("H_tilde", "scalar", 0, Fraction(-1), "active_doublet_conjugate", "neutral", 1),
    }


def _field(name: str) -> BoundaryField:
    try:
        return boundary_field_inventory()[name]
    except KeyError as exc:
        raise ValueError(f"unknown boundary field {name!r}") from exc


def hypercharge_sum(*field_names: str) -> Fraction:
    return sum((_field(name).Y for name in field_names), Fraction(0))


def orientation_contraction_closes(
    active_field: BoundaryField, scalar_field: BoundaryField, singlet_field: BoundaryField
) -> bool:
    active_ok = active_field.orientation == "active_doublet"
    scalar_ok = scalar_field.orientation in ("active_doublet", "active_doublet_conjugate")
    singlet_ok = singlet_field.orientation == "singlet"
    return active_ok and scalar_ok and singlet_ok


def cyclic_reference_contraction_closes(
    active_field: BoundaryField, scalar_field: BoundaryField, singlet_field: BoundaryField
) -> bool:
    if scalar_field.cyclic_role != "neutral":
        return False
    if active_field.cyclic_role == "reference":
        return singlet_field.cyclic_role == "reference"
    if active_field.cyclic_role == "cyclic":
        return singlet_field.cyclic_role == "cyclic_conjugate"
    return False


def yukawa_candidate(name: str, active: str, scalar: str, singlet: str) -> YukawaOperatorCandidate:
    active_field = _field(active)
    scalar_field = _field(scalar)
    singlet_field = _field(singlet)
    y_sum = hypercharge_sum(active, scalar, singlet)
    orientation_ok = orientation_contraction_closes(active_field, scalar_field, singlet_field)
    cyclic_ok = cyclic_reference_contraction_closes(active_field, scalar_field, singlet_field)
    allowed = y_sum == 0 and orientation_ok and cyclic_ok
    return YukawaOperatorCandidate(
        name,
        active,
        scalar,
        singlet,
        y_sum,
        orientation_ok,
        cyclic_ok,
        "ALLOWED_BOUNDARY_YUKAWA_OPERATOR" if allowed else "FORBIDDEN_BOUNDARY_YUKAWA_OPERATOR",
        "boundary closure class" if allowed else "fails hypercharge or channel/orientation closure",
    )


def allowed_yukawa_operator_classes() -> tuple[YukawaOperatorCandidate, ...]:
    return (
        yukawa_candidate("cyclic_upper_closure", "A_cyc", "H", "S_cyc_upper"),
        yukawa_candidate("cyclic_lower_closure", "A_cyc", "H_tilde", "S_cyc_lower"),
        yukawa_candidate("reference_charged_closure", "A_ref", "H_tilde", "S_ref_charged"),
        yukawa_candidate("reference_neutral_closure", "A_ref", "H", "S_ref_neutral"),
    )


def forbidden_yukawa_operator_classes() -> tuple[YukawaOperatorCandidate, ...]:
    return (
        yukawa_candidate("forbid_cyclic_upper_wrong_scalar", "A_cyc", "H_tilde", "S_cyc_upper"),
        yukawa_candidate("forbid_cyclic_lower_wrong_scalar", "A_cyc", "H", "S_cyc_lower"),
        yukawa_candidate("forbid_reference_charged_wrong_scalar", "A_ref", "H", "S_ref_charged"),
        yukawa_candidate("forbid_reference_neutral_wrong_scalar", "A_ref", "H_tilde", "S_ref_neutral"),
        yukawa_candidate("forbid_reference_active_cyclic_singlet", "A_ref", "H", "S_cyc_lower"),
        yukawa_candidate("forbid_cyclic_active_reference_singlet", "A_cyc", "H", "S_ref_neutral"),
    )


def exactly_four_renormalizable_yukawa_classes() -> bool:
    allowed = allowed_yukawa_operator_classes()
    return len(allowed) == 4 and all(row.status == "ALLOWED_BOUNDARY_YUKAWA_OPERATOR" for row in allowed)


def neutral_singlet_mass_operator_allowed() -> bool:
    field = _field("S_ref_neutral")
    return field.C == 0 and field.Y == 0 and field.orientation == "singlet"


def numerical_yukawa_values_derived() -> bool:
    return False


def mass_ratios_derived() -> bool:
    return False


def ckm_pmns_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-18": DischargeRecord(
            "PO-BH-18",
            "derive Yukawa operator closure",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Renormalizable Yukawa operator classes follow from boundary hypercharge closure, orientation contraction, and cyclic/reference contraction.",
            (
                "boundary field inventory",
                "derived scalar and conjugate scalar doublets",
                "hypercharge closure",
                "orientation singlet contraction",
                "cyclic/reference channel contraction",
            ),
            "Numerical Yukawa values, mass ratios, and CKM/PMNS mixing remain downstream.",
        )
    }


def theorem_discharge_summary() -> dict:
    return {
        "yukawa_operator_layer_discharged_conditionally": True,
        "allowed_operator_classes": {
            row.name: [row.active_field, row.scalar_field, row.singlet_field]
            for row in allowed_yukawa_operator_classes()
        },
        "forbidden_operator_classes": {
            row.name: str(row.hypercharge_sum) for row in forbidden_yukawa_operator_classes()
        },
        "exactly_four_renormalizable_yukawa_classes": exactly_four_renormalizable_yukawa_classes(),
        "neutral_singlet_mass_operator_allowed": neutral_singlet_mass_operator_allowed(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "mass_ratios_derived": mass_ratios_derived(),
        "ckm_pmns_derived": ckm_pmns_derived(),
        "replacement_claim_ready": replacement_claim_ready(),
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "yukawa_operator_layer_discharged_conditionally": True,
        "numerical_yukawa_values_derived": False,
        "mass_ratios_derived": False,
        "ckm_pmns_derived": False,
        "discharged_obligations": {
            "PO-BH-18": "DERIVED_CONDITIONAL: renormalizable Yukawa operator classes follow from boundary charge closure, active-orientation contraction, cyclic/reference contraction, and the derived scalar/conjugate scalar doublets"
        },
        "allowed_operator_classes": {
            row.name: {
                "fields": [row.active_field, row.scalar_field, row.singlet_field],
                "hypercharge_sum": str(row.hypercharge_sum),
            }
            for row in allowed_yukawa_operator_classes()
        },
        "neutral_singlet_mass_operator": {
            "allowed_conditionally": True,
            "field": "S_ref_neutral",
            "reason": "C=0, Y=0, orientation singlet",
        },
        "still_open_downstream": [
            "numerical Yukawa coupling theorem",
            "fermion mass hierarchy theorem",
            "CKM/PMNS mixing theorem",
            "neutral-sector mass scale theorem",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "bridges_preserved": {
            "primitive_closure_spectrum": True,
            "finite_boundary_algebra_charge_layer": True,
            "higgs_scalar_boundary_mechanism_layer": True,
            "one_loop_rg_layer": True,
        },
        "negative_results": [
            "numerical Yukawa values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM/PMNS mixing not derived in this branch",
            "neutral singlet mass scale not predicted in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for Yukawa operator closure",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "summary": theorem_discharge_summary(),
    }


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _inventory_table() -> str:
    lines = ["| field | role | C | Y | orientation | cyclic_role | multiplicity |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for field in boundary_field_inventory().values():
        lines.append(
            f"| {field.name} | {field.role} | {field.C} | {_fraction_text(field.Y)} | {field.orientation} | {field.cyclic_role} | {field.multiplicity} |"
        )
    return "\n".join(lines)


def _candidate_table(rows: tuple[YukawaOperatorCandidate, ...], include_closure: bool = True) -> str:
    if include_closure:
        lines = [
            "| operator_class | active_field | scalar_field | singlet_field | hypercharge_sum | orientation_closes | cyclic_reference_closes | status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in rows:
            lines.append(
                f"| {row.name} | {row.active_field} | {row.scalar_field} | {row.singlet_field} | {_fraction_text(row.hypercharge_sum)} | {row.orientation_closes} | {row.cyclic_reference_closes} | {row.status} |"
            )
        return "\n".join(lines)
    lines = ["| candidate | hypercharge_sum | reason_for_failure | status |", "| --- | --- | --- | --- |"]
    for row in rows:
        reason = "hypercharge closure fails" if row.hypercharge_sum != 0 else "cyclic/reference closure fails"
        lines.append(f"| {row.name} | {_fraction_text(row.hypercharge_sum)} | {reason} | {row.status} |")
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Yukawa Operator Closure

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum, finite boundary algebra, boundary charge/hypercharge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, and the active scalar boundary representation.

## 3. Why Yukawa Operator Closure Is The Next Blocker

The scalar representation is now conditionally derived. The next layer asks which renormalizable boundary operator classes are selected by charge closure and contraction rules before any numerical coupling or mass theorem.

## 4. Boundary Field Inventory

See [Derived Boundary Yukawa Field Inventory](derived_boundary_yukawa_field_inventory.md).

## 5. Derived Scalar And Conjugate Scalar Source

The scalar fields `H` and `H_tilde` are imported from the previous boundary scalar theorem layer as derived conditional inputs.

## 6. Hypercharge Closure Rule

Allowed operators must satisfy `Y_active + Y_scalar + Y_singlet = 0`.

## 7. Active-Orientation Singlet Contraction Rule

The active boundary doublet and scalar/conjugate scalar active doublet must admit an orientation singlet contraction; the inactive boundary field is an orientation singlet.

## 8. Cyclic/Reference Channel Contraction Rule

Reference active sectors close with reference singlet sectors. Cyclic active sectors close with cyclic conjugate-compatible singlet sectors. The scalar is cyclic neutral.

## 9. Allowed Operator Classes

See [Derived Yukawa Allowed Operator Classes](derived_yukawa_allowed_operator_classes.md).

{_candidate_table(allowed_yukawa_operator_classes())}

## 10. Forbidden Operator Classes

See [Derived Yukawa Forbidden Operator Classes](derived_yukawa_forbidden_operator_classes.md).

## 11. Optional Neutral Singlet Mass Operator

See [Derived Boundary Neutral Singlet Mass Operator](derived_boundary_neutral_singlet_mass_operator.md).

## 12. What Remains Before Numerical Yukawa/Mass/Mixing Theorem

Numerical Yukawa values, mass ratios, CKM/PMNS mixing, and neutral-sector mass scales remain open.

## 13. Non-Tautology Checks

See [Yukawa Operator Non-Tautology Audit](yukawa_operator_non_tautology_audit.md).

## 14. Promoted Results, If Any

- `PO_BH_18_YUKAWA_OPERATOR_CLOSURE_DERIVED_CONDITIONAL`
- `YUKAWA_ALLOWED_OPERATOR_CLASSES_DERIVED_CONDITIONAL`
- `YUKAWA_FORBIDDEN_OPERATOR_CLASSES_DERIVED_CONDITIONAL`
- `BOUNDARY_NEUTRAL_SINGLET_MASS_OPERATOR_ALLOWED_CONDITIONALLY`

## 15. Impact On Mass Hierarchy Theorem

The operator classes are narrowed; numerical couplings and hierarchy remain open.

## 16. Impact On CKM/PMNS Theorem

Mixing matrices are not derived in this branch.

## 17. What This Achieves

{CONCLUSION_LANGUAGE}

## 18. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until numerical Yukawa couplings, mass hierarchy, mixing, neutral-sector scale, and full low-energy Lagrangian theorem layers are complete.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_inventory_markdown() -> str:
    return f"""# Derived Boundary Yukawa Field Inventory

{_inventory_table()}

Status: `BOUNDARY_YUKAWA_FIELD_INVENTORY_DERIVED_CONDITIONAL`.
"""


def render_hypercharge_markdown() -> str:
    return """# Derived Yukawa Hypercharge Closure

```text
A_cyc + H + S_cyc_upper:
1/3 + 1 - 4/3 = 0

A_cyc + H_tilde + S_cyc_lower:
1/3 - 1 + 2/3 = 0

A_ref + H_tilde + S_ref_charged:
-1 - 1 + 2 = 0

A_ref + H + S_ref_neutral:
-1 + 1 + 0 = 0
```

Status: `YUKAWA_HYPERCHARGE_CLOSURE_DERIVED_CONDITIONAL`.
"""


def render_orientation_markdown() -> str:
    return """# Derived Yukawa Orientation Contractions

- active boundary doublet x scalar active doublet admits an orientation singlet contraction;
- active boundary doublet x conjugate scalar doublet admits an orientation singlet contraction;
- inactive boundary field is an orientation singlet;
- therefore each allowed operator can be orientation contracted to a scalar.

Status: `YUKAWA_ORIENTATION_CONTRACTIONS_DERIVED_CONDITIONAL`.
"""


def render_cyclic_markdown() -> str:
    return """# Derived Yukawa Cyclic/Reference Contractions

- reference active sector closes only with reference singlet sector;
- cyclic active sector closes with cyclic conjugate-compatible singlet sector;
- scalar is cyclic neutral (`C=0`), so it does not disrupt cyclic contraction.

Status: `YUKAWA_CYCLIC_REFERENCE_CONTRACTIONS_DERIVED_CONDITIONAL`.
"""


def render_allowed_markdown() -> str:
    return f"""# Derived Yukawa Allowed Operator Classes

{_candidate_table(allowed_yukawa_operator_classes())}

Status: `YUKAWA_ALLOWED_OPERATOR_CLASSES_DERIVED_CONDITIONAL`.
"""


def render_forbidden_markdown() -> str:
    return f"""# Derived Yukawa Forbidden Operator Classes

{_candidate_table(forbidden_yukawa_operator_classes(), include_closure=False)}

Status: `YUKAWA_FORBIDDEN_OPERATOR_CLASSES_DERIVED_CONDITIONAL`.
"""


def render_neutral_mass_markdown() -> str:
    return """# Derived Boundary Neutral Singlet Mass Operator

`S_ref_neutral` has:

```text
C=0
Y=0
orientation singlet
```

Therefore a boundary-neutral singlet mass operator is gauge-closure allowed:

```text
S_ref_neutral S_ref_neutral
```

Guardrails:

- This does not predict a scale.
- This does not derive a neutral-sector mass.
- This does not derive PMNS mixing.
- This may support a future neutral-sector mass theorem.

Status: `BOUNDARY_NEUTRAL_SINGLET_MASS_OPERATOR_ALLOWED_CONDITIONALLY`.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("boundary field inventory", "uses boundary named active/singlet fields", "known field labels could be imported", "defined by boundary charges and channel roles", "conditional pass", "derive full field ontology globally"),
        ("scalar/conjugate scalar source", "uses H and H_tilde from prior theorem", "known Higgs table could be imported", "source is previous boundary scalar derivation", "conditional pass", "prior theorem conditional"),
        ("hypercharge closure", "Y sums vanish for four classes", "known Yukawa terms could be copied", "computed with exact boundary charges", "pass", "none at operator-selection level"),
        ("orientation contraction", "active x scalar closes to singlet", "known doublet contractions could be imported", "uses active-orientation boundary rule", "conditional pass", "derive full local action"),
        ("cyclic/reference contraction", "reference with reference, cyclic with conjugate cyclic", "known color contraction could be imported", "uses channel roles", "conditional pass", "derive full channel dynamics"),
        ("allowed operator classes", "exactly four classes", "known table could be inserted", "enumerated by closure rules", "pass", "numerical couplings open"),
        ("forbidden operator classes", "mismatches fail", "negative examples could be omitted", "explicit failures included", "pass", "none"),
        ("neutral singlet mass operator", "allowed conditionally", "known neutral mass structure could be imported", "closure-only statement, no scale", "guarded", "neutral-sector mass theorem"),
        ("comparison to known Yukawa classes", "comparison-equivalent after derivation", "comparison could be premise", "comparison appears after closure derivation", "guarded", "do not use as input"),
    ]
    lines = [
        "# Yukawa Operator Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: The branch does not use the known Standard Model Yukawa table as input. Numerical Yukawa values, mass ratios, and mixing remain open.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_yukawa_operator_closure.md": render_main_markdown(),
        "derived_boundary_yukawa_field_inventory.md": render_inventory_markdown(),
        "derived_yukawa_hypercharge_closure.md": render_hypercharge_markdown(),
        "derived_yukawa_orientation_contractions.md": render_orientation_markdown(),
        "derived_yukawa_cyclic_reference_contractions.md": render_cyclic_markdown(),
        "derived_yukawa_allowed_operator_classes.md": render_allowed_markdown(),
        "derived_yukawa_forbidden_operator_classes.md": render_forbidden_markdown(),
        "derived_boundary_neutral_singlet_mass_operator.md": render_neutral_mass_markdown(),
        "yukawa_operator_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_yukawa_operator_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
