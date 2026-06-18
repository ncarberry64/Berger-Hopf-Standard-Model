from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from candidate_boundary_integer_anomaly import anomaly_report
from candidate_boundary_integer_primitives import (
    electric_charge_from_integer_primitives,
    hypercharge_from_integer_primitives,
    t3_from_integer_primitives,
)


BRANCH = "bhsm-boundary-state-primitive-derivation-gate-v1"
STATUS = "candidate_only"

VALID_CHANNEL_CLASSES = {"three_channel_active", "single_channel_boundary"}
VALID_CLOSURE_CLASSES = {"leptonic_closure", "hadronic_closure"}
VALID_ORIENTATIONS = {"upper", "lower"}
VALID_INTERFACE_ACTIVITY = {"active", "inactive"}

CLAIM_LABELS = [
    "BOUNDARY_STATE_PRIMITIVE_DERIVATION_GATE_CANDIDATE",
    "C_ELL_SIGMA_W_FROM_BOUNDARY_STATE_CANDIDATE",
    "BOUNDARY_STATE_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC",
    "BOUNDARY_STATE_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC",
    "BOUNDARY_STATE_CLASSES_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "BOUNDARY_STATE_PRIMITIVE_DERIVATION_GATE_COMPLETE",
    "C_ELL_SIGMA_W_FROM_BOUNDARY_STATE_CANDIDATE",
    "BOUNDARY_STATE_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC",
    "BOUNDARY_STATE_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC",
    "BOUNDARY_STATE_CLASSES_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


@dataclass(frozen=True)
class BoundaryState:
    channel_class: str
    closure_class: str
    orientation: str
    interface_activity: str


def validate_boundary_state(state: BoundaryState) -> None:
    if state.channel_class not in VALID_CHANNEL_CLASSES:
        raise ValueError("invalid channel_class")
    if state.closure_class not in VALID_CLOSURE_CLASSES:
        raise ValueError("invalid closure_class")
    if state.orientation not in VALID_ORIENTATIONS:
        raise ValueError("invalid orientation")
    if state.interface_activity not in VALID_INTERFACE_ACTIVITY:
        raise ValueError("invalid interface_activity")


def C_from_boundary_state(state: BoundaryState) -> int:
    validate_boundary_state(state)
    return 1 if state.channel_class == "three_channel_active" else 0


def ell_from_boundary_state(state: BoundaryState) -> int:
    validate_boundary_state(state)
    return 1 if state.closure_class == "leptonic_closure" else 0


def sigma_from_boundary_state(state: BoundaryState) -> int:
    validate_boundary_state(state)
    return 1 if state.orientation == "upper" else -1


def w_from_boundary_state(state: BoundaryState) -> int:
    validate_boundary_state(state)
    return 1 if state.interface_activity == "active" else 0


def integer_primitives_from_boundary_state(state: BoundaryState) -> dict[str, int]:
    return {
        "C": C_from_boundary_state(state),
        "ell": ell_from_boundary_state(state),
        "sigma": sigma_from_boundary_state(state),
        "w": w_from_boundary_state(state),
    }


def t3_y_q_from_boundary_state(state: BoundaryState) -> dict[str, Fraction]:
    primitives = integer_primitives_from_boundary_state(state)
    C = primitives["C"]
    ell = primitives["ell"]
    sigma = primitives["sigma"]
    w = primitives["w"]
    return {
        "T3": t3_from_integer_primitives(sigma, w),
        "Y": hypercharge_from_integer_primitives(C, ell, sigma, w),
        "Q": electric_charge_from_integer_primitives(C, ell, sigma, w),
    }


def physical_boundary_state_registry(include_nu_r: bool = True) -> dict[str, BoundaryState]:
    states = {
        "nu_L": BoundaryState(
            "single_channel_boundary", "leptonic_closure", "upper", "active"
        ),
        "e_L": BoundaryState(
            "single_channel_boundary", "leptonic_closure", "lower", "active"
        ),
        "u_L": BoundaryState(
            "three_channel_active", "hadronic_closure", "upper", "active"
        ),
        "d_L": BoundaryState(
            "three_channel_active", "hadronic_closure", "lower", "active"
        ),
        "e_R": BoundaryState(
            "single_channel_boundary", "leptonic_closure", "lower", "inactive"
        ),
        "u_R": BoundaryState(
            "three_channel_active", "hadronic_closure", "upper", "inactive"
        ),
        "d_R": BoundaryState(
            "three_channel_active", "hadronic_closure", "lower", "inactive"
        ),
    }
    if include_nu_r:
        states["nu_R"] = BoundaryState(
            "single_channel_boundary", "leptonic_closure", "upper", "inactive"
        )
    return states


def physical_boundary_state_charge_table(include_nu_r: bool = True) -> dict[str, dict[str, Fraction]]:
    return {
        name: t3_y_q_from_boundary_state(state)
        for name, state in physical_boundary_state_registry(include_nu_r).items()
    }


def anomaly_bridge_confirmed() -> bool:
    report = anomaly_report(include_nu_r=True)
    return (
        report["SU3_SU3_U1"] == 0
        and report["SU2_SU2_U1"] == 0
        and report["U1_cubed"] == 0
        and report["gravity_gravity_U1"] == 0
        and report["witten_su2_doublet_count"] == 4
        and report["witten_su2_passes"] is True
    )


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _state_text(state: BoundaryState) -> str:
    return (
        f"channel={state.channel_class}, closure={state.closure_class}, "
        f"orientation={state.orientation}, interface={state.interface_activity}"
    )


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "primitive_derivation_complete": False,
        "boundary_state_classes_derived": False,
        "boundary_state_outputs": {
            "C": "from channel_class",
            "ell": "from closure_class",
            "sigma": "from orientation",
            "w": "from interface_activity",
        },
        "bridges_confirmed": {
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": anomaly_bridge_confirmed(),
        },
        "claim_labels": CLAIM_LABELS,
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "boundary-state system maps to C, ell, sigma, w",
            "charge/hypercharge bridge remains diagnostic",
            "anomaly closure remains diagnostic",
            "boundary state classes themselves still require derivation from Berger-Hopf geometry",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _registry_table() -> str:
    rows = [
        ("three_channel_active", "active three-channel boundary sector", "C", "1", "candidate, not derived"),
        ("single_channel_boundary", "single boundary channel sector", "C", "0", "candidate, not derived"),
        ("leptonic_closure", "lepton-sector closure class", "ell", "1", "candidate, not derived"),
        ("hadronic_closure", "hadron/quark-sector closure class", "ell", "0", "candidate, not derived"),
        ("upper", "upper weak-interface orientation", "sigma", "+1", "candidate, not derived"),
        ("lower", "lower weak-interface orientation", "sigma", "-1", "candidate, not derived"),
        ("active", "weak-interface active/doublet-like", "w", "1", "candidate, not derived"),
        ("inactive", "weak-interface inactive/singlet-like", "w", "0", "candidate, not derived"),
    ]
    headers = [
        "state component",
        "candidate BHSM meaning",
        "output primitive",
        "output value",
        "derivation status",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def _physical_state_table() -> str:
    headers = ["field", "boundary state", "C", "ell", "sigma", "w", "T3", "Y", "Q"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for name, state in physical_boundary_state_registry(include_nu_r=True).items():
        primitives = integer_primitives_from_boundary_state(state)
        charges = t3_y_q_from_boundary_state(state)
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    _state_text(state),
                    str(primitives["C"]),
                    str(primitives["ell"]),
                    str(primitives["sigma"]),
                    str(primitives["w"]),
                    _fraction_text(charges["T3"]),
                    _fraction_text(charges["Y"]),
                    _fraction_text(charges["Q"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_gate_markdown() -> str:
    return f"""# Boundary-State Primitive Derivation Gate

## 1. Motivation

The integer primitive bridge reproduces the Standard Model charge/hypercharge table and the one-generation anomaly cancellation sums diagnostically. This gate asks whether those integer primitives can be organized as outputs of a minimal BHSM-native boundary-state system.

## 2. What Previous Gates Achieved

- The charge/hypercharge bridge maps `(C, ell, sigma, w)` to `T3`, `Y`, and `Q`.
- The anomaly closure gate verifies one-generation anomaly cancellation under left-handed Weyl conventions.

## 3. Why `(C, ell, sigma, w)` Still Need Derivation

The labels remain candidate primitives. They are not yet outputs of the Berger-Hopf boundary action, admissible phase closure, automorphism structure, or topographic stability analysis.

## 4. Candidate Boundary-State System

```text
BoundaryState = (channel_class, closure_class, orientation, interface_activity)
```

```text
channel_class:
  "three_channel_active" -> C=1
  "single_channel_boundary" -> C=0

closure_class:
  "leptonic_closure" -> ell=1
  "hadronic_closure" -> ell=0

orientation:
  "upper" -> sigma=+1
  "lower" -> sigma=-1

interface_activity:
  "active" -> w=1
  "inactive" -> w=0
```

## 5. Boundary-State To Integer-Primitives Map

{_registry_table()}

## 6. Boundary-State To Charge/Hypercharge Bridge

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = T3 + Y/2
```

{_physical_state_table()}

Interface activity `w` changes `T3` and `Y`, but not `Q`, for fixed channel/closure/orientation. This explains why weak doublet/singlet partners can preserve electric charge while changing weak/hypercharge assignments. This is diagnostic, not a full derivation.

## 7. Boundary-State To Anomaly-Closure Bridge

The boundary-state registry maps to the same integer primitive charge table used by the anomaly closure gate. Therefore it confirms the anomaly bridge diagnostically:

```text
SU(3)^2 U(1)_Y = 0
SU(2)^2 U(1)_Y = 0
U(1)_Y^3 = 0
gravity^2 U(1)_Y = 0
Witten SU(2) doublet count = 4, even
```

## 8. What This Achieves

This gate proposes and tests a candidate boundary-state source for `C`, `ell`, `sigma`, and `w`.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 9. What This Does Not Prove

This gate does not fully derive the Standard Model. It proposes and tests a candidate boundary-state system whose outputs reproduce the previously audited integer primitive bridge. The remaining proof obligation is to derive the boundary state classes themselves from Berger-Hopf boundary action, admissible phase closure, automorphism structure, and topographic stability.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived.

## 10. Next Proof Obligations

- Derive `channel_class` from Berger-Hopf channel geometry and automorphism algebra.
- Derive `closure_class` from admissible boundary phase closure.
- Derive `orientation` from boundary orientation/asymmetry.
- Derive `interface_activity` from boundary interface dynamics and explain its relation to SM chiral doublet/singlet structure.
- Derive anomaly cancellation from global boundary closure.

## Related Finite Algebra Gate

- [Boundary projector algebra gate](boundary_projector_algebra_gate.md)
- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
"""


def render_registry_markdown() -> str:
    return f"""# Boundary-State Primitive Registry

Candidate state classes:

```text
channel_class:
  three_channel_active
  single_channel_boundary

closure_class:
  leptonic_closure
  hadronic_closure

orientation:
  upper
  lower

interface_activity:
  active
  inactive
```

{_registry_table()}
"""


def render_sm_bridge_markdown() -> str:
    return f"""# Boundary-State To SM Bridge

This file maps candidate boundary states to the existing integer primitive charge bridge. It is diagnostic, not a full derivation.

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = sigma/2 + C/6 - ell/2
```

Physical field boundary-state registry:

{_physical_state_table()}

Interface activity `w` changes `T3` and `Y`, but not `Q`, for fixed channel/closure/orientation. This is the diagnostic bridge between weak doublet/singlet activity and conserved electric charge.
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "boundary_state_primitive_derivation_gate.md": render_gate_markdown(),
        "boundary_state_primitive_registry.md": render_registry_markdown(),
        "boundary_state_to_sm_bridge.md": render_sm_bridge_markdown(),
        "boundary_state_primitive_derivation_results.json": json.dumps(
            payload, indent=2, sort_keys=True
        )
        + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
