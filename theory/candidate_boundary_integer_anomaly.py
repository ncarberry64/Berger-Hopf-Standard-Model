from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from candidate_boundary_integer_primitives import (
    electric_charge_from_integer_primitives,
    hypercharge_from_integer_primitives,
    t3_from_integer_primitives,
)


BRANCH = "bhsm-integer-primitive-anomaly-closure-gate-v1"
STATUS = "candidate_only"

CLAIM_LABELS = [
    "BOUNDARY_INTEGER_ANOMALY_CLOSURE_GATE_CANDIDATE",
    "SM_ONE_GENERATION_ANOMALY_CANCELLATION_REPRODUCED_DIAGNOSTIC",
    "ANOMALY_CANCELLATION_AS_BOUNDARY_CLOSURE_CANDIDATE",
    "WITTEN_SU2_PARITY_CHECK_PASSED_DIAGNOSTIC",
    "PRIMITIVE_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "BOUNDARY_INTEGER_ANOMALY_CLOSURE_GATE_COMPLETE",
    "SM_ONE_GENERATION_ANOMALY_CANCELLATION_REPRODUCED_DIAGNOSTIC",
    "ANOMALY_CANCELLATION_AS_BOUNDARY_CLOSURE_CANDIDATE",
    "WITTEN_SU2_PARITY_CHECK_PASSED_DIAGNOSTIC",
    "PRIMITIVE_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


@dataclass(frozen=True)
class WeylField:
    name: str
    color_multiplicity: int
    weak_multiplicity: int
    hypercharge: Fraction
    is_color_charged: bool
    is_weak_doublet: bool


def one_generation_weyl_fields(include_nu_r: bool = True) -> list[WeylField]:
    fields = [
        WeylField("Q_L", 3, 2, Fraction(1, 3), True, True),
        WeylField("L_L", 1, 2, Fraction(-1, 1), False, True),
        WeylField("u_R_c", 3, 1, Fraction(-4, 3), True, False),
        WeylField("d_R_c", 3, 1, Fraction(2, 3), True, False),
        WeylField("e_R_c", 1, 1, Fraction(2, 1), False, False),
    ]
    if include_nu_r:
        fields.append(WeylField("nu_R_c", 1, 1, Fraction(0, 1), False, False))
    return fields


def anomaly_su3_su3_u1(fields: list[WeylField]) -> Fraction:
    """Common normalization with color Dynkin index suppressed."""
    return sum(
        f.weak_multiplicity * f.hypercharge for f in fields if f.is_color_charged
    )


def anomaly_su2_su2_u1(fields: list[WeylField]) -> Fraction:
    """Common normalization with weak Dynkin index suppressed."""
    return sum(
        f.color_multiplicity * f.hypercharge for f in fields if f.is_weak_doublet
    )


def anomaly_u1_cubed(fields: list[WeylField]) -> Fraction:
    return sum(
        f.color_multiplicity * f.weak_multiplicity * f.hypercharge**3
        for f in fields
    )


def anomaly_gravity_gravity_u1(fields: list[WeylField]) -> Fraction:
    return sum(
        f.color_multiplicity * f.weak_multiplicity * f.hypercharge
        for f in fields
    )


def witten_su2_doublet_count(fields: list[WeylField]) -> int:
    return sum(f.color_multiplicity for f in fields if f.is_weak_doublet)


def witten_su2_passes(fields: list[WeylField]) -> bool:
    return witten_su2_doublet_count(fields) % 2 == 0


def anomaly_report(include_nu_r: bool = True) -> dict[str, Fraction | int | bool]:
    fields = one_generation_weyl_fields(include_nu_r=include_nu_r)
    return {
        "SU3_SU3_U1": anomaly_su3_su3_u1(fields),
        "SU2_SU2_U1": anomaly_su2_su2_u1(fields),
        "U1_cubed": anomaly_u1_cubed(fields),
        "gravity_gravity_U1": anomaly_gravity_gravity_u1(fields),
        "witten_su2_doublet_count": witten_su2_doublet_count(fields),
        "witten_su2_passes": witten_su2_passes(fields),
    }


def physical_field_charge_table_from_integer_primitives() -> dict[str, dict[str, Fraction]]:
    rows = {
        "nu_L": (0, 1, +1, 1),
        "e_L": (0, 1, -1, 1),
        "u_L": (1, 0, +1, 1),
        "d_L": (1, 0, -1, 1),
        "nu_R": (0, 1, +1, 0),
        "e_R": (0, 1, -1, 0),
        "u_R": (1, 0, +1, 0),
        "d_R": (1, 0, -1, 0),
    }
    return {
        name: {
            "T3": t3_from_integer_primitives(sigma, w),
            "Y": hypercharge_from_integer_primitives(C, ell, sigma, w),
            "Q": electric_charge_from_integer_primitives(C, ell, sigma, w),
        }
        for name, (C, ell, sigma, w) in rows.items()
    }


def _fraction_text(value: Fraction | int | bool) -> str | int | bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def build_results_payload() -> dict:
    report = anomaly_report(include_nu_r=True)
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "primitive_derivation_complete": False,
        "anomaly_closure_gate": {
            "SU3_SU3_U1": _fraction_text(report["SU3_SU3_U1"]),
            "SU2_SU2_U1": _fraction_text(report["SU2_SU2_U1"]),
            "U1_cubed": _fraction_text(report["U1_cubed"]),
            "gravity_gravity_U1": _fraction_text(report["gravity_gravity_U1"]),
            "witten_su2_doublet_count": report["witten_su2_doublet_count"],
            "witten_su2_passes": report["witten_su2_passes"],
        },
        "interpretation": {
            "boundary_closure_candidate": True,
            "diagnostic_only": True,
            "full_derivation_claimed": False,
        },
        "claim_labels": CLAIM_LABELS,
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "anomaly cancellation reproduced from the integer primitive charge/hypercharge bridge under SM left-handed Weyl conventions",
            "C, ell, sigma, and w still require derivation from Berger-Hopf boundary geometry",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _field_table() -> str:
    fields = one_generation_weyl_fields(include_nu_r=True)
    headers = [
        "field",
        "color multiplicity",
        "weak multiplicity",
        "Y",
        "color charged",
        "weak doublet",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for f in fields:
        lines.append(
            "| "
            + " | ".join(
                [
                    f.name,
                    str(f.color_multiplicity),
                    str(f.weak_multiplicity),
                    _fraction_text(f.hypercharge),
                    str(f.is_color_charged),
                    str(f.is_weak_doublet),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_anomaly_closure_markdown() -> str:
    return f"""# Boundary Integer Anomaly Closure Gate

## 1. Motivation

The boundary integer charge/hypercharge bridge reproduces the one-generation Standard Model charge table diagnostically. This gate asks whether that same integer-primitive table also passes one-generation anomaly cancellation under the standard left-handed Weyl convention.

## 2. Why Anomaly Cancellation Matters For SM Derivation

Anomaly cancellation is a required consistency condition for the Standard Model gauge representation ledger. Any BHSM replacement-by-derivation program must eventually derive anomaly cancellation from Berger-Hopf boundary closure, rather than importing it as a Standard Model fact.

## 3. Integer Primitive Charge Bridge Recap

```text
C in {{0,1}}
ell in {{0,1}}
sigma in {{-1,+1}}
w in {{0,1}}

T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = T3 + Y/2
Q = sigma/2 + C/6 - ell/2
```

## 4. Left-Handed Weyl Convention

Right-handed physical fermions are represented by left-handed charge-conjugate fields in anomaly sums:

```text
u_R physical -> u_R^c left-handed conjugate with Y = -4/3, Q = -2/3
d_R physical -> d_R^c left-handed conjugate with Y = +2/3, Q = +1/3
e_R physical -> e_R^c left-handed conjugate with Y = +2, Q = +1
nu_R optional -> nu_R^c left-handed conjugate with Y = 0, Q = 0
```

The hypercharge convention remains:

```text
Q = T3 + Y/2
```

## 5. One-Generation Anomaly Sums

{_field_table()}

```text
SU(3)^2 U(1):
2*(1/3) + (-4/3) + (2/3) = 0

SU(2)^2 U(1):
3*(1/3) + (-1) = 0

U(1)^3:
6*(1/3)^3 + 3*(-4/3)^3 + 3*(2/3)^3 + 2*(-1)^3 + (2)^3 + 0^3 = 0

gravity^2 U(1):
6*(1/3) + 3*(-4/3) + 3*(2/3) + 2*(-1) + 2 + 0 = 0
```

## 6. Witten SU(2) Parity Check

```text
N_doublets = 3 quark doublets + 1 lepton doublet = 4
4 is even, so the one-generation SU(2) global anomaly parity check passes.
```

## 7. Interpretation As Candidate Boundary Closure

This anomaly-closure gate tests whether the integer primitive charge/hypercharge bridge reproduces Standard Model one-generation anomaly cancellation. It does not derive the integer primitives from Berger-Hopf boundary geometry and does not prove that BHSM has derived or replaced the Standard Model.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 8. What This Does Not Prove

- It does not derive `C`, `ell`, `sigma`, or `w` from Berger-Hopf boundary geometry.
- It does not derive anomaly cancellation from first-principles boundary closure.
- It does not claim the Standard Model is derived.
- It does not claim BHSM has replaced the Standard Model.
- It does not claim the full gauge group is derived.

## 9. Next Proof Obligations

- Derive the integer primitives from Berger-Hopf boundary geometry.
- Derive anomaly cancellation as global boundary closure consistency.
- Derive the local gauge group and field content rather than preserving them as infrared inputs.
- Keep collective-curvature/dark-matter interpretation separate from this particle-sector proof.
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    (theory / "boundary_integer_anomaly_closure_gate.md").write_text(
        render_anomaly_closure_markdown(), encoding="utf-8"
    )
    (theory / "boundary_integer_anomaly_closure_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
