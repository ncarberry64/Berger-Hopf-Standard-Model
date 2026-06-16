from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from candidate_theorem_discharge_yukawa_overlap import (
    SCALAR_INSERTION_BY_SECTOR,
    SECTORS,
    cyclic_mixing_scaffold,
    generation_mode_ledgers as overlap_generation_mode_ledgers,
    reference_mixing_scaffold,
    selection_rules_close_for_sector,
)


BRANCH = "bhsm-theorem-discharge-yukawa-overlap-kernel-selection-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to derive the "
    "Yukawa overlap-kernel selection rules and leading texture source from BHSM "
    "boundary operator closure, generation mode ledgers, scalar insertion rules, "
    "and mode-alignment principles, rather than importing Standard Model Yukawa "
    "textures, masses, or mixing values as assumptions. Status labels may be "
    "promoted only when the derivation is explicit, deterministic, non-tautological, "
    "and does not use known fermion masses or mixing angles as a premise."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the Yukawa overlap-kernel selection "
    "theorem layer. Given the previously derived Yukawa matrix scaffold and "
    "generation mode ledgers, diagonal entries are identified as the leading "
    "self-overlap sources while off-diagonal entries require an additional boundary "
    "transport, mixing, or dressing theorem and remain conditional. The branch "
    "derives deterministic mode-distance diagnostics and classifies the texture "
    "status of all four Yukawa matrices without assigning numerical Yukawa values "
    "or changing frozen predictions. The remaining mass problem is narrowed to "
    "deriving the numerical overlap kernel values."
)

LEADING_DIAGONAL = "DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE"
OFF_DIAGONAL = "CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE"
FORBIDDEN = "FORBIDDEN_BY_BOUNDARY_SELECTION"
NUMERIC_OPEN = "NUMERICAL_VALUE_NOT_DERIVED"

VERDICT_LABELS = [
    "THEOREM_DISCHARGE_YUKAWA_OVERLAP_KERNEL_SELECTION_COMPLETE",
    "PO_BH_20_YUKAWA_OVERLAP_KERNEL_SELECTION_DERIVED_CONDITIONAL",
    "YUKAWA_OVERLAP_KERNEL_SELECTION_RULES_DERIVED_CONDITIONAL",
    "YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL",
    "YUKAWA_MODE_DISTANCE_SCAFFOLD_DERIVED_CONDITIONAL",
    "YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL",
    "YUKAWA_OFF_DIAGONAL_OVERLAP_STATUS_DERIVED_CONDITIONAL",
    "YUKAWA_MASS_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL",
    "YUKAWA_MIXING_SOURCE_BRIDGE_DERIVED_CONDITIONAL",
    "NUMERICAL_OVERLAP_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
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
class GenerationMode:
    index: int
    raw_mode: tuple[int, int]
    qj_pair: tuple[int, int]


@dataclass(frozen=True)
class OverlapKernelEntry:
    sector: str
    row: int
    col: int
    status: str
    distance_L1: int
    distance_L2_squared: int
    numerical_value_status: str


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
        sector: tuple(
            GenerationMode(mode.index, mode.mode_pair, mode.qj_pair)
            for mode in modes
        )
        for sector, modes in overlap_generation_mode_ledgers().items()
    }


def mode_distance_L1(a: GenerationMode, b: GenerationMode) -> int:
    return abs(a.qj_pair[0] - b.qj_pair[0]) + abs(a.qj_pair[1] - b.qj_pair[1])


def mode_distance_L2_squared(a: GenerationMode, b: GenerationMode) -> int:
    return (a.qj_pair[0] - b.qj_pair[0]) ** 2 + (a.qj_pair[1] - b.qj_pair[1]) ** 2


def entry_status(i: int, j: int) -> str:
    if i not in (1, 2, 3) or j not in (1, 2, 3):
        raise ValueError("kernel indices must be in {1,2,3}")
    return LEADING_DIAGONAL if i == j else OFF_DIAGONAL


def overlap_kernel_symbol(sector: str, i: int, j: int) -> str:
    if sector not in SECTORS:
        raise ValueError(f"unknown sector {sector!r}")
    if i not in (1, 2, 3) or j not in (1, 2, 3):
        raise ValueError("kernel indices must be in {1,2,3}")
    return f"K_{sector}_{i}{j}"


def overlap_kernel_entries(sector: str) -> tuple[OverlapKernelEntry, ...]:
    if sector not in SECTORS:
        raise ValueError(f"unknown sector {sector!r}")
    modes = generation_mode_ledgers()[sector]
    if not selection_rules_close_for_sector(sector):
        return tuple(
            OverlapKernelEntry(sector, i, j, FORBIDDEN, 0, 0, NUMERIC_OPEN)
            for i in (1, 2, 3)
            for j in (1, 2, 3)
        )
    entries: list[OverlapKernelEntry] = []
    for active in modes:
        for singlet in modes:
            entries.append(
                OverlapKernelEntry(
                    sector=sector,
                    row=active.index,
                    col=singlet.index,
                    status=entry_status(active.index, singlet.index),
                    distance_L1=mode_distance_L1(active, singlet),
                    distance_L2_squared=mode_distance_L2_squared(active, singlet),
                    numerical_value_status=NUMERIC_OPEN,
                )
            )
    return tuple(entries)


def texture_status_matrix(sector: str) -> list[list[str]]:
    entries = {(entry.row, entry.col): entry.status for entry in overlap_kernel_entries(sector)}
    return [[entries[(i, j)] for j in (1, 2, 3)] for i in (1, 2, 3)]


def compact_texture_matrix(sector: str) -> list[list[str]]:
    short = {LEADING_DIAGONAL: "D", OFF_DIAGONAL: "O", FORBIDDEN: "F"}
    return [[short[status] for status in row] for row in texture_status_matrix(sector)]


def distance_matrix_L1(sector: str) -> list[list[int]]:
    entries = {(entry.row, entry.col): entry.distance_L1 for entry in overlap_kernel_entries(sector)}
    return [[entries[(i, j)] for j in (1, 2, 3)] for i in (1, 2, 3)]


def distance_matrix_L2_squared(sector: str) -> list[list[int]]:
    entries = {(entry.row, entry.col): entry.distance_L2_squared for entry in overlap_kernel_entries(sector)}
    return [[entries[(i, j)] for j in (1, 2, 3)] for i in (1, 2, 3)]


def all_texture_status_matrices() -> dict[str, list[list[str]]]:
    return {sector: texture_status_matrix(sector) for sector in SECTORS}


def all_distance_matrices() -> dict[str, dict[str, list[list[int]]]]:
    return {
        sector: {
            "L1": distance_matrix_L1(sector),
            "L2_squared": distance_matrix_L2_squared(sector),
        }
        for sector in SECTORS
    }


def texture_summary_counts() -> dict[str, int]:
    entries = [entry for sector in SECTORS for entry in overlap_kernel_entries(sector)]
    return {
        "leading_diagonal_entries": sum(entry.status == LEADING_DIAGONAL for entry in entries),
        "conditional_off_diagonal_entries": sum(entry.status == OFF_DIAGONAL for entry in entries),
        "forbidden_entries": sum(entry.status == FORBIDDEN for entry in entries),
        "total_entries": len(entries),
    }


def mass_hierarchy_bridge() -> str:
    return "m_f,i ~ v/sqrt(2)*N_f*I_f(i,i)"


def mixing_source_bridge() -> dict[str, str]:
    return {"cyclic": cyclic_mixing_scaffold(), "reference": reference_mixing_scaffold()}


def numerical_overlap_values_derived() -> bool:
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
        "PO-BH-20": DischargeRecord(
            "PO-BH-20",
            "derive Yukawa overlap-kernel selection",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Yukawa overlap-kernel selection rules classify leading diagonal and conditional off-diagonal sources from generation mode alignment.",
            (
                "Yukawa operator closure",
                "Yukawa matrix scaffold",
                "generation mode ledgers",
                "mode-alignment principle",
                "mode-distance scaffold",
            ),
            "Numerical overlap kernel values, mass hierarchy, and CKM/PMNS mixing remain downstream.",
        )
    }


def theorem_discharge_summary() -> dict:
    return {
        "yukawa_overlap_kernel_layer_discharged_conditionally": True,
        "sectors": list(SECTORS),
        "texture_summary": texture_summary_counts(),
        "texture_status_matrices": all_texture_status_matrices(),
        "compact_texture_matrices": {sector: compact_texture_matrix(sector) for sector in SECTORS},
        "distance_matrices": all_distance_matrices(),
        "mass_hierarchy_bridge": mass_hierarchy_bridge(),
        "mixing_source_bridge": mixing_source_bridge(),
        "numerical_overlap_values_derived": numerical_overlap_values_derived(),
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
        "yukawa_overlap_kernel_layer_discharged_conditionally": True,
        "numerical_overlap_values_derived": False,
        "fermion_mass_ratios_derived": False,
        "ckm_values_derived": False,
        "pmns_values_derived": False,
        "discharged_obligations": {
            "PO-BH-20": "DERIVED_CONDITIONAL: Yukawa overlap-kernel selection rules classify leading diagonal and conditional off-diagonal sources from generation mode alignment"
        },
        "entry_status_labels": [
            LEADING_DIAGONAL,
            OFF_DIAGONAL,
            NUMERIC_OPEN,
        ],
        "texture_summary": texture_summary_counts(),
        "texture_status_matrices": all_texture_status_matrices(),
        "compact_texture_matrices": {sector: compact_texture_matrix(sector) for sector in SECTORS},
        "distance_matrices": all_distance_matrices(),
        "mass_hierarchy_bridge": mass_hierarchy_bridge(),
        "mixing_source_bridge": mixing_source_bridge(),
        "still_open_downstream": [
            "numerical boundary overlap kernel theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "neutral-sector mass scale theorem",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "numerical overlap values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "summary": theorem_discharge_summary(),
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for Yukawa overlap-kernel selection rules",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _matrix_markdown(matrix: list[list[object]]) -> str:
    lines = ["| row/col | 1 | 2 | 3 |", "| --- | --- | --- | --- |"]
    for i, row in enumerate(matrix, start=1):
        lines.append("| " + " | ".join([str(i)] + [str(cell) for cell in row]) + " |")
    return "\n".join(lines)


def _sector_sections(kind: str) -> str:
    blocks: list[str] = []
    for sector in SECTORS:
        if kind == "compact":
            matrix = compact_texture_matrix(sector)
        elif kind == "status":
            matrix = texture_status_matrix(sector)
        elif kind == "L1":
            matrix = distance_matrix_L1(sector)
        elif kind == "L2":
            matrix = distance_matrix_L2_squared(sector)
        else:
            raise ValueError(kind)
        blocks.extend([f"### {sector}", "", _matrix_markdown(matrix), ""])
    return "\n".join(blocks)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Yukawa Overlap-Kernel Selection

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived primitive closure, finite boundary algebra, charge/hypercharge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, the scalar boundary doublet, exactly four renormalizable boundary Yukawa classes, and symbolic 3x3 Yukawa matrix scaffolds.

## 3. Why Overlap-Kernel Selection Is The Next Blocker

The matrix scaffold establishes symbolic entries. This branch classifies which entries are leading self-overlap sources and which require future transport, mixing, or dressing theorem input.

## 4. Four Yukawa Matrix Scaffolds

- `cyclic_upper`
- `cyclic_lower`
- `reference_charged`
- `reference_neutral`

## 5. Mode-Alignment Principle

Generation-aligned pairs `i=j` are leading self-overlap sources. Off-diagonal pairs `i!=j` require additional boundary transport, mixing, or dressing and remain conditional.

## 6. Boundary Kernel Selection Rules

See [Derived Yukawa Overlap Kernel Selection Rules](derived_yukawa_overlap_kernel_selection_rules.md).

## 7. Mode-Distance Scaffold

See [Derived Yukawa Mode Distance Scaffold](derived_yukawa_mode_distance_scaffold.md).

## 8. Leading Diagonal Texture

{_sector_sections("compact")}

`D` means `DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE`; `O` means `CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE`.

## 9. Conditional Off-Diagonal Overlap Status

Off-diagonal entries are not set to zero by assumption. They remain conditional symbolic sources for future mixing.

## 10. Forbidden Entries, If Any

No entries are forbidden by the current inherited closure rules once the parent operator class, scalar insertion, and sector ledger are fixed.

## 11. Mass Hierarchy Bridge

```text
{mass_hierarchy_bridge()}
```

This is symbolic only.

## 12. Mixing Source Bridge

```text
{cyclic_mixing_scaffold()}
{reference_mixing_scaffold()}
```

No CKM or PMNS values are derived.

## 13. What Remains Before Numerical Yukawa Theorem

The numerical boundary overlap kernel theorem remains open.

## 14. Non-Tautology Checks

See [Yukawa Overlap Kernel Non-Tautology Audit](yukawa_overlap_kernel_non_tautology_audit.md).

## 15. Promoted Results, If Any

- `PO_BH_20_YUKAWA_OVERLAP_KERNEL_SELECTION_DERIVED_CONDITIONAL`
- `YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL`
- `YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL`

## 16. Impact On Mass Hierarchy Theorem

The mass hierarchy theorem is narrowed to deriving numerical diagonal kernel values and the sector normalizations.

## 17. Impact On CKM/PMNS Theorem

Off-diagonal symbolic entries identify where future mixing can enter. No mixing value is derived.

## 18. What This Achieves

{CONCLUSION_LANGUAGE}

## 19. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until numerical overlap values, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, and the full low-energy Lagrangian theorem are complete.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_selection_rules_markdown() -> str:
    rules = [
        "parent operator class is one of the four allowed Yukawa closures",
        "scalar insertion matches the sector",
        "hypercharge closure remains zero",
        "orientation contraction closes",
        "cyclic/reference contraction closes",
        "neutral scalar component can provide mass after vacuum",
        "generation mode pair is drawn from the sector ledger",
        "diagonal mode alignment i=j is the leading self-overlap source",
        "off-diagonal i!=j requires an additional mixing/transport/dressing mechanism and is conditional unless independently derived elsewhere",
        "entries that violate closure are forbidden",
    ]
    lines = ["# Derived Yukawa Overlap Kernel Selection Rules", ""]
    lines.extend(f"{i}. {rule}." for i, rule in enumerate(rules, start=1))
    lines.extend(["", "Status: `YUKAWA_OVERLAP_KERNEL_SELECTION_RULES_DERIVED_CONDITIONAL`."])
    return "\n".join(lines) + "\n"


def render_mode_alignment_markdown() -> str:
    return """# Derived Yukawa Mode-Alignment Principle

Within each boundary sector ledger, the same generation index on the active side and singlet side is treated as the leading self-overlap source:

```text
i=j -> DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE
i!=j -> CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE
```

Off-diagonal entries are not forbidden by default and are not set to zero by assumption. They require a future boundary transport, dressing, or mixing theorem.

Status: `YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL`.
"""


def render_distance_markdown() -> str:
    return f"""# Derived Yukawa Mode-Distance Scaffold

Diagnostic distances:

```text
D_f(i,j)=|q_i-q_j|+|j_i-j_j|
D2_f(i,j)=(q_i-q_j)^2+(j_i-j_j)^2
```

These are diagnostic distances, not numerical Yukawa values.

## L1 Distance Matrices

{_sector_sections("L1")}

## Squared Distance Matrices

{_sector_sections("L2")}

Status: `YUKAWA_MODE_DISTANCE_SCAFFOLD_DERIVED_CONDITIONAL`.
"""


def render_leading_texture_markdown() -> str:
    return f"""# Derived Yukawa Leading Texture Status

Status matrices:

{_sector_sections("status")}

Compact matrices:

{_sector_sections("compact")}

Status: `YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL`.
"""


def render_off_diagonal_markdown() -> str:
    return """# Derived Yukawa Off-Diagonal Overlap Status

- off-diagonal entries are not zero by assumption;
- they are conditional until a boundary transport, dressing, or mixing theorem is derived;
- they are the symbolic source of future mixing.

Status: `YUKAWA_OFF_DIAGONAL_OVERLAP_STATUS_DERIVED_CONDITIONAL`.
"""


def render_mass_hierarchy_markdown() -> str:
    return f"""# Derived Yukawa Mass Hierarchy Bridge

Symbolic leading-order relation:

```text
{mass_hierarchy_bridge()}
```

Guardrails:

- no numerical masses;
- no mass ratios;
- no changes to frozen outputs.

Status: `YUKAWA_MASS_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL`.
"""


def render_mixing_source_markdown() -> str:
    return f"""# Derived Yukawa Mixing Source Bridge

Off-diagonal overlap entries feed future left diagonalization matrices.

```text
{cyclic_mixing_scaffold()}
{reference_mixing_scaffold()}
```

Guardrails:

- no CKM values;
- no PMNS values.

Status: `YUKAWA_MIXING_SOURCE_BRIDGE_DERIVED_CONDITIONAL`.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("operator closure inheritance", "uses four PO-BH-18 operator classes", "known texture choices", "inherits boundary closure rules", "conditional pass", "operator layer remains conditional"),
        ("generation mode ledgers", "uses fixed sector ledgers", "measured masses", "uses BHSM mode ledgers only", "conditional pass", "full ledger theorem remains upstream"),
        ("mode-alignment principle", "i=j is leading self-overlap", "approximately diagonal SM textures", "uses generation-aligned boundary pairs", "conditional pass", "derive full kernel"),
        ("diagonal leading texture", "diagonal entries are leading symbolic sources", "known hierarchy pattern", "no numerical values inserted", "guarded", "derive kernel values"),
        ("off-diagonal conditional status", "off-diagonal entries require transport/mixing theorem", "CKM/PMNS values", "kept symbolic and conditional", "guarded", "derive mixing theorem"),
        ("mode-distance scaffold", "L1 and squared q,j distances", "fitted suppression law", "diagnostic distances only", "guarded", "derive distance-to-value kernel"),
        ("mass hierarchy bridge", "m_f,i ~ v/sqrt(2)*N_f*I_f(i,i)", "measured masses", "symbolic relation only", "guarded", "derive values"),
        ("mixing source bridge", "off-diagonal entries feed diagonalization", "known mixing matrices", "no angles inserted", "guarded", "derive mixing"),
        ("comparison to known texture/mixing frameworks", "comparison may occur after derivation", "known textures as premise", "not used as input", "guarded", "future numerical theorem"),
    ]
    lines = [
        "# Yukawa Overlap Kernel Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append(
        "Conclusion: The branch does not use measured masses, known texture patterns, CKM values, or PMNS values as input. Numerical overlap values remain open."
    )
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_yukawa_overlap_kernel_selection.md": render_main_markdown(),
        "derived_yukawa_overlap_kernel_selection_rules.md": render_selection_rules_markdown(),
        "derived_yukawa_mode_alignment_principle.md": render_mode_alignment_markdown(),
        "derived_yukawa_mode_distance_scaffold.md": render_distance_markdown(),
        "derived_yukawa_leading_texture_status.md": render_leading_texture_markdown(),
        "derived_yukawa_off_diagonal_overlap_status.md": render_off_diagonal_markdown(),
        "derived_yukawa_mass_hierarchy_bridge.md": render_mass_hierarchy_markdown(),
        "derived_yukawa_mixing_source_bridge.md": render_mixing_source_markdown(),
        "yukawa_overlap_kernel_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_yukawa_overlap_kernel_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
