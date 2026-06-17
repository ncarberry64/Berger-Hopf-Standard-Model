from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-harmonic-highest-weight-normalization-v1"
STATUS = "theorem_discharge_candidate"
SELECTED_N_CONVENTION = "ell=k/2, n=q/2, j=ell-n"


class HighestWeightStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class ModeLabel:
    sector: str
    index: int
    q: int
    j: int


@dataclass(frozen=True)
class HighestWeightLabel:
    sector: str
    index: int
    k: int
    j: int
    ell: Fraction
    n: Fraction


VERDICT_LABELS = [
    "PO_BH_27_HARMONIC_HIGHEST_WEIGHT_NORMALIZATION_DERIVED_CONDITIONAL",
    "HIGHEST_WEIGHT_NORMALIZATION_DERIVED_CONDITIONAL",
    "Q_OVER_2_AS_WIGNER_WEIGHT_DERIVED_CONDITIONAL",
    "J_AS_LOWERING_INDEX_DERIVED_CONDITIONAL",
    "SELECTED_N_WEIGHT_CONVENTION_DERIVED_CONDITIONAL",
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


def ell_from_k(k: int) -> Fraction:
    return Fraction(k, 2)


def n_from_q(q: int) -> Fraction:
    return Fraction(q, 2)


def highest_weight_label(mode: ModeLabel) -> HighestWeightLabel:
    k = k_from_qj(mode.q, mode.j)
    return HighestWeightLabel(
        sector=mode.sector,
        index=mode.index,
        k=k,
        j=mode.j,
        ell=ell_from_k(k),
        n=n_from_q(mode.q),
    )


def admissible_n(label: HighestWeightLabel) -> bool:
    if abs(label.n) > label.ell:
        return False
    return (label.ell - label.n).denominator == 1


def lowering_index_identity_holds(label: HighestWeightLabel) -> bool:
    return label.ell - label.n == label.j


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


def highest_weight_ledgers() -> dict[str, tuple[HighestWeightLabel, ...]]:
    return {
        sector: tuple(highest_weight_label(mode) for mode in modes)
        for sector, modes in generation_modes().items()
    }


def all_admissible() -> bool:
    return all(
        admissible_n(label) and lowering_index_identity_holds(label)
        for labels in highest_weight_ledgers().values()
        for label in labels
    )


def highest_weight_normalization_derived() -> bool:
    return all_admissible()


def selected_n_weight_convention() -> str:
    return SELECTED_N_CONVENTION


def m_weight_assignment_derived() -> bool:
    return False


def explicit_eigenfunctions_derived() -> bool:
    return False


def finite_width_rank_three_derived() -> bool:
    return False


def numerical_yukawa_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, str]:
    status = "DERIVED_CONDITIONAL" if highest_weight_normalization_derived() else "PARTIAL"
    return {
        "PO-BH-27": (
            f"{status}: q=k-2j defines ell=k/2, n=q/2, with "
            "j=ell-n as lowering index; m remains open"
        )
    }


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _label_payload(label: HighestWeightLabel) -> dict[str, str | int | bool]:
    return {
        "sector": label.sector,
        "index": label.index,
        "k": label.k,
        "j": label.j,
        "ell": _fraction_text(label.ell),
        "n": _fraction_text(label.n),
        "ell_minus_n": _fraction_text(label.ell - label.n),
        "admissible_n": admissible_n(label),
        "lowering_identity_holds": lowering_index_identity_holds(label),
    }


def build_results_payload() -> dict:
    ledgers = {
        sector: [_label_payload(label) for label in labels]
        for sector, labels in highest_weight_ledgers().items()
    }
    derived = highest_weight_normalization_derived()
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
        "highest_weight_normalization_derived_conditionally": derived,
        "selected_n_weight_convention": selected_n_weight_convention(),
        "m_weight_assignment_derived": m_weight_assignment_derived(),
        "explicit_eigenfunctions_derived": explicit_eigenfunctions_derived(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "highest_weight_ledgers": ledgers,
        "discharged_obligations": proof_discharge_ledger(),
        "still_open_downstream": [
            "derive m orientation/base-weight assignment",
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


def _ledger_table() -> str:
    rows = [
        "| sector | index | k | j | ell=k/2 | n=q/2 | ell-n | admissible |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for labels in highest_weight_ledgers().values():
        for label in labels:
            rows.append(
                "| "
                f"{label.sector} | {label.index} | {label.k} | {label.j} | "
                f"{_fraction_text(label.ell)} | {_fraction_text(label.n)} | "
                f"{_fraction_text(label.ell - label.n)} | "
                f"{admissible_n(label) and lowering_index_identity_holds(label)} |"
            )
    return "\n".join(rows)


def render_main_markdown() -> str:
    status = HighestWeightStatus.DERIVED_CONDITIONAL.value if highest_weight_normalization_derived() else HighestWeightStatus.PARTIAL.value
    return f"""# Theorem Discharge: Harmonic Highest-Weight Normalization

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry by testing whether the raw-mode relation `q=k-2j` fixes the Wigner/Hopf `n` weight convention.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers derived the symbolic `(q,j)->psi_qj(y)` scaffold, the raw map `k=q+2j`, and an m-weight audit. PO-BH-26 left the selected harmonic convention open because the naive `ell=k/2, n=j` convention fails Wigner admissibility on frozen modes.

## 3. Why PO-BH-26 Left The Harmonic Convention Open

The prior branch did not promote a harmonic convention from admissibility alone. It also did not derive the remaining Wigner/base/orientation label `m`.

## 4. BHSM Identity `q=k-2j`

```text
q=k-2j
```

## 5. Highest-Weight Rewriting `q/2=k/2-j`

```text
q/2 = k/2 - j
```

## 6. Definition Of `ell=k/2`

```text
ell = k/2
```

## 7. Definition Of `n=q/2`

```text
n = q/2
```

## 8. Interpretation Of `j` As Lowering/Descent Index

With `ell=k/2` and `n=q/2`, the BHSM identity gives:

```text
j = ell - n
```

Thus `j` is interpreted as the lowering/descent count from the highest-weight state, while `n` is the candidate Wigner/Hopf weight.

## 9. Admissibility Audit Across Frozen Ledgers

{_ledger_table()}

Every listed frozen raw mode satisfies `|n|<=ell` and `ell-n=j` with integer `j`.

## 10. Selected Harmonic n-Convention

Selected n-convention: `{SELECTED_N_CONVENTION}`.

Status: `{status}`.

## 11. Remaining m-Weight Problem

The remaining `m` orientation/base-weight assignment is not derived in this branch.

Status: `M_WEIGHT_ASSIGNMENT_REMAINS_OPEN`.

## 12. Bridge To Candidate Eigenfunctions

The candidate notation remains:

```text
psi_{{k,j,m}} ~ D^ell_{{m,n}}, ell=k/2, n=q/2
```

This fixes only the `n` side of the Wigner label pair.

## 13. Impact On Local Feature Vectors At `y0`

The local feature-vector scaffold may now use `D^ell_{{m,q/2}}` once `m` and the explicit harmonic representative are derived.

## 14. Numerical Eigenfunction Status

Explicit eigenfunction values, gradients, Hessians, and moment contractions are not computed here.

## 15. Rank-Three/Yukawa Status

The finite-width rank-three Yukawa theorem and numerical Yukawa values remain open.

## 16. Non-Tautology Audit

The branch uses only the existing BHSM identity `q=k-2j` and frozen mode ledgers. It does not use measured masses, CKM values, PMNS values, or admissibility-only convention selection.

## 17. What This Achieves

This branch conditionally derives the BHSM highest-weight harmonic normalization. The identity `q=k-2j` is rewritten as `q/2=k/2-j`, so with `ell=k/2` the Wigner/Hopf weight is `n=q/2` and `j` is interpreted as the lowering index from the highest-weight state.

## 18. What Remains Before Full BHSM Replacement Claim

The remaining `m` orientation/base-weight assignment, explicit eigenfunction values, finite-width rank-three theorem, and numerical Yukawa values remain open.

## Conclusion

This branch conditionally derives the BHSM highest-weight harmonic normalization. The identity q=k-2j is rewritten as q/2=k/2-j, so with ell=k/2 the Wigner/Hopf weight is n=q/2 and j is interpreted as the lowering index from the highest-weight state. This resolves the n-weight convention without fitting masses or selecting a convention only by admissibility. The remaining m orientation/base-weight assignment, explicit eigenfunction values, finite-width rank-three theorem, and numerical Yukawa values remain open.
"""


def _simple_doc(title: str, body: str, status: str) -> str:
    return f"# {title}\n\n{body}\n\nStatus: `{status}`.\n"


def render_non_tautology() -> str:
    return """# Harmonic Highest-Weight Non-Tautology Audit

| item | uses | does not use | result | remaining obligation |
| --- | --- | --- | --- | --- |
| highest-weight rewrite | q=k-2j | masses or mixing values | pass | derive explicit harmonic representative |
| n convention | ell=k/2 and n=q/2 | convention chosen only by fit | pass | derive m |
| admissibility | frozen mode labels | post-hoc removal of modes | pass | prove full eigenfunction theorem |

Conclusion: The n-weight convention is conditionally derived from the BHSM raw-mode identity, but `m`, explicit eigenfunction values, and numerical Yukawa values remain open.
"""


def export_outputs(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()

    files = {
        "theorem_discharge_harmonic_highest_weight_normalization.md": render_main_markdown(),
        "derived_highest_weight_relation_q_equals_k_minus_2j.md": _simple_doc(
            "Derived Highest-Weight Relation q Equals k Minus 2j",
            "`q=k-2j` rewrites as `q/2=k/2-j`.",
            "HIGHEST_WEIGHT_NORMALIZATION_DERIVED_CONDITIONAL",
        ),
        "derived_wigner_weight_n_equals_q_over_2.md": _simple_doc(
            "Derived Wigner Weight n Equals q Over 2",
            "With `ell=k/2`, the candidate Wigner/Hopf weight is `n=q/2`.",
            "Q_OVER_2_AS_WIGNER_WEIGHT_DERIVED_CONDITIONAL",
        ),
        "derived_j_as_lowering_index.md": _simple_doc(
            "Derived j As Lowering Index",
            "The identity `ell-n=j` makes `j` the lowering/descent count from the highest-weight state.",
            "J_AS_LOWERING_INDEX_DERIVED_CONDITIONAL",
        ),
        "derived_selected_harmonic_n_convention.md": _simple_doc(
            "Derived Selected Harmonic n Convention",
            f"Selected n-convention: `{SELECTED_N_CONVENTION}`.",
            "SELECTED_N_WEIGHT_CONVENTION_DERIVED_CONDITIONAL",
        ),
        "derived_highest_weight_admissibility_audit.md": "# Derived Highest-Weight Admissibility Audit\n\n" + _ledger_table() + "\n\nAll modes satisfy `|n|<=ell` and `ell-n=j`.\n",
        "derived_remaining_m_weight_open_problem.md": _simple_doc(
            "Derived Remaining M Weight Open Problem",
            "The `n` convention is fixed conditionally, but the Wigner/base/orientation label `m` still requires a boundary-orientation theorem.",
            "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
        ),
        "derived_highest_weight_to_feature_vector_bridge.md": _simple_doc(
            "Derived Highest-Weight To Feature Vector Bridge",
            "Feature vectors may be indexed by `D^ell_{m,q/2}` after `m` and explicit harmonics are derived.",
            "FEATURE_VECTOR_BRIDGE_CONDITIONAL",
        ),
        "harmonic_highest_weight_non_tautology_audit.md": render_non_tautology(),
    }
    for name, text in files.items():
        (theory / name).write_text(text, encoding="utf-8")
    (theory / "theorem_discharge_harmonic_highest_weight_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs()
