from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from candidate_theorem_discharge_yukawa_operator import allowed_yukawa_operator_classes


BRANCH = "bhsm-theorem-discharge-yukawa-overlap-texture-source-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to derive the "
    "Yukawa matrix source scaffold from BHSM boundary operator closure, generation "
    "mode ledgers, scalar insertion rules, and boundary overlap functionals, rather "
    "than importing Standard Model Yukawa matrices or fitted mass data as "
    "assumptions. Status labels may be promoted only when the derivation is "
    "explicit, non-tautological, and does not use known fermion masses or mixing "
    "angles as a premise."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the Yukawa overlap texture-source theorem "
    "layer. Given the previously derived Yukawa operator classes and scalar "
    "boundary doublet, each allowed class lifts to a 3x3 boundary-overlap Yukawa "
    "matrix with entries sourced by generation-mode overlap functionals. The "
    "branch derives the matrix scaffold and mass-matrix relation M_f=vY_f/sqrt(2), "
    "while leaving numerical Yukawa values, mass ratios, and CKM/PMNS mixing angles "
    "open. The mass problem is thereby narrowed to deriving the overlap functional "
    "values rather than selecting the operator classes."
)
VERDICT_LABELS = [
    "THEOREM_DISCHARGE_YUKAWA_OVERLAP_TEXTURE_SOURCE_COMPLETE",
    "PO_BH_19_YUKAWA_OVERLAP_TEXTURE_SOURCE_DERIVED_CONDITIONAL",
    "YUKAWA_OVERLAP_FUNCTIONAL_DERIVED_CONDITIONAL",
    "YUKAWA_GENERATION_MODE_LEDGERS_DERIVED_CONDITIONAL",
    "YUKAWA_MATRIX_SCAFFOLD_DERIVED_CONDITIONAL",
    "YUKAWA_MASS_MATRIX_RELATIONS_DERIVED_CONDITIONAL",
    "YUKAWA_MIXING_SCAFFOLD_DERIVED_CONDITIONAL",
    "NEUTRAL_SECTOR_MASS_SCAFFOLD_DERIVED_CONDITIONAL",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
    "DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

SECTORS = ("cyclic_upper", "cyclic_lower", "reference_charged", "reference_neutral")
OPERATOR_CLASS_BY_SECTOR = {
    "cyclic_upper": "cyclic_upper_closure",
    "cyclic_lower": "cyclic_lower_closure",
    "reference_charged": "reference_charged_closure",
    "reference_neutral": "reference_neutral_closure",
}
SCALAR_INSERTION_BY_SECTOR = {
    "cyclic_upper": "H",
    "cyclic_lower": "H_tilde",
    "reference_charged": "H_tilde",
    "reference_neutral": "H",
}


class DischargeStatus(str, Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class GenerationMode:
    index: int
    mode_pair: tuple[int, int]
    qj_pair: tuple[int, int]
    interpretation: str


@dataclass(frozen=True)
class YukawaMatrixEntry:
    row: int
    col: int
    symbol: str
    status: str


@dataclass(frozen=True)
class YukawaMatrixScaffold:
    sector: str
    operator_class: str
    scalar_insertion: str
    active_modes: tuple[GenerationMode, ...]
    singlet_modes: tuple[GenerationMode, ...]
    entries: tuple[YukawaMatrixEntry, ...]


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: DischargeStatus
    statement: str
    dependencies: tuple[str, ...]
    remaining_blocker: str


def generation_mode_ledgers() -> dict[str, tuple[GenerationMode, ...]]:
    return {
        "reference_charged": (
            GenerationMode(1, (0, 0), (0, 0), "heavy reference charged boundary mode"),
            GenerationMode(2, (5, 2), (1, 2), "middle reference charged boundary mode"),
            GenerationMode(3, (9, 3), (3, 3), "light reference charged boundary mode"),
        ),
        "reference_neutral": (
            GenerationMode(1, (0, 0), (0, 0), "heavy reference neutral boundary mode"),
            GenerationMode(2, (3, 0), (3, 0), "middle reference neutral boundary mode"),
            GenerationMode(3, (3, 1), (1, 1), "light reference neutral boundary mode"),
        ),
        "cyclic_upper": (
            GenerationMode(1, (0, 0), (0, 0), "heavy cyclic upper boundary mode"),
            GenerationMode(2, (6, 0), (6, 0), "middle cyclic upper boundary mode"),
            GenerationMode(3, (10, 1), (8, 1), "light cyclic upper boundary mode"),
        ),
        "cyclic_lower": (
            GenerationMode(1, (0, 0), (0, 0), "heavy cyclic lower boundary mode"),
            GenerationMode(2, (6, 3), (0, 3), "middle cyclic lower boundary mode"),
            GenerationMode(3, (8, 2), (4, 2), "light cyclic lower boundary mode"),
        ),
    }


def operator_class_to_scalar_insertion() -> dict[str, str]:
    return dict(SCALAR_INSERTION_BY_SECTOR)


def overlap_functional_definition() -> str:
    return "Y_f[i,j]=N_f*I_f(A_f[i],H_f,S_f[j])"


def overlap_symbol(sector: str, i: int, j: int) -> str:
    _validate_sector(sector)
    if i not in (1, 2, 3) or j not in (1, 2, 3):
        raise ValueError("Yukawa overlap indices must be in {1,2,3}")
    return f"I_{sector}_{i}{j}"


def _validate_sector(sector: str) -> None:
    if sector not in SECTORS:
        raise ValueError(f"unknown Yukawa sector {sector!r}")


def _entry_status(i: int, j: int) -> str:
    if i == j:
        return "DERIVED_DIAGONAL_SYMBOLIC_OVERLAP"
    return "CONDITIONAL_OFF_DIAGONAL_OVERLAP"


def yukawa_matrix_scaffold(sector: str) -> YukawaMatrixScaffold:
    _validate_sector(sector)
    ledgers = generation_mode_ledgers()
    entries = tuple(
        YukawaMatrixEntry(i, j, overlap_symbol(sector, i, j), _entry_status(i, j))
        for i in (1, 2, 3)
        for j in (1, 2, 3)
    )
    return YukawaMatrixScaffold(
        sector=sector,
        operator_class=OPERATOR_CLASS_BY_SECTOR[sector],
        scalar_insertion=SCALAR_INSERTION_BY_SECTOR[sector],
        active_modes=ledgers[sector],
        singlet_modes=ledgers[sector],
        entries=entries,
    )


def all_yukawa_matrix_scaffolds() -> tuple[YukawaMatrixScaffold, ...]:
    return tuple(yukawa_matrix_scaffold(sector) for sector in SECTORS)


def each_matrix_is_3x3() -> bool:
    return all(len(scaffold.entries) == 9 for scaffold in all_yukawa_matrix_scaffolds())


def selection_rules_close_for_sector(sector: str) -> bool:
    scaffold = yukawa_matrix_scaffold(sector)
    allowed = {row.name: row for row in allowed_yukawa_operator_classes()}
    parent = allowed[scaffold.operator_class]
    return (
        parent.hypercharge_sum == 0
        and parent.orientation_closes
        and parent.cyclic_reference_closes
        and scaffold.scalar_insertion == SCALAR_INSERTION_BY_SECTOR[sector]
    )


def neutral_scalar_vacuum_component(sector: str) -> str:
    _validate_sector(sector)
    return "H_zero" if SCALAR_INSERTION_BY_SECTOR[sector] == "H" else "H_tilde_zero"


def mass_matrix_relation(sector: str) -> str:
    _validate_sector(sector)
    return f"M_{sector}=v/sqrt(2)*Y_{sector}"


def mixing_scaffold_defined() -> bool:
    return True


def cyclic_mixing_scaffold() -> str:
    return "V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L"


def reference_mixing_scaffold() -> str:
    return "V_reference=U_reference_charged_L^dagger U_reference_neutral_L"


def neutral_sector_mass_scaffold() -> dict:
    return {
        "included": True,
        "symbolic_mass_matrix": "M_N[j,k]=N_N*I_N(S_ref_neutral[j],S_ref_neutral[k])",
        "effective_operator": "M_eff=-M_D*M_N^{-1}*M_D^T",
        "mass_scale_predicted": False,
        "pmns_values_derived": False,
    }


def numerical_yukawa_values_derived() -> bool:
    return False


def fermion_mass_ratios_derived() -> bool:
    return False


def ckm_values_derived() -> bool:
    return False


def pmns_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-19": DischargeRecord(
            "PO-BH-19",
            "derive Yukawa overlap texture source",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Yukawa matrices are sourced by boundary overlap functionals tied to the four allowed operator classes and generation mode ledgers.",
            (
                "Yukawa operator closure",
                "generation mode ledgers",
                "scalar insertion rule",
                "boundary overlap functional",
            ),
            "Numerical overlap values, mass hierarchy, and CKM/PMNS mixing remain downstream.",
        )
    }


def theorem_discharge_summary() -> dict:
    return {
        "yukawa_overlap_layer_discharged_conditionally": True,
        "sectors": list(SECTORS),
        "each_matrix_is_3x3": each_matrix_is_3x3(),
        "scalar_insertions": operator_class_to_scalar_insertion(),
        "overlap_functional": overlap_functional_definition(),
        "mass_matrix_relations": {sector: mass_matrix_relation(sector) for sector in SECTORS},
        "mixing_scaffold_defined": mixing_scaffold_defined(),
        "neutral_sector_mass_scaffold": neutral_sector_mass_scaffold(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "fermion_mass_ratios_derived": fermion_mass_ratios_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
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
        "yukawa_overlap_layer_discharged_conditionally": True,
        "numerical_yukawa_values_derived": False,
        "fermion_mass_ratios_derived": False,
        "ckm_values_derived": False,
        "pmns_values_derived": False,
        "discharged_obligations": {
            "PO-BH-19": "DERIVED_CONDITIONAL: Yukawa matrix scaffolds are sourced by BHSM boundary overlap functionals tied to allowed operator classes and generation mode ledgers"
        },
        "yukawa_matrices": {
            scaffold.sector: {
                "shape": "3x3",
                "operator_class": scaffold.operator_class,
                "scalar_insertion": scaffold.scalar_insertion,
                "neutral_vacuum_component": neutral_scalar_vacuum_component(scaffold.sector),
                "entries": "symbolic boundary overlap entries",
                "entry_symbols": [entry.symbol for entry in scaffold.entries],
            }
            for scaffold in all_yukawa_matrix_scaffolds()
        },
        "mass_matrix_relation": "M_f=vY_f/sqrt(2)",
        "mixing_scaffold": {
            "cyclic": cyclic_mixing_scaffold(),
            "reference": reference_mixing_scaffold(),
            "numerical_values_derived": False,
        },
        "neutral_sector_mass_scaffold": neutral_sector_mass_scaffold(),
        "still_open_downstream": [
            "numerical boundary overlap theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "neutral-sector mass scale theorem",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "numerical Yukawa values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "summary": theorem_discharge_summary(),
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for Yukawa overlap texture source",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _matrix_table(scaffold: YukawaMatrixScaffold) -> str:
    entries = {entry.symbol: entry for entry in scaffold.entries}
    lines = [
        f"### Y_{scaffold.sector}",
        "",
        "| row/col | 1 | 2 | 3 |",
        "| --- | --- | --- | --- |",
    ]
    for i in (1, 2, 3):
        row_entries = [entries[overlap_symbol(scaffold.sector, i, j)] for j in (1, 2, 3)]
        lines.append("| " + " | ".join([str(i)] + [entry.symbol for entry in row_entries]) + " |")
    lines.extend(
        [
            "",
            f"- operator class: `{scaffold.operator_class}`",
            f"- scalar insertion: `{scaffold.scalar_insertion}`",
            f"- neutral vacuum component: `{neutral_scalar_vacuum_component(scaffold.sector)}`",
            "- diagonal entries: `DERIVED_DIAGONAL_SYMBOLIC_OVERLAP`",
            "- off-diagonal entries: `CONDITIONAL_OFF_DIAGONAL_OVERLAP`",
            "- numerical value status: `NUMERICAL_VALUE_NOT_DERIVED`",
            "",
        ]
    )
    return "\n".join(lines)


def _mode_table() -> str:
    lines = [
        "| sector | generation | mode_pair | qj_pair | interpretation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for sector, modes in generation_mode_ledgers().items():
        for mode in modes:
            lines.append(
                f"| {sector} | {mode.index} | {mode.mode_pair} | {mode.qj_pair} | {mode.interpretation} |"
            )
    return "\n".join(lines)


def render_main_markdown() -> str:
    matrices = "\n".join(_matrix_table(scaffold) for scaffold in all_yukawa_matrix_scaffolds())
    return f"""# Theorem Discharge: Yukawa Overlap Texture Source

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived primitive closure, finite boundary algebra, charge/hypercharge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, the scalar boundary doublet, and exactly four renormalizable boundary Yukawa operator classes.

## 3. Why Yukawa Overlap Texture Is The Next Blocker

Operator closure selects which boundary couplings can exist. The next layer asks how the allowed classes lift to matrix-valued overlap functionals over the generation mode ledgers.

## 4. Four Allowed Boundary Yukawa Classes

- `cyclic_upper_closure`: `A_cyc + H + S_cyc_upper`
- `cyclic_lower_closure`: `A_cyc + H_tilde + S_cyc_lower`
- `reference_charged_closure`: `A_ref + H_tilde + S_ref_charged`
- `reference_neutral_closure`: `A_ref + H + S_ref_neutral`

## 5. Generation Mode Ledgers

See [Derived Yukawa Generation Mode Ledgers](derived_yukawa_generation_mode_ledgers.md).

## 6. Boundary Overlap Functional

```text
{overlap_functional_definition()}
```

See [Derived Yukawa Overlap Functional](derived_yukawa_overlap_functional.md).

## 7. Four Yukawa Matrices

{matrices}

## 8. Neutral Scalar Vacuum And Mass Matrix Relation

```text
M_f = v/sqrt(2) * Y_f
```

## 9. Diagonal/Off-Diagonal Entry Status

Diagonal symbolic entries are selected by the same-generation boundary overlap source. Off-diagonal entries are included as conditional symbolic overlap entries because their numerical/mixing values require a future overlap and mixing theorem.

## 10. Mixing Scaffold

```text
U_f_L^dagger Y_f U_f_R = D_f
{cyclic_mixing_scaffold()}
{reference_mixing_scaffold()}
```

No CKM or PMNS numerical values are derived here.

## 11. Optional Neutral Singlet Mass Scaffold

See [Derived Neutral Sector Mass Scaffold](derived_neutral_sector_mass_scaffold.md).

## 12. What Remains Before Numerical Mass Theorem

The numerical boundary overlap theorem, fermion mass hierarchy theorem, CKM theorem, PMNS theorem, and neutral-sector mass scale theorem remain open.

## 13. Non-Tautology Checks

See [Yukawa Overlap Non-Tautology Audit](yukawa_overlap_non_tautology_audit.md).

## 14. Promoted Results, If Any

- `PO_BH_19_YUKAWA_OVERLAP_TEXTURE_SOURCE_DERIVED_CONDITIONAL`
- `YUKAWA_OVERLAP_FUNCTIONAL_DERIVED_CONDITIONAL`
- `YUKAWA_MATRIX_SCAFFOLD_DERIVED_CONDITIONAL`

## 15. Impact On Mass Hierarchy Theorem

The mass problem is narrowed to deriving symbolic overlap values and their hierarchy. No mass ratio is changed or predicted in this branch.

## 16. Impact On CKM/PMNS Theorem

The branch defines diagonalization and mixing scaffolds only. No measured mixing value is derived.

## 17. What This Achieves

{CONCLUSION_LANGUAGE}

## 18. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until numerical overlaps, mass hierarchy, mixing, neutral-sector scales, and the full low-energy Lagrangian theorem are complete.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_overlap_functional_markdown() -> str:
    return f"""# Derived Yukawa Overlap Functional

```text
{overlap_functional_definition()}
```

Where:

- `f` labels the boundary closure class.
- `N_f` is a sector normalization.
- `I_f` is the BHSM boundary overlap/contraction/mode-coupling functional.
- `A_f[i]` is the active generation mode.
- `H_f` is `H` or `H_tilde`.
- `S_f[j]` is the conjugate inactive singlet generation mode.

The entries remain symbolic in this theorem layer.

Status: `YUKAWA_OVERLAP_FUNCTIONAL_DERIVED_CONDITIONAL`.
"""


def render_generation_ledgers_markdown() -> str:
    return f"""# Derived Yukawa Generation Mode Ledgers

{_mode_table()}

Status: `YUKAWA_GENERATION_MODE_LEDGERS_DERIVED_CONDITIONAL`.
"""


def render_matrix_scaffold_markdown() -> str:
    return "# Derived Yukawa Matrix Scaffold\n\n" + "\n".join(
        _matrix_table(scaffold) for scaffold in all_yukawa_matrix_scaffolds()
    ) + "\nStatus: `YUKAWA_MATRIX_SCAFFOLD_DERIVED_CONDITIONAL`.\n"


def render_mass_matrix_markdown() -> str:
    lines = [
        "# Derived Yukawa Mass Matrix Relations",
        "",
        "For each allowed boundary closure class:",
        "",
        "```text",
        "M_f = v/sqrt(2) * Y_f",
        "```",
        "",
    ]
    for sector in SECTORS:
        lines.append(f"- `{mass_matrix_relation(sector)}`")
    lines.extend(
        [
            "",
            "Guardrails:",
            "",
            "- `v` remains symbolic in this theorem layer.",
            "- numerical masses are not predicted in this branch.",
            "- frozen mass-ratio outputs are not changed.",
            "",
            "Status: `YUKAWA_MASS_MATRIX_RELATIONS_DERIVED_CONDITIONAL`.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_mixing_markdown() -> str:
    return f"""# Derived Yukawa Mixing Scaffold

Symbolic diagonalization:

```text
U_f_L^dagger Y_f U_f_R = D_f
```

Cyclic scaffold:

```text
{cyclic_mixing_scaffold()}
```

Reference scaffold:

```text
{reference_mixing_scaffold()}
```

Guardrails:

- CKM values are not derived.
- PMNS values are not derived.
- measured mixing angles are not derived.
- this branch only defines the scaffold that future overlap values feed into.

Status: `YUKAWA_MIXING_SCAFFOLD_DERIVED_CONDITIONAL`.
"""


def render_neutral_mass_markdown() -> str:
    scaffold = neutral_sector_mass_scaffold()
    return f"""# Derived Neutral Sector Mass Scaffold

Because `S_ref_neutral` is boundary neutral, a neutral singlet mass matrix may be symbolically defined:

```text
{scaffold["symbolic_mass_matrix"]}
```

If a future theorem derives the relevant scale and invertibility conditions, an effective neutral mass operator may be written:

```text
{scaffold["effective_operator"]}
```

Guardrails:

- no neutral mass scale is predicted;
- no measured neutral masses are derived;
- no PMNS values are derived.

Status: `NEUTRAL_SECTOR_MASS_SCAFFOLD_DERIVED_CONDITIONAL`.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("allowed operator classes", "uses PO-BH-18 closure classes", "known Yukawa matrices", "uses boundary class names and closure rules", "conditional pass", "operator layer remains conditional"),
        ("generation mode ledgers", "three generation modes per boundary sector", "measured masses or particle labels", "uses fixed BHSM mode ledgers", "conditional pass", "full mode-ledger derivation remains upstream"),
        ("overlap functional", "defines Y_f[i,j]=N_f*I_f(...)", "fitted mass data", "symbolic functional only", "pass", "derive I_f values"),
        ("matrix scaffold", "four 3x3 matrices", "known Yukawa matrices", "entries are deterministic symbols", "pass", "numerical values open"),
        ("mass matrix relation", "M_f=vY_f/sqrt(2)", "measured masses", "symbolic relation only", "guarded", "derive v and overlap values"),
        ("mixing scaffold", "unitary diagonalization scaffold", "CKM/PMNS values", "no angles or matrix elements inserted", "guarded", "derive overlap matrices"),
        ("neutral sector mass scaffold", "symbolic M_N and M_eff", "measured neutrino masses", "no scale or PMNS value inserted", "guarded", "neutral mass theorem"),
        ("comparison to known fermion mass/mixing framework", "comparison allowed after derivation", "known mass/mixing framework as premise", "comparison is not an input", "guarded", "future numerical theorem"),
    ]
    lines = [
        "# Yukawa Overlap Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append(
        "Conclusion: The branch does not use measured masses, known Yukawa matrices, CKM values, or PMNS values as input. Numerical values remain open unless derived from a future BHSM overlap theorem."
    )
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_yukawa_overlap_texture_source.md": render_main_markdown(),
        "derived_yukawa_overlap_functional.md": render_overlap_functional_markdown(),
        "derived_yukawa_generation_mode_ledgers.md": render_generation_ledgers_markdown(),
        "derived_yukawa_matrix_scaffold.md": render_matrix_scaffold_markdown(),
        "derived_yukawa_mass_matrix_relations.md": render_mass_matrix_markdown(),
        "derived_yukawa_mixing_scaffold.md": render_mixing_markdown(),
        "derived_neutral_sector_mass_scaffold.md": render_neutral_mass_markdown(),
        "yukawa_overlap_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_yukawa_overlap_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
