from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-leading-axis-m-weight-v1"
STATUS = "partial_theorem_scaffold"
CANDIDATE_ASSIGNMENT = "m=n=q/2"


class LeadingAxisStatus(str, Enum):
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
class LeadingAxisLabel:
    sector: str
    index: int
    k: int
    ell: Fraction
    n: Fraction
    m: Fraction
    j: int


VERDICT_LABELS = [
    "PO_BH_28_LEADING_AXIS_M_WEIGHT_ASSIGNMENT_PARTIAL",
    "M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
    "LEADING_AXIS_ADMISSIBILITY_CONFIRMED",
    "Y0_AXIS_SAMPLING_REMAINS_OPEN",
    "EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN",
    "RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def k_from_qj(q: int, j: int) -> int:
    return q + 2 * j


def leading_axis_label(mode: ModeLabel) -> LeadingAxisLabel:
    k = k_from_qj(mode.q, mode.j)
    ell = Fraction(k, 2)
    n = Fraction(mode.q, 2)
    m = n
    return LeadingAxisLabel(mode.sector, mode.index, k, ell, n, m, mode.j)


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


def leading_axis_ledgers() -> dict[str, tuple[LeadingAxisLabel, ...]]:
    return {
        sector: tuple(leading_axis_label(mode) for mode in modes)
        for sector, modes in generation_modes().items()
    }


def admissible(label: LeadingAxisLabel) -> bool:
    if abs(label.m) > label.ell:
        return False
    if abs(label.n) > label.ell:
        return False
    if (label.ell - label.m).denominator != 1:
        return False
    if (label.ell - label.n).denominator != 1:
        return False
    return label.ell - label.n == label.j and label.ell - label.m == label.j


def all_leading_axis_labels_admissible() -> bool:
    return all(
        admissible(label)
        for labels in leading_axis_ledgers().values()
        for label in labels
    )


def candidate_harmonic_representative(label: LeadingAxisLabel) -> str:
    return f"D^({fraction_text(label.ell)})_({fraction_text(label.m)},{fraction_text(label.n)})"


def y0_axis_sampling_derived_from_repo() -> bool:
    return False


def leading_axis_m_assignment_derived() -> bool:
    return y0_axis_sampling_derived_from_repo() and all_leading_axis_labels_admissible()


def finite_width_rank_three_derived() -> bool:
    return False


def numerical_yukawa_values_derived() -> bool:
    return False


def ckm_values_derived() -> bool:
    return False


def pmns_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, str]:
    if leading_axis_m_assignment_derived():
        return {
            "PO-BH-28": "DERIVED_CONDITIONAL: y0 axis sampling selects m=n=q/2 for the leading focused harmonic component"
        }
    return {
        "PO-BH-28": (
            "PARTIAL: m=n=q/2 leading-axis assignment is admissible and "
            "structurally motivated; y0 axis-sampling derivation remains required"
        )
    }


def y0_axis_sampling_audit() -> tuple[dict[str, str | bool], ...]:
    return (
        {
            "route": "group identity",
            "repo_support": False,
            "status": LeadingAxisStatus.OPEN.value,
            "note": "The repo has symbolic y0 sampling but no theorem identifying y0 with the group identity.",
        },
        {
            "route": "north/south Hopf pole",
            "repo_support": False,
            "status": LeadingAxisStatus.OPEN.value,
            "note": "No theorem identifies y0 with a Hopf pole or proves pole sampling for Wigner labels.",
        },
        {
            "route": "squashed-axis focal point",
            "repo_support": False,
            "status": LeadingAxisStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "note": "The legacy overlap bridge gives a distinguished sharp-peak point y0, not an axis identity theorem.",
        },
        {
            "route": "generic internal point",
            "repo_support": True,
            "status": LeadingAxisStatus.PARTIAL.value,
            "note": "Current repo support treats y0 as a symbolic topographic sampling point.",
        },
    )


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def label_payload(label: LeadingAxisLabel) -> dict[str, str | int | bool]:
    return {
        "sector": label.sector,
        "index": label.index,
        "k": label.k,
        "j": label.j,
        "ell": fraction_text(label.ell),
        "n": fraction_text(label.n),
        "m": fraction_text(label.m),
        "ell_minus_n": fraction_text(label.ell - label.n),
        "ell_minus_m": fraction_text(label.ell - label.m),
        "admissible": admissible(label),
        "candidate_harmonic_representative": candidate_harmonic_representative(label),
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS if not leading_axis_m_assignment_derived() else "theorem_discharge_candidate",
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
        "leading_axis_m_weight_layer_completed": True,
        "y0_axis_sampling_derived": y0_axis_sampling_derived_from_repo(),
        "leading_axis_m_assignment_derived": leading_axis_m_assignment_derived(),
        "candidate_assignment": CANDIDATE_ASSIGNMENT,
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "y0_axis_sampling_audit": list(y0_axis_sampling_audit()),
        "leading_axis_ledgers": {
            sector: [label_payload(label) for label in labels]
            for sector, labels in leading_axis_ledgers().items()
        },
        "discharged_obligations": proof_discharge_ledger(),
        "still_open_downstream": [
            "derive y0 as Berger/Hopf identity axis or equivalent focal point",
            "derive Wigner/Hopf axis sampling rule in BHSM notation",
            "promote leading-axis m assignment",
            "explicit Berger/BHSM harmonic representatives",
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
            "leading-axis m assignment not promoted unless y0 axis sampling is derived",
            "finite-width rank-three not derived in this branch",
            "numerical Yukawa values not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
    }


def ledger_table() -> str:
    rows = [
        "| sector | index | k | ell | n | m | j | ell-n | ell-m | admissible |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for labels in leading_axis_ledgers().values():
        for label in labels:
            rows.append(
                "| "
                f"{label.sector} | {label.index} | {label.k} | {fraction_text(label.ell)} | "
                f"{fraction_text(label.n)} | {fraction_text(label.m)} | {label.j} | "
                f"{fraction_text(label.ell - label.n)} | {fraction_text(label.ell - label.m)} | "
                f"{admissible(label)} |"
            )
    return "\n".join(rows)


def y0_audit_table() -> str:
    rows = [
        "| route | repo support | status | note |",
        "| --- | --- | --- | --- |",
    ]
    for row in y0_axis_sampling_audit():
        rows.append(f"| {row['route']} | `{row['repo_support']}` | `{row['status']}` | {row['note']} |")
    return "\n".join(rows)


def representative_table() -> str:
    rows = [
        "| sector | index | representative | scope |",
        "| --- | ---: | --- | --- |",
    ]
    for labels in leading_axis_ledgers().values():
        for label in labels:
            rows.append(
                f"| {label.sector} | {label.index} | `{candidate_harmonic_representative(label)}` | leading-axis candidate only |"
            )
    return "\n".join(rows)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Leading-Axis M-Weight Assignment

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to test whether the leading focused component at the distinguished internal point `y0` fixes the remaining Wigner/base/orientation label `m`.

## 2. Previous Theorem Layers Achieved

PO-BH-27 conditionally derived `ell=k/2`, `n=q/2`, and `j=ell-n`.

## 3. PO-BH-27 Highest-Weight Normalization

The current candidate harmonic form is:

```text
D^ell_{{m,n}} = D^(k/2)_{{m,q/2}}
```

## 4. Why `m` Remains The Next Blocker

The `n` side of the Wigner label pair is fixed conditionally, but the `m` side is still required before explicit internal harmonics and local feature values can be computed.

## 5. The Role Of `y0`

Prior overlap layers use `y0` as a distinguished sharp-peak/topographic sampling point. They do not yet prove that `y0` is the group identity, Hopf pole, or equivalent Wigner axis.

## 6. Audit Of `y0` As Identity/Hopf Axis/Focal Point

{y0_audit_table()}

## 7. Wigner Identity-Axis Selection Rule

For a group identity axis one expects:

```text
D^ell_{{m,n}}(e)=delta_{{m,n}}
```

The repo does not yet contain the BHSM theorem identifying `y0` with this axis or translating the rule into the Berger/Hopf sampling setup.

## 8. Candidate Assignment `m=n`

Candidate leading-axis assignment:

```text
m=n
```

Status: `M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

## 9. Resulting Assignment `m=q/2`

Using PO-BH-27, the candidate leading component is:

```text
m=n=q/2
```

## 10. Admissibility Audit Across Frozen Ledgers

{ledger_table()}

## 11. Leading-Axis Harmonic Representatives

{representative_table()}

## 12. Scope: Leading Focused Component Only

This is only a leading-axis/focused-component scaffold. It does not supply finite-width corrections, transport, mixing, or rank-three support.

## 13. What Remains For Finite-Width Rank-Three

Finite-width moment contractions, independent local features, and off-diagonal transport/dressing terms remain open.

## 14. Numerical Yukawa Status

No numerical eigenfunction values, Yukawa values, mass ratios, CKM values, or PMNS values are derived here.

## 15. Non-Tautology Audit

The branch does not use measured masses, CKM values, PMNS values, or fitted residuals. It also does not promote `m=n` from admissibility alone.

## 16. What This Achieves

This branch records that `m=n=q/2` is an admissible leading-axis candidate on the frozen ledgers.

## 17. What Remains Before Full BHSM Replacement Claim

The next blocker is to derive `y0` as a Berger/Hopf identity axis or equivalent focal point and derive the corresponding Wigner/Hopf axis sampling rule in BHSM notation.

## Conclusion

This branch audits the candidate leading-axis m-weight assignment m=n=q/2. The assignment is admissible on the frozen ledgers, but it is not promoted because the repo does not yet support y0 as the Berger/Hopf identity axis or equivalent focal point and does not yet support the relevant Wigner/Hopf axis sampling rule. Explicit eigenfunctions, finite-width rank-three support, numerical Yukawa values, and replacement-level claims remain open.
"""


def simple_doc(title: str, body: str, status: str) -> str:
    return f"# {title}\n\n{body}\n\nStatus: `{status}`.\n"


def render_non_tautology() -> str:
    return """# Leading-Axis M-Weight Non-Tautology Audit

| item | uses | does not use | result | remaining obligation |
| --- | --- | --- | --- | --- |
| m=n candidate | Wigner identity-axis heuristic | masses, CKM, PMNS | structural candidate | derive y0 axis |
| admissibility | frozen mode labels | fitted mode removal | pass | prove sampling theorem |
| representative | D^(k/2)_(q/2,q/2) | eigenfunction values | candidate only | compute explicit harmonics |

Conclusion: No leading-axis m assignment is promoted unless y0 axis sampling is derived.
"""


def export_outputs(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "theorem_discharge_leading_axis_m_weight.md": render_main_markdown(),
        "derived_y0_axis_sampling_audit.md": "# Derived Y0 Axis Sampling Audit\n\n" + y0_audit_table() + "\n\nStatus: `Y0_AXIS_SAMPLING_REMAINS_OPEN`.\n",
        "derived_wigner_identity_axis_selection.md": simple_doc(
            "Derived Wigner Identity Axis Selection",
            "`D^ell_{m,n}(e)=delta_{m,n}` is the candidate identity-axis selection rule, but the BHSM `y0` axis identification remains open.",
            "Y0_AXIS_SAMPLING_REMAINS_OPEN",
        ),
        "derived_m_equals_n_leading_axis_assignment.md": simple_doc(
            "Derived M Equals N Leading Axis Assignment",
            "The candidate assignment `m=n` is structural unless `y0` is derived as the identity/axis sampling point.",
            "M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        ),
        "derived_m_equals_q_over_2_leading_component.md": simple_doc(
            "Derived M Equals Q Over 2 Leading Component",
            "Using PO-BH-27, the candidate leading component is `m=n=q/2`.",
            "M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        ),
        "derived_leading_axis_harmonic_representatives.md": "# Derived Leading Axis Harmonic Representatives\n\n" + representative_table() + "\n\nStatus: `LEADING_AXIS_REPRESENTATIVES_CANDIDATE_ONLY`.\n",
        "derived_leading_axis_admissibility_audit.md": "# Derived Leading Axis Admissibility Audit\n\n" + ledger_table() + "\n\nAll candidate labels satisfy `|m|<=ell`, `|n|<=ell`, `ell-m=j`, and `ell-n=j`.\n",
        "derived_leading_axis_to_feature_vector_bridge.md": simple_doc(
            "Derived Leading Axis To Feature Vector Bridge",
            "The leading feature-vector bridge may use `D^(k/2)_(q/2,q/2)` only after the `y0` axis sampling theorem is derived.",
            "FEATURE_VECTOR_BRIDGE_CANDIDATE_ONLY",
        ),
        "derived_leading_axis_m_weight_status.md": simple_doc(
            "Derived Leading Axis M Weight Status",
            "The candidate `m=n=q/2` assignment is admissible but not promoted in this branch.",
            "LEADING_AXIS_M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
        ),
        "leading_axis_m_weight_non_tautology_audit.md": render_non_tautology(),
    }
    for name, text in files.items():
        (theory / name).write_text(text, encoding="utf-8")
    (theory / "theorem_discharge_leading_axis_m_weight_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs()
