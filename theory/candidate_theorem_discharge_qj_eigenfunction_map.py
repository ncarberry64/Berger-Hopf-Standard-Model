from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-qj-eigenfunction-map-v1"
STATUS = "partial_theorem_scaffold"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch sharpens the "
    "finite-width overlap-rank blocker by isolating the missing non-fitted map "
    "from generation labels `(q,j)` to internal Berger/BHSM eigenfunctions."
)
CONCLUSION_LANGUAGE = (
    "This branch derives the symbolic scaffold for the missing BHSM map from "
    "generation labels (q,j) to internal Berger/BHSM eigenfunctions psi_qj(y). "
    "The branch identifies local values, gradients, Hessians, and finite-width "
    "moment contractions as the required data for proving diagonal hierarchy "
    "support and full rank-three Yukawa support. Because an explicit "
    "theorem-derived eigenfunction map and evaluated local feature independence "
    "are not derived in this branch, numerical Yukawa values, fermion mass "
    "ratios, CKM values, PMNS values, and replacement-level claims remain open."
)


class EigenfunctionMapStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    SCAFFOLD_DERIVED_CONDITIONAL = "SCAFFOLD_DERIVED_CONDITIONAL"
    PARTIAL = "PARTIAL"
    OPEN = "OPEN"


@dataclass(frozen=True)
class GenerationMode:
    sector: str
    index: int
    q: int
    j: int


@dataclass(frozen=True)
class MapComponent:
    name: str
    statement: str
    status: str
    guardrail: str


VERDICT_LABELS = [
    "PO_BH_24_QJ_TO_INTERNAL_EIGENFUNCTION_MAP_PARTIAL",
    "QJ_EIGENFUNCTION_MAP_SCAFFOLD_DERIVED_CONDITIONAL",
    "INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL",
    "DIAGONAL_HIERARCHY_ROUTE_IDENTIFIED_CONDITIONAL",
    "FULL_RANK_THREE_ROUTE_CONDITION_DERIVED_CONDITIONAL",
    "QJ_TO_BERGER_EIGENFUNCTION_MAP_REMAINS_OPEN",
    "INTERNAL_FEATURE_INDEPENDENCE_REMAINS_OPEN",
    "RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def generation_modes() -> dict[str, tuple[GenerationMode, ...]]:
    return {
        "reference_charged": (
            GenerationMode("reference_charged", 0, 0, 0),
            GenerationMode("reference_charged", 1, 1, 2),
            GenerationMode("reference_charged", 2, 3, 3),
        ),
        "reference_neutral": (
            GenerationMode("reference_neutral", 0, 0, 0),
            GenerationMode("reference_neutral", 1, 3, 0),
            GenerationMode("reference_neutral", 2, 1, 1),
        ),
        "cyclic_upper": (
            GenerationMode("cyclic_upper", 0, 0, 0),
            GenerationMode("cyclic_upper", 1, 6, 0),
            GenerationMode("cyclic_upper", 2, 8, 1),
        ),
        "cyclic_lower": (
            GenerationMode("cyclic_lower", 0, 0, 0),
            GenerationMode("cyclic_lower", 1, 0, 3),
            GenerationMode("cyclic_lower", 2, 4, 2),
        ),
    }


def symbolic_eigenfunction(mode: GenerationMode) -> str:
    return f"psi_q{mode.q}_j{mode.j}(y)"


def qj_to_eigenfunction_map() -> str:
    return "E:(q,j)->psi_qj(y)"


def qj_to_eigenfunction_map_status() -> str:
    return EigenfunctionMapStatus.SCAFFOLD_DERIVED_CONDITIONAL.value


def local_feature_vector(mode: GenerationMode) -> tuple[str, ...]:
    psi = symbolic_eigenfunction(mode)
    return (
        f"{psi}|_y0",
        f"d1 {psi}|_y0",
        f"d2 {psi}|_y0",
        f"d3 {psi}|_y0",
        f"d11 {psi}|_y0",
        f"d12 {psi}|_y0",
        f"d13 {psi}|_y0",
        f"d22 {psi}|_y0",
        f"d23 {psi}|_y0",
        f"d33 {psi}|_y0",
    )


def finite_width_moment_feature_contraction() -> str:
    return "I_ij=M0 A_i^* S_j + M_ab G_A_i^{a*} G_S_j^b + M_abcd H_A_i^{ab*} H_S_j^{cd} + ..."


def diagonal_hierarchy_route() -> str:
    return "diagonal hierarchy may arise from generation-dependent singlet/internal amplitudes or diagonal finite-width overlaps"


def full_rank_three_route() -> str:
    return "full rank-three matrix requires derived active-mode structure, delta_ij channel selection, finite-width moment independence, or boundary transport/dressing"


def rank_three_support_condition() -> str:
    return "rank-three support requires three generation feature vectors to remain independent under universal finite-width moment contractions"


def explicit_qj_eigenfunction_map_derived() -> bool:
    return False


def internal_feature_independence_derived() -> bool:
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
        "PO-BH-24": (
            "PARTIAL: symbolic (q,j)->psi_qj(y) eigenfunction map scaffold and "
            "feature-rank condition derived; explicit map and rank-three "
            "independence remain open unless found elsewhere in the repo"
        )
    }


def map_components() -> tuple[MapComponent, ...]:
    return (
        MapComponent(
            "qj_symbolic_map",
            qj_to_eigenfunction_map(),
            "QJ_EIGENFUNCTION_MAP_SCAFFOLD_DERIVED_CONDITIONAL",
            "symbolic scaffold only; explicit Berger eigenfunctions remain open",
        ),
        MapComponent(
            "local_feature_vectors",
            "F_n=(value, gradient, Hessian components at y0)",
            "INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL",
            "features are symbolic, not evaluated",
        ),
        MapComponent(
            "diagonal_hierarchy_route",
            diagonal_hierarchy_route(),
            "DIAGONAL_HIERARCHY_ROUTE_IDENTIFIED_CONDITIONAL",
            "hierarchy route is not a full rank-three matrix theorem",
        ),
        MapComponent(
            "full_rank_three_route",
            full_rank_three_route(),
            "FULL_RANK_THREE_ROUTE_CONDITION_DERIVED_CONDITIONAL",
            "condition is not asserted satisfied",
        ),
        MapComponent(
            "rank_three_support_condition",
            rank_three_support_condition(),
            "INTERNAL_FEATURE_INDEPENDENCE_REMAINS_OPEN",
            "requires explicit eigenfunction independence proof",
        ),
    )


def _modes_payload() -> dict[str, list[dict[str, int | str]]]:
    return {
        sector: [
            {
                "sector": mode.sector,
                "index": mode.index,
                "q": mode.q,
                "j": mode.j,
                "symbolic_eigenfunction": symbolic_eigenfunction(mode),
                "feature_vector": list(local_feature_vector(mode)),
            }
            for mode in modes
        ]
        for sector, modes in generation_modes().items()
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
        "qj_eigenfunction_map_scaffold_completed": True,
        "explicit_qj_eigenfunction_map_derived": explicit_qj_eigenfunction_map_derived(),
        "internal_feature_independence_derived": internal_feature_independence_derived(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "fermion_mass_ratios_derived": fermion_mass_ratios_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "discharged_obligations": proof_discharge_ledger(),
        "mode_ledgers": _modes_payload(),
        "formulas": {
            "qj_to_eigenfunction_map": qj_to_eigenfunction_map(),
            "finite_width_moment_feature_contraction": finite_width_moment_feature_contraction(),
            "diagonal_hierarchy_route": diagonal_hierarchy_route(),
            "full_rank_three_route": full_rank_three_route(),
            "rank_three_support_condition": rank_three_support_condition(),
        },
        "routes": {
            "diagonal_hierarchy_route": "generation-dependent singlet/internal amplitudes or diagonal finite-width overlaps may support hierarchy scaffolding",
            "full_rank_three_route": "requires derived active-mode structure, delta_ij channel selection, finite-width moment independence, or boundary transport/dressing",
        },
        "map_components": [
            {
                "name": component.name,
                "statement": component.statement,
                "status": component.status,
                "guardrail": component.guardrail,
            }
            for component in map_components()
        ],
        "still_open_downstream": [
            "explicit Berger/BHSM internal eigenfunction theorem",
            "qj-to-eigenfunction map",
            "eigenfunction amplitudes at y0",
            "eigenfunction gradient and Hessian values near y0",
            "finite-width moment contractions",
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
            "explicit qj-to-eigenfunction map not derived in this branch",
            "internal feature independence not promoted without explicit eigenfunction structure",
            "finite-width rank-three not promoted without independence proof",
            "numerical Yukawa values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "repo search found no completed theorem-derived Wigner/Hopf/Berger eigenfunction machinery",
            "diagonal hierarchy route is separated from full rank-three route",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _mode_table() -> str:
    lines = ["| sector | index | q | j | symbolic eigenfunction |", "| --- | ---: | ---: | ---: | --- |"]
    for sector, modes in generation_modes().items():
        for mode in modes:
            lines.append(f"| {sector} | {mode.index} | {mode.q} | {mode.j} | `{symbolic_eigenfunction(mode)}` |")
    return "\n".join(lines)


def _components_table() -> str:
    lines = ["| component | statement | status | guardrail |", "| --- | --- | --- | --- |"]
    for component in map_components():
        lines.append(
            f"| {component.name} | `{component.statement}` | `{component.status}` | {component.guardrail} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: QJ To Internal Eigenfunction Map

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the closure spectrum, finite boundary algebra, charge operators, gauge skeletons, scalar doublet, Yukawa operator closure, symbolic Yukawa matrix scaffolds, overlap-kernel selection rules, distance diagnostics, the legacy geometric-overlap kernel bridge, and the finite-width rank condition.

## 3. PO-BH-23 Rank Condition

PO-BH-23 derived the symbolic condition that finite-width moment terms can lift the rank if independent internal feature structures exist. It did not prove the required internal eigenfunction independence.

## 4. Why `(q,j) -> psi_qj(y)` Is The Next Blocker

The finite-width rank condition cannot be tested until the generation labels `(q,j)` are mapped to actual internal Berger/BHSM eigenfunctions or harmonics.

## 5. BHSM Generation Mode Ledgers

{_mode_table()}

## 6. Candidate/Internal Eigenfunction Map

```text
{qj_to_eigenfunction_map()}
```

Status: `{qj_to_eigenfunction_map_status()}`. This is a symbolic scaffold, not an explicit Wigner/Hopf/Berger eigenfunction theorem.

## 7. Local Value/Gradient/Hessian Data At `y0`

For each mode, the required data are value, gradient, and Hessian components at `y0`.

## 8. Finite-Width Feature Vectors

```text
F_n = [psi_n(y0), d1 psi_n(y0), d2 psi_n(y0), d3 psi_n(y0), d11 psi_n(y0), d12 psi_n(y0), d13 psi_n(y0), d22 psi_n(y0), d23 psi_n(y0), d33 psi_n(y0)]
```

## 9. Diagonal Hierarchy Route

```text
{diagonal_hierarchy_route()}
```

## 10. Full Rank-Three Matrix Route

```text
{full_rank_three_route()}
```

## 11. Internal Feature Independence Condition

```text
{rank_three_support_condition()}
```

## 12. Numerical Eigenfunction Status

Explicit eigenfunctions, local amplitudes, gradients, Hessians, and moment contractions are not computed in this branch.

## 13. Impact On Yukawa Values

Numerical Yukawa values remain open.

## 14. Impact On CKM/PMNS

CKM and PMNS values remain open because no numerical off-diagonal kernel values or diagonalization matrices are derived.

## 15. Non-Tautology Audit

See [QJ Eigenfunction Map Non-Tautology Audit](qj_eigenfunction_map_non_tautology_audit.md).

## 16. What This Achieves

{_components_table()}

## 17. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until explicit internal eigenfunctions, finite-width moment contractions, numerical Yukawa values, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, scalar potential numerics, and the full low-energy Lagrangian theorem are complete.

## Conclusion

{CONCLUSION_LANGUAGE}

## Verdict Labels

{chr(10).join(f"- `{label}`" for label in VERDICT_LABELS)}
"""


def render_qj_map_markdown() -> str:
    return f"""# Derived QJ To Internal Eigenfunction Map

```text
{qj_to_eigenfunction_map()}
```

Mode ledger:

{_mode_table()}

This branch defines the symbolic map needed by later theorem layers. It does not derive explicit Berger/BHSM eigenfunction formulas.

Status: `QJ_EIGENFUNCTION_MAP_SCAFFOLD_DERIVED_CONDITIONAL`.
"""


def render_mode_scaffold_markdown() -> str:
    lines = ["# Derived Internal Eigenfunction Mode Scaffold", ""]
    for sector, modes in generation_modes().items():
        lines.append(f"## {sector}")
        for mode in modes:
            lines.append(f"- generation `{mode.index}`: `(q,j)=({mode.q},{mode.j}) -> {symbolic_eigenfunction(mode)}`")
        lines.append("")
    lines.append("Status: `INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL`.")
    return "\n".join(lines)


def render_local_features_markdown() -> str:
    sample = generation_modes()["cyclic_upper"][1]
    lines = [
        "# Derived Internal Local Feature Vectors",
        "",
        "Feature vector template:",
        "",
        "```text",
        "\n".join(local_feature_vector(sample)),
        "```",
        "",
        "Each vector contains one value, three gradient components, and six Hessian components at `y0`.",
        "",
        "Status: `INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL`.",
    ]
    return "\n".join(lines) + "\n"


def render_diagonal_route_markdown() -> str:
    return f"""# Derived Diagonal Hierarchy Route

```text
{diagonal_hierarchy_route()}
```

This route may support diagonal hierarchy scaffolding. It does not by itself prove a full unrestricted rank-three Yukawa matrix because it can be compatible with generation-aligned or diagonal-only structures.

Status: `DIAGONAL_HIERARCHY_ROUTE_IDENTIFIED_CONDITIONAL`.
"""


def render_full_rank_route_markdown() -> str:
    return f"""# Derived Full Rank-Three Route

```text
{full_rank_three_route()}
```

This branch does not prove that any one of these mechanisms is satisfied. It records the required mechanism list and keeps rank-three open.

Status: `FULL_RANK_THREE_ROUTE_CONDITION_DERIVED_CONDITIONAL`.
"""


def render_feature_independence_markdown() -> str:
    return f"""# Derived Internal Feature Independence Condition

```text
{rank_three_support_condition()}
```

The condition is not promoted because explicit theorem-derived eigenfunctions and local feature values are not present.

Status: `INTERNAL_FEATURE_INDEPENDENCE_REMAINS_OPEN`.
"""


def render_moment_contractions_markdown() -> str:
    return f"""# Derived Finite-Width Moment Feature Contractions

```text
{finite_width_moment_feature_contraction()}
```

The formula restates the PO-BH-23 finite-width scaffold using local value, gradient, and Hessian feature symbols. No numerical moment contractions are computed.

Status: `FINITE_WIDTH_MOMENT_FEATURE_CONTRACTIONS_SCAFFOLD_DERIVED_CONDITIONAL`.
"""


def render_map_status_markdown() -> str:
    return """# Derived QJ Eigenfunction Map Status

| item | status |
| --- | --- |
| symbolic `(q,j)->psi_qj(y)` scaffold | `SCAFFOLD_DERIVED_CONDITIONAL` |
| explicit Berger/BHSM eigenfunction map | `OPEN` |
| internal feature independence | `OPEN` |
| finite-width rank three | `False` |
| numerical Yukawa values | `OPEN` |

Verdict: PO-BH-24 is partial. The scaffold is in place, but the explicit eigenfunction map remains open.
"""


def render_numerical_open_problem_markdown() -> str:
    return """# Derived Internal Eigenfunction Numerical Open Problem

To promote this theorem layer, BHSM must derive explicit internal eigenfunctions `psi_qj(y)` for the generation modes, evaluate their values, gradients, and Hessians at `y0`, and compute finite-width moment contractions under the universal profile.

The computation must not use measured fermion masses, known Yukawa matrices, CKM values, or PMNS values as inputs.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("mode ledger", "fixed q,j ledgers", "measured masses", "uses existing BHSM ledgers only", "pass", "derive explicit eigenfunctions"),
        ("symbolic eigenfunction map", "E:(q,j)->psi_qj(y)", "invented formulas", "keeps explicit formulas open", "guarded", "Berger/BHSM eigenfunction theorem"),
        ("local features", "value/gradient/Hessian scaffold", "known hierarchy", "no numerical values inserted", "pass", "compute local features"),
        ("diagonal route", "amplitude sampling route", "full rank-three claim", "kept separate from full matrix route", "pass", "diagonal hierarchy theorem"),
        ("full rank-three route", "feature independence condition", "known CKM/PMNS", "not promoted", "guarded", "independence proof"),
        ("numerical values", "remain open", "measured masses or mixing", "all numerical flags false", "pass", "eigenfunction/moment calculation"),
    ]
    lines = [
        "# QJ Eigenfunction Map Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: The scaffold does not use measured masses, known Yukawa matrices, CKM values, or PMNS values. The explicit eigenfunction map and feature independence remain open.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_qj_eigenfunction_map.md": render_main_markdown(),
        "derived_qj_to_internal_eigenfunction_map.md": render_qj_map_markdown(),
        "derived_internal_eigenfunction_mode_scaffold.md": render_mode_scaffold_markdown(),
        "derived_internal_local_feature_vectors.md": render_local_features_markdown(),
        "derived_diagonal_hierarchy_route.md": render_diagonal_route_markdown(),
        "derived_full_rank_three_route.md": render_full_rank_route_markdown(),
        "derived_internal_feature_independence_condition.md": render_feature_independence_markdown(),
        "derived_finite_width_moment_feature_contractions.md": render_moment_contractions_markdown(),
        "derived_qj_eigenfunction_map_status.md": render_map_status_markdown(),
        "derived_internal_eigenfunction_numerical_open_problem.md": render_numerical_open_problem_markdown(),
        "qj_eigenfunction_map_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_qj_eigenfunction_map_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
