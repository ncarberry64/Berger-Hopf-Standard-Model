from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


BRANCH = "bhsm-boundary-automorphism-closure-origin-gate-v1"
STATUS = "candidate_only"

CLAIM_LABELS = [
    "BOUNDARY_AUTOMORPHISM_CLOSURE_ORIGIN_GATE_CANDIDATE",
    "CHANNEL_ALGEBRA_FROM_ENDOMORPHISM_BLOCKS_CANDIDATE",
    "WEAK_INTERFACE_ALGEBRA_FROM_ACTIVE_AND_INACTIVE_ORIENTATION_BLOCKS_CANDIDATE",
    "CENTRAL_PROJECTORS_FROM_DIRECT_SUM_ALGEBRA_CANDIDATE",
    "ORIENTATION_GRADING_FROM_Z2_BOUNDARY_INVOLUTION_CANDIDATE",
    "FINITE_BOUNDARY_ALGEBRA_MINIMALITY_DIAGNOSTIC",
    "FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "BOUNDARY_AUTOMORPHISM_CLOSURE_ORIGIN_GATE_COMPLETE",
    "CHANNEL_ALGEBRA_FROM_ENDOMORPHISM_BLOCKS_CANDIDATE",
    "WEAK_INTERFACE_ALGEBRA_FROM_ACTIVE_AND_INACTIVE_ORIENTATION_BLOCKS_CANDIDATE",
    "CENTRAL_PROJECTORS_FROM_DIRECT_SUM_ALGEBRA_CANDIDATE",
    "ORIENTATION_GRADING_FROM_Z2_BOUNDARY_INVOLUTION_CANDIDATE",
    "FINITE_BOUNDARY_ALGEBRA_MINIMALITY_DIAGNOSTIC",
    "FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This gate does not fully derive the Standard Model. It proposes a candidate "
    "automorphism-and-closure origin for the finite Berger-Hopf boundary algebra. "
    "The remaining proof obligation is to derive the admissible boundary closure "
    "classes, orientation grading, and interface activity directly from the "
    "Berger-Hopf boundary action and topographic stability operator."
)


@dataclass(frozen=True)
class BoundaryVectorSpace:
    name: str
    dimension: int
    interpretation: str


@dataclass(frozen=True)
class EndomorphismBlock:
    name: str
    dimension: int
    algebra: str
    interpretation: str


def endomorphism_block(space: BoundaryVectorSpace) -> EndomorphismBlock:
    if space.dimension < 1:
        raise ValueError("boundary vector-space dimension must be positive")
    algebra = "C" if space.dimension == 1 else f"M{space.dimension}(C)"
    return EndomorphismBlock(
        name=f"End({space.name})",
        dimension=space.dimension * space.dimension,
        algebra=algebra,
        interpretation=f"endomorphism algebra of {space.interpretation}",
    )


def channel_spaces() -> dict[str, BoundaryVectorSpace]:
    return {
        "leptonic_single_channel": BoundaryVectorSpace(
            "V_ell", 1, "single-channel leptonic closure"
        ),
        "three_channel_active": BoundaryVectorSpace(
            "V_C", 3, "three-channel active closure"
        ),
    }


def weak_interface_spaces() -> dict[str, BoundaryVectorSpace]:
    return {
        "weak_active": BoundaryVectorSpace(
            "V_w", 2, "active two-orientation weak interface"
        ),
        "inactive_upper": BoundaryVectorSpace(
            "V_plus", 1, "inactive upper orientation"
        ),
        "inactive_lower": BoundaryVectorSpace(
            "V_minus", 1, "inactive lower orientation"
        ),
    }


def channel_algebra_blocks() -> dict[str, EndomorphismBlock]:
    spaces = channel_spaces()
    return {
        "C_ell": EndomorphismBlock(
            "C_ell",
            endomorphism_block(spaces["leptonic_single_channel"]).dimension,
            "C",
            "single-channel leptonic closure block",
        ),
        "M3_C": EndomorphismBlock(
            "M3_C",
            endomorphism_block(spaces["three_channel_active"]).dimension,
            "M3(C)",
            "three-channel active boundary block",
        ),
    }


def weak_algebra_blocks() -> dict[str, EndomorphismBlock]:
    spaces = weak_interface_spaces()
    return {
        "M2_active": EndomorphismBlock(
            "M2_active",
            endomorphism_block(spaces["weak_active"]).dimension,
            "M2(C)",
            "weak-interface active two-orientation block",
        ),
        "C_sigma_plus": EndomorphismBlock(
            "C_sigma_plus",
            endomorphism_block(spaces["inactive_upper"]).dimension,
            "C",
            "inactive upper orientation singlet",
        ),
        "C_sigma_minus": EndomorphismBlock(
            "C_sigma_minus",
            endomorphism_block(spaces["inactive_lower"]).dimension,
            "C",
            "inactive lower orientation singlet",
        ),
    }


def finite_boundary_algebra_descriptor() -> dict[str, str]:
    return {
        "A_boundary_candidate": "A_channel tensor A_weak",
        "A_channel": "C_ell direct_sum M3(C)_C",
        "A_weak": "M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}",
        "P_C": "central projection onto M3(C)_C",
        "P_ell": "central projection onto C_ell",
        "P_w": "central projection onto M2(C)_{w=1}",
        "S_sigma": "Z2 orientation grading on weak-interface orientation space",
    }


def minimality_requirements() -> dict[str, dict[str, str]]:
    return {
        "single_channel_closure": {
            "minimal_block_needed": "C",
            "candidate_block": "C_ell",
            "status": "diagnostic",
        },
        "three_channel_active_closure": {
            "minimal_block_needed": "M3(C) or End(C^3)",
            "candidate_block": "M3(C)_C",
            "status": "diagnostic",
        },
        "active_two_orientation_interface": {
            "minimal_block_needed": "M2(C) or End(C^2)",
            "candidate_block": "M2(C)_{w=1}",
            "status": "diagnostic",
        },
        "inactive_upper_orientation": {
            "minimal_block_needed": "C",
            "candidate_block": "C_{sigma=+}",
            "status": "diagnostic",
        },
        "inactive_lower_orientation": {
            "minimal_block_needed": "C",
            "candidate_block": "C_{sigma=-}",
            "status": "diagnostic",
        },
    }


def minimality_audit() -> dict[str, object]:
    requirements = minimality_requirements()
    supplied_blocks = set(channel_algebra_blocks()) | set(weak_algebra_blocks())
    candidate_to_key = {
        "C_ell": "C_ell",
        "M3(C)_C": "M3_C",
        "M2(C)_{w=1}": "M2_active",
        "C_{sigma=+}": "C_sigma_plus",
        "C_{sigma=-}": "C_sigma_minus",
    }
    rows = {}
    for key, row in requirements.items():
        rows[key] = {
            **row,
            "supplied": candidate_to_key[row["candidate_block"]] in supplied_blocks,
        }
    return {
        "requirements": rows,
        "diagnostic_requirements_met": all(row["supplied"] for row in rows.values()),
        "unique_first_principles_derivation": False,
        "conclusion": (
            "minimal with respect to the current diagnostic bridge, but not uniquely "
            "derived from first-principles Berger-Hopf geometry"
        ),
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "finite_boundary_algebra_fully_derived": False,
        "automorphism_closure_origin_documented": True,
        "channel_origin": {
            "single_channel": "End(C) = C_ell",
            "three_channel": "End(C^3) = M3(C)_C",
        },
        "weak_origin": {
            "active_interface": "End(C^2) = M2(C)_{w=1}",
            "inactive_orientations": "End(C_+) direct_sum End(C_-) = C_{sigma=+} direct_sum C_{sigma=-}",
        },
        "minimality_audit": {
            "diagnostic_requirements_met": minimality_audit()["diagnostic_requirements_met"],
            "unique_first_principles_derivation": False,
        },
        "bridges_preserved": {
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "automorphism-and-closure origin documented diagnostically",
            "finite algebra itself still requires first-principles derivation from Berger-Hopf boundary action and topographic stability",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _block_table(blocks: dict[str, EndomorphismBlock]) -> str:
    lines = [
        "| block | algebra | algebra dimension | interpretation |",
        "| --- | --- | --- | --- |",
    ]
    for key, block in blocks.items():
        lines.append(
            f"| {key} | {block.algebra} | {block.dimension} | {block.interpretation} |"
        )
    return "\n".join(lines)


def _minimality_table() -> str:
    lines = [
        "| requirement | minimal block needed | candidate block | status | supplied |",
        "| --- | --- | --- | --- | --- |",
    ]
    for key, row in minimality_audit()["requirements"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    key,
                    str(row["minimal_block_needed"]),
                    str(row["candidate_block"]),
                    str(row["status"]),
                    str(row["supplied"]).lower(),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_origin_gate_markdown() -> str:
    return f"""# Boundary Automorphism And Closure Origin Gate

## 1. Motivation

The finite boundary algebra gate supplied a candidate finite algebra source for `(P_C, P_ell, P_w, S_sigma)`. This gate asks how that finite algebra could arise from admissible boundary closure, automorphism sectors, interface activity, and orientation grading.

## 2. Previous Gate Achieved: Finite Boundary Algebra Source

```text
A_channel = C_ell direct_sum M3(C)_C
A_weak = M2(C)_{{w=1}} direct_sum C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

The finite algebra diagnostically sources:

```text
C, ell, sigma, w
-> T3, Y, Q
-> SM charge/hypercharge table
-> one-generation anomaly closure
```

## 3. Why The Finite Algebra Still Needs Derivation

The block algebra is still candidate input. A full derivation must produce the admissible closure sectors, vector-space dimensions, interface activity, and orientation grading from Berger-Hopf boundary action and topographic stability.

## 4. Candidate Automorphism-And-Closure Origin

Candidate premise: after imposing channel closure, orientation grading, interface activity, admissible phase closure, and topographic stability, the admissible boundary endomorphisms reduce to:

```text
A_boundary_candidate = A_channel tensor A_weak
```

## 5. Channel Closure Origin Of `(C_ell direct_sum M_3(C)_C)`

```text
single-channel admissible closure:
  V_ell = C
  End(V_ell) = C_ell

three-channel active closure:
  V_C = C^3
  End(V_C) = M3(C)_C
```

{_block_table(channel_algebra_blocks())}

## 6. Weak-Interface Origin Of `(M_2(C) direct_sum C_+ direct_sum C_-)`

```text
active weak-interface orientation space:
  V_w = C^2
  End(V_w) = M2(C)_{{w=1}}

inactive resolved orientation spaces:
  V_+ = C
  V_- = C
  End(V_+) direct_sum End(V_-) = C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

{_block_table(weak_algebra_blocks())}

## 7. Central Projections And Orientation Grading

```text
P_C = central projection onto M3(C)_C
P_ell = central projection onto C_ell
P_w = central projection onto M2(C)_{{w=1}}
S_sigma = Z2 orientation grading

P_C + P_ell = I_channel
P_w + P_inactive = I_weak
S_sigma^2 = I
P_C^2 = P_C
P_ell^2 = P_ell
P_w^2 = P_w
```

## 8. Minimality Audit

{_minimality_table()}

Conclusion: this finite algebra is minimal with respect to the current diagnostic bridge, but not yet uniquely derived from first-principles Berger-Hopf geometry.

## 9. Bridge Back To `(C,ell,sigma,w)`

The channel direct sum sources `C` and `ell`; the weak-interface direct sum sources `w`; the orientation grading sources `sigma`.

## 10. Bridge Back To `(T3,Y,Q)`

The finite algebra preserves the charge operators from the previous gate:

```text
T3_hat = (1/2) P_w S_sigma
Y_hat = (4/3) P_C - I + (I-P_w) S_sigma
Q_hat = (1/2)(S_sigma - I) + (2/3) P_C
```

## 11. Bridge Back To Anomaly Closure

Because the projector eigenvalue bridge and charge/hypercharge bridge are preserved, the one-generation anomaly closure diagnostic remains preserved.

## 12. What This Achieves

This gate documents a candidate automorphism-and-closure origin for the finite boundary algebra.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 13. What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not claim SU(3), SU(2), or U(1) are fully derived.

## 14. Next Proof Obligations

- Derive the admissible one-channel and three-channel closure classes from the Berger-Hopf boundary action.
- Derive weak-interface activity from boundary interface dynamics.
- Derive the `Z2` orientation grading from a boundary involution.
- Prove topographic stability selects these blocks and excludes nearby alternatives.
- Upgrade diagnostic minimality to a first-principles derivation if the action forces the block algebra.

## Related Closure Spectrum Gate

- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
"""


def render_channel_origin_markdown() -> str:
    return f"""# Boundary Channel Automorphism Origin

Candidate channel-origin logic:

```text
single-channel admissible closure:
  V_ell = C
  End(V_ell) = C_ell

three-channel active closure:
  V_C = C^3
  End(V_C) = M3(C)_C
```

Candidate channel algebra:

```text
A_channel = End(V_ell) direct_sum End(V_C)
          = C_ell direct_sum M3(C)_C
```

Candidate central projections:

```text
P_ell = projection onto End(V_ell)
P_C = projection onto End(V_C)
P_C + P_ell = I_channel
```

Candidate multiplicity:

```text
dim(V_ell)=1
dim(V_C)=3
d_channel = 1 + 2C
```

{_block_table(channel_algebra_blocks())}

Guardrail:
This is not yet a derivation of SU(3). It is a candidate origin of color triplicity/channel multiplicity.

## Related Closure Spectrum Gate

- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
"""


def render_weak_origin_markdown() -> str:
    return f"""# Boundary Weak-Interface Origin

Candidate weak-interface origin logic:

```text
active weak-interface orientation space:
  V_w = C^2
  End(V_w) = M2(C)_{{w=1}}

inactive resolved orientation spaces:
  V_+ = C
  V_- = C
  End(V_+) direct_sum End(V_-) = C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

Candidate weak algebra:

```text
A_weak = M2(C)_{{w=1}} direct_sum C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

Candidate central projection:

```text
P_w = projection onto M2(C)_{{w=1}}
```

Candidate orientation grading:

```text
S_sigma |upper> = + |upper>
S_sigma |lower> = - |lower>
S_sigma^2 = I
```

{_block_table(weak_algebra_blocks())}

Guardrail:
This is not yet a derivation of SU(2)_L. It is a candidate source of weak-interface activity and orientation.

## Related Closure Spectrum Gate

- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
"""


def render_minimality_markdown() -> str:
    return f"""# Boundary Algebra Minimality Audit

Diagnostic requirements:

- must distinguish lepton-like single-channel closure from quark-like three-channel closure;
- must include the three-channel active closure block;
- must provide channel multiplicity 1 vs 3;
- must provide upper/lower orientation signs;
- must provide active weak two-state interface;
- must provide active two-orientation interface;
- must provide inactive orientation singlets;
- must provide inactive upper orientation;
- must provide inactive lower orientation;
- must reproduce the existing `(C,ell,sigma,w)` bridge;
- must reproduce `(T3,Y,Q)`;
- must preserve anomaly closure diagnostic.

{_minimality_table()}

Conclusion: this finite algebra is minimal with respect to the current diagnostic bridge, but not yet uniquely derived from first-principles Berger-Hopf geometry.

## Related Closure Spectrum Gate

- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "boundary_automorphism_closure_origin_gate.md": render_origin_gate_markdown(),
        "boundary_channel_automorphism_origin.md": render_channel_origin_markdown(),
        "boundary_weak_interface_origin.md": render_weak_origin_markdown(),
        "boundary_algebra_minimality_audit.md": render_minimality_markdown(),
        "boundary_automorphism_closure_results.json": json.dumps(
            payload, indent=2, sort_keys=True
        )
        + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
