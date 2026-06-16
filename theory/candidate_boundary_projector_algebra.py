from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from candidate_boundary_integer_anomaly import anomaly_report


BRANCH = "bhsm-boundary-projector-algebra-gate-v1"
STATUS = "candidate_only"

VALID_C = {0, 1}
VALID_ELL = {0, 1}
VALID_SIGMA = {-1, 1}
VALID_W = {0, 1}

CLAIM_LABELS = [
    "BOUNDARY_PROJECTOR_ALGEBRA_GATE_CANDIDATE",
    "C_ELL_SIGMA_W_AS_PROJECTOR_EIGENVALUES_CANDIDATE",
    "FERMION_CLOSURE_COMPLEMENTARITY_CANDIDATE",
    "CHANNEL_MULTIPLICITY_RULE_CANDIDATE",
    "PROJECTOR_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC",
    "PROJECTOR_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC",
    "PROJECTOR_ALGEBRA_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "BOUNDARY_PROJECTOR_ALGEBRA_GATE_COMPLETE",
    "C_ELL_SIGMA_W_AS_PROJECTOR_EIGENVALUES_CANDIDATE",
    "FERMION_CLOSURE_COMPLEMENTARITY_CANDIDATE",
    "CHANNEL_MULTIPLICITY_RULE_CANDIDATE",
    "PROJECTOR_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC",
    "PROJECTOR_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC",
    "PROJECTOR_ALGEBRA_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


@dataclass(frozen=True)
class ProjectorEigenState:
    C: int
    ell: int
    sigma: int
    w: int


def validate_projector_eigenstate(state: ProjectorEigenState) -> None:
    if state.C not in VALID_C:
        raise ValueError("C must be 0 or 1")
    if state.ell not in VALID_ELL:
        raise ValueError("ell must be 0 or 1")
    if state.sigma not in VALID_SIGMA:
        raise ValueError("sigma must be -1 or 1")
    if state.w not in VALID_W:
        raise ValueError("w must be 0 or 1")


def closure_complementarity_passes(state: ProjectorEigenState) -> bool:
    validate_projector_eigenstate(state)
    return state.C + state.ell == 1


def channel_multiplicity(C: int) -> int:
    if C not in VALID_C:
        raise ValueError("C must be 0 or 1")
    return 1 + 2 * C


def t3_from_projector_state(state: ProjectorEigenState) -> Fraction:
    validate_projector_eigenstate(state)
    return Fraction(state.w * state.sigma, 2)


def hypercharge_from_projector_state(state: ProjectorEigenState) -> Fraction:
    validate_projector_eigenstate(state)
    return Fraction(state.C, 3) - Fraction(state.ell, 1) + Fraction(
        (1 - state.w) * state.sigma, 1
    )


def electric_charge_from_projector_state(state: ProjectorEigenState) -> Fraction:
    return t3_from_projector_state(state) + hypercharge_from_projector_state(state) / 2


def physical_projector_state_registry(include_nu_r: bool = True) -> dict[str, ProjectorEigenState]:
    states = {
        "nu_L": ProjectorEigenState(0, 1, +1, 1),
        "e_L": ProjectorEigenState(0, 1, -1, 1),
        "u_L": ProjectorEigenState(1, 0, +1, 1),
        "d_L": ProjectorEigenState(1, 0, -1, 1),
        "e_R": ProjectorEigenState(0, 1, -1, 0),
        "u_R": ProjectorEigenState(1, 0, +1, 0),
        "d_R": ProjectorEigenState(1, 0, -1, 0),
    }
    if include_nu_r:
        states["nu_R"] = ProjectorEigenState(0, 1, +1, 0)
    return states


def physical_projector_charge_table(include_nu_r: bool = True) -> dict[str, dict[str, Fraction]]:
    return {
        name: {
            "T3": t3_from_projector_state(state),
            "Y": hypercharge_from_projector_state(state),
            "Q": electric_charge_from_projector_state(state),
        }
        for name, state in physical_projector_state_registry(include_nu_r).items()
    }


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


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "projector_algebra_derived_from_geometry": False,
        "primitive_derivation_complete": False,
        "projector_eigenvalues": {
            "P_C": "C in {0,1}",
            "P_ell": "ell in {0,1}",
            "S_sigma": "sigma in {-1,+1}",
            "P_w": "w in {0,1}",
        },
        "candidate_constraints": {
            "P_C_plus_P_ell": "I",
            "C_plus_ell": 1,
            "channel_multiplicity": "1 + 2C",
        },
        "bridges_confirmed": {
            "boundary_state_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": anomaly_closure_bridge_confirmed(),
        },
        "claim_labels": CLAIM_LABELS,
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "named boundary-state classes replaced by candidate projector eigenvalues",
            "projector algebra itself still requires derivation from Berger-Hopf boundary geometry",
            "charge/hypercharge bridge remains diagnostic",
            "anomaly closure remains diagnostic",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _state_table() -> str:
    headers = ["field", "C", "ell", "sigma", "w", "T3", "Y", "Q", "d_channel"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for field, state in physical_projector_state_registry(include_nu_r=True).items():
        lines.append(
            "| "
            + " | ".join(
                [
                    field,
                    str(state.C),
                    str(state.ell),
                    str(state.sigma),
                    str(state.w),
                    _fraction_text(t3_from_projector_state(state)),
                    _fraction_text(hypercharge_from_projector_state(state)),
                    _fraction_text(electric_charge_from_projector_state(state)),
                    str(channel_multiplicity(state.C)),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_gate_markdown() -> str:
    return f"""# Boundary Projector Algebra Gate

## 1. Motivation

The previous boundary-state gate defined named state classes whose outputs reproduce the integer primitive bridge. This gate replaces those named classes with candidate commuting boundary projectors and an orientation involution.

## 2. Previous Gates Achieved

```text
C, ell, sigma, w
-> T3, Y, Q
-> SM charge/hypercharge table
-> one-generation anomaly closure
```

## 3. Why Boundary-State Classes Still Need Derivation

The boundary-state class names are still candidate inputs. A replacement-by-derivation program needs operators whose joint eigenvalues produce those labels.

## 4. Candidate Boundary-Projector Algebra

```text
P_C      color/channel projector
P_ell    lepton-closure projector
S_sigma  weak-interface orientation involution
P_w      weak-interface activity projector
```

```text
P_C |psi> = C |psi>,          C in {{0,1}}
P_ell |psi> = ell |psi>,      ell in {{0,1}}
S_sigma |psi> = sigma |psi>,  sigma in {{-1,+1}}
P_w |psi> = w |psi>,          w in {{0,1}}
```

Candidate algebra constraints:

```text
P_C^2 = P_C
P_ell^2 = P_ell
P_w^2 = P_w
S_sigma^2 = I
[P_C, P_ell] = [P_C, P_w] = [P_C, S_sigma] = [P_ell, P_w] = [P_ell, S_sigma] = [P_w, S_sigma] = 0
```

## 5. Joint Eigenvalue Interpretation

```text
C=1 -> three-channel active sector
C=0 -> single-channel boundary sector
ell=1 -> lepton-closure sector
ell=0 -> hadron/quark-closure sector
sigma=+1 -> upper weak-interface orientation
sigma=-1 -> lower weak-interface orientation
w=1 -> weak-interface active / doublet-like
w=0 -> weak-interface inactive / singlet-like
```

## 6. Closure Constraint

```text
P_C + P_ell = I
C + ell = 1
```

For minimal fermion boundary sectors, the color/channel and lepton-closure projectors are complementary.

## 7. Channel Multiplicity Rule

```text
d_channel = 1 + 2C
C=0 -> d_channel=1
C=1 -> d_channel=3
```

This is a candidate bridge toward color triplicity, not a full SU(3) derivation.

## 8. Bridge To `(T3,Y,Q)`

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = sigma/2 + C/6 - ell/2
```

{_state_table()}

## 9. Bridge To Anomaly Closure

The physical projector-state registry reproduces the same charge table used by the one-generation anomaly closure gate. The anomaly closure bridge remains diagnostic.

## 10. What This Achieves

This gate makes `(C, ell, sigma, w)` candidate joint eigenvalues of a boundary-projector algebra.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 11. What This Does Not Prove

This gate does not fully derive the Standard Model. It replaces named boundary-state classes with a candidate boundary-projector algebra whose joint eigenvalues reproduce the previously audited \\(C,\\ell,\\sigma,w\\) primitive bridge. The remaining proof obligation is to derive the projector algebra itself from Berger-Hopf boundary action, automorphism structure, admissible phase closure, and topographic stability.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived.

## 12. Next Proof Obligations

- Derive `P_C` from admissible three-channel boundary automorphisms.
- Derive `P_ell` from complementary closure condition.
- Derive `S_sigma` from interface orientation.
- Derive `P_w` from weak-interface activity.
- Derive local SU(3), SU(2), and U(1) algebras from projector/automorphism structure.
"""


def render_to_state_bridge_markdown() -> str:
    return """# Boundary Projector To State Bridge

```text
P_C eigenvalue 0 -> single_channel_boundary
P_C eigenvalue 1 -> three_channel_active

P_ell eigenvalue 1 -> leptonic_closure
P_ell eigenvalue 0 -> hadronic_closure

S_sigma eigenvalue +1 -> upper orientation
S_sigma eigenvalue -1 -> lower orientation

P_w eigenvalue 1 -> interface active
P_w eigenvalue 0 -> interface inactive
```

Physical registry:

```text
nu_L: C=0, ell=1, sigma=+1, w=1
e_L:  C=0, ell=1, sigma=-1, w=1
u_L:  C=1, ell=0, sigma=+1, w=1
d_L:  C=1, ell=0, sigma=-1, w=1
nu_R optional: C=0, ell=1, sigma=+1, w=0
e_R:  C=0, ell=1, sigma=-1, w=0
u_R:  C=1, ell=0, sigma=+1, w=0
d_R:  C=1, ell=0, sigma=-1, w=0
```
"""


def render_closure_constraints_markdown() -> str:
    return """# Boundary Projector Closure Constraints

Candidate closure constraints:

```text
P_C + P_ell = I
C + ell = 1
d_channel = 1 + 2C
```

Candidate interpretation:

- Fermion sectors are either three-channel active or leptonic single-channel closure, but not both.
- This reproduces the quark/lepton split as a boundary complementarity condition.
- `d_channel=3` for `C=1` is a candidate bridge to color triplicity.
- This is not yet a derivation of SU(3).

Future proof obligations:

- derive `P_C` from admissible three-channel boundary automorphisms;
- derive `P_ell` from complementary closure condition;
- derive `S_sigma` from interface orientation;
- derive `P_w` from weak-interface activity;
- derive the local SU(3), SU(2), and U(1) algebras from projector/automorphism structure.
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "boundary_projector_algebra_gate.md": render_gate_markdown(),
        "boundary_projector_to_state_bridge.md": render_to_state_bridge_markdown(),
        "boundary_projector_closure_constraints.md": render_closure_constraints_markdown(),
        "boundary_projector_algebra_results.json": json.dumps(
            payload, indent=2, sort_keys=True
        )
        + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
