from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import cos
from pathlib import Path


BRANCH = "bhsm-boundary-action-second-variation-audit-v1"
STATUS = "candidate_only"

VERDICT_LABELS = [
    "BOUNDARY_ACTION_SECOND_VARIATION_AUDIT_COMPLETE",
    "PHASE_CLOSURE_HESSIAN_COEFFICIENT_CANDIDATE",
    "ORIENTATION_INVOLUTION_HESSIAN_BLOCK_CANDIDATE",
    "CYCLIC_CHANNEL_HESSIAN_COEFFICIENT_CANDIDATE",
    "TOPOGRAPHIC_EXCESS_HESSIAN_BRIDGE_CANDIDATE",
    "ACTION_TERMS_TO_HESSIAN_PROJECTORS_DIAGNOSTIC",
    "BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This audit does not fully derive the Standard Model. It computes candidate "
    "second-variation behavior of the finite boundary action surrogates and shows "
    "that their local quadratic structure supports the previously introduced "
    "Hessian projector scaffold. The full Berger-Hopf boundary action and full "
    "topographic Hessian remain unproved."
)

REQUIRED_CONCLUSION_LANGUAGE = (
    "The audit supports a candidate route from realized boundary action terms to "
    "the Hessian projector scaffold. It does not prove that the actual Berger-Hopf "
    "boundary action uniquely produces these projectors."
)


@dataclass(frozen=True)
class SecondVariationResult:
    term: str
    sector: str
    coefficient: Fraction
    convention: str
    interpretation: str


def validate_positive_int(value: int, name: str = "value") -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def phase_hessian_coefficient(d: int) -> Fraction:
    validate_positive_int(d, "d")
    return Fraction(2 * d * d, 1)


def phase_quadratic_coefficient(d: int) -> Fraction:
    validate_positive_int(d, "d")
    return Fraction(d * d, 1)


def phase_exact_value_near_closure(d: int, epsilon: float) -> float:
    validate_positive_int(d, "d")
    return float(2.0 - 2.0 * cos(d * epsilon))


def orientation_hessian_matrix(
    size: int = 2, lambda_trace: Fraction = Fraction(1, 1)
) -> tuple[tuple[Fraction, ...], ...]:
    validate_positive_int(size, "size")
    lambda_trace = Fraction(lambda_trace)
    return tuple(
        tuple(
            (Fraction(8, 1) if row == col else Fraction(0, 1))
            + Fraction(2, 1) * lambda_trace
            for col in range(size)
        )
        for row in range(size)
    )


def orientation_pair_hessian_matrix(
    lambda_trace: Fraction = Fraction(1, 1)
) -> tuple[tuple[Fraction, ...], ...]:
    return orientation_hessian_matrix(2, lambda_trace)


def orientation_hessian_positive_diagonal(
    matrix: tuple[tuple[Fraction, ...], ...]
) -> bool:
    if not matrix:
        return False
    return all(row[index] > 0 for index, row in enumerate(matrix))


def cyclic_hessian_coefficient(order: int = 3) -> Fraction:
    validate_positive_int(order, "order")
    return Fraction(2 * order * order, 1)


def topographic_lambda(k: int, B: Fraction = Fraction(1, 1)) -> Fraction:
    if not isinstance(k, int) or k < 0:
        raise ValueError("k must be a nonnegative integer")
    B = Fraction(B)
    if B < 0:
        raise ValueError("B must be nonnegative for the stable diagnostic convention")
    return Fraction(k * k, 1) + B * Fraction(k**4, 1)


def excess_hessian_coefficient(d: int, gamma: Fraction = Fraction(1, 1)) -> Fraction:
    validate_positive_int(d, "d")
    gamma = Fraction(gamma)
    if gamma < 0:
        raise ValueError("gamma must be nonnegative")
    if d <= 3:
        return Fraction(0, 1)
    return Fraction(2, 1) * gamma


def projector_second_variation_registry() -> dict:
    return {
        "P_ref": {
            "sector": "reference",
            "coefficient": "0",
            "interpretation": "reference-normalized",
        },
        "P_orient": {
            "sector": "orientation",
            "coefficient": "8 I + 2 lambda_trace J",
            "matrix_lambda_1": [
                [str(value) for value in row]
                for row in orientation_pair_hessian_matrix(Fraction(1, 1))
            ],
            "interpretation": "orientation involution Hessian block",
        },
        "P_cyclic": {
            "sector": "cyclic",
            "coefficient": str(cyclic_hessian_coefficient(3)),
            "interpretation": "cyclic-channel Hessian coefficient",
        },
        "P_excess": {
            "sector": "excess",
            "coefficient": str(excess_hessian_coefficient(4)),
            "interpretation": "excess/gapped Hessian coefficient",
        },
    }


def hessian_projector_scaffold_supported() -> bool:
    registry = projector_second_variation_registry()
    return (
        registry["P_ref"]["coefficient"] == "0"
        and orientation_hessian_positive_diagonal(
            orientation_pair_hessian_matrix(Fraction(1, 1))
        )
        and cyclic_hessian_coefficient(3) > 0
        and excess_hessian_coefficient(4) > 0
    )


def selected_low_energy_dims_from_second_variation(max_d: int = 8) -> list[int]:
    validate_positive_int(max_d, "max_d")
    selected = []
    for d in range(1, max_d + 1):
        phase_stiff = phase_hessian_coefficient(d) > 0
        low_branch = excess_hessian_coefficient(d) == 0
        if phase_stiff and low_branch:
            selected.append(d)
    return selected


def second_variation_summary() -> dict:
    return {
        "phase_H_1": str(phase_hessian_coefficient(1)),
        "phase_H_2": str(phase_hessian_coefficient(2)),
        "phase_H_3": str(phase_hessian_coefficient(3)),
        "orientation_pair_matrix_lambda_1": [
            [str(value) for value in row]
            for row in orientation_pair_hessian_matrix(Fraction(1, 1))
        ],
        "cyclic_H_3": str(cyclic_hessian_coefficient(3)),
        "topographic_lambda_0": str(topographic_lambda(0)),
        "topographic_lambda_1": str(topographic_lambda(1)),
        "topographic_lambda_2": str(topographic_lambda(2)),
        "excess_H_4": str(excess_hessian_coefficient(4)),
        "projector_scaffold_supported": hessian_projector_scaffold_supported(),
        "selected_low_energy_dims": selected_low_energy_dims_from_second_variation(8),
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "boundary_action_fully_derived": False,
        "full_hessian_proof_complete": False,
        "second_variation_audit_complete": True,
        "second_variation_coefficients": {
            "H_phase_d": "2 d^2",
            "H_orientation": "8 I + 2 lambda_trace J",
            "H_cyclic_n": "2 n^2",
            "H_cyclic_3": "18",
            "H_excess": "0 for d<=3, 2 gamma for d>3 continuous-surrogate classification",
        },
        "hessian_projector_bridge": {
            "P_ref": "reference-normalized",
            "P_orient": "orientation involution Hessian block",
            "P_cyclic": "cyclic-channel Hessian coefficient",
            "P_excess": "excess/gapped Hessian coefficient",
        },
        "diagnostic_selected_low_energy_dims": selected_low_energy_dims_from_second_variation(8),
        "bridges_preserved": {
            "boundary_action_term_realization": True,
            "boundary_action_hessian_scaffold": True,
            "closure_spectrum_selection": True,
            "finite_boundary_algebra_bridge": True,
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "negative_results": [
            "boundary action not fully derived",
            "full Hessian proof remains open",
            "second-variation coefficients are computed for finite diagnostic surrogates",
            "actual Berger-Hopf boundary Hessian remains to be derived",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "candidate second-variation behavior documented",
            "action terms support Hessian projector scaffold diagnostically",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "summary": second_variation_summary(),
    }


def _projector_table() -> str:
    lines = [
        "| projector | coefficient / block | interpretation |",
        "| --- | --- | --- |",
    ]
    registry = projector_second_variation_registry()
    for name in ["P_ref", "P_orient", "P_cyclic", "P_excess"]:
        row = registry[name]
        lines.append(f"| `{name}` | `{row['coefficient']}` | {row['interpretation']} |")
    return "\n".join(lines)


def _selected_dims_table() -> str:
    lines = [
        "| d | H_phase(d) | H_excess(d) | selected low-energy |",
        "| --- | --- | --- | --- |",
    ]
    for d in range(1, 9):
        selected = d in selected_low_energy_dims_from_second_variation(8)
        lines.append(
            f"| {d} | {phase_hessian_coefficient(d)} | {excess_hessian_coefficient(d)} | "
            f"{str(selected).lower()} |"
        )
    return "\n".join(lines)


def render_audit_markdown() -> str:
    return f"""# Boundary Action Second-Variation Audit

## Motivation

The boundary action term-realization audit supplied finite candidate functionals for the phase, orientation, cyclic-channel, topographic, and excess terms. This audit computes their local quadratic behavior near candidate minima.

## Previous Gate Achieved: Candidate Action Term Realization

The previous gate realized the schematic terms:

```text
S_phase(d, theta)=|exp(i d theta)-1|^2
S_orientation(R)=||R^2-I||^2 + lambda_trace |Tr(R)|^2
S_cyclic_channel: U_3^3=I diagnostic
S_topographic: lambda_n(k)=k^2+B*k^4
S_excess(d)=gamma max(d-3,0)^2
```

## Why Second Variation Is Needed

The Hessian projector scaffold needs local quadratic coefficients, not only finite functional labels. The coefficients here are computed for diagnostic surrogates and are not yet the actual Berger-Hopf Hessian.

## Phase Closure Hessian Coefficient

For `theta = 2*pi/d + epsilon`,

```text
S_phase = 2 - 2 cos(d epsilon)
        = d^2 epsilon^2 + O(epsilon^4)
```

Using `S ~= 1/2 H epsilon^2`, the candidate Hessian coefficient is

```text
H_phase(d)=2d^2
```

This enforces local phase-closure stiffness but does not by itself select the closure spectrum.

## Orientation Involution Hessian Block

For `R = diag(s_i + epsilon_i)` with `s_i^2=1`,

```text
S_orientation_quad ~= 4 sum_i epsilon_i^2 + lambda_trace (sum_i epsilon_i)^2
H_orientation = 8 I + 2 lambda_trace J
```

For `R=diag(+1,-1)`, this is a candidate source of `Z_2` orientation grading, `S_sigma`, `P_orient`, and the `d=2` orientation-pair closure. It is not a full `SU(2)` derivation.

## Cyclic-Channel Hessian Coefficient

For an order-`n` cyclic phase perturbation,

```text
S_cyclic(n, epsilon)=|exp(i n epsilon)-1|^2
S_cyclic ~= n^2 epsilon^2
H_cyclic(n)=2n^2
```

For `n=3`, `H_cyclic(3)=18`. This supports a candidate stable cyclic-channel Hessian coefficient for `P_cyclic`, not a full `SU(3)` derivation.

## Topographic/Excess Hessian Bridge

The topographic diagnostic uses

```text
lambda_n(k)=k^2+B*k^4
```

with `B>0` as the stable convention. The excess term uses

```text
S_excess(d)=gamma max(d-3,0)^2
H_excess = 0 for d <= 3
H_excess = 2 gamma for d > 3
```

Higher closures are gapped/excess under the diagnostic scaffold, not mathematically impossible.

## Candidate Hessian Projector Decomposition

{_projector_table()}

## Closure Spectrum Bridge

{_selected_dims_table()}

## Finite Algebra Bridge

The selected diagnostic dimensions `[1, 2, 3]` preserve the finite algebra bridge to `C`, `M2(C)`, and `M3(C)`.

## Projector Eigenvalue Bridge

The local second-variation coefficients support the existing `P_ref`, `P_orient`, `P_cyclic`, and `P_excess` decomposition diagnostically.

## Charge/Hypercharge And Anomaly Bridge

Because the finite algebra and projector bridges are preserved, the downstream charge/hypercharge and anomaly bridges remain unchanged. No official or frozen prediction output is recomputed here.

## What This Achieves

{REQUIRED_CONCLUSION_LANGUAGE}

## What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It also makes no replacement claim, no full gauge-group derivation claim, and no exclusion claim for higher closures.

## Next Proof Obligations

- Derive the finite surrogate functionals from the full Berger-Hopf boundary action.
- Derive the second variation from the complete boundary action rather than diagnostic coordinates.
- Prove the full topographic Hessian and projector decomposition.

## Claim Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_phase_markdown() -> str:
    return """# Phase Closure Second Variation

The phase closure functional is

```text
S_phase(d, theta)=|exp(i d theta)-1|^2
```

At

```text
theta = 2*pi/d + epsilon
```

we obtain

```text
S_phase = 2 - 2 cos(d epsilon)
        = d^2 epsilon^2 + O(epsilon^4)
```

Under the `S ~= 1/2 H epsilon^2` convention,

```text
H_phase(d)=2d^2
```

Guardrail: this enforces local phase-closure stiffness but does not alone select the closure spectrum.
"""


def render_orientation_markdown() -> str:
    return """# Orientation Involution Second Variation

The orientation functional is

```text
S_orientation(R)=||R^2-I||^2 + lambda_trace |Tr(R)|^2
```

For the diagonal surrogate

```text
R = diag(s_i + epsilon_i), s_i^2=1
```

the quadratic term is

```text
S_orientation_quad ~= 4 sum_i epsilon_i^2 + lambda_trace (sum_i epsilon_i)^2
```

and the diagnostic Hessian is

```text
H_orientation = 8 I + 2 lambda_trace J
```

For `R=diag(+1,-1)`, this is a candidate source of `Z_2` orientation grading, `S_sigma`, `P_orient`, and `d=2` orientation-pair closure.

Guardrail: this is not a full `SU(2)` derivation.
"""


def render_cyclic_markdown() -> str:
    return """# Cyclic-Channel Second Variation

The cyclic-channel diagnostic is

```text
S_cyclic(n, epsilon)=|exp(i n epsilon)-1|^2
```

Thus

```text
S_cyclic ~= n^2 epsilon^2
H_cyclic(n)=2n^2
```

For `n=3`,

```text
H_cyclic(3)=18
```

This is a candidate stable cyclic-channel Hessian coefficient for `P_cyclic`.

Guardrail: this is not a full `SU(3)` derivation.
"""


def render_topographic_markdown() -> str:
    return """# Topographic/Excess Hessian Bridge

The topographic branch diagnostic uses

```text
lambda_n(k)=k^2+B*k^4
```

Branch interpretation:

- reference-normalized mode;
- orientation stable branch candidate;
- cyclic stable branch candidate;
- excess gapped branch candidate.

The excess term is

```text
S_excess(d)=gamma max(d-3,0)^2
```

For continuous-surrogate classification:

```text
H_excess = 0 for d <= 3
H_excess = 2 gamma for d > 3
```

Guardrail: higher closures are gapped/excess under the diagnostic scaffold, not mathematically impossible.
"""


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "boundary_action_second_variation_audit.md": render_audit_markdown(),
        "phase_closure_second_variation.md": render_phase_markdown(),
        "orientation_involution_second_variation.md": render_orientation_markdown(),
        "cyclic_channel_second_variation.md": render_cyclic_markdown(),
        "topographic_excess_hessian_bridge.md": render_topographic_markdown(),
        "boundary_action_second_variation_results.json": json.dumps(
            payload, indent=2, sort_keys=True
        )
        + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
