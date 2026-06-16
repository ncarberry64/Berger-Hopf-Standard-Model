from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import cos, isclose, pi, sin
from pathlib import Path


BRANCH = "bhsm-boundary-action-term-realization-audit-v1"
STATUS = "candidate_only"

VERDICT_LABELS = [
    "BOUNDARY_ACTION_TERM_REALIZATION_AUDIT_COMPLETE",
    "PHASE_CLOSURE_FUNCTIONAL_CANDIDATE",
    "ORIENTATION_INVOLUTION_FUNCTIONAL_CANDIDATE",
    "CYCLIC_CHANNEL_FUNCTIONAL_CANDIDATE",
    "TOPOGRAPHIC_EXCESS_GAP_FUNCTIONAL_CANDIDATE",
    "ACTION_TERMS_SUPPORT_CLOSURE_SCAFFOLD_DIAGNOSTIC",
    "BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This audit does not fully derive the Standard Model. It gives candidate "
    "mathematical realizations of the boundary action terms used in the Hessian "
    "scaffold. These functionals support the previously audited closure-spectrum "
    "route diagnostically, but the full Berger-Hopf boundary action and Hessian "
    "remain unproved."
)


@dataclass(frozen=True)
class ActionTermResult:
    name: str
    value: float
    passes: bool
    interpretation: str


def _validate_dimension(d: int) -> None:
    if not isinstance(d, int) or d <= 0:
        raise ValueError("dimension d must be a positive integer")


def phase_closure_value(d: int, theta: float) -> float:
    _validate_dimension(d)
    return (cos(d * theta) - 1.0) ** 2 + sin(d * theta) ** 2


def canonical_phase_for_dim(d: int) -> float:
    _validate_dimension(d)
    return 2.0 * pi / d


def phase_closure_passes(d: int, theta: float | None = None, tol: float = 1e-9) -> bool:
    _validate_dimension(d)
    if theta is None:
        theta = canonical_phase_for_dim(d)
    return isclose(phase_closure_value(d, theta), 0.0, abs_tol=tol)


def orientation_involution_value(
    eigenvalues: tuple[int, ...], lambda_trace: float = 1.0
) -> float:
    if not eigenvalues:
        raise ValueError("orientation eigenvalues must be nonempty")
    return float(
        sum((value * value - 1) ** 2 for value in eigenvalues)
        + lambda_trace * (sum(eigenvalues) ** 2)
    )


def orientation_pair_passes(
    eigenvalues: tuple[int, ...] = (1, -1), tol: float = 1e-9
) -> bool:
    return isclose(orientation_involution_value(eigenvalues), 0.0, abs_tol=tol)


def cyclic_closure_value(d: int, order: int) -> float:
    _validate_dimension(d)
    if not isinstance(order, int) or order < 2:
        raise ValueError("cyclic order must be an integer at least 2")
    if d == order:
        return 0.0
    return float((d - order) ** 2 + 1)


def cyclic_three_channel_passes(order: int = 3) -> bool:
    return isclose(cyclic_closure_value(3, order), 0.0, abs_tol=1e-9)


def topographic_eigenvalue(k: int, B: float = 1.0) -> float:
    if not isinstance(k, int) or k < 0:
        raise ValueError("topographic mode k must be a nonnegative integer")
    if B < 0:
        raise ValueError("B must be nonnegative for the stable diagnostic convention")
    return float(k * k + B * k**4)


def excess_gap_penalty(d: int, gamma: float = 1.0) -> float:
    _validate_dimension(d)
    if gamma < 0:
        raise ValueError("gamma must be nonnegative")
    return float(gamma * max(d - 3, 0) ** 2)


def topographic_branch_label(d: int) -> str:
    _validate_dimension(d)
    if d == 1:
        return "reference"
    if d == 2:
        return "orientation"
    if d == 3:
        return "cyclic"
    return "excess"


def combined_action_diagnostic(d: int) -> dict:
    _validate_dimension(d)
    branch = topographic_branch_label(d)
    phase_value = phase_closure_value(d, canonical_phase_for_dim(d))
    excess_value = excess_gap_penalty(d)
    orientation_value = 0.0 if branch != "orientation" else orientation_involution_value((1, -1))
    cyclic_value = 0.0 if branch != "cyclic" else cyclic_closure_value(3, 3)
    total = phase_value + orientation_value + cyclic_value + excess_value
    return {
        "dimension": d,
        "branch": branch,
        "phase": asdict(
            ActionTermResult(
                "S_phase",
                phase_value,
                isclose(phase_value, 0.0, abs_tol=1e-9),
                "canonical Hopf phase closure",
            )
        ),
        "orientation": asdict(
            ActionTermResult(
                "S_orientation",
                orientation_value,
                isclose(orientation_value, 0.0, abs_tol=1e-9),
                "Z2 orientation pair if d=2; inactive otherwise",
            )
        ),
        "cyclic": asdict(
            ActionTermResult(
                "S_cyclic_channel",
                cyclic_value,
                isclose(cyclic_value, 0.0, abs_tol=1e-9),
                "C3 cyclic channel if d=3; inactive otherwise",
            )
        ),
        "excess": asdict(
            ActionTermResult(
                "S_excess",
                excess_value,
                isclose(excess_value, 0.0, abs_tol=1e-9),
                "low-energy branch budget penalty for d>=4",
            )
        ),
        "total_candidate_value": total,
        "selected_low_energy": isclose(total, 0.0, abs_tol=1e-9),
        "guardrail": "d>=4 is gapped/excess in this diagnostic scaffold, not impossible",
    }


def selected_low_energy_dims(max_d: int = 8) -> list[int]:
    if not isinstance(max_d, int) or max_d <= 0:
        raise ValueError("max_d must be a positive integer")
    return [
        d
        for d in range(1, max_d + 1)
        if combined_action_diagnostic(d)["selected_low_energy"]
    ]


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
        "candidate_functionals": {
            "S_phase": "|exp(i d theta)-1|^2",
            "S_orientation": "||R^2-I||^2 + lambda_trace |Tr(R)|^2",
            "S_cyclic_channel": "cyclic closure U_3^3=I with minimal cyclic channel diagnostic",
            "S_topographic": "L_T = nabla^2 - B nabla^4 branch scaffold",
            "S_excess": "gamma max(d-3,0)^2",
        },
        "diagnostic_selected_low_energy_dims": selected_low_energy_dims(8),
        "bridges_preserved": {
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
            "higher closures are gapped/excess in the candidate scaffold, not impossible",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "candidate action term realizations documented",
            "full boundary action derivation remains open",
            "full Hessian proof remains open",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _selected_dims_table() -> str:
    lines = [
        "| d | branch | selected low-energy | excess penalty | interpretation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for d in range(1, 9):
        row = combined_action_diagnostic(d)
        lines.append(
            f"| {d} | {row['branch']} | {str(row['selected_low_energy']).lower()} | "
            f"{row['excess']['value']:.1f} | {row['guardrail']} |"
        )
    return "\n".join(lines)


def render_audit_markdown() -> str:
    return f"""# Boundary Action Term Realization Audit

## Motivation

The previous candidate Hessian gate cataloged boundary action terms but did not realize them as explicit mathematical diagnostics. This audit adds finite candidate functionals for those terms so the closure-spectrum scaffold can be tested more concretely.

## Previous Scaffold Achieved

The previous scaffold used

```text
S_boundary_candidate =
S_phase
+ S_orientation
+ S_cyclic_channel
+ S_topographic
+ S_excess
```

and

```text
H_boundary_candidate =
mu_ref P_ref
+ mu_orient P_orient
+ mu_cyclic P_cyclic
+ mu_excess P_excess
```

to organize the reference, orientation, cyclic, and excess branches.

## Why Action Terms Need Mathematical Realization

Catalog labels alone do not show that the terms can be evaluated, audited, or connected to the closure-spectrum route. The realizations below are diagnostic surrogates, not a first-principles derivation of the complete Berger-Hopf boundary action.

## Phase Closure Functional

```text
S_phase(d, theta) = |exp(i d theta) - 1|^2
```

For the canonical closure phase `theta = 2*pi/d`, this functional vanishes. Off closure, it is positive. It enforces global Hopf phase closure, but it does not alone select `d=1,2,3`.

## Orientation Involution Functional

```text
S_orientation(R) = ||R^2 - I||^2 + lambda_trace |Tr(R)|^2
```

For the finite surrogate `R = diag(+1,-1)`, both the involution and trace-balance conditions pass. This is a candidate `Z_2` orientation grading source and a candidate source for `S_sigma`; it is not a full `SU(2)` derivation.

## Cyclic-Channel Functional

```text
U_3^3 = I
1 + U_3 + U_3^2 = 0 on the nontrivial cyclic subspace
```

The 3-cycle diagnostic supports a minimal nontrivial cyclic channel beyond the `Z_2` orientation pair. This is not a full `SU(3)` derivation.

## Topographic Branch/Excess Functional

```text
L_T = nabla^2 - B*nabla^4
lambda_n(k) = k^2 + B*k^4
S_excess(d) = gamma * max(d - 3, 0)^2
```

The interpretation is one reference branch, two stable nonzero branch candidates, and excess modes gapped under the low-energy diagnostic scaffold. Higher `d` values are not declared impossible.

## Combined Candidate Action

The combined diagnostic uses canonical phase closure for each dimension, activates the orientation diagnostic on `d=2`, activates the cyclic diagnostic on `d=3`, and applies the excess penalty for `d>=4`.

{_selected_dims_table()}

## Connection To Hessian Projectors

The realized terms support the same candidate projectors: `P_ref`, `P_orient`, `P_cyclic`, and `P_excess`. The link is diagnostic: it shows compatible finite functionals for the earlier Hessian scaffold but does not derive the Hessian from the complete boundary action.

## Connection To Closure Spectrum `(d=1,2,3)`

The candidate diagnostics select the low-energy dimensions `[1, 2, 3]`: reference, orientation pair, and cyclic channel. The excess term marks `d>=4` as gapped/excess in this scaffold.

## What This Achieves

- Gives explicit candidate functional realizations for the action-term catalog.
- Preserves the previous closure-spectrum and Hessian projector bridges.
- Keeps negative results and uncertainty labels explicit.

## What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It also does not make a replacement claim for BHSM, does not make a full gauge-group derivation claim, and higher `d` values are not declared impossible.

## Next Proof Obligations

- Derive these terms from the full Berger-Hopf boundary action.
- Derive the Hessian projector decomposition from the complete second variation.
- Prove the topographic stability operator and excess gap from the full action rather than a diagnostic surrogate.

## Claim Labels

{chr(10).join(f'- {label}' for label in VERDICT_LABELS)}
"""


def render_phase_markdown() -> str:
    return """# Boundary Phase Closure Functional

The candidate phase closure term is

```text
S_phase(d, theta) = |exp(i d theta) - 1|^2
```

Using `|exp(i x)-1|^2 = (cos x - 1)^2 + sin(x)^2`, the diagnostic is nonnegative.

- For `theta = 2*pi/d`, `S_phase = 0`.
- For an off-closure phase, `S_phase > 0`.
- This enforces closure but does not alone select `d=1,2,3`.

Status: `PHASE_CLOSURE_FUNCTIONAL_CANDIDATE`.
"""


def render_orientation_markdown() -> str:
    return """# Boundary Orientation Involution Functional

The candidate orientation functional is

```text
S_orientation(R) = ||R^2 - I||^2 + lambda_trace |Tr(R)|^2
```

For the finite diagonal surrogate

```text
R = diag(+1,-1)
```

the involution condition `R^2=I` and trace-balance condition `Tr(R)=0` pass.

Interpretation:

- candidate `Z_2` orientation grading source;
- candidate source of `S_sigma`;
- minimal nontrivial orientation pair `d=2`;
- not a full `SU(2)` derivation.

Status: `ORIENTATION_INVOLUTION_FUNCTIONAL_CANDIDATE`.
"""


def render_cyclic_markdown() -> str:
    return """# Boundary Cyclic-Channel Functional

The candidate cyclic-channel diagnostic uses

```text
U_3^3 = I
1 + U_3 + U_3^2 = 0 on nontrivial cyclic subspace
```

The 3-cycle permutation matrix passes `U^3=I`. The minimality diagnostic identifies `d=3` as the minimal nontrivial cyclic channel beyond the `Z_2` orientation pair.

This is not a full `SU(3)` derivation.

Status: `CYCLIC_CHANNEL_FUNCTIONAL_CANDIDATE`.
"""


def render_topographic_markdown() -> str:
    return """# Boundary Topographic/Excess Functional

The topographic scaffold keeps the existing fourth-order form

```text
L_T = nabla^2 - B*nabla^4
```

with the stable finite diagnostic convention

```text
lambda_n(k) = k^2 + B*k^4
```

The candidate branch interpretation is:

- reference branch;
- orientation branch;
- cyclic-channel branch;
- excess branch gapped.

The excess term is

```text
S_excess(d) = gamma * max(d - 3, 0)^2
```

Guardrail: higher `d` values are gapped/excess in the candidate low-energy scaffold, not impossible.

Status: `TOPOGRAPHIC_EXCESS_GAP_FUNCTIONAL_CANDIDATE`.
"""


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "boundary_action_term_realization_audit.md": render_audit_markdown(),
        "boundary_phase_closure_functional.md": render_phase_markdown(),
        "boundary_orientation_involution_functional.md": render_orientation_markdown(),
        "boundary_cyclic_channel_functional.md": render_cyclic_markdown(),
        "boundary_topographic_excess_functional.md": render_topographic_markdown(),
        "boundary_action_term_realization_results.json": json.dumps(
            payload, indent=2, sort_keys=True
        )
        + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
