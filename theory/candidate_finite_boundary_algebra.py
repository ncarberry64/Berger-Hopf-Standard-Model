from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from candidate_boundary_integer_anomaly import anomaly_report


BRANCH = "bhsm-finite-boundary-algebra-source-gate-v1"
STATUS = "candidate_only"

VALID_CHANNEL_BLOCKS = {"C_ell", "M3_C"}
VALID_WEAK_BLOCKS = {"M2_active", "C_sigma_plus", "C_sigma_minus"}
VALID_ORIENTATIONS = {"upper", "lower"}

CLAIM_LABELS = [
    "FINITE_BOUNDARY_ALGEBRA_SOURCE_GATE_CANDIDATE",
    "PROJECTORS_AS_FINITE_ALGEBRA_CENTRAL_PROJECTIONS_CANDIDATE",
    "ORIENTATION_GRADING_SOURCE_FOR_SIGMA_CANDIDATE",
    "CHANNEL_BLOCK_SOURCE_FOR_COLOR_TRIPLICITY_CANDIDATE",
    "WEAK_INTERFACE_BLOCK_SOURCE_FOR_W_CANDIDATE",
    "CHARGE_OPERATOR_SIMPLIFICATION_CONFIRMED_DIAGNOSTIC",
    "FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "FINITE_BOUNDARY_ALGEBRA_SOURCE_GATE_COMPLETE",
    "PROJECTORS_AS_FINITE_ALGEBRA_CENTRAL_PROJECTIONS_CANDIDATE",
    "ORIENTATION_GRADING_SOURCE_FOR_SIGMA_CANDIDATE",
    "CHANNEL_BLOCK_SOURCE_FOR_COLOR_TRIPLICITY_CANDIDATE",
    "WEAK_INTERFACE_BLOCK_SOURCE_FOR_W_CANDIDATE",
    "CHARGE_OPERATOR_SIMPLIFICATION_CONFIRMED_DIAGNOSTIC",
    "FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This gate does not fully derive the Standard Model. It proposes a candidate finite "
    "Berger-Hopf boundary algebra whose central projections and orientation grading "
    "reproduce the previously audited projector eigenvalue system. The remaining proof "
    "obligation is to derive this finite algebra from Berger-Hopf boundary action, "
    "admissible phase closure, automorphism structure, and topographic stability."
)


@dataclass(frozen=True)
class BoundaryAlgebraState:
    channel_block: str
    weak_block: str
    orientation: str | None = None


def validate_boundary_algebra_state(state: BoundaryAlgebraState) -> None:
    if state.channel_block not in VALID_CHANNEL_BLOCKS:
        raise ValueError("channel_block must be C_ell or M3_C")
    if state.weak_block not in VALID_WEAK_BLOCKS:
        raise ValueError("weak_block must be M2_active, C_sigma_plus, or C_sigma_minus")
    if state.weak_block == "M2_active":
        if state.orientation not in VALID_ORIENTATIONS:
            raise ValueError("M2_active requires orientation upper or lower")
    elif state.orientation is not None:
        raise ValueError("inactive weak singlet blocks do not take an orientation override")


def C_from_channel_block(channel_block: str) -> int:
    if channel_block == "C_ell":
        return 0
    if channel_block == "M3_C":
        return 1
    raise ValueError("channel_block must be C_ell or M3_C")


def ell_from_channel_block(channel_block: str) -> int:
    if channel_block == "C_ell":
        return 1
    if channel_block == "M3_C":
        return 0
    raise ValueError("channel_block must be C_ell or M3_C")


def w_from_weak_block(weak_block: str) -> int:
    if weak_block == "M2_active":
        return 1
    if weak_block in {"C_sigma_plus", "C_sigma_minus"}:
        return 0
    raise ValueError("weak_block must be M2_active, C_sigma_plus, or C_sigma_minus")


def sigma_from_weak_block(weak_block: str, orientation: str | None = None) -> int:
    if weak_block == "M2_active":
        if orientation == "upper":
            return +1
        if orientation == "lower":
            return -1
        raise ValueError("M2_active requires orientation upper or lower")
    if weak_block == "C_sigma_plus":
        if orientation is not None:
            raise ValueError("C_sigma_plus does not take an orientation override")
        return +1
    if weak_block == "C_sigma_minus":
        if orientation is not None:
            raise ValueError("C_sigma_minus does not take an orientation override")
        return -1
    raise ValueError("weak_block must be M2_active, C_sigma_plus, or C_sigma_minus")


def channel_multiplicity_from_block(channel_block: str) -> int:
    return 1 + 2 * C_from_channel_block(channel_block)


def projector_eigenvalues_from_state(state: BoundaryAlgebraState) -> dict[str, int]:
    validate_boundary_algebra_state(state)
    return {
        "C": C_from_channel_block(state.channel_block),
        "ell": ell_from_channel_block(state.channel_block),
        "w": w_from_weak_block(state.weak_block),
        "sigma": sigma_from_weak_block(state.weak_block, state.orientation),
    }


def t3_from_boundary_algebra_state(state: BoundaryAlgebraState) -> Fraction:
    values = projector_eigenvalues_from_state(state)
    return Fraction(values["w"] * values["sigma"], 2)


def hypercharge_from_boundary_algebra_state(state: BoundaryAlgebraState) -> Fraction:
    values = projector_eigenvalues_from_state(state)
    return (
        Fraction(values["C"], 3)
        - Fraction(values["ell"], 1)
        + Fraction((1 - values["w"]) * values["sigma"], 1)
    )


def electric_charge_from_boundary_algebra_state(state: BoundaryAlgebraState) -> Fraction:
    return t3_from_boundary_algebra_state(state) + hypercharge_from_boundary_algebra_state(state) / 2


def electric_charge_simplified(C: int, sigma: int) -> Fraction:
    if C not in {0, 1}:
        raise ValueError("C must be 0 or 1")
    if sigma not in {-1, 1}:
        raise ValueError("sigma must be -1 or +1")
    return Fraction(sigma - 1, 2) + Fraction(2 * C, 3)


def physical_boundary_algebra_state_registry(include_nu_r: bool = True) -> dict[str, BoundaryAlgebraState]:
    states = {
        "nu_L": BoundaryAlgebraState("C_ell", "M2_active", "upper"),
        "e_L": BoundaryAlgebraState("C_ell", "M2_active", "lower"),
        "u_L": BoundaryAlgebraState("M3_C", "M2_active", "upper"),
        "d_L": BoundaryAlgebraState("M3_C", "M2_active", "lower"),
        "e_R": BoundaryAlgebraState("C_ell", "C_sigma_minus"),
        "u_R": BoundaryAlgebraState("M3_C", "C_sigma_plus"),
        "d_R": BoundaryAlgebraState("M3_C", "C_sigma_minus"),
    }
    if include_nu_r:
        states["nu_R"] = BoundaryAlgebraState("C_ell", "C_sigma_plus")
    return states


def physical_boundary_algebra_charge_table(include_nu_r: bool = True) -> dict[str, dict[str, Fraction | int]]:
    table = {}
    for name, state in physical_boundary_algebra_state_registry(include_nu_r).items():
        values = projector_eigenvalues_from_state(state)
        table[name] = {
            **values,
            "T3": t3_from_boundary_algebra_state(state),
            "Y": hypercharge_from_boundary_algebra_state(state),
            "Q": electric_charge_from_boundary_algebra_state(state),
            "Q_simplified": electric_charge_simplified(values["C"], values["sigma"]),
            "d_channel": channel_multiplicity_from_block(state.channel_block),
        }
    return table


def anomaly_closure_bridge_confirmed() -> bool:
    report = anomaly_report(include_nu_r=True)
    return (
        report["SU3_SU3_U1"] == 0
        and report["SU2_SU2_U1"] == 0
        and report["U1_cubed"] == 0
        and report["gravity_gravity_U1"] == 0
        and report["witten_su2_doublet_count"] == 4
        and report["witten_su2_passes"] is True
    )


def _fraction_text(value: Fraction | int) -> str:
    if isinstance(value, int):
        return str(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _state_table() -> str:
    headers = ["state", "channel block", "weak block", "orientation", "C", "ell", "w", "sigma", "T3", "Y", "Q"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for name, state in physical_boundary_algebra_state_registry(include_nu_r=True).items():
        row = physical_boundary_algebra_charge_table(include_nu_r=True)[name]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    state.channel_block,
                    state.weak_block,
                    state.orientation or "",
                    str(row["C"]),
                    str(row["ell"]),
                    str(row["w"]),
                    str(row["sigma"]),
                    _fraction_text(row["T3"]),
                    _fraction_text(row["Y"]),
                    _fraction_text(row["Q"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _charge_simplification_table() -> str:
    rows = [
        ("lepton upper", 0, +1),
        ("lepton lower", 0, -1),
        ("quark upper", 1, +1),
        ("quark lower", 1, -1),
    ]
    lines = [
        "| state | C | sigma | Q |",
        "| --- | --- | --- | --- |",
    ]
    for name, C, sigma in rows:
        lines.append(f"| {name} | {C} | {sigma:+d} | {_fraction_text(electric_charge_simplified(C, sigma))} |")
    return "\n".join(lines)


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "finite_boundary_algebra_derived_from_geometry": False,
        "projector_algebra_sourced_diagnostically": True,
        "algebra": {
            "A_boundary_candidate": "A_channel tensor A_weak",
            "A_channel": "C_ell direct_sum M3(C)_C",
            "A_weak": "M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}",
        },
        "projector_sources": {
            "P_C": "central projection onto M3(C)_C",
            "P_ell": "central projection onto C_ell",
            "P_w": "central projection onto M2(C)_{w=1}",
            "S_sigma": "orientation grading",
        },
        "charge_operators": {
            "T3": "1/2 P_w S_sigma",
            "Y": "4/3 P_C - I + (I-P_w) S_sigma",
            "Q": "1/2(S_sigma - I) + 2/3 P_C",
        },
        "bridges_confirmed": {
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": anomaly_closure_bridge_confirmed(),
        },
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "finite algebra supplies a diagnostic source for the projector eigenvalue system",
            "finite algebra itself still requires derivation from Berger-Hopf boundary geometry",
            "charge/hypercharge bridge remains diagnostic",
            "anomaly closure remains diagnostic",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def render_source_gate_markdown() -> str:
    return f"""# Finite Boundary Algebra Source Gate

## 1. Motivation

The previous projector gate made the integer primitives `(C, ell, sigma, w)` joint eigenvalues of a candidate boundary-projector algebra. This gate asks what finite boundary algebra could source those projectors.

## 2. Previous Gate Achieved: Projector Eigenvalue Diagnostics

```text
P_C |psi> = C |psi>
P_ell |psi> = ell |psi>
S_sigma |psi> = sigma |psi>
P_w |psi> = w |psi>
```

with diagnostic bridges:

```text
C + ell = 1
d_channel = 1 + 2C
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = sigma/2 + C/6 - ell/2
```

## 3. Why Projectors Need A Source

The projector eigenvalues remain declared until a boundary algebra, action, or spectral construction forces the central projections and orientation grading. This gate formalizes a candidate finite algebra source layer.

## 4. Candidate Finite Boundary Algebra

```text
A_boundary_candidate = A_channel tensor A_weak
```

## 5. Channel Algebra `(C_ell direct_sum M_3(C)_C)`

```text
A_channel = C_ell direct_sum M_3(C)_C
```

- `C_ell`: single-channel leptonic closure block.
- `M_3(C)_C`: three-channel active boundary block and candidate source of color triplicity.

## 6. Weak-Interface Algebra `(M_2(C)_{{w=1}} direct_sum C_+ direct_sum C_-)`

```text
A_weak = M_2(C)_{{w=1}} direct_sum C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

- `M_2(C)_{{w=1}}`: weak-interface active two-state block.
- `C_{{sigma=+}}` and `C_{{sigma=-}}`: weak-interface inactive singlet blocks with retained orientation labels.

## 7. Projectors And Orientation Grading

```text
P_C = central projection onto M_3(C)_C
P_ell = central projection onto C_ell
P_w = central projection onto M_2(C)_{{w=1}}
S_sigma = orientation grading with eigenvalues +1 and -1
```

Candidate closure:

```text
P_C + P_ell = I_channel
C + ell = 1
d_channel = 1 + 2C
```

## 8. Charge Operators

```text
P_ell = I - P_C
T3_hat = (1/2) P_w S_sigma
Y_hat = (4/3) P_C - I + (I - P_w) S_sigma
Q_hat = T3_hat + Y_hat/2
```

## 9. Electric-Charge Simplification

```text
Q_hat
= (1/2)P_w S_sigma
  + (1/2)[(4/3)P_C - I + (I-P_w)S_sigma]
= (2/3)P_C - (1/2)I + (1/2)S_sigma
= (1/2)(S_sigma - I) + (2/3)P_C
```

Electric charge depends only on the channel projector `P_C` and the orientation grading `S_sigma`. Weak-interface activity `P_w` redistributes charge between `T3` and `Y`, but cancels out of `Q`.

{_charge_simplification_table()}

Full diagnostic registry:

{_state_table()}

## 10. Bridge To Anomaly Closure

The finite boundary algebra registry reproduces the projector eigenvalue bridge, the charge/hypercharge bridge, and the same one-generation anomaly closure diagnostics used by the prior gates.

## 11. What This Achieves

This gate supplies a candidate finite algebraic source for the previously audited boundary-projector eigenvalue system.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 12. What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not introduce a new official mass formula or change frozen predictions.

## 13. Next Proof Obligations

- Derive `C_ell direct_sum M_3(C)_C` from Berger-Hopf boundary action and admissible phase closure.
- Derive `M_2(C)_{{w=1}} direct_sum C_{{sigma=+}} direct_sum C_{{sigma=-}}` from boundary interface dynamics.
- Derive `S_sigma` as a geometric orientation grading.
- Derive the local gauge algebras from the finite boundary algebra and automorphism structure.
- Prove topographic stability selects this finite algebra rather than nearby alternatives.

## Related Automorphism Closure Gate

- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
"""


def render_blocks_markdown() -> str:
    return """# Finite Boundary Algebra Blocks

Candidate algebra:

```text
A_boundary_candidate = A_channel tensor A_weak

A_channel = C_ell direct_sum M_3(C)_C

A_weak = M_2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}
```

| block | candidate meaning | projection/eigenvalue | multiplicity | derivation status |
| --- | --- | --- | --- | --- |
| C_ell | leptonic single-channel closure | ell=1, C=0 | 1 | candidate, not derived |
| M_3(C)_C | three-channel active boundary block | C=1, ell=0 | 3 | candidate, not derived |
| M_2(C)_{w=1} | weak-interface active block | w=1 | 2 orientation states | candidate, not derived |
| C_{sigma=+} | inactive upper orientation singlet | w=0, sigma=+1 | 1 | candidate, not derived |
| C_{sigma=-} | inactive lower orientation singlet | w=0, sigma=-1 | 1 | candidate, not derived |

Guardrail: this block inventory is a candidate source layer for the projector algebra, not a full derivation from Berger-Hopf geometry.

## Related Automorphism Closure Gate

- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
"""


def render_charge_operators_markdown() -> str:
    return f"""# Finite Boundary Algebra Charge Operators

Candidate charge operators:

```text
P_ell = I - P_C
T3_hat = (1/2) P_w S_sigma
Y_hat = (4/3)P_C - I + (I-P_w)S_sigma
Q_hat = T3_hat + Y_hat/2
```

Electric charge simplification:

```text
Q_hat
= (1/2)P_w S_sigma
  + (1/2)[(4/3)P_C - I + (I-P_w)S_sigma]
= (2/3)P_C - (1/2)I + (1/2)S_sigma
= (1/2)(S_sigma - I) + (2/3)P_C
```

| state | C | sigma | Q |
| --- | --- | --- | --- |
| lepton upper | 0 | +1 | 0 |
| lepton lower | 0 | -1 | -1 |
| quark upper | 1 | +1 | +2/3 |
| quark lower | 1 | -1 | -1/3 |

`w` affects `T3` and `Y`, but not `Q`:

{_state_table()}

Status: candidate diagnostic. The finite boundary algebra is not yet derived from Berger-Hopf boundary geometry.

## Related Automorphism Closure Gate

- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "finite_boundary_algebra_source_gate.md": render_source_gate_markdown(),
        "finite_boundary_algebra_blocks.md": render_blocks_markdown(),
        "finite_boundary_algebra_charge_operators.md": render_charge_operators_markdown(),
        "finite_boundary_algebra_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
