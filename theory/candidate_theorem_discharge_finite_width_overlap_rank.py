from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-finite-width-overlap-rank-v1"
STATUS = "partial_theorem_scaffold"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch investigates whether "
    "finite-width moments of the universal scalar/topographic profile can lift "
    "the BHSM Yukawa overlap kernel beyond the strict point-sampling rank-one "
    "limit without fitted fermion masses or mixing data."
)
CONCLUSION_LANGUAGE = (
    "This branch derives the finite-width overlap-moment scaffold for the BHSM "
    "Yukawa kernel and identifies the condition under which the overlap matrix "
    "can exceed the strict point-sampling rank-one limit. The strict sharp-peak "
    "term remains rank-limited, while finite-width moments can in principle "
    "raise the rank if the relevant internal eigenfunction derivative and "
    "moment structures are linearly independent. This branch does not promote "
    "numerical Yukawa values, fermion mass ratios, CKM values, or PMNS values. "
    "Rank-three Yukawa structure remains open unless the required internal "
    "eigenfunction independence is derived from BHSM geometry."
)


class RankStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    PARTIAL = "PARTIAL"
    OPEN = "OPEN"
    NOT_DERIVED = "NOT_DERIVED"


@dataclass(frozen=True)
class RankComponent:
    name: str
    statement: str
    status: str
    guardrail: str


VERDICT_LABELS = [
    "PO_BH_23_FINITE_WIDTH_OVERLAP_RANK_THEOREM_PARTIAL",
    "FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL",
    "SHARP_PEAK_RANK_ONE_LIMIT_DERIVED_CONDITIONAL",
    "RANK_THREE_OVERLAP_CONDITION_DERIVED_CONDITIONAL",
    "INTERNAL_EIGENFUNCTION_INDEPENDENCE_REMAINS_OPEN",
    "UNIVERSAL_PROFILE_WIDTH_GUARDRAIL_DERIVED_CONDITIONAL",
    "FINITE_WIDTH_RANK_THREE_REMAINS_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def bhsm_overlap_kernel() -> str:
    return "I_f(i,j)=integral_{B^3} Psi_A_f_i^*(y) Phi_H_f(y) Psi_S_f_j(y) dV_gamma"


def universal_profile() -> str:
    return "Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]"


def local_mode_expansion(side: str) -> str:
    if side not in {"A", "S"}:
        raise ValueError("side must be A or S")
    return (
        f"Psi_{side}_i(y)=Psi_{side}_i(y0)+xi^a partial_a Psi_{side}_i(y0)"
        f"+1/2 xi^a xi^b partial_a partial_b Psi_{side}_i(y0)+..."
    )


def moment_tensor_formula(order: str) -> str:
    formulas = {
        "M0": "M0=integral Phi(y) dV_gamma",
        "Mab": "M_ab=integral xi_a xi_b Phi(y) dV_gamma",
        "Mabcd": "M_abcd=integral xi_a xi_b xi_c xi_d Phi(y) dV_gamma",
    }
    if order not in formulas:
        raise ValueError("order must be M0, Mab, or Mabcd")
    return formulas[order]


def sharp_peak_rank_bound() -> str:
    return "rank(I)<=1 for strict point-sampling I_ij=a_i^* b_j"


def moment_expansion_formula() -> str:
    return "I_ij=M0 a_i^* b_j + M_ab (partial_a a_i^*)(partial_b b_j) + higher finite-width moments"


def rank_three_condition() -> str:
    return "rank(I_f)=3 if finite-width moment contributions span three independent row/column structures"


def internal_eigenfunction_independence_condition() -> str:
    return (
        "the sets {a_i, partial_a a_i, partial_a partial_b a_i, ...} and "
        "{b_j, partial_a b_j, partial_a partial_b b_j, ...}, contracted with "
        "universal profile moments, must provide at least three independent "
        "matrix structures"
    )


def universal_width_guardrail() -> str:
    return "sigma must be fixed by internal geometry and cannot be tuned by flavor or generation"


def strict_point_sampling_rank_three_derived() -> bool:
    return False


def finite_width_rank_three_derived() -> bool:
    return False


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


def proof_discharge_ledger() -> dict[str, str]:
    return {
        "PO-BH-23": (
            "PARTIAL: finite-width overlap moment scaffold and rank-three "
            "condition derived; actual rank-three Yukawa theorem remains open "
            "unless internal eigenfunction independence is derived"
        )
    }


def rank_components() -> tuple[RankComponent, ...]:
    return (
        RankComponent(
            "sharp_peak_outer_product",
            sharp_peak_rank_bound(),
            "SHARP_PEAK_RANK_ONE_LIMIT_DERIVED_CONDITIONAL",
            "strict point sampling cannot produce rank three",
        ),
        RankComponent(
            "finite_width_moment_expansion",
            moment_expansion_formula(),
            "FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL",
            "symbolic expansion only; no numerical moments computed",
        ),
        RankComponent(
            "rank_three_condition",
            rank_three_condition(),
            "RANK_THREE_OVERLAP_CONDITION_DERIVED_CONDITIONAL",
            "condition is not asserted satisfied",
        ),
        RankComponent(
            "internal_eigenfunction_independence",
            internal_eigenfunction_independence_condition(),
            "INTERNAL_EIGENFUNCTION_INDEPENDENCE_REMAINS_OPEN",
            "requires BHSM eigenfunction theorem or computation",
        ),
        RankComponent(
            "universal_width_guardrail",
            universal_width_guardrail(),
            "UNIVERSAL_PROFILE_WIDTH_GUARDRAIL_DERIVED_CONDITIONAL",
            "no flavor or generation tuning of sigma",
        ),
    )


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
        "finite_width_overlap_rank_layer_completed": True,
        "strict_point_sampling_rank_three_derived": strict_point_sampling_rank_three_derived(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "fermion_mass_ratios_derived": fermion_mass_ratios_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "discharged_obligations": proof_discharge_ledger(),
        "formulas": {
            "bhsm_kernel": bhsm_overlap_kernel(),
            "universal_profile": universal_profile(),
            "active_mode_expansion": local_mode_expansion("A"),
            "singlet_mode_expansion": local_mode_expansion("S"),
            "M0": moment_tensor_formula("M0"),
            "Mab": moment_tensor_formula("Mab"),
            "Mabcd": moment_tensor_formula("Mabcd"),
            "moment_expansion": moment_expansion_formula(),
            "sharp_peak_rank_bound": sharp_peak_rank_bound(),
            "rank_three_condition": rank_three_condition(),
            "universal_width_guardrail": universal_width_guardrail(),
        },
        "rank_results": {
            "strict_point_sampling": "rank <= 1",
            "finite_width_moments": "can raise rank if independent internal eigenfunction moment structures are derived",
            "rank_three_status": "OPEN",
        },
        "rank_components": [
            {
                "name": component.name,
                "statement": component.statement,
                "status": component.status,
                "guardrail": component.guardrail,
            }
            for component in rank_components()
        ],
        "still_open_downstream": [
            "internal Berger/BHSM eigenfunction theorem",
            "eigenfunction amplitudes at y0",
            "finite-width moment values",
            "rank-three Yukawa matrix theorem",
            "numerical Yukawa coupling theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "neutral-sector mass scale theorem",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "strict point sampling alone does not derive rank-three Yukawa matrices",
            "finite-width rank-three not promoted without internal eigenfunction independence",
            "numerical Yukawa values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "finite-width moments provide a symbolic route beyond the outer-product term",
            "rank-three condition is derived but not proven satisfied",
            "universal sigma guardrail forbids flavor/generation width fitting",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _components_table() -> str:
    lines = ["| component | statement | status | guardrail |", "| --- | --- | --- | --- |"]
    for component in rank_components():
        lines.append(
            f"| {component.name} | `{component.statement}` | `{component.status}` | {component.guardrail} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Finite-Width Overlap Rank

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the closure spectrum, finite boundary algebra, charge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, scalar doublet, Yukawa operator closure, symbolic Yukawa matrix scaffolds, overlap-kernel selection rules, distance diagnostics, and the legacy geometric-overlap kernel bridge.

## 3. PO-BH-22 Geometric Kernel Bridge

PO-BH-22 identified the BHSM overlap kernel with the legacy scalar-topographic internal overlap integral:

```text
{bhsm_overlap_kernel()}
```

with universal profile:

```text
{universal_profile()}
```

## 4. Why Strict Point Sampling Is Rank-Limited

```text
{sharp_peak_rank_bound()}
```

Strict point sampling gives an outer product. It cannot by itself generate a rank-three Yukawa matrix.

## 5. Finite-Width Profile And Local Coordinate Expansion

Using local coordinates `xi` around `y0`:

```text
{local_mode_expansion("A")}
```

```text
{local_mode_expansion("S")}
```

## 6. Moment Tensors Of The Universal Profile

```text
{moment_tensor_formula("M0")}
{moment_tensor_formula("Mab")}
{moment_tensor_formula("Mabcd")}
```

## 7. Finite-Width Overlap Expansion

```text
{moment_expansion_formula()}
```

The `M0` term is the strict point-sampling outer-product contribution. Higher finite-width moment terms can add independent matrix structures.

## 8. Rank-Three Condition

```text
{rank_three_condition()}
```

## 9. Internal Eigenfunction Independence Condition

```text
{internal_eigenfunction_independence_condition()}
```

This condition is not yet proven from BHSM eigenfunctions.

## 10. Universal Profile Width Guardrail

```text
{universal_width_guardrail()}
```

## 11. Status Of Rank-Three Derivation

Finite-width moments can in principle raise the rank, but this branch does not derive the required independence of the internal mode amplitudes and derivatives. Rank-three remains open.

## 12. Status Of Numerical Yukawa Values

Numerical Yukawa values are not derived in this branch.

## 13. Impact On Mass Hierarchy Theorem

The mass hierarchy theorem remains narrowed to deriving internal eigenfunctions, their derivatives near `y0`, and finite-width moment contractions without fitting measured fermion masses.

## 14. Impact On CKM/PMNS Theorem

CKM and PMNS values remain open because no numerical off-diagonal kernel values or diagonalization matrices are derived.

## 15. Non-Tautology Audit

See [Finite-Width Overlap Rank Non-Tautology Audit](finite_width_overlap_rank_non_tautology_audit.md).

## 16. What This Achieves

{_components_table()}

## 17. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until numerical overlap values, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, scalar potential numerics, and the full low-energy Lagrangian theorem are complete.

## Conclusion

{CONCLUSION_LANGUAGE}

## Verdict Labels

{chr(10).join(f"- `{label}`" for label in VERDICT_LABELS)}
"""


def render_moment_expansion_markdown() -> str:
    return f"""# Derived Finite-Width Overlap Moment Expansion

The finite-width scaffold expands the active and singlet internal modes around `y0` and contracts them with universal profile moments.

```text
{local_mode_expansion("A")}
{local_mode_expansion("S")}
```

Moment tensors:

```text
{moment_tensor_formula("M0")}
{moment_tensor_formula("Mab")}
{moment_tensor_formula("Mabcd")}
```

Finite-width expansion:

```text
{moment_expansion_formula()}
```

Status: `FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL`.
"""


def render_sharp_peak_limit_markdown() -> str:
    return f"""# Derived Sharp-Peak Outer Product Limit

```text
{sharp_peak_rank_bound()}
```

The `M0` or strict point-sampling term has the matrix form `I_ij=a_i^* b_j`, so it is an outer product. It is a leading focusing term only and does not derive rank three.

Status: `SHARP_PEAK_RANK_ONE_LIMIT_DERIVED_CONDITIONAL`.
"""


def render_rank_three_condition_markdown() -> str:
    return f"""# Derived Rank-Three Overlap Condition

```text
{rank_three_condition()}
```

The condition is structural: finite-width terms must supply at least three independent row/column structures after contraction with the universal profile moments. The condition is not asserted satisfied in this branch.

Status: `RANK_THREE_OVERLAP_CONDITION_DERIVED_CONDITIONAL`.
"""


def render_independence_condition_markdown() -> str:
    return f"""# Derived Internal Eigenfunction Independence Condition

```text
{internal_eigenfunction_independence_condition()}
```

This remains open because the repo does not yet contain a theorem computing the relevant Berger/BHSM internal eigenfunctions, their derivatives at `y0`, and their finite-width moment contractions.

Status: `INTERNAL_EIGENFUNCTION_INDEPENDENCE_REMAINS_OPEN`.
"""


def render_width_guardrail_markdown() -> str:
    return f"""# Derived Universal Profile Width Guardrail

```text
{universal_width_guardrail()}
```

The profile width cannot be chosen separately by flavor, generation, or matrix entry. Otherwise finite-width rank lifting would become a fitted Yukawa matrix ansatz instead of a BHSM derivation.

Status: `UNIVERSAL_PROFILE_WIDTH_GUARDRAIL_DERIVED_CONDITIONAL`.
"""


def render_rank_status_markdown() -> str:
    return """# Derived Finite-Width Overlap Rank Status

| item | status |
| --- | --- |
| strict point-sampling rank three | `False` |
| finite-width rank three derived | `False` |
| finite-width rank-three condition | `DERIVED_CONDITIONAL` |
| internal eigenfunction independence | `OPEN` |
| numerical Yukawa values | `OPEN` |

Verdict: finite-width moment scaffolding is derived conditionally, but rank-three Yukawa structure remains open.
"""


def render_rank_open_problem_markdown() -> str:
    return """# Derived Yukawa Rank-Three Open Problem

To promote the finite-width rank condition, BHSM still needs a theorem or computation showing that the universal-profile moment contractions of the internal eigenfunctions generate three independent matrix structures for each charged sector.

Open tasks:

- derive the internal Berger/BHSM eigenfunctions for the generation modes;
- compute amplitudes and derivatives near `y0`;
- compute finite-width profile moments from the internal metric;
- prove the contracted matrix structures span rank three;
- do all of the above without measured fermion masses or CKM/PMNS inputs.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("sharp-peak term", "outer-product rank <= 1", "rank-three matrix claim", "rank-three explicitly false", "pass", "finite-width terms"),
        ("moment expansion", "Taylor/moment scaffold", "fitted Yukawa entries", "symbolic moments only", "guarded", "compute geometric moments"),
        ("rank condition", "independent structures imply rank three", "known mass hierarchy", "condition not asserted satisfied", "guarded", "eigenfunction independence"),
        ("width guardrail", "single universal sigma", "flavor/generation tuning", "tuning forbidden", "pass", "derive sigma from geometry"),
        ("numerical values", "remain open", "measured masses or CKM/PMNS", "all numerical flags false", "pass", "full eigenfunction theorem"),
    ]
    lines = [
        "# Finite-Width Overlap Rank Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: The finite-width rank scaffold does not use measured masses, known Yukawa matrices, CKM values, or PMNS values as inputs. Rank-three remains open until internal eigenfunction independence is derived.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_finite_width_overlap_rank.md": render_main_markdown(),
        "derived_finite_width_overlap_moment_expansion.md": render_moment_expansion_markdown(),
        "derived_sharp_peak_outer_product_limit.md": render_sharp_peak_limit_markdown(),
        "derived_rank_three_overlap_condition.md": render_rank_three_condition_markdown(),
        "derived_internal_eigenfunction_independence_condition.md": render_independence_condition_markdown(),
        "derived_universal_profile_width_guardrail.md": render_width_guardrail_markdown(),
        "derived_finite_width_overlap_rank_status.md": render_rank_status_markdown(),
        "derived_yukawa_rank_three_open_problem.md": render_rank_open_problem_markdown(),
        "finite_width_overlap_rank_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_finite_width_overlap_rank_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
