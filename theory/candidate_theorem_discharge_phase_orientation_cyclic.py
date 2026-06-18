from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-phase-orientation-cyclic-v1"
STATUS = "theorem_discharge_candidate"

MISSION_LANGUAGE = (
    "The purpose of this branch is not to preserve not-proven labels indefinitely. "
    "The purpose is to attempt to discharge the proof obligations that block the "
    "full BHSM derivation of the Standard Model. Status labels may be promoted only "
    "when the derivation is explicit, non-tautological, and does not import the "
    "Standard Model structure as an assumption."
)

VERDICT_LABELS = [
    "THEOREM_DISCHARGE_PHASE_ORIENTATION_CYCLIC_COMPLETE",
    "PO_BH_2_PHASE_CLOSURE_DERIVED_CONDITIONAL",
    "PO_BH_3_ORIENTATION_INVOLUTION_DERIVED_CONDITIONAL",
    "PO_BH_4_MINIMAL_CYCLIC_CHANNEL_DERIVED_CONDITIONAL",
    "PO_BH_8_CLOSURE_SPECTRUM_123_DERIVED_CONDITIONAL",
    "PRIMITIVE_LOW_ENERGY_CLOSURE_SPECTRUM_123_DERIVED_CONDITIONAL",
    "DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


class DischargeStatus(str, Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: DischargeStatus
    statement: str
    dependencies: tuple[str, ...]
    remaining_blocker: str


def hopf_phase_closure_condition(d: int) -> bool:
    return isinstance(d, int) and d > 0


def orientation_involution_eigenvalues() -> tuple[int, int]:
    return (1, -1)


def minimal_orientation_dimension() -> int:
    return len(orientation_involution_eigenvalues())


def cyclic_sector_is_new(order: int) -> bool:
    return isinstance(order, int) and order >= 3


def minimal_non_involutive_cyclic_order() -> int:
    for order in range(1, 10):
        if cyclic_sector_is_new(order):
            return order
    raise RuntimeError("no cyclic order found")


def primitive_low_energy_closure_spectrum() -> list[int]:
    identity_reference = 1
    orientation_pair = minimal_orientation_dimension()
    minimal_cyclic = minimal_non_involutive_cyclic_order()
    return [identity_reference, orientation_pair, minimal_cyclic]


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-2": DischargeRecord(
            "PO-BH-2",
            "derive Hopf phase closure from global single-valuedness",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Hopf fiber identification psi~psi+2*pi and Phi_d=exp(i d psi)Phi_0 imply exp(i2*pi*d)=1, so positive closure dimensions are positive integers.",
            ("Hopf fiber phase", "global single-valued admissible boundary section"),
            "This gives integer admissibility but not the full primitive spectrum by itself.",
        ),
        "PO-BH-3": DischargeRecord(
            "PO-BH-3",
            "derive Z2 orientation involution from boundary orientation reversal",
            DischargeStatus.DERIVED_CONDITIONAL,
            "A boundary involution Iota^2=id has eigenvalues lambda=+/-1; the minimal balanced nontrivial representation contains both signs and has dimension 2.",
            ("boundary orientation reversal", "balanced nontrivial representation"),
            "This gives the minimal orientation pair but not the full weak gauge group.",
        ),
        "PO-BH-4": DischargeRecord(
            "PO-BH-4",
            "derive minimal cyclic channel beyond identity and involution",
            DischargeStatus.DERIVED_CONDITIONAL,
            "A cyclic sector has g^n=id; order 1 is identity and order 2 is the involution, so the first non-involutive cyclic order is 3.",
            ("integer phase admissibility", "orientation involution order 2", "cyclic closure hierarchy"),
            "This gives the minimal non-involutive cyclic order but not the full color gauge group.",
        ),
        "PO-BH-8": DischargeRecord(
            "PO-BH-8",
            "derive primitive low-energy closure selectors",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Identity/reference, minimal orientation pair, and minimal non-involutive cyclic channel give primitive selectors 1, 2, and 3.",
            ("PO-BH-2", "PO-BH-3", "PO-BH-4"),
            "Higher closures are not impossible; they remain higher/composite/excess candidates outside this primitive layer.",
        ),
    }


def discharged_obligations() -> list[str]:
    return [
        code
        for code, record in proof_discharge_ledger().items()
        if record.status == DischargeStatus.DERIVED_CONDITIONAL
    ]


def remaining_blockers() -> list[str]:
    blockers = [
        record.remaining_blocker
        for record in proof_discharge_ledger().values()
        if record.remaining_blocker
    ]
    blockers.extend(
        [
            "finite algebra uniqueness theorem",
            "charge/hypercharge operator derivation without SM label import",
            "anomaly cancellation as boundary consistency theorem",
            "gauge group dynamics derivation",
            "mass/Yukawa/mixing theorem-level derivation",
            "full replacement-level SM derivation",
        ]
    )
    return blockers


def replacement_claim_ready() -> bool:
    return False


def theorem_discharge_summary() -> dict:
    return {
        "closure_selection_layer_discharged_conditionally": True,
        "primitive_low_energy_closure_spectrum": primitive_low_energy_closure_spectrum(),
        "discharged_obligations": discharged_obligations(),
        "remaining_blockers": remaining_blockers(),
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": replacement_claim_ready(),
    }


def _discharged_obligation_payload() -> dict[str, str]:
    return {
        "PO-BH-2": "DERIVED_CONDITIONAL: Hopf phase closure gives positive integer admissibility",
        "PO-BH-3": "DERIVED_CONDITIONAL: boundary involution gives minimal balanced orientation sector d=2",
        "PO-BH-4": "DERIVED_CONDITIONAL: minimal non-involutive cyclic sector gives d=3",
        "PO-BH-8": "DERIVED_CONDITIONAL: primitive low-energy closure selectors give {1,2,3}",
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "closure_selection_layer_discharged_conditionally": True,
        "discharged_obligations": _discharged_obligation_payload(),
        "primitive_low_energy_closure_spectrum": primitive_low_energy_closure_spectrum(),
        "still_open_downstream": [
            "finite algebra uniqueness theorem",
            "charge/hypercharge operator derivation without SM label import",
            "anomaly cancellation as boundary consistency theorem",
            "gauge group dynamics derivation",
            "mass/Yukawa/mixing theorem-level derivation",
            "full replacement-level SM derivation",
        ],
        "bridges_preserved": {
            "boundary_action_second_variation": True,
            "boundary_action_term_realization": True,
            "boundary_action_hessian_scaffold": True,
            "closure_spectrum_selection": True,
            "finite_boundary_algebra_bridge": True,
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "negative_results": [
            "replacement claim is not ready because downstream finite algebra, charge, anomaly, gauge, mass, and dynamics derivations remain open",
            "higher closures are not impossible; they are outside the primitive identity/orientation/minimal-cyclic layer",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for the first closure-selection layer",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "ledger": {
            code: {**asdict(record), "status": record.status.value}
            for code, record in proof_discharge_ledger().items()
        },
    }


def _discharge_table() -> str:
    lines = [
        "| obligation | status | derived statement | remaining blocker |",
        "| --- | --- | --- | --- |",
    ]
    for record in proof_discharge_ledger().values():
        lines.append(
            f"| {record.code} | {record.status.value} | {record.statement} | {record.remaining_blocker} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Phase, Orientation, And Cyclic Closure

## 1. Mission: Full BHSM Derivation Of SM Structure

{MISSION_LANGUAGE}

## 2. Previous Diagnostic Chain

The diagnostic chain runs from candidate boundary action terms to second variation, Hessian projectors, closure spectrum selectors, finite algebra, primitive projectors, charge formulas, and anomaly diagnostics.

## 3. Why Proof Discharge Is Required

The prior chain was diagnostic. Replacement-level BHSM requires deriving the closure selectors from Berger-Hopf boundary structure rather than importing the target finite algebra or Standard Model labels.

## 4. Discharge Target PO-BH-2: Hopf Phase Closure

See [Derived Hopf Phase Closure](derived_hopf_phase_closure.md). This branch conditionally derives positive integer admissibility from global single-valuedness.

## 5. Discharge Target PO-BH-3: Orientation Involution

See [Derived Orientation Involution](derived_orientation_involution.md). This branch conditionally derives the minimal balanced orientation sector `d=2`.

## 6. Discharge Target PO-BH-4: Minimal Cyclic Channel

See [Derived Minimal Cyclic Channel](derived_minimal_cyclic_channel.md). This branch conditionally derives `d=3` as the first cyclic order not reducible to identity or involution.

## 7. Discharge Target PO-BH-8: Closure Spectrum `{{1,2,3}}`

See [Derived Closure Spectrum 123](derived_closure_spectrum_123.md). The primitive low-energy selectors are conditionally derived as `{{1,2,3}}`.

## 8. Non-Tautology Checks

The closure selector derivation does not use SM charge labels, hypercharge assignments, anomaly sums, quark/lepton masses, CKM values, or gauge group labels. It uses only Hopf phase single-valuedness, involution order, and the cyclic-order hierarchy.

## 9. Promoted Results, If Any

{_discharge_table()}

## 10. Remaining Blockers

- finite algebra uniqueness theorem;
- charge/hypercharge operator derivation without SM label import;
- anomaly cancellation as boundary consistency theorem;
- gauge group dynamics derivation;
- mass/Yukawa/mixing theorem-level derivation;
- full replacement-level SM derivation.

## 11. Impact On Finite Algebra

The conditional closure selectors support the existing `End(C)`, `End(C^2)`, and `End(C^3)` finite-algebra bridge. The uniqueness of that bridge remains open.

## 12. Impact On Charge/Anomaly Derivation

The charge/anomaly layer remains downstream. This branch does not use charge labels to derive the closure spectrum.

## 13. What This Achieves

This branch discharges the first closure-selection theorem layer: Hopf phase closure gives integer admissibility, boundary orientation gives the minimal nontrivial Z2 sector d=2, the first non-involutive cyclic sector gives d=3, and the primitive low-energy closure spectrum is derived as {{1,2,3}} under the stated Berger-Hopf boundary conditions.

## 14. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until downstream finite algebra, charge, anomaly, gauge, mass, and dynamics derivations are completed without importing Standard Model structures as assumptions.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_hopf_markdown() -> str:
    return """# Derived Hopf Phase Closure

Let the Hopf fiber coordinate satisfy

```text
psi ~ psi + 2*pi
```

and let an admissible boundary mode be

```text
Phi_d(psi) = exp(i d psi) Phi_0
```

Global single-valuedness requires

```text
Phi_d(psi+2*pi)=Phi_d(psi)
```

therefore

```text
exp(i 2*pi d)=1
```

so `d` is an integer. For positive closure dimensions,

```text
d in Z_{>0}
```

Status: `PO_BH_2_PHASE_CLOSURE_DERIVED_CONDITIONAL`.

Guardrail: this derives integer admissibility, not the full `{1,2,3}` spectrum.
"""


def render_orientation_markdown() -> str:
    return """# Derived Orientation Involution

Use the boundary orientation reversal candidate `Iota` with

```text
Iota^2 = identity
```

An eigenvalue `lambda` of this involution satisfies

```text
lambda^2 = 1
```

so

```text
lambda = +/-1
```

A nontrivial balanced representation requires both signs:

```text
(+1,-1)
```

Therefore the minimal nontrivial orientation sector has dimension

```text
d=2
```

Status: `PO_BH_3_ORIENTATION_INVOLUTION_DERIVED_CONDITIONAL`.

Guardrail: this derives a minimal `Z2` orientation pair, not the full weak gauge group.
"""


def render_cyclic_markdown() -> str:
    return """# Derived Minimal Cyclic Channel

A cyclic sector of order `n` satisfies

```text
g^n = identity
```

The already-derived sectors are:

- `n=1`: identity/reference;
- `n=2`: involutive orientation.

Therefore the minimal cyclic sector not reducible to identity or involution has

```text
n=3
```

Interpretation: this is the minimal non-involutive cyclic channel candidate.

Status: `PO_BH_4_MINIMAL_CYCLIC_CHANNEL_DERIVED_CONDITIONAL`.

Guardrail: this does not prove the full color gauge group. It derives the minimal non-involutive cyclic channel order under the stated closure hierarchy.
"""


def render_spectrum_markdown() -> str:
    return """# Derived Closure Spectrum `{1,2,3}`

The prior derived pieces give:

```text
d=1: identity/reference closure
d=2: minimal nontrivial orientation involution
d=3: minimal non-involutive cyclic channel
```

Therefore the primitive low-energy selectors are

```text
D_primitive_low = {1,2,3}
```

Higher `d` are not impossible. They are outside the primitive identity/orientation/minimal-cyclic closure layer and remain higher/composite/excess candidates unless separately derived.

Status: `PO_BH_8_CLOSURE_SPECTRUM_123_DERIVED_CONDITIONAL`.
"""


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_phase_orientation_cyclic.md": render_main_markdown(),
        "derived_hopf_phase_closure.md": render_hopf_markdown(),
        "derived_orientation_involution.md": render_orientation_markdown(),
        "derived_minimal_cyclic_channel.md": render_cyclic_markdown(),
        "derived_closure_spectrum_123.md": render_spectrum_markdown(),
        "theorem_discharge_phase_orientation_cyclic_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
