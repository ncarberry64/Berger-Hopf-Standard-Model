from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-boundary-action-hessian-scaffold-v1"
STATUS = "candidate_only"
PROJECTOR_NAMES = ("P_ref", "P_orient", "P_cyclic", "P_excess")

CLAIM_LABELS = [
    "BOUNDARY_ACTION_HESSIAN_SCAFFOLD_GATE_CANDIDATE",
    "BOUNDARY_ACTION_TERMS_CATALOGED_CANDIDATE",
    "HESSIAN_PROJECTOR_DECOMPOSITION_CANDIDATE",
    "REFERENCE_ORIENTATION_CYCLIC_PROJECTORS_CANDIDATE",
    "EXCESS_CLOSURE_GAP_CANDIDATE",
    "CLOSURE_SPECTRUM_FROM_HESSIAN_SCAFFOLD_DIAGNOSTIC",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "BOUNDARY_ACTION_HESSIAN_SCAFFOLD_GATE_COMPLETE",
    "BOUNDARY_ACTION_TERMS_CATALOGED_CANDIDATE",
    "HESSIAN_PROJECTOR_DECOMPOSITION_CANDIDATE",
    "REFERENCE_ORIENTATION_CYCLIC_PROJECTORS_CANDIDATE",
    "EXCESS_CLOSURE_GAP_CANDIDATE",
    "CLOSURE_SPECTRUM_FROM_HESSIAN_SCAFFOLD_DIAGNOSTIC",
    "BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This gate does not fully derive the Standard Model. It introduces a candidate "
    "Berger-Hopf boundary action and Hessian scaffold whose low-energy projector "
    "structure matches the previously audited closure-spectrum selection rule. The "
    "full proof still requires deriving this Hessian from the actual Berger-Hopf "
    "boundary action, admissible phase closure, and topographic stability operator."
)


@dataclass(frozen=True)
class HessianProjector:
    name: str
    closure_dimension: str
    interpretation: str
    low_energy_selected: bool


@dataclass(frozen=True)
class HessianEigenvalue:
    projector: str
    eigenvalue: Fraction
    status: str


def boundary_action_terms() -> dict[str, str]:
    return {
        "S_phase": "Hopf phase closure / global boundary consistency",
        "S_orientation": "Z2 upper/lower boundary orientation pair",
        "S_cyclic_channel": "minimal cyclic three-channel closure",
        "S_topographic": "fourth-order topographic branch stability",
        "S_excess": "gap penalty for higher/composite closures",
    }


def hessian_projector_registry() -> dict[str, HessianProjector]:
    return {
        "P_ref": HessianProjector("P_ref", "1", "reference/single closure", True),
        "P_orient": HessianProjector("P_orient", "2", "orientation-pair closure", True),
        "P_cyclic": HessianProjector("P_cyclic", "3", "cyclic three-channel closure", True),
        "P_excess": HessianProjector("P_excess", ">=4", "higher/composite/excess closure", False),
    }


def candidate_hessian_eigenvalues(gap: int = 10) -> dict[str, HessianEigenvalue]:
    if not isinstance(gap, int) or gap <= 1:
        raise ValueError("gap must be an integer greater than 1")
    return {
        "P_ref": HessianEigenvalue("P_ref", Fraction(0), "reference-normalized"),
        "P_orient": HessianEigenvalue("P_orient", Fraction(1), "stable low-energy"),
        "P_cyclic": HessianEigenvalue("P_cyclic", Fraction(1), "stable low-energy"),
        "P_excess": HessianEigenvalue("P_excess", Fraction(gap), "gapped/excess"),
    }


def stability_hierarchy_passes(gap: int = 10) -> bool:
    values = candidate_hessian_eigenvalues(gap)
    mu_ref = values["P_ref"].eigenvalue
    mu_orient = values["P_orient"].eigenvalue
    mu_cyclic = values["P_cyclic"].eigenvalue
    mu_excess = values["P_excess"].eigenvalue
    return mu_ref <= 0 < mu_orient < mu_excess and 0 < mu_cyclic < mu_excess


def closure_dimension_from_projector(projector: str) -> str:
    registry = hessian_projector_registry()
    if projector not in registry:
        raise ValueError("unknown Hessian projector")
    return registry[projector].closure_dimension


def finite_algebra_block_from_projector(projector: str) -> str:
    mapping = {
        "P_ref": "C",
        "P_orient": "M2(C)",
        "P_cyclic": "M3(C)",
        "P_excess": "higher/composite",
    }
    if projector not in mapping:
        raise ValueError("unknown Hessian projector")
    return mapping[projector]


def closure_selection_summary(gap: int = 10) -> dict:
    registry = hessian_projector_registry()
    eigenvalues = candidate_hessian_eigenvalues(gap)
    rows = {}
    for name in PROJECTOR_NAMES:
        rows[name] = {
            "projector": asdict(registry[name]),
            "eigenvalue": str(eigenvalues[name].eigenvalue),
            "eigenvalue_status": eigenvalues[name].status,
            "finite_algebra_block": finite_algebra_block_from_projector(name),
        }
    return {
        "selected_low_energy_spectrum": [1, 2, 3],
        "projectors": rows,
        "stability_hierarchy_passes": stability_hierarchy_passes(gap),
        "boundary_action_derived": False,
        "full_hessian_proof_complete": False,
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "full_hessian_proof_complete": False,
        "boundary_action_derived": False,
        "candidate_action_terms": list(boundary_action_terms()),
        "hessian_projectors": {
            "P_ref": "d=1 reference/single closure",
            "P_orient": "d=2 orientation-pair closure",
            "P_cyclic": "d=3 cyclic three-channel closure",
            "P_excess": "d>=4 higher/composite closures",
        },
        "candidate_stability_hierarchy": {
            "mu_ref": "0 or reference-normalized",
            "mu_orient": "stable low-energy",
            "mu_cyclic": "stable low-energy",
            "mu_excess": "gapped/excess",
        },
        "bridges_preserved": {
            "closure_spectrum_selection": True,
            "finite_boundary_algebra_bridge": True,
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "boundary action/Hessian scaffold documented",
            "full Hessian proof remains open",
            "boundary action derivation remains open",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _action_terms_table() -> str:
    lines = [
        "| term | purpose / candidate role | selects | remains unproven |",
        "| --- | --- | --- | --- |",
    ]
    selections = {
        "S_phase": "Hopf phase closure / global boundary consistency",
        "S_orientation": "minimal Z2 upper/lower orientation pair",
        "S_cyclic_channel": "minimal cyclic three-channel closure",
        "S_topographic": "zero/reference plus two stable nonzero branches from L_T",
        "S_excess": "gap penalty for sectors outside the low-energy branch budget",
    }
    for term, purpose in boundary_action_terms().items():
        lines.append(
            f"| {term} | {purpose} | {selections[term]} | first-principles derivation from boundary action |"
        )
    return "\n".join(lines)


def _projector_table() -> str:
    lines = [
        "| projector | closure dimension | interpretation | low-energy selected | eigenvalue | status | finite block |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    registry = hessian_projector_registry()
    eigenvalues = candidate_hessian_eigenvalues()
    for name in PROJECTOR_NAMES:
        p = registry[name]
        e = eigenvalues[name]
        lines.append(
            f"| {name} | {p.closure_dimension} | {p.interpretation} | "
            f"{str(p.low_energy_selected).lower()} | {e.eigenvalue} | {e.status} | "
            f"{finite_algebra_block_from_projector(name)} |"
        )
    return "\n".join(lines)


def render_gate_markdown() -> str:
    return f"""# Boundary Action Hessian Scaffold Gate

## 1. Motivation

The closure-spectrum selection audit supported `{1,2,3}` using candidate screens. This gate introduces the next proof scaffold: a boundary action and Hessian projector decomposition whose low-energy sectors match that audited selection rule.

## 2. Previous Gate Achieved: Candidate Closure-Spectrum Selection Audit

```text
d=1 reference/single closure
d=2 orientation-pair closure
d=3 cyclic three-channel closure
d>=4 excess/higher/composite closure sectors
```

## 3. Why Action/Hessian Scaffolding Is Now Required

The selection screens remain diagnostic until they are derived from boundary action terms and the full topographic Hessian.

## 4. Candidate Boundary Action

```text
S_boundary_candidate =
S_phase
+ S_orientation
+ S_cyclic_channel
+ S_topographic
+ S_excess
```

{_action_terms_table()}

## 5. Candidate Hessian Projector Decomposition

```text
H_boundary_candidate =
mu_ref P_ref
+ mu_orient P_orient
+ mu_cyclic P_cyclic
+ mu_excess P_excess
```

{_projector_table()}

## 6. Stable Low-Energy Branch Interpretation

```text
mu_ref = 0 or reference-normalized
mu_orient > 0 stable
mu_cyclic > 0 stable
mu_excess >= gap > max(mu_orient, mu_cyclic)
```

The values are schematic diagnostics, not physical predictions.

## 7. Closure Spectrum Bridge

```text
P_ref     -> d=1 reference/single closure
P_orient  -> d=2 orientation-pair closure
P_cyclic  -> d=3 cyclic three-channel closure
P_excess  -> d>=4 higher/composite/unsupported low-energy closures
```

## 8. Bridge To Finite Boundary Algebra

```text
P_ref     -> d=1 -> End(C^1)=C
P_orient  -> d=2 -> End(C^2)=M2(C)
P_cyclic  -> d=3 -> End(C^3)=M3(C)
P_excess  -> d>=4 -> higher/composite/unsupported low-energy closures
```

## 9. Bridge To Projector Eigenvalues `(C,ell,sigma,w)`

The Hessian scaffold preserves the previously audited route from closure dimensions to finite algebra blocks and then to the central projectors and orientation grading.

## 10. Bridge To `(T3,Y,Q)`

Because the finite algebra bridge is preserved, the charge operators from the projector gates remain diagnostic consequences.

## 11. Bridge To Anomaly Closure

The one-generation anomaly closure diagnostic remains preserved through the charge/hypercharge bridge.

## 12. What This Achieves

This gate catalogs candidate action terms and a candidate Hessian projector decomposition for the closure-spectrum selection rule.

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 13. What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not claim the closure spectrum is uniquely derived. It does not claim the full Hessian proof is complete.

## 14. Next Proof Obligations

- derive `S_phase`, `S_orientation`, `S_cyclic_channel`, `S_topographic`, and `S_excess` from the actual boundary action;
- compute the full Berger-Hopf boundary Hessian;
- prove the projector decomposition and gap hierarchy;
- prove or reject exclusion of higher closures from low-energy fundamental sectors.
"""


def render_terms_markdown() -> str:
    return f"""# Boundary Action Candidate Terms

Schematic action:

```text
S_boundary_candidate =
S_phase
+ S_orientation
+ S_cyclic_channel
+ S_topographic
+ S_excess
```

{_action_terms_table()}

Guardrail: these terms are not yet derived from first principles. They are a scaffold for the next proof.
"""


def render_hessian_markdown() -> str:
    return f"""# Boundary Hessian Projector Decomposition

Candidate decomposition:

```text
H_boundary_candidate =
mu_ref P_ref
+ mu_orient P_orient
+ mu_cyclic P_cyclic
+ mu_excess P_excess
```

Projector meanings:

```text
P_ref: reference/single closure sector
P_orient: Z2 orientation-pair sector
P_cyclic: cyclic three-channel sector
P_excess: remaining higher/composite closure sector
```

Candidate orthogonality/completeness:

```text
P_i P_j = 0 for i != j
P_ref + P_orient + P_cyclic + P_excess = I
```

Candidate stability hierarchy:

```text
mu_ref = 0 or reference-normalized
0 < mu_orient < mu_excess
0 < mu_cyclic < mu_excess
mu_excess >= gap
```

{_projector_table()}

Required guardrail: this is a candidate Hessian decomposition, not the full Hessian proof.
"""


def render_bridge_markdown() -> str:
    return """# Boundary Hessian Closure Selection Bridge

Bridge:

```text
P_ref     -> d=1 -> End(C^1)=C
P_orient  -> d=2 -> End(C^2)=M2(C)
P_cyclic  -> d=3 -> End(C^3)=M3(C)
P_excess  -> d>=4 -> higher/composite/unsupported low-energy closures
```

Recover:

```text
A_channel = C_ell direct_sum M3(C)_C
A_weak = M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}
```

This bridge supports the finite algebra source diagnostically, but does not uniquely derive it.
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "boundary_action_hessian_scaffold_gate.md": render_gate_markdown(),
        "boundary_action_candidate_terms.md": render_terms_markdown(),
        "boundary_hessian_projector_decomposition.md": render_hessian_markdown(),
        "boundary_hessian_closure_selection_bridge.md": render_bridge_markdown(),
        "boundary_action_hessian_scaffold_results.json": json.dumps(payload, indent=2, sort_keys=True)
        + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
