from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-m-multiplet-harmonic-features-v1"
STATUS = "theorem_discharge_candidate"


class MultipletStatus(str, Enum):
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
class MultipletLabel:
    sector: str
    index: int
    k: int
    ell: Fraction
    n: Fraction
    m_values: tuple[Fraction, ...]


VERDICT_LABELS = [
    "PO_BH_30_M_MULTIPLET_HARMONIC_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL",
    "M_MULTIPLET_SCAFFOLD_DERIVED_CONDITIONAL",
    "AXIS_COLLAPSE_CASE_DOCUMENTED",
    "GENERIC_Y0_WIGNER_EVALUATION_CASE_DOCUMENTED",
    "FINITE_WIDTH_RANK_THREE_REMAINS_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
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


def allowed_m_values(ell: Fraction) -> tuple[Fraction, ...]:
    count = int(2 * ell) + 1
    return tuple(-ell + i for i in range(count))


def multiplet_label(mode: ModeLabel) -> MultipletLabel:
    k = k_from_qj(mode.q, mode.j)
    ell = ell_from_k(k)
    n = n_from_q(mode.q)
    return MultipletLabel(mode.sector, mode.index, k, ell, n, allowed_m_values(ell))


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


def multiplet_ledgers() -> dict[str, tuple[MultipletLabel, ...]]:
    return {
        sector: tuple(multiplet_label(mode) for mode in modes)
        for sector, modes in generation_modes().items()
    }


def _is_integral(value: Fraction) -> bool:
    return value.denominator == 1


def n_admissible(label: MultipletLabel) -> bool:
    return abs(label.n) <= label.ell and _is_integral(label.ell - label.n)


def m_admissible(label: MultipletLabel, m: Fraction) -> bool:
    return abs(m) <= label.ell and _is_integral(label.ell - m)


def all_multiplets_admissible() -> bool:
    return all(
        n_admissible(label) and all(m_admissible(label, m) for m in label.m_values)
        for labels in multiplet_ledgers().values()
        for label in labels
    )


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def harmonic_representative(label: MultipletLabel, m: Fraction) -> str:
    return f"D^({_fraction_text(label.ell)})_({_fraction_text(m)},{_fraction_text(label.n)})"


def multiplet_representatives(label: MultipletLabel) -> tuple[str, ...]:
    return tuple(harmonic_representative(label, m) for m in label.m_values)


def axis_collapse_rule() -> str:
    return "If y0 is derived as an identity/Hopf-axis point, D^ell_{m,n}(y0)=delta_mn and the leading component is m=n=q/2."


def generic_y0_rule() -> str:
    return "If y0 is generic, retain the full D^ell_{m,n}(alpha0,beta0,gamma0) multiplet for Wigner evaluation at the universal sampling point."


def local_feature_vector(label: MultipletLabel) -> tuple[str, ...]:
    features: list[str] = []
    for m in label.m_values:
        rep = harmonic_representative(label, m)
        features.extend((rep, f"partial_a {rep}", f"partial_a partial_b {rep}"))
    return tuple(features)


def m_multiplet_scaffold_derived() -> bool:
    return all_multiplets_admissible()


def single_m_assignment_forced() -> bool:
    return False


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


def rank_support_condition() -> dict[str, str | bool]:
    return {
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "condition": "rank-three support would require independent finite-width local feature moments across the retained multiplet components",
        "guardrail": "This branch derives the feature scaffold, not the finite-width moment theorem.",
    }


def yukawa_bridge_status() -> dict[str, str | bool]:
    return {
        "multiplet_features_available": m_multiplet_scaffold_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "guardrail": "Feature availability is not a numerical Yukawa, CKM, or PMNS derivation.",
    }


def proof_discharge_ledger() -> dict[str, str]:
    status = MultipletStatus.DERIVED_CONDITIONAL.value if m_multiplet_scaffold_derived() else MultipletStatus.OPEN.value
    return {
        "PO-BH-30": f"{status}: admissible m-multiplet harmonic feature scaffold derived; axis collapse and generic y0 cases remain conditional"
    }


def multiplet_table_rows() -> tuple[dict[str, str | int | bool], ...]:
    rows: list[dict[str, str | int | bool]] = []
    for sector, labels in multiplet_ledgers().items():
        for label in labels:
            rows.append(
                {
                    "sector": sector,
                    "index": label.index,
                    "k": label.k,
                    "ell": _fraction_text(label.ell),
                    "n": _fraction_text(label.n),
                    "m_count": len(label.m_values),
                    "m_values": ", ".join(_fraction_text(m) for m in label.m_values),
                    "n_admissible": n_admissible(label),
                }
            )
    return tuple(rows)


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "m_multiplet_scaffold_derived_conditionally": m_multiplet_scaffold_derived(),
        "axis_collapse_case_documented": True,
        "generic_y0_case_documented": True,
        "single_m_assignment_forced": single_m_assignment_forced(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "multiplet_rows": list(multiplet_table_rows()),
        "rank_support_condition": rank_support_condition(),
        "yukawa_bridge_status": yukawa_bridge_status(),
        "discharged_obligations": proof_discharge_ledger(),
        "still_open_downstream": [
            "derive y0 as group identity, Hopf pole, Berger axis, or canonical focal point",
            "derive Wigner/Hopf axis-sampling rule in BHSM notation",
            "prove finite-width rank-three local feature independence",
            "compute finite-width moment contractions",
            "derive numerical Yukawa values",
            "derive fermion mass ratios from the feature scaffold",
            "derive CKM mixing values",
            "derive PMNS mixing values",
            "complete replacement-level Standard Model derivation",
        ],
        "negative_results": [
            "single m assignment not forced",
            "finite-width rank-three not derived in this branch",
            "numerical Yukawa values not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
    }


def _multiplet_table_markdown() -> str:
    rows = [
        "| sector | index | k | ell | n | m count | m values | n admissible |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in multiplet_table_rows():
        rows.append(
            f"| {row['sector']} | {row['index']} | {row['k']} | {row['ell']} | {row['n']} | {row['m_count']} | {row['m_values']} | `{row['n_admissible']}` |"
        )
    return "\n".join(rows)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: M-Multiplet Harmonic Features

## 1. Mission

This branch derives a conditional m-multiplet harmonic feature scaffold for BHSM internal modes. It does not force a single m-weight assignment.

## 2. Mode Labels

For each mode, the scaffold uses:

```text
k = q + 2j
ell = k/2
n = q/2
m in {{-ell, -ell+1, ..., ell}}
```

## 3. Multiplet Definition

```text
Psi_{{k,q}}^multiplet(y) = {{ D^{{k/2}}_{{m,q/2}}(y) }}_{{m=-ell}}^ell
```

## 4. Local Feature Multiplet

```text
F_{{k,q}}(y0) = {{
  D^{{k/2}}_{{m,q/2}}(y0),
  partial_a D^{{k/2}}_{{m,q/2}}(y0),
  partial_a partial_b D^{{k/2}}_{{m,q/2}}(y0)
}}_{{m=-ell}}^ell
```

## 5. Admissible Multiplets

{_multiplet_table_markdown()}

## 6. Axis-Collapse Case

{axis_collapse_rule()}

This case remains conditional on a future derivation of `y0` as the relevant identity/Hopf-axis point.

## 7. Generic Y0 Case

{generic_y0_rule()}

## 8. Rank Support Condition

Finite-width rank-three support remains open. The current branch only supplies the local harmonic feature scaffold required by a future finite-width moment theorem.

## 9. Yukawa Bridge

The multiplet scaffold can feed a future Yukawa overlap theorem, but this branch does not derive numerical Yukawa values, mass ratios, CKM, PMNS, or replacement readiness.

## 10. Non-Tautology Guardrail

The branch avoids promoting `m=n=q/2` as a single forced label. The full admissible m-multiplet is retained unless the stronger y0 axis-sampling theorem is later derived.

## Conclusion

This branch derives the m-multiplet harmonic feature scaffold for BHSM internal modes. Rather than forcing a single m-weight assignment, each mode with ell=k/2 and n=q/2 is assigned its full admissible Wigner/Hopf m-multiplet. If y0 is later derived as an identity/Hopf-axis point, the multiplet can collapse to the leading m=n=q/2 component. If y0 is generic, the full multiplet remains available for Wigner evaluation at the universal sampling point. This branch does not derive finite-width rank-three Yukawa matrices, numerical Yukawa values, CKM, PMNS, or replacement readiness.
"""


def simple_doc(title: str, body: str, status: str) -> str:
    return f"# {title}\n\n{body}\n\nStatus: `{status}`.\n"


def render_non_tautology() -> str:
    return """# M-Multiplet Harmonic Features Non-Tautology Audit

| check | result | guardrail |
| --- | --- | --- |
| full m multiplet retained | yes | single m assignment is not forced |
| axis-collapse case | documented | conditional on y0 identity/Hopf-axis theorem |
| generic y0 case | documented | full Wigner multiplet remains available |
| rank-three theorem | open | feature scaffold is not a rank theorem |
| numerical Yukawa values | open | no empirical fitting or prediction update |

Conclusion: PO-BH-30 is discharged only as a conditional harmonic feature scaffold.
"""


def export_outputs(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "theorem_discharge_m_multiplet_harmonic_features.md": render_main_markdown(),
        "derived_m_multiplet_admissible_set.md": "# Derived M-Multiplet Admissible Set\n\n" + _multiplet_table_markdown() + "\n\nStatus: `DERIVED_CONDITIONAL`.\n",
        "derived_m_multiplet_harmonic_representatives.md": simple_doc(
            "Derived M-Multiplet Harmonic Representatives",
            "Each admissible mode is represented by the full set `D^ell_(m,n)` over all admissible m weights.",
            "DERIVED_CONDITIONAL",
        ),
        "derived_axis_collapse_vs_generic_y0_sampling.md": simple_doc(
            "Derived Axis Collapse Vs Generic Y0 Sampling",
            f"{axis_collapse_rule()}\n\n{generic_y0_rule()}",
            "DERIVED_CONDITIONAL",
        ),
        "derived_generic_y0_wigner_evaluation_scaffold.md": simple_doc(
            "Derived Generic Y0 Wigner Evaluation Scaffold",
            "For generic `y0=(alpha0,beta0,gamma0)`, evaluate the retained full multiplet rather than collapsing to one m component.",
            "DERIVED_CONDITIONAL",
        ),
        "derived_m_multiplet_local_feature_vectors.md": simple_doc(
            "Derived M-Multiplet Local Feature Vectors",
            "Local feature vectors consist of values, first derivatives, and second derivatives of every retained multiplet component at y0.",
            "DERIVED_CONDITIONAL",
        ),
        "derived_m_multiplet_rank_support_condition.md": simple_doc(
            "Derived M-Multiplet Rank Support Condition",
            rank_support_condition()["condition"],
            "FINITE_WIDTH_RANK_THREE_REMAINS_OPEN",
        ),
        "derived_m_multiplet_yukawa_bridge.md": simple_doc(
            "Derived M-Multiplet Yukawa Bridge",
            yukawa_bridge_status()["guardrail"],
            "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
        ),
        "derived_m_multiplet_open_problem.md": simple_doc(
            "Derived M-Multiplet Open Problem",
            "Derive the y0 axis theorem or finite-width moment theorem needed to turn the feature scaffold into numerical mass and mixing predictions.",
            "OPEN",
        ),
        "m_multiplet_harmonic_features_non_tautology_audit.md": render_non_tautology(),
    }
    for name, text in files.items():
        (theory / name).write_text(text, encoding="utf-8")
    (theory / "theorem_discharge_m_multiplet_harmonic_features_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs()
