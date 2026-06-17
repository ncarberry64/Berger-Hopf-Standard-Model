from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-raw-mode-berger-harmonic-map-v1"
STATUS = "partial_theorem_scaffold"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch refines the symbolic "
    "`(q,j)->psi_qj(y)` scaffold by using the existing BHSM relation `q=k-2j` "
    "to derive the raw-mode map `(q,j)->(k=q+2j,j)`."
)
CONCLUSION_LANGUAGE = (
    "This branch derives the raw-mode map `k=q+2j` from the existing BHSM "
    "definition `q=k-2j` and converts the generation ledgers into raw `(k,j)` "
    "mode labels. It identifies a candidate Berger/Hopf harmonic notation "
    "`psi_{k,j,m}` and records the structural interpretation of `j` as a "
    "candidate Hopf/fiber weight. The remaining orientation/base weight `m`, "
    "explicit eigenfunction values, finite-width rank-three support, numerical "
    "Yukawa values, and replacement-level claims remain open."
)


class HarmonicMapStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    STRUCTURALLY_MOTIVATED_NOT_DERIVED = "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class ModeLabel:
    sector: str
    index: int
    q: int
    j: int


@dataclass(frozen=True)
class RawModeLabel:
    sector: str
    index: int
    k: int
    j: int


@dataclass(frozen=True)
class HarmonicComponent:
    name: str
    statement: str
    status: str
    guardrail: str


VERDICT_LABELS = [
    "PO_BH_25_RAW_MODE_BERGER_HARMONIC_MAP_PARTIAL",
    "RAW_MODE_MAP_DERIVED_CONDITIONAL",
    "J_AS_HOPF_FIBER_WEIGHT_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
    "BERGER_HARMONIC_FORM_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
    "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
    "EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN",
    "RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def k_from_qj(q: int, j: int) -> int:
    return q + 2 * j


def raw_mode(mode: ModeLabel) -> RawModeLabel:
    return RawModeLabel(mode.sector, mode.index, k_from_qj(mode.q, mode.j), mode.j)


def generation_modes() -> dict[str, tuple[ModeLabel, ...]]:
    return {
        "reference_charged": (
            ModeLabel("reference_charged", 0, 0, 0),
            ModeLabel("reference_charged", 1, 1, 2),
            ModeLabel("reference_charged", 2, 3, 3),
        ),
        "reference_neutral": (
            ModeLabel("reference_neutral", 0, 0, 0),
            ModeLabel("reference_neutral", 1, 3, 0),
            ModeLabel("reference_neutral", 2, 1, 1),
        ),
        "cyclic_upper": (
            ModeLabel("cyclic_upper", 0, 0, 0),
            ModeLabel("cyclic_upper", 1, 6, 0),
            ModeLabel("cyclic_upper", 2, 8, 1),
        ),
        "cyclic_lower": (
            ModeLabel("cyclic_lower", 0, 0, 0),
            ModeLabel("cyclic_lower", 1, 0, 3),
            ModeLabel("cyclic_lower", 2, 4, 2),
        ),
    }


def raw_mode_ledgers() -> dict[str, tuple[RawModeLabel, ...]]:
    return {sector: tuple(raw_mode(mode) for mode in modes) for sector, modes in generation_modes().items()}


def raw_mode_map_formula() -> str:
    return "raw_mode(q,j)=(k,j)=(q+2j,j)"


def candidate_berger_harmonic_form() -> str:
    return "psi_{k,j,m}(alpha,beta,gamma) ~ D^{k/2}_{m,j}(alpha,beta,gamma)"


def candidate_berger_harmonic_factorized_form() -> str:
    return "psi_{k,j,m}(alpha,beta,gamma) ~ exp(i m alpha) d^{k/2}_{m,j}(beta) exp(i j gamma)"


def j_fiber_weight_status() -> str:
    return HarmonicMapStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value


def berger_harmonic_form_status() -> str:
    return HarmonicMapStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value


def m_weight_assignment_derived() -> bool:
    return False


def explicit_eigenfunctions_derived() -> bool:
    return False


def numerical_yukawa_values_derived() -> bool:
    return False


def finite_width_rank_three_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def m_weight_candidate_sources() -> tuple[str, ...]:
    return (
        "active/singlet side",
        "weak orientation",
        "T3",
        "charge closure",
        "sector label",
        "boundary orientation algebra",
        "scalar insertion H or H_tilde",
        "cyclic/reference channel",
        "left/right chirality",
    )


def raw_mode_feature_bridge() -> str:
    return "F_{k,j,m}(y0)=(psi, d_a psi, d_a d_b psi)|_{y0}"


def proof_discharge_ledger() -> dict[str, str]:
    return {
        "PO-BH-25": (
            "PARTIAL: raw-mode map k=q+2j derived; candidate Berger/Hopf "
            "harmonic form identified; m-weight assignment and explicit "
            "eigenfunction values remain open"
        )
    }


def harmonic_components() -> tuple[HarmonicComponent, ...]:
    return (
        HarmonicComponent(
            "raw_mode_map",
            raw_mode_map_formula(),
            "RAW_MODE_MAP_DERIVED_CONDITIONAL",
            "direct algebraic inversion of q=k-2j",
        ),
        HarmonicComponent(
            "j_fiber_weight",
            "j is structurally consistent with a Hopf/fiber harmonic weight",
            "J_AS_HOPF_FIBER_WEIGHT_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
            "repo lacks a full harmonic theorem fixing conventions",
        ),
        HarmonicComponent(
            "candidate_harmonic_form",
            candidate_berger_harmonic_form(),
            "BERGER_HARMONIC_FORM_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
            "notation only; explicit eigenfunctions not derived",
        ),
        HarmonicComponent(
            "m_weight_assignment",
            "m must be fixed by orientation/base-weight structure",
            "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
            "m is not guessed or fitted",
        ),
        HarmonicComponent(
            "feature_bridge",
            raw_mode_feature_bridge(),
            "RAW_MODE_TO_FEATURE_VECTOR_BRIDGE_DERIVED_CONDITIONAL",
            "symbolic local features only",
        ),
    )


def _raw_ledgers_payload() -> dict[str, list[dict[str, int | str]]]:
    return {
        sector: [
            {
                "sector": mode.sector,
                "index": mode.index,
                "k": mode.k,
                "j": mode.j,
                "candidate_harmonic": f"psi_{{{mode.k},{mode.j},m}}(y)",
            }
            for mode in modes
        ]
        for sector, modes in raw_mode_ledgers().items()
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
        "raw_mode_map_completed": True,
        "raw_mode_map_formula": "k=q+2j",
        "candidate_harmonic_form": candidate_berger_harmonic_form(),
        "candidate_harmonic_factorized_form": candidate_berger_harmonic_factorized_form(),
        "j_fiber_weight_derived": False,
        "j_fiber_weight_status": j_fiber_weight_status(),
        "berger_harmonic_form_status": berger_harmonic_form_status(),
        "m_weight_assignment_derived": m_weight_assignment_derived(),
        "explicit_eigenfunctions_derived": explicit_eigenfunctions_derived(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "discharged_obligations": proof_discharge_ledger(),
        "qj_ledgers": {
            sector: [mode.__dict__ for mode in modes] for sector, modes in generation_modes().items()
        },
        "raw_mode_ledgers": _raw_ledgers_payload(),
        "m_weight_candidate_sources": list(m_weight_candidate_sources()),
        "still_open_downstream": [
            "derive j as Hopf/fiber weight from BHSM geometry",
            "derive m-weight assignment",
            "explicit Berger/BHSM harmonic theorem",
            "eigenfunction amplitudes at y0",
            "finite-width moment contractions",
            "rank-three Yukawa matrix theorem",
            "numerical Yukawa coupling theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "m-weight assignment not derived in this branch",
            "explicit eigenfunction values not derived in this branch",
            "rank-three Yukawa theorem not derived in this branch",
            "numerical Yukawa values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
    }


def _raw_table() -> str:
    lines = ["| sector | index | q | j | k=q+2j | raw `(k,j)` |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for sector, modes in generation_modes().items():
        for mode in modes:
            raw = raw_mode(mode)
            lines.append(f"| {sector} | {mode.index} | {mode.q} | {mode.j} | {raw.k} | `({raw.k},{raw.j})` |")
    return "\n".join(lines)


def _component_table() -> str:
    lines = ["| component | statement | status | guardrail |", "| --- | --- | --- | --- |"]
    for component in harmonic_components():
        lines.append(f"| {component.name} | `{component.statement}` | `{component.status}` | {component.guardrail} |")
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Raw-Mode Berger Harmonic Map

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the geometric overlap kernel, finite-width rank scaffold, and symbolic `(q,j)->psi_qj(y)` eigenfunction map scaffold.

## 3. Why PO-BH-24 Left The Explicit Eigenfunction Map Open

PO-BH-24 defined symbolic `psi_qj(y)` labels but did not connect them to raw Berger/Hopf harmonic labels or fix the remaining orientation/base weight.

## 4. The BHSM Relation `q=k-2j`

The existing BHSM Hopf charge relation is:

```text
q=k-2j
```

## 5. Raw-Mode Map `k=q+2j`

```text
{raw_mode_map_formula()}
```

## 6. Generation Ledgers In `q,j` And Raw `k,j` Form

{_raw_table()}

## 7. Candidate Berger/Hopf Harmonic Interpretation

```text
{candidate_berger_harmonic_form()}
{candidate_berger_harmonic_factorized_form()}
```

## 8. Audit Of `j` As Hopf/Fiber Weight

`j` is structurally compatible with the fiber-side index in the candidate harmonic notation, but this is not promoted to a completed harmonic theorem.

## 9. The Remaining `m` Orientation/Base-Weight Problem

`m` remains open and is not guessed.

## 10. Candidate Sources For `m`

{chr(10).join(f"- {source}" for source in m_weight_candidate_sources())}

## 11. Bridge To Local Feature Vectors At `y0`

```text
{raw_mode_feature_bridge()}
```

## 12. Numerical Eigenfunction Status

Explicit eigenfunction values are not derived.

## 13. Rank-Three/Yukawa Status

Finite-width rank three and numerical Yukawa values remain open.

## 14. Non-Tautology Audit

See [Raw-Mode Berger Harmonic Non-Tautology Audit](raw_mode_berger_harmonic_non_tautology_audit.md).

## 15. What This Achieves

{_component_table()}

## 16. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until `m`, explicit eigenfunctions, feature values, moment contractions, numerical Yukawa values, mixing values, and the full low-energy Lagrangian theorem are derived.

## Conclusion

{CONCLUSION_LANGUAGE}

## Verdict Labels

{chr(10).join(f"- `{label}`" for label in VERDICT_LABELS)}
"""


def render_simple_doc(title: str, body: str, status: str) -> str:
    return f"# {title}\n\n{body}\n\nStatus: `{status}`.\n"


def render_non_tautology() -> str:
    rows = [
        ("raw mode map", "k=q+2j", "mass data", "algebraic inversion of q=k-2j", "pass", "none for raw map"),
        ("candidate harmonic form", "Wigner/Hopf notation", "invented eigenfunctions", "kept structurally motivated", "guarded", "derive harmonic theorem"),
        ("j fiber weight", "structural compatibility", "convention overclaim", "not marked derived", "guarded", "fix conventions"),
        ("m assignment", "open orientation/base weight", "guessed m", "explicitly open", "pass", "derive m source"),
        ("numerics", "remain open", "measured masses or mixing", "all numerical flags false", "pass", "compute eigenfunctions"),
    ]
    lines = [
        "# Raw-Mode Berger Harmonic Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: The raw-mode map uses the existing BHSM charge relation and does not import measured masses, known Yukawa matrices, CKM values, or PMNS values.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    docs = {
        "theorem_discharge_raw_mode_berger_harmonic_map.md": render_main_markdown(),
        "derived_raw_mode_map_k_equals_q_plus_2j.md": render_simple_doc(
            "Derived Raw Mode Map K Equals Q Plus 2J",
            f"`q=k-2j` implies `{raw_mode_map_formula()}`.",
            "RAW_MODE_MAP_DERIVED_CONDITIONAL",
        ),
        "derived_generation_raw_mode_ledgers.md": render_simple_doc(
            "Derived Generation Raw Mode Ledgers",
            _raw_table(),
            "RAW_MODE_MAP_DERIVED_CONDITIONAL",
        ),
        "derived_candidate_berger_hopf_harmonic_form.md": render_simple_doc(
            "Derived Candidate Berger Hopf Harmonic Form",
            f"```text\n{candidate_berger_harmonic_form()}\n{candidate_berger_harmonic_factorized_form()}\n```\n\nThis is structurally motivated notation, not a completed harmonic theorem.",
            "BERGER_HARMONIC_FORM_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        ),
        "derived_j_fiber_weight_audit.md": render_simple_doc(
            "Derived J Fiber Weight Audit",
            "`j` is structurally compatible with the candidate Hopf/fiber harmonic weight, but the repo does not yet derive the full convention from Berger-Hopf geometry.",
            "J_AS_HOPF_FIBER_WEIGHT_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        ),
        "derived_m_weight_assignment_open_problem.md": render_simple_doc(
            "Derived M Weight Assignment Open Problem",
            "`m` must be fixed by existing BHSM structure, not guessed. Candidate sources:\n\n" + "\n".join(f"- {s}" for s in m_weight_candidate_sources()),
            "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
        ),
        "derived_raw_mode_to_feature_vector_bridge.md": render_simple_doc(
            "Derived Raw Mode To Feature Vector Bridge",
            f"```text\n{raw_mode_feature_bridge()}\n```\n\nThe bridge is symbolic; explicit feature values remain open.",
            "RAW_MODE_TO_FEATURE_VECTOR_BRIDGE_DERIVED_CONDITIONAL",
        ),
        "derived_raw_mode_harmonic_map_status.md": render_simple_doc(
            "Derived Raw Mode Harmonic Map Status",
            "\n".join(
                [
                    "| item | status |",
                    "| --- | --- |",
                    "| raw mode map | `DERIVED_CONDITIONAL` |",
                    "| j fiber-weight interpretation | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` |",
                    "| Berger harmonic form | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` |",
                    "| m assignment | `OPEN` |",
                    "| explicit eigenfunction values | `OPEN` |",
                    "| finite-width rank three | `False` |",
                ]
            ),
            "PO_BH_25_RAW_MODE_BERGER_HARMONIC_MAP_PARTIAL",
        ),
        "raw_mode_berger_harmonic_non_tautology_audit.md": render_non_tautology(),
        "theorem_discharge_raw_mode_berger_harmonic_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in docs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
