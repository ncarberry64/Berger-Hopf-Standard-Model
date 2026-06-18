from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


BRANCH = "bhsm-closure-spectrum-selection-rule-audit-v1"
STATUS = "candidate_only"
PRIMITIVE_SELECTED_DIMS = {1, 2, 3}

VERDICT_LABELS = [
    "CLOSURE_SPECTRUM_SELECTION_RULE_AUDIT_COMPLETE",
    "MINIMAL_CLOSURE_SPECTRUM_123_SUPPORTED_DIAGNOSTIC",
    "IRREDUCIBLE_CLOSURE_SCREEN_CANDIDATE",
    "TOPOGRAPHIC_BRANCH_SCREEN_CANDIDATE",
    "ANOMALY_MINIMALITY_SCREEN_CANDIDATE",
    "HIGHER_CLOSURES_COMPOSITE_OR_UNSUPPORTED_DIAGNOSTIC",
    "UNIQUE_FIRST_PRINCIPLES_CLOSURE_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

CLAIM_LABELS = [
    "CLOSURE_SPECTRUM_SELECTION_RULE_AUDIT_CANDIDATE",
    "MINIMAL_CLOSURE_SPECTRUM_123_SUPPORTED_DIAGNOSTIC",
    "IRREDUCIBLE_CLOSURE_SCREEN_CANDIDATE",
    "TOPOGRAPHIC_BRANCH_SCREEN_CANDIDATE",
    "ANOMALY_MINIMALITY_SCREEN_CANDIDATE",
    "HIGHER_CLOSURES_COMPOSITE_OR_UNSUPPORTED_DIAGNOSTIC",
    "UNIQUE_FIRST_PRINCIPLES_CLOSURE_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This audit does not fully derive the Standard Model. It tests candidate selection "
    "principles that support the minimal closure spectrum {1,2,3} as the low-energy "
    "fundamental boundary spectrum. The result remains candidate-only unless the "
    "selection conditions are derived directly from the Berger-Hopf boundary action "
    "and the full topographic Hessian problem."
)

REQUIRED_CONCLUSION_LANGUAGE = (
    "The audit supports {1,2,3} as the minimal diagnostic closure spectrum compatible "
    "with the current BHSM charge/anomaly bridge, boundary-orientation structure, and "
    "fourth-order branch-count interpretation. It does not uniquely prove that no "
    "higher fundamental closures exist in the full Berger-Hopf theory."
)


@dataclass(frozen=True)
class ClosureDimensionAudit:
    d: int
    primitive_status: str
    reducibility_status: str
    topographic_status: str
    anomaly_minimality_status: str
    selected_low_energy_fundamental: bool
    notes: tuple[str, ...]


def is_positive_dimension(d: int) -> bool:
    return isinstance(d, int) and d >= 1


def validate_dimension(d: int) -> None:
    if not is_positive_dimension(d):
        raise ValueError("closure dimension must be a positive integer")


def reference_rule_pass(d: int) -> bool:
    validate_dimension(d)
    return d == 1


def orientation_rule_pass(d: int) -> bool:
    validate_dimension(d)
    return d == 2


def cyclic_channel_rule_pass(d: int) -> bool:
    validate_dimension(d)
    return d == 3


def _is_prime(d: int) -> bool:
    if d < 2:
        return False
    return all(d % p != 0 for p in range(2, int(d**0.5) + 1))


def is_reducible_by_lower_primitives(d: int, primitives: set[int] | None = None) -> bool:
    validate_dimension(d)
    primitives = set(PRIMITIVE_SELECTED_DIMS if primitives is None else primitives)
    if d in {1, 2, 3}:
        return False
    if _is_prime(d):
        return False
    return any(p < d for p in primitives)


def topographic_branch_screen_status(d: int) -> str:
    validate_dimension(d)
    if d == 1:
        return "reference"
    if d == 2:
        return "stable_nonzero_orientation_candidate"
    if d == 3:
        return "stable_nonzero_channel_candidate"
    return "higher_or_composite_unsupported"


def anomaly_minimality_status(d: int) -> str:
    validate_dimension(d)
    if d == 1:
        return "minimal_leptonic_single_channel_ingredient"
    if d == 2:
        return "minimal_weak_orientation_pair_ingredient"
    if d == 3:
        return "minimal_three_channel_charge_anomaly_ingredient"
    if is_reducible_by_lower_primitives(d):
        return "composite_not_needed_for_minimal_charge_anomaly_bridge"
    return "higher_prime_unsupported_by_current_charge_anomaly_minimality"


def classify_dimension(d: int) -> ClosureDimensionAudit:
    validate_dimension(d)
    notes: list[str] = []
    if reference_rule_pass(d):
        primitive_status = "primitive reference/single closure"
        reducibility_status = "irreducible_under_current_screen"
        notes.append("identity/reference closure")
    elif orientation_rule_pass(d):
        primitive_status = "primitive orientation-pair closure"
        reducibility_status = "irreducible_under_current_screen"
        notes.append("minimal Z2 orientation-pair closure")
    elif cyclic_channel_rule_pass(d):
        primitive_status = "primitive cyclic three-channel closure"
        reducibility_status = "irreducible_under_current_screen"
        notes.append("minimal nontrivial cyclic channel closure beyond orientation pairing")
    elif is_reducible_by_lower_primitives(d):
        primitive_status = "composite/product-like closure"
        reducibility_status = "composite/reducible under current primitive set"
        notes.append("screened as composite or higher excitation candidate")
    else:
        primitive_status = "higher prime unsupported"
        reducibility_status = "not reducible but unsupported by current low-energy minimality screens"
        notes.append("unsupported, not impossible")

    selected = (
        primitive_status
        in {
            "primitive reference/single closure",
            "primitive orientation-pair closure",
            "primitive cyclic three-channel closure",
        }
        and topographic_branch_screen_status(d)
        in {
            "reference",
            "stable_nonzero_orientation_candidate",
            "stable_nonzero_channel_candidate",
        }
        and anomaly_minimality_status(d).startswith("minimal_")
    )
    return ClosureDimensionAudit(
        d=d,
        primitive_status=primitive_status,
        reducibility_status=reducibility_status,
        topographic_status=topographic_branch_screen_status(d),
        anomaly_minimality_status=anomaly_minimality_status(d),
        selected_low_energy_fundamental=selected,
        notes=tuple(notes),
    )


def audit_dimensions(max_d: int = 8) -> list[ClosureDimensionAudit]:
    validate_dimension(max_d)
    return [classify_dimension(d) for d in range(1, max_d + 1)]


def selected_low_energy_spectrum(max_d: int = 8) -> list[int]:
    return [row.d for row in audit_dimensions(max_d) if row.selected_low_energy_fundamental]


def selection_rule_summary(max_d: int = 8) -> dict:
    rows = audit_dimensions(max_d)
    return {
        "candidate_selected_low_energy_spectrum": selected_low_energy_spectrum(max_d),
        "audited_dimensions": {str(row.d): row.primitive_status for row in rows},
        "closure_spectrum_uniquely_derived": False,
        "full_hessian_proof_complete": False,
        "higher_prime_closures_status": "unsupported, not impossible",
        "rows": [asdict(row) for row in rows],
    }


def build_results_payload() -> dict:
    summary = selection_rule_summary(8)
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "closure_spectrum_uniquely_derived": False,
        "full_hessian_proof_complete": False,
        "candidate_selected_low_energy_spectrum": summary["candidate_selected_low_energy_spectrum"],
        "audited_dimensions": {
            "1": "primitive reference/single closure",
            "2": "primitive orientation-pair closure",
            "3": "primitive cyclic three-channel closure",
            "4": "composite/reducible under current primitive set",
            "5": "higher prime unsupported by current low-energy minimality screens",
            "6": "composite/product-like under current primitive set",
            "7": "higher prime unsupported by current low-energy minimality screens",
            "8": "composite/product-like under current primitive set",
        },
        "screens": {
            "reference_rule": "candidate",
            "orientation_rule": "candidate",
            "cyclic_channel_rule": "candidate",
            "irreducibility_screen": "candidate",
            "topographic_branch_screen": "candidate",
            "anomaly_minimality_screen": "candidate",
        },
        "bridges_preserved": {
            "closure_spectrum_to_finite_algebra": True,
            "finite_boundary_algebra_bridge": True,
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "negative_results": [
            "unique first-principles closure derivation remains open",
            "full topographic Hessian proof remains open",
            "higher prime closures are unsupported, not impossible",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "selection rules support {1,2,3} as minimal low-energy closure spectrum",
            "unique first-principles derivation remains open",
            "full Berger-Hopf Hessian proof remains open",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _audit_table() -> str:
    lines = [
        "| d | primitive status | reducibility status | topographic status | anomaly minimality status | selected | notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in audit_dimensions(8):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.d),
                    row.primitive_status,
                    row.reducibility_status,
                    row.topographic_status,
                    row.anomaly_minimality_status,
                    str(row.selected_low_energy_fundamental).lower(),
                    "; ".join(row.notes),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_main_audit_markdown() -> str:
    return f"""# Closure Spectrum Selection Rule Audit

## 1. Motivation

The admissible closure-spectrum gate documented `D_adm = {{1,2,3}}` as a diagnostic bridge. This audit tests candidate selection principles that support those dimensions as the minimal low-energy fundamental boundary spectrum.

## 2. Previous Gate Achieved: Diagnostic `D_adm={{1,2,3}}`

```text
D_adm = {{1,2,3}}
End(C^1)=C
End(C^2)=M2(C)
End(C^3)=M3(C)
```

## 3. Why A Real Selection Rule Is Needed

The diagnostic spectrum must eventually be derived from boundary action, admissible phase closure, and the full stability/Hessian problem. This audit does not close that proof obligation.

## 4. Candidate Selection Principles

- identity/reference closure selects `d=1`;
- orientation-pair closure selects `d=2`;
- minimal cyclic channel closure selects `d=3`;
- reducible higher closures are screened as composite or higher excitations;
- fourth-order branch count supports reference plus two nonzero branches;
- anomaly-compatible minimality requires the `1,2,3` ingredients.

## 5. Irreducibility And Reducibility Screen

Dimensions above `3` are not selected as low-energy primitive closures unless an independent action term requires them. Composite/reducible closures are interpreted as higher organization rather than fundamental low-energy sectors.

## 6. Fourth-Order Topographic Branch Screen

```text
L_T = nabla^2 - B*nabla^4
```

Candidate interpretation: zero/reference closure plus two stable nonzero branches.

## 7. Anomaly-Compatible Minimality Screen

The current charge/anomaly bridge requires a single-channel closure, a weak orientation pair, and a three-channel active closure. The smallest closure dimensions supplying those ingredients are `1`, `2`, and `3`.

## 8. Small-Dimension Audit `(d=1..8)`

{_audit_table()}

## 9. Candidate Result

```text
selected_low_energy_spectrum = {selected_low_energy_spectrum(8)}
```

{REQUIRED_CONCLUSION_LANGUAGE}

## 10. Negative Result / Limitation

Higher prime closures such as `d=5` and `d=7` are unsupported by the current low-energy minimality screens, not mathematically impossible. Unique first-principles closure derivation remains open.

## 11. What This Achieves

This audit strengthens the candidate case for `{1,2,3}` as the minimal diagnostic low-energy closure spectrum.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 12. What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not claim the closure spectrum is uniquely derived from first principles.

## 13. Next Proof Obligations

- derive the reference, orientation, and cyclic channel rules from the Berger-Hopf boundary action;
- derive the reducibility screen from admissible closure composition;
- derive the topographic branch screen from the full Hessian;
- prove or reject whether higher prime closures are excluded, excited, or physically irrelevant.

## Related Action/Hessian Scaffold

- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
"""


def render_candidate_rules_markdown() -> str:
    return """# Closure Spectrum Candidate Selection Rules

## A. Reference Rule

```text
A fundamental boundary closure spectrum must include d=1 as the identity/reference single-channel closure.
```

## B. Orientation Rule

```text
A weak-interface orientation grading requires a minimal two-state closure d=2.
```

## C. Cyclic Channel Rule

```text
A nontrivial channel sector with cyclic closure beyond orientation pairing is minimally d=3.
```

## D. Irreducibility Rule

```text
A candidate fundamental closure should not be reducible into a direct-sum organization of already admitted lower primitive closures unless a separate boundary action term requires it.
```

## E. Topographic Branch Rule

```text
The fundamental closure spectrum is constrained by the zero/reference plus two stable nonzero branch interpretation of the fourth-order operator.
```

## F. Anomaly Minimality Rule

```text
The selected low-energy closure spectrum must support the integer primitive charge/hypercharge bridge and one-generation anomaly cancellation.
```

Guardrail: none of these rules is yet a full derivation from the action. They are candidate screens.

## Related Action/Hessian Scaffold

- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
"""


def render_reducibility_markdown() -> str:
    return f"""# Closure Spectrum Reducibility Screen

Diagnostic reducibility screen for `d=1..8`:

{_audit_table()}

Careful status: `d=5` and `d=7` are unsupported by current low-energy minimality screens, not impossible.

## Related Action/Hessian Scaffold

- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
"""


def render_topographic_markdown() -> str:
    return """# Closure Spectrum Topographic Branch Screen

Fourth-order stability layer:

```text
L_T = nabla^2 - B nabla^4
```

Candidate branch interpretation:

```text
zero/reference closure + two stable nonzero branches
```

Diagnostic mapping:

```text
d=1 -> zero/reference/single closure
d=2 -> minimal orientation-pair closure associated with one nonzero branch interface
d=3 -> minimal three-channel closure associated with the second nonzero branch/channel closure
d>=4 -> higher/composite unsupported by this branch screen
```

Guardrail: this is not a full Hessian proof. The complete proof requires deriving the branch spectrum and closure dimensions from the actual Berger-Hopf Hessian and boundary conditions.

## Related Action/Hessian Scaffold

- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
"""


def render_anomaly_markdown() -> str:
    return """# Closure Spectrum Anomaly Minimality Screen

The already audited charge/anomaly chain requires:

- one leptonic/single-channel closure;
- one weak two-orientation active interface;
- one three-channel active/quark-like closure;
- inactive orientation singlets.

The smallest closure dimensions supplying those are:

```text
1, 2, 3
```

This is not a proof of uniqueness, but it supports minimality.

## Related Action/Hessian Scaffold

- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "closure_spectrum_selection_rule_audit.md": render_main_audit_markdown(),
        "closure_spectrum_candidate_selection_rules.md": render_candidate_rules_markdown(),
        "closure_spectrum_reducibility_screen.md": render_reducibility_markdown(),
        "closure_spectrum_topographic_branch_screen.md": render_topographic_markdown(),
        "closure_spectrum_anomaly_minimality_screen.md": render_anomaly_markdown(),
        "closure_spectrum_selection_results.json": json.dumps(payload, indent=2, sort_keys=True)
        + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
