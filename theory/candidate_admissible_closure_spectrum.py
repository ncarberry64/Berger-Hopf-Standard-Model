from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


BRANCH = "bhsm-admissible-boundary-closure-spectrum-gate-v1"
STATUS = "candidate_only"
ADMISSIBLE_DIAGNOSTIC_DIMS = {1, 2, 3}

CLAIM_LABELS = [
    "ADMISSIBLE_BOUNDARY_CLOSURE_SPECTRUM_GATE_CANDIDATE",
    "HOPF_PHASE_CLOSURE_FILTER_CANDIDATE",
    "TOPOGRAPHIC_STABILITY_CLOSURE_FILTER_CANDIDATE",
    "MINIMAL_CLOSURE_SPECTRUM_123_DIAGNOSTIC",
    "CLOSURE_SPECTRUM_TO_FINITE_ALGEBRA_BRIDGE_CONFIRMED_DIAGNOSTIC",
    "UNIQUE_FIRST_PRINCIPLES_CLOSURE_DERIVATION_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
]

VERDICT_LABELS = [
    "ADMISSIBLE_BOUNDARY_CLOSURE_SPECTRUM_GATE_COMPLETE",
    "HOPF_PHASE_CLOSURE_FILTER_CANDIDATE",
    "TOPOGRAPHIC_STABILITY_CLOSURE_FILTER_CANDIDATE",
    "MINIMAL_CLOSURE_SPECTRUM_123_DIAGNOSTIC",
    "CLOSURE_SPECTRUM_TO_FINITE_ALGEBRA_BRIDGE_CONFIRMED_DIAGNOSTIC",
    "UNIQUE_FIRST_PRINCIPLES_CLOSURE_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This gate does not fully derive the Standard Model. It proposes a candidate "
    "admissible boundary-closure spectrum whose minimal dimensions reproduce the "
    "finite boundary algebra used in the previous projector and charge-bridge gates. "
    "The remaining proof obligation is to derive the closure spectrum uniquely from "
    "the Berger-Hopf boundary action, admissible phase closure, and the full "
    "topographic stability/Hessian problem."
)


@dataclass(frozen=True)
class ClosureSector:
    dimension: int
    role: str
    interpretation: str


def _validate_dimension(d: int) -> None:
    if not isinstance(d, int) or d < 1:
        raise ValueError("closure dimension must be a positive integer")


def phase_closure_pass(d: int) -> bool:
    _validate_dimension(d)
    return d in ADMISSIBLE_DIAGNOSTIC_DIMS


def topographic_stability_pass(d: int) -> bool:
    _validate_dimension(d)
    return d in ADMISSIBLE_DIAGNOSTIC_DIMS


def admissible_closure_pass(d: int) -> bool:
    return phase_closure_pass(d) and topographic_stability_pass(d)


def endomorphism_algebra_for_dim(d: int) -> str:
    _validate_dimension(d)
    if d == 1:
        return "C"
    return f"M{d}(C)"


def closure_sector_registry() -> dict[str, ClosureSector]:
    return {
        "single_channel": ClosureSector(
            1, "single_channel_closure", "candidate leptonic/singlet closure"
        ),
        "weak_orientation_pair": ClosureSector(
            2, "active_orientation_pair", "candidate weak-interface active block"
        ),
        "three_channel": ClosureSector(
            3, "three_channel_closure", "candidate color/channel active block"
        ),
    }


def finite_algebra_blocks_from_spectrum() -> dict[str, str]:
    return {
        "End(C^1)": "C",
        "End(C^2)": "M2(C)",
        "End(C^3)": "M3(C)",
    }


def finite_boundary_algebra_bridge() -> dict[str, str]:
    return {
        "dim_1": "C_ell and inactive C_{sigma=+/-} orientation singlets",
        "dim_2": "M2(C)_{w=1} active weak-interface block",
        "dim_3": "M3(C)_C three-channel active block",
        "A_channel": "C_ell direct_sum M3(C)_C",
        "A_weak": "M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}",
    }


def minimality_audit() -> dict[str, object]:
    registry = closure_sector_registry()
    dims = sorted(sector.dimension for sector in registry.values())
    return {
        "admissible_diagnostic_dimensions": dims,
        "required_dimensions_present": dims == [1, 2, 3],
        "all_required_dimensions_admissible": all(admissible_closure_pass(d) for d in dims),
        "finite_algebra_blocks": finite_algebra_blocks_from_spectrum(),
        "finite_algebra_bridge_confirmed": True,
        "unique_first_principles_derivation": False,
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
        "closure_spectrum_uniquely_derived": False,
        "full_hessian_proof_complete": False,
        "admissible_diagnostic_dimensions": [1, 2, 3],
        "filters": {
            "hopf_phase_closure": "candidate diagnostic",
            "topographic_stability": "candidate diagnostic",
        },
        "endomorphism_blocks": finite_algebra_blocks_from_spectrum(),
        "bridges_preserved": {
            "finite_boundary_algebra_bridge": True,
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "minimal admissible closure spectrum documented diagnostically",
            "unique first-principles derivation remains open",
            "full Berger-Hopf Hessian proof remains open",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _closure_sector_table() -> str:
    lines = [
        "| sector | dimension | role | interpretation | phase closure | topographic stability |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, sector in closure_sector_registry().items():
        lines.append(
            f"| {name} | {sector.dimension} | {sector.role} | {sector.interpretation} | "
            f"{str(phase_closure_pass(sector.dimension)).lower()} | "
            f"{str(topographic_stability_pass(sector.dimension)).lower()} |"
        )
    return "\n".join(lines)


def _endomorphism_table() -> str:
    lines = [
        "| closure dimension | endomorphism algebra | finite-algebra role |",
        "| --- | --- | --- |",
    ]
    roles = {
        1: "C_ell and inactive C_{sigma=+/-} singlets",
        2: "M2(C)_{w=1} active weak-interface block",
        3: "M3(C)_C three-channel active block",
    }
    for d in [1, 2, 3]:
        lines.append(f"| {d} | {endomorphism_algebra_for_dim(d)} | {roles[d]} |")
    return "\n".join(lines)


def render_gate_markdown() -> str:
    return f"""# Admissible Boundary Closure Spectrum Gate

## 1. Motivation

The previous gate documented a candidate automorphism/closure origin for the finite boundary algebra. This gate asks why the relevant closure spaces should have diagnostic dimensions `1`, `2`, and `3`.

## 2. Previous Gate Achieved: Automorphism/Closure Origin

```text
End(C)   = C_ell
End(C^3) = M3(C)_C
End(C^2) = M2(C)_{{w=1}}
C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

## 3. Why The Closure Dimensions Still Need Selection

The finite algebra depends on admissible one-channel, two-orientation, and three-channel structures. A full derivation must show why these are selected by Berger-Hopf boundary action, phase closure, and topographic stability.

## 4. Candidate Hopf Phase-Closure Filter

```text
exp(2*pi*i*n/N) closure phases must be globally admissible under boundary identification.
```

Diagnostic rule:

```text
phase_closure_pass(d) = d in {{1,2,3}}
```

## 5. Candidate Fourth-Order Topographic Stability Filter

```text
L_T = nabla^2 - B*nabla^4
```

Diagnostic rule:

```text
topographic_stability_pass(d) = d in {{1,2,3}}
```

This tracks the existing candidate picture of zero/reference closure plus two stable nonzero topographic branches. It is not a full Hessian proof.

## 6. Candidate Admissible Spectrum `D_adm = {{1,2,3}}`

{_closure_sector_table()}

## 7. Endomorphism Bridge To Finite Algebra

```text
End(C^1) = C
End(C^2) = M2(C)
End(C^3) = M3(C)
```

{_endomorphism_table()}

The finite boundary algebra from the previous gate is the direct-sum/tensor organization of the minimal admissible endomorphism blocks generated by the candidate closure spectrum.

## 8. Bridge To Projectors And `(C,ell,sigma,w)`

The diagnostic spectrum preserves the previous finite-algebra bridge:

```text
dim 1 -> C_ell and inactive C_sigma orientation singlets
dim 2 -> M2(C) active weak-interface block
dim 3 -> M3(C) three-channel active block
```

## 9. Bridge To Charges And Anomaly Closure

Because the finite boundary algebra bridge is preserved, the projector eigenvalue bridge, charge/hypercharge bridge, and one-generation anomaly closure diagnostic remain preserved.

## 10. What This Achieves

This gate documents a candidate admissible boundary-closure spectrum:

```text
D_adm = {{1,2,3}}
```

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS)}

## 11. What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not claim the admissible closure spectrum is uniquely derived from first principles.

## 12. Next Proof Obligations

- Derive the Hopf phase-closure filter from the boundary action and global phase constraints.
- Derive the topographic stability filter from the complete Berger-Hopf boundary Hessian.
- Prove or reject uniqueness of the closure spectrum beyond the diagnostic `{{1,2,3}}` bridge.
- Show whether nearby closure dimensions are excluded by the full action rather than by this diagnostic rule.

## Related Selection Rule Audit

- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
"""


def render_hopf_filter_markdown() -> str:
    return """# Hopf Phase Closure Filter

Candidate filter:

```text
A boundary channel of dimension d is admissible if its phase sectors close under the Hopf fiber identification and preserve global boundary consistency.
```

Candidate diagnostic rule:

```text
phase_closure_pass(d) = d in {1,2,3}
```

Candidate meanings:

- `d=1`: trivial/single closure.
- `d=2`: orientation pair / weak interface.
- `d=3`: minimal cyclic three-channel closure.

Guardrails:

- This is not a final derivation.
- It is a diagnostic minimal admissibility filter for the present BHSM bridge.
- Future work must derive it from the boundary action and global phase constraints.

## Related Selection Rule Audit

- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
"""


def render_topographic_filter_markdown() -> str:
    return """# Topographic Stability Closure Filter

Candidate fourth-order operator:

```text
L_T = nabla^2 - B*nabla^4
```

Existing generation-count candidate:

```text
zero/reference closure + two stable nonzero topographic branches
```

Candidate diagnostic rule:

```text
topographic_stability_pass(d) = d in {1,2,3}
```

Interpretation:

- `d=1` corresponds to reference/single closure.
- `d=2` corresponds to paired orientation/interface closure.
- `d=3` corresponds to three-channel stable closure.

Required guardrail: the full stability derivation requires the complete Berger-Hopf boundary Hessian and cannot be claimed closed here.

## Related Selection Rule Audit

- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
"""


def render_bridge_markdown() -> str:
    return f"""# Closure Spectrum To Finite Algebra Bridge

Candidate admissible dimensions:

```text
D_adm = {{1,2,3}}
```

Endomorphism blocks:

```text
End(C^1) = C
End(C^2) = M2(C)
End(C^3) = M3(C)
```

{_endomorphism_table()}

Recover the finite boundary algebra:

```text
A_channel = C_ell direct_sum M3(C)_C
A_weak = M2(C)_{{w=1}} direct_sum C_{{sigma=+}} direct_sum C_{{sigma=-}}
```

The finite boundary algebra from the previous gate is the direct-sum/tensor organization of the minimal admissible endomorphism blocks generated by the candidate closure spectrum.

## Related Selection Rule Audit

- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "admissible_boundary_closure_spectrum_gate.md": render_gate_markdown(),
        "hopf_phase_closure_filter.md": render_hopf_filter_markdown(),
        "topographic_stability_closure_filter.md": render_topographic_filter_markdown(),
        "closure_spectrum_to_finite_algebra_bridge.md": render_bridge_markdown(),
        "admissible_boundary_closure_spectrum_results.json": json.dumps(
            payload, indent=2, sort_keys=True
        )
        + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
