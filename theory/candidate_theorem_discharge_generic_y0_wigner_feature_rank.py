from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-generic-y0-wigner-feature-rank-v1"
STATUS = "theorem_discharge_candidate"


class GenericY0Status(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    SYMBOLIC_SCAFFOLD = "SYMBOLIC_SCAFFOLD"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class ModeLabel:
    sector: str
    index: int
    q: int
    j: int


@dataclass(frozen=True)
class GenericY0FeatureLabel:
    sector: str
    index: int
    k: int
    ell: Fraction
    n: Fraction
    m: Fraction
    expression: str


VERDICT_LABELS = [
    "PO_BH_31_GENERIC_Y0_WIGNER_FEATURE_RANK_SCAFFOLD_DERIVED_CONDITIONAL",
    "GENERIC_Y0_WIGNER_EVALUATION_SCAFFOLD_DERIVED_CONDITIONAL",
    "REDUCED_WIGNER_BETA_SELECTOR_IDENTIFIED_CONDITIONAL",
    "GENERIC_Y0_PHASE_STRUCTURE_IDENTIFIED_CONDITIONAL",
    "AXIS_COLLAPSE_RECOVERY_CASE_DOCUMENTED",
    "Y0_COORDINATES_REMAIN_OPEN",
    "FEATURE_RANK_INDEPENDENCE_REMAINS_OPEN",
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


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def wigner_y0_expression(ell: Fraction, m: Fraction, n: Fraction) -> str:
    return (
        f"exp(-i*{_fraction_text(m)}*alpha0)"
        f"*d^({_fraction_text(ell)})_({_fraction_text(m)},{_fraction_text(n)})(beta0)"
        f"*exp(-i*{_fraction_text(n)}*gamma0)"
    )


def generic_y0_feature_labels(mode: ModeLabel) -> tuple[GenericY0FeatureLabel, ...]:
    k = k_from_qj(mode.q, mode.j)
    ell = ell_from_k(k)
    n = n_from_q(mode.q)
    return tuple(
        GenericY0FeatureLabel(
            sector=mode.sector,
            index=mode.index,
            k=k,
            ell=ell,
            n=n,
            m=m,
            expression=wigner_y0_expression(ell, m, n),
        )
        for m in allowed_m_values(ell)
    )


def all_generic_y0_feature_labels() -> dict[str, tuple[GenericY0FeatureLabel, ...]]:
    return {
        f"{mode.sector}:{mode.index}": generic_y0_feature_labels(mode)
        for modes in generation_modes().values()
        for mode in modes
    }


def beta_selector_statement() -> str:
    return "beta0 controls reduced-Wigner magnitude structure through d^ell_{m,n}(beta0)"


def phase_structure_statement() -> str:
    return "alpha0 and gamma0 enter as phase factors exp(-i m alpha0) and exp(-i n gamma0)"


def axis_collapse_recovery_statement() -> str:
    return "beta0=0 recovers the identity-axis collapse D^ell_{m,n}=delta_mn"


def derivative_identities() -> dict[str, str]:
    return {
        "partial_alpha": "partial_alpha D^ell_{m,n} = -i m D^ell_{m,n}",
        "partial_gamma": "partial_gamma D^ell_{m,n} = -i n D^ell_{m,n}",
        "partial_beta": "partial_beta D^ell_{m,n} = exp(-i m alpha) (partial_beta d^ell_{m,n}(beta)) exp(-i n gamma)",
    }


def local_feature_vector(label: GenericY0FeatureLabel) -> tuple[str, ...]:
    d = derivative_identities()
    return (
        label.expression,
        f"-i*{_fraction_text(label.m)}*({label.expression})",
        f"partial_beta[{label.expression}]",
        f"-i*{_fraction_text(label.n)}*({label.expression})",
        f"partial_alpha partial_alpha[{label.expression}]",
        f"partial_alpha partial_beta[{label.expression}]",
        f"partial_alpha partial_gamma[{label.expression}]",
        f"partial_beta partial_beta[{label.expression}]",
        f"partial_beta partial_gamma[{label.expression}]",
        f"partial_gamma partial_gamma[{label.expression}]",
        d["partial_alpha"],
        d["partial_beta"],
        d["partial_gamma"],
    )


def all_feature_label_counts() -> dict[str, int]:
    return {key: len(labels) for key, labels in all_generic_y0_feature_labels().items()}


def y0_coordinates_derived() -> bool:
    return False


def feature_rank_independence_derived() -> bool:
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


def feature_rank_condition() -> dict[str, str | bool]:
    return {
        "feature_rank_independence_derived": feature_rank_independence_derived(),
        "condition": "Rank-three support requires the three generation-mode feature multiplets in a sector to remain independent under universal finite-width moment contractions.",
        "guardrail": "This branch derives symbolic generic-y0 features, not feature-rank independence.",
    }


def yukawa_bridge_status() -> dict[str, str | bool]:
    return {
        "generic_y0_features_available": True,
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "guardrail": "Wigner feature evaluation is not a numerical Yukawa, CKM, or PMNS derivation.",
    }


def core_formula() -> str:
    return "D^{k/2}_{m,q/2}(y0)=exp(-i*m*alpha0)*d^{k/2}_{m,q/2}(beta0)*exp(-i*(q/2)*gamma0)"


def proof_discharge_ledger() -> dict[str, str]:
    return {
        "PO-BH-31": "DERIVED_CONDITIONAL: generic-y0 Wigner evaluation scaffold derived symbolically; y0 coordinates, feature-rank independence, and numerical Yukawa values remain open"
    }


def feature_table_rows() -> tuple[dict[str, str | int], ...]:
    rows: list[dict[str, str | int]] = []
    for key, labels in all_generic_y0_feature_labels().items():
        if not labels:
            continue
        first = labels[0]
        rows.append(
            {
                "mode": key,
                "sector": first.sector,
                "index": first.index,
                "k": first.k,
                "ell": _fraction_text(first.ell),
                "n": _fraction_text(first.n),
                "m_count": len(labels),
                "first_expression": first.expression,
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
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
        "generic_y0_wigner_scaffold_derived_conditionally": True,
        "y0_coordinates_derived": y0_coordinates_derived(),
        "feature_rank_independence_derived": feature_rank_independence_derived(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "discharged_obligations": proof_discharge_ledger(),
        "core_formula": core_formula(),
        "beta_selector_statement": beta_selector_statement(),
        "phase_structure_statement": phase_structure_statement(),
        "axis_collapse_recovery_statement": axis_collapse_recovery_statement(),
        "feature_label_counts": all_feature_label_counts(),
        "feature_rows": list(feature_table_rows()),
        "feature_rank_condition": feature_rank_condition(),
        "yukawa_bridge_status": yukawa_bridge_status(),
        "still_open_downstream": [
            "derive or constrain y0 coordinates alpha0,beta0,gamma0",
            "evaluate reduced Wigner beta selector",
            "evaluate local feature vectors at y0",
            "finite-width moment contractions",
            "rank-three Yukawa matrix theorem",
            "numerical Yukawa coupling theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "y0 coordinates not derived in this branch",
            "feature-rank independence not derived in this branch",
            "finite-width rank-three not derived in this branch",
            "numerical Yukawa values not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
    }


def _feature_table_markdown() -> str:
    rows = [
        "| mode | k | ell | n | m count | first generic-y0 expression |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in feature_table_rows():
        rows.append(
            f"| {row['mode']} | {row['k']} | {row['ell']} | {row['n']} | {row['m_count']} | `{row['first_expression']}` |"
        )
    return "\n".join(rows)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Generic Y0 Wigner Feature Rank

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

This branch derives a symbolic generic-y0 Wigner evaluation scaffold for the BHSM m-multiplet harmonic feature space.

## 2. Previous Theorem Layers Achieved

PO-BH-27 conditionally derived `ell=k/2`, `n=q/2`, and `j=ell-n`. PO-BH-30 conditionally assigned the full admissible m-multiplet to each `(k,q)` internal mode.

## 3. Why Generic Y0 Evaluation Is Needed

PO-BH-29 leaves the identity/Hopf-axis status of `y0` open. Therefore this branch keeps the universal internal sampling point symbolic as `(alpha0,beta0,gamma0)`.

## 4. Highest-Weight Convention

```text
ell = k/2
n = q/2
```

## 5. Full M-Multiplet Scaffold

Each mode retains all `m` in `{{-ell,-ell+1,...,ell}}`. No single `m` assignment is forced.

## 6. Generic Y0 Coordinates

```text
y0 = (alpha0,beta0,gamma0)
```

The coordinates are not numerically derived in this branch.

## 7. Wigner Evaluation At Y0

```text
D^ell_{{m,n}}(alpha,beta,gamma)
= exp(-i m alpha) d^ell_{{m,n}}(beta) exp(-i n gamma)
```

```text
{core_formula()}
```

## 8. Reduced Wigner Beta Selector

{beta_selector_statement()}.

## 9. Phase Structure From Alpha0 And Gamma0

{phase_structure_statement()}.

## 10. Axis-Collapse Recovery Case

{axis_collapse_recovery_statement()}.

## 11. Local Feature Vectors

The local feature scaffold includes the Wigner value, first derivatives with respect to `alpha`, `beta`, and `gamma`, and second-derivative features for each retained `m` component.

```text
partial_alpha D^ell_{{m,n}} = -i m D^ell_{{m,n}}
partial_gamma D^ell_{{m,n}} = -i n D^ell_{{m,n}}
partial_beta D^ell_{{m,n}} = exp(-i m alpha) (partial_beta d^ell_{{m,n}}(beta)) exp(-i n gamma)
```

{_feature_table_markdown()}

## 12. Feature-Rank Support Condition

{feature_rank_condition()["condition"]}

## 13. Bridge To Finite-Width Yukawa Overlap

The symbolic features can feed a future finite-width moment theorem, but this branch does not compute moment contractions.

## 14. Numerical Yukawa Status

No numerical Yukawa values are derived.

## 15. CKM/PMNS Status

No CKM or PMNS values are derived.

## 16. Non-Tautology Audit

The branch does not fit fermion masses, import measured masses, import CKM/PMNS values, choose `alpha0,beta0,gamma0` from data, or force `m=q/2`.

## 17. What This Achieves

This branch supplies the symbolic Wigner evaluation route needed between the m-multiplet scaffold and future finite-width feature-rank analysis.

## 18. What Remains Before Full BHSM Replacement Claim

The highest-value open step is to derive or constrain `alpha0,beta0,gamma0`, then prove feature-rank independence under universal finite-width moment contractions.

## Conclusion

This branch derives the generic-y0 Wigner evaluation scaffold for the BHSM m-multiplet harmonic feature space. The internal sampling point y0 is represented symbolically by Hopf/Euler coordinates (alpha0,beta0,gamma0), and each mode evaluates through D^{{k/2}}_{{m,q/2}}(y0). The reduced Wigner factor d^{{k/2}}_{{m,q/2}}(beta0) is identified as the primary magnitude selector, while alpha0 and gamma0 provide phase structure. This branch does not derive numerical y0 coordinates, finite-width rank-three Yukawa matrices, numerical Yukawa values, CKM, PMNS, or replacement readiness.
"""


def simple_doc(title: str, body: str, status: str) -> str:
    return f"# {title}\n\n{body}\n\nStatus: `{status}`.\n"


def render_non_tautology() -> str:
    return """# Generic Y0 Wigner Feature Rank Non-Tautology Audit

| check | result | guardrail |
| --- | --- | --- |
| symbolic y0 coordinates | yes | no numeric coordinate fitting |
| Wigner evaluation formula | yes | no reduced-Wigner numerical values |
| beta selector | identified | no magnitude theorem from data |
| feature-rank independence | open | no rank-three promotion |
| numerical Yukawa/CKM/PMNS | open | no empirical imports |

Conclusion: PO-BH-31 is discharged only as a symbolic generic-y0 Wigner feature scaffold.
"""


def export_outputs(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "theorem_discharge_generic_y0_wigner_feature_rank.md": render_main_markdown(),
        "derived_generic_y0_coordinate_scaffold.md": simple_doc(
            "Derived Generic Y0 Coordinate Scaffold",
            "`y0` is represented symbolically as `(alpha0,beta0,gamma0)` because PO-BH-29 leaves axis identification open.",
            "SYMBOLIC_SCAFFOLD",
        ),
        "derived_generic_y0_wigner_evaluation_formula.md": simple_doc(
            "Derived Generic Y0 Wigner Evaluation Formula",
            core_formula(),
            "DERIVED_CONDITIONAL",
        ),
        "derived_reduced_wigner_beta_selector.md": simple_doc(
            "Derived Reduced Wigner Beta Selector",
            beta_selector_statement(),
            "DERIVED_CONDITIONAL",
        ),
        "derived_generic_y0_phase_structure.md": simple_doc(
            "Derived Generic Y0 Phase Structure",
            phase_structure_statement(),
            "DERIVED_CONDITIONAL",
        ),
        "derived_generic_y0_local_feature_vectors.md": simple_doc(
            "Derived Generic Y0 Local Feature Vectors",
            "The scaffold includes values, alpha/beta/gamma first derivatives, and second-derivative features for every retained m component.",
            "DERIVED_CONDITIONAL",
        ),
        "derived_generic_y0_feature_rank_condition.md": simple_doc(
            "Derived Generic Y0 Feature Rank Condition",
            feature_rank_condition()["condition"],
            "FEATURE_RANK_INDEPENDENCE_REMAINS_OPEN",
        ),
        "derived_axis_collapse_recovery_case.md": simple_doc(
            "Derived Axis Collapse Recovery Case",
            axis_collapse_recovery_statement(),
            "AXIS_COLLAPSE_RECOVERY_CASE_DOCUMENTED",
        ),
        "derived_generic_y0_yukawa_bridge.md": simple_doc(
            "Derived Generic Y0 Yukawa Bridge",
            yukawa_bridge_status()["guardrail"],
            "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
        ),
        "derived_generic_y0_open_problem.md": simple_doc(
            "Derived Generic Y0 Open Problem",
            "Derive or constrain `(alpha0,beta0,gamma0)` and prove feature-rank independence under universal finite-width moment contractions.",
            "OPEN",
        ),
        "generic_y0_wigner_feature_rank_non_tautology_audit.md": render_non_tautology(),
    }
    for name, text in files.items():
        (theory / name).write_text(text, encoding="utf-8")
    (theory / "theorem_discharge_generic_y0_wigner_feature_rank_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs()
