from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-boundary-integer-primitives-bridge-v1"
STATUS = "candidate_only"

CLAIM_LABELS = [
    "BOUNDARY_INTEGER_CHARGE_HYPERCHARGE_BRIDGE_CANDIDATE",
    "SM_CHARGE_TABLE_REPRODUCED_DIAGNOSTIC",
    "HYPERCHARGE_REWRITE_FROM_INTEGER_PRIMITIVES",
    "WEAK_INTERFACE_ACTIVITY_DERIVATION_REMAINS_OPEN",
    "CHIRAL_STRUCTURE_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

OPEN_PROOF_OBLIGATIONS = [
    "Derive C as a color-active boundary sector from Berger-Hopf channel geometry.",
    "Derive ell as a lepton-sector boundary indicator from boundary closure.",
    "Derive sigma as upper/lower weak-interface orientation.",
    "Derive w as weak-interface activity and explain why it corresponds to SM chiral doublet/singlet structure.",
    "Derive anomaly cancellation from global boundary closure using the integer primitive charge table.",
]

FIELDS = [
    ("nu_L", 0, 1, +1, 1),
    ("e_L", 0, 1, -1, 1),
    ("u_L", 1, 0, +1, 1),
    ("d_L", 1, 0, -1, 1),
    ("nu_R optional", 0, 1, +1, 0),
    ("e_R", 0, 1, -1, 0),
    ("u_R", 1, 0, +1, 0),
    ("d_R", 1, 0, -1, 0),
]


def validate_C(C: int) -> None:
    if C not in (0, 1):
        raise ValueError("C must be 0 or 1")


def validate_ell(ell: int) -> None:
    if ell not in (0, 1):
        raise ValueError("ell must be 0 or 1")


def validate_sigma(sigma: int) -> None:
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or 1")


def validate_w(w: int) -> None:
    if w not in (0, 1):
        raise ValueError("w must be 0 or 1")


def t3_from_integer_primitives(sigma: int, w: int) -> Fraction:
    validate_sigma(sigma)
    validate_w(w)
    return Fraction(w * sigma, 2)


def hypercharge_from_integer_primitives(C: int, ell: int, sigma: int, w: int) -> Fraction:
    validate_C(C)
    validate_ell(ell)
    validate_sigma(sigma)
    validate_w(w)
    return Fraction(C, 3) - Fraction(ell, 1) + Fraction((1 - w) * sigma, 1)


def electric_charge_from_integer_primitives(C: int, ell: int, sigma: int, w: int) -> Fraction:
    T3 = t3_from_integer_primitives(sigma, w)
    Y = hypercharge_from_integer_primitives(C, ell, sigma, w)
    return T3 + Fraction(Y, 2)


def electric_charge_closed_form(C: int, ell: int, sigma: int) -> Fraction:
    validate_C(C)
    validate_ell(ell)
    validate_sigma(sigma)
    return Fraction(sigma, 2) + Fraction(C, 6) - Fraction(ell, 2)


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value.numerator}/{value.denominator}"


def sm_charge_table() -> list[dict[str, object]]:
    rows = []
    for field, C, ell, sigma, w in FIELDS:
        T3 = t3_from_integer_primitives(sigma, w)
        Y = hypercharge_from_integer_primitives(C, ell, sigma, w)
        Q = electric_charge_from_integer_primitives(C, ell, sigma, w)
        rows.append(
            {
                "field": field,
                "C": C,
                "ell": ell,
                "sigma": sigma,
                "w": w,
                "T3": _fraction_text(T3),
                "Y": _fraction_text(Y),
                "Q": _fraction_text(Q),
            }
        )
    return rows


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "claim_labels": CLAIM_LABELS,
        "charge_hypercharge_bridge": {
            "status": "candidate_diagnostic",
            "T3": "w*sigma/2",
            "Y": "C/3 - ell + (1-w)*sigma",
            "Q": "sigma/2 + C/6 - ell/2",
            "sm_charge_table_reproduced": True,
            "primitive_derivation_complete": False,
            "full_sm_derivation_claimed": False,
        },
        "integer_primitives": {
            "C": "3B color-active boundary-sector indicator",
            "ell": "L lepton-sector boundary indicator",
            "sigma": "2T3_orientation upper/lower weak-interface orientation",
            "w": "weak-interface activity indicator",
        },
        "sm_charge_table": sm_charge_table(),
        "open_proof_obligations": OPEN_PROOF_OBLIGATIONS,
        "notes": [
            "candidate-only",
            "diagnostic mapping only",
            "weak-interface activity is not yet fully derived chirality",
            "no official prediction changes",
            "no frozen prediction changes",
            "full Standard Model derivation is not claimed",
        ],
    }


def _markdown_table(rows: list[dict[str, object]]) -> str:
    headers = ["field", "C", "ell", "sigma", "w", "T3", "Y", "Q"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(row[h]) for h in headers) + " |" for row in rows)
    return "\n".join(lines)


def render_charge_hypercharge_bridge_markdown() -> str:
    return f"""# Boundary Integer Charge/Hypercharge Bridge

Status: `candidate_diagnostic`

This bridge reproduces the Standard Model electric charge and hypercharge table from integer candidate primitives under a diagnostic mapping. It does not yet derive those primitives from Berger-Hopf boundary geometry and does not constitute a full Standard Model derivation.

## Claim Labels

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## Integer Candidate Primitives

```text
C = 3B
ell = L
sigma = 2T3_orientation
w = weak-interface activity
```

Interpretation of the new bridge primitive:

```text
w in {{0,1}}
w=1 -> weak doublet / interface-active state
w=0 -> weak singlet / interface-inactive state
```

This is not fully derived chirality. The remaining proof obligation is to derive why weak-interface activity corresponds to SM chiral structure.

## Bridge Equations

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = T3 + Y/2
Q = sigma/2 + C/6 - ell/2
```

## Diagnostic Charge Table

{_markdown_table(sm_charge_table())}

## Open Proof Obligations

{chr(10).join(f"- {item}" for item in OPEN_PROOF_OBLIGATIONS)}

## Guardrails

- Candidate bridge only.
- No official predictions are changed.
- No frozen predictions are changed.
- No full Standard Model derivation is claimed.
- No BHSM replacement claim is made.
- No full gauge-group derivation is claimed.

## Related Finite Algebra Gate

- [Boundary projector algebra gate](boundary_projector_algebra_gate.md)
- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    (theory / "boundary_integer_charge_hypercharge_bridge.md").write_text(
        render_charge_hypercharge_bridge_markdown(), encoding="utf-8"
    )
    (theory / "boundary_integer_primitives_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
