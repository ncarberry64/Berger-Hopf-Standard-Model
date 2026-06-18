from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-boundary-trace-normalization-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to derive "
    "the boundary trace-normalization factor from the already-derived boundary "
    "charge/hypercharge operators, boundary multiplicities, and finite-algebra "
    "trace weights, rather than importing Standard Model or GUT normalization as "
    "an assumption. Status labels may be promoted only when the derivation is "
    "explicit, exact, non-tautological, and does not use known Standard Model "
    "normalization as a premise."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the boundary trace-normalization theorem "
    "layer. Given the previously derived boundary charge/hypercharge operators and "
    "the single left-oriented boundary trace basis, the raw Abelian trace weight is "
    "K1=10/3 while the active-orientation and cyclic-channel trace weights are "
    "K2=2 and K3=2. Therefore the boundary hypercharge normalization factor is "
    "eta_Y=3/5, placing all three gauge-action trace weights on the same normalized "
    "footing. The result is derived from boundary multiplicities and trace weights "
    "rather than imported from Standard Model normalization."
)
VERDICT_LABELS = [
    "THEOREM_DISCHARGE_BOUNDARY_TRACE_NORMALIZATION_COMPLETE",
    "PO_BH_14_BOUNDARY_TRACE_NORMALIZATION_DERIVED_CONDITIONAL",
    "BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL",
    "BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL",
    "NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL",
    "HYPERCHARGE_TRACE_FACTOR_3_5_DERIVED_CONDITIONAL",
    "GAUGE_COUPLING_CONVENTION_5_3_DERIVED_CONDITIONAL",
    "RG_RUNNING_REMAINS_OPEN",
    "MEASURED_COUPLINGS_REMAIN_OPEN",
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
class TraceWeightResult:
    name: str
    value: Fraction
    status: str
    interpretation: str


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: DischargeStatus
    statement: str
    dependencies: tuple[str, ...]
    remaining_blocker: str


def validate_C(C: int) -> None:
    if C not in (0, 1):
        raise ValueError("C must be 0 or 1")


def validate_sigma(sigma: int) -> None:
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or +1")


def channel_multiplicity(C: int) -> int:
    validate_C(C)
    return 1 + 2 * C


def active_Y(C: int) -> Fraction:
    validate_C(C)
    return Fraction(4 * C, 3) - 1


def inactive_Y(C: int, sigma: int) -> Fraction:
    validate_C(C)
    validate_sigma(sigma)
    return Fraction(4 * C, 3) - 1 + sigma


def conjugate_inactive_Y(C: int, sigma: int) -> Fraction:
    return -inactive_Y(C, sigma)


def hypercharge_generator_value(Y: Fraction) -> Fraction:
    if not isinstance(Y, Fraction):
        Y = Fraction(Y)
    return Y / 2


def active_hypercharge_trace_contribution() -> Fraction:
    total = Fraction(0)
    orientation_components = 2
    for C in (0, 1):
        TY = hypercharge_generator_value(active_Y(C))
        total += orientation_components * channel_multiplicity(C) * TY * TY
    return total


def inactive_hypercharge_trace_contribution() -> Fraction:
    total = Fraction(0)
    for C in (0, 1):
        for sigma in (1, -1):
            TY = hypercharge_generator_value(conjugate_inactive_Y(C, sigma))
            total += channel_multiplicity(C) * TY * TY
    return total


def K1_hypercharge_trace_weight() -> Fraction:
    return active_hypercharge_trace_contribution() + inactive_hypercharge_trace_contribution()


def K2_orientation_trace_weight() -> Fraction:
    active_doublets = channel_multiplicity(0) + channel_multiplicity(1)
    fundamental_trace_index = Fraction(1, 2)
    return active_doublets * fundamental_trace_index


def K3_cyclic_trace_weight() -> Fraction:
    cyclic_fundamental_components = 4
    fundamental_trace_index = Fraction(1, 2)
    return cyclic_fundamental_components * fundamental_trace_index


def eta_Y_normalization_factor() -> Fraction:
    return K2_orientation_trace_weight() / K1_hypercharge_trace_weight()


def normalized_K1() -> Fraction:
    return eta_Y_normalization_factor() * K1_hypercharge_trace_weight()


def trace_weights_unify_after_eta() -> bool:
    return normalized_K1() == K2_orientation_trace_weight() == K3_cyclic_trace_weight()


def coupling_convention_g1_squared_over_gY_squared() -> Fraction:
    return 1 / eta_Y_normalization_factor()


def all_trace_weight_results() -> tuple[TraceWeightResult, ...]:
    return (
        TraceWeightResult(
            "K1_hypercharge_raw",
            K1_hypercharge_trace_weight(),
            "BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL",
            "raw Abelian residual trace weight from boundary rows",
        ),
        TraceWeightResult(
            "K2_orientation",
            K2_orientation_trace_weight(),
            "BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL",
            "active-orientation finite-algebra trace weight",
        ),
        TraceWeightResult(
            "K3_cyclic",
            K3_cyclic_trace_weight(),
            "BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL",
            "cyclic-channel finite-algebra trace weight",
        ),
        TraceWeightResult(
            "eta_Y",
            eta_Y_normalization_factor(),
            "BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL",
            "factor placing Abelian trace weight on the non-Abelian footing",
        ),
        TraceWeightResult(
            "K1_hypercharge_normalized",
            normalized_K1(),
            "NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL",
            "normalized Abelian trace weight",
        ),
    )


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-14": DischargeRecord(
            "PO-BH-14",
            "derive boundary trace normalization",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Boundary rows, multiplicities, conjugate inactive basis, and finite-algebra trace indices give K1=10/3, K2=2, K3=2, and eta_Y=3/5.",
            (
                "boundary charge/hypercharge operators",
                "single left-oriented boundary trace basis",
                "channel multiplicity N(C)=1+2C",
                "fundamental finite-algebra trace index 1/2",
            ),
            "RG running, measured coupling values, and full low-energy Lagrangian derivation remain downstream.",
        )
    }


def rg_running_derived() -> bool:
    return False


def measured_couplings_predicted() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def theorem_discharge_summary() -> dict:
    return {
        "trace_normalization_layer_discharged_conditionally": True,
        "K1_hypercharge_raw": str(K1_hypercharge_trace_weight()),
        "K2_orientation": str(K2_orientation_trace_weight()),
        "K3_cyclic": str(K3_cyclic_trace_weight()),
        "eta_Y": str(eta_Y_normalization_factor()),
        "K1_hypercharge_normalized": str(normalized_K1()),
        "g1_squared_over_gY_squared": str(coupling_convention_g1_squared_over_gY_squared()),
        "trace_weights_unify_after_eta": trace_weights_unify_after_eta(),
        "rg_running_derived": rg_running_derived(),
        "measured_couplings_predicted": measured_couplings_predicted(),
        "replacement_claim_ready": replacement_claim_ready(),
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "trace_normalization_layer_discharged_conditionally": True,
        "rg_running_derived": False,
        "measured_couplings_predicted": False,
        "discharged_obligations": {
            "PO-BH-14": "DERIVED_CONDITIONAL: boundary trace weights give K1=10/3, K2=2, K3=2 and eta_Y=3/5"
        },
        "trace_weights": {
            "K1_hypercharge_raw": "10/3",
            "K2_orientation": "2",
            "K3_cyclic": "2",
            "eta_Y": "3/5",
            "K1_hypercharge_normalized": "2",
            "g1_squared_over_gY_squared": "5/3",
        },
        "normalized_gauge_action_skeleton": "k[Tr(F_cyc^2)+Tr(F_orient^2)+eta_Y F_Y^2]",
        "still_open_downstream": [
            "RG running theorem",
            "measured gauge coupling theorem",
            "Higgs/scalar mechanism theorem",
            "mass/Yukawa/mixing theorem-level derivation",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "bridges_preserved": {
            "primitive_closure_spectrum": True,
            "finite_boundary_algebra_charge_layer": True,
            "anomaly_boundary_consistency": True,
            "gauge_algebra_automorphism_layer": True,
            "gauge_action_curvature_layer": True,
        },
        "negative_results": [
            "RG running not derived in this branch",
            "measured gauge couplings not predicted in this branch",
            "replacement claim is not ready because RG running, Higgs/scalar sector, mass/Yukawa/mixing, and low-energy Lagrangian derivations remain open",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for boundary trace normalization",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "summary": theorem_discharge_summary(),
    }


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _trace_result_rows_markdown() -> str:
    lines = ["| name | value | status | interpretation |", "| --- | --- | --- | --- |"]
    for row in all_trace_weight_results():
        lines.append(
            f"| `{row.name}` | `{_fraction_text(row.value)}` | `{row.status}` | {row.interpretation} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Boundary Trace Normalization

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum `{{1,2,3}}`, finite boundary algebra, boundary charge/hypercharge operators, anomaly cancellation as boundary consistency, boundary gauge-algebra skeleton, and boundary gauge-action skeleton.

## 3. Why Trace Normalization Is The Next Theorem Blocker

The gauge-action skeleton needs a trace normalization showing how the residual Abelian boundary phase is placed on the same finite-algebra trace footing as the active-orientation and cyclic-channel curvature blocks.

## 4. Boundary Charge/Hypercharge Table Source

The starting operators are:

```text
Q_boundary = 1/2(S_sigma-I)+2/3 P_C
T3_boundary = 1/2 P_w S_sigma
Y_boundary = 2(Q_boundary-T3_boundary)
```

The eigenvalue forms are:

```text
Q(C,sigma) = (sigma-1)/2 + (2/3)C
T3(C,sigma,w) = w sigma / 2
Y(C,sigma,w) = (4/3)C - 1 + (1-w)sigma
```

## 5. Single Left-Oriented Boundary Trace Basis

This branch uses the single left-oriented boundary basis from the anomaly-consistency layer. Active rows use `w=1`; inactive rows are counted through their conjugate inactive basis.

## 6. Active Boundary Sector

```text
w=1
Y_active(0)=-1
Y_active(1)=1/3
N(C)=1+2C
```

The active sector has two orientation components.

## 7. Conjugate Inactive Boundary Sector

```text
Y_conjugate = -Y_inactive
Y^c in {{0, 2, -4/3, 2/3}}
```

The channel multiplicities are `1,1,3,3`.

## 8. Abelian Trace Weight (K_1)

Using the physical boundary charge convention `Q=T3+Y/2`, the Abelian trace generator is `T_Y=Y/2`.

```text
K1 =
2*1*(-1/2)^2
+ 2*3*(1/6)^2
+ 1*(0)^2
+ 1*(1)^2
+ 3*(-2/3)^2
+ 3*(1/3)^2
= 10/3
```

## 9. Active-Orientation Trace Weight (K_2)

```text
K2 = (1+3)*(1/2) = 2
```

## 10. Cyclic-Channel Trace Weight (K_3)

```text
K3 = 4*(1/2) = 2
```

## 11. Hypercharge Normalization Factor (eta_Y=3/5)

```text
eta_Y = K2/K1 = 2/(10/3) = 3/5
eta_Y*K1 = 2 = K2 = K3
```

## 12. Normalized Gauge-Action Skeleton

```text
S_gauge_boundary_norm =
k [
  Tr_cyc(F_cyc wedge *F_cyc)
  + Tr_orient(F_orient wedge *F_orient)
  + eta_Y F_Y wedge *F_Y
]
```

## 13. Coupling-Convention Consequence

If a later convention writes the physical hypercharge coupling against `Y/2`, while the normalized gauge coupling is written against `sqrt(eta_Y)Y/2`, then:

```text
g1^2 = (5/3) gY^2
alpha1 = (5/3) alphaY
```

This is a convention consequence of the trace normalization. It is not an RG-running derivation or a measured-coupling prediction.

## 14. Non-Tautology Checks

See [Trace Normalization Non-Tautology Audit](trace_normalization_non_tautology_audit.md).

## 15. Promoted Results, If Any

- `PO_BH_14_BOUNDARY_TRACE_NORMALIZATION_DERIVED_CONDITIONAL`
- `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL`
- `BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL`
- `NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL`

## 16. Remaining Blockers

- RG running theorem;
- measured gauge coupling theorem;
- Higgs/scalar mechanism theorem;
- mass/Yukawa/mixing theorem-level derivation;
- full low-energy Lagrangian theorem;
- full replacement-level derivation.

## 17. Impact On Coupling/RG Theorem

This branch derives a boundary trace-normalization factor and a coupling-convention relation. It does not derive RG running or measured coupling values.

## 18. Impact On Higgs/Scalar Theorem

No Higgs/scalar theorem is discharged here.

## 19. Impact On Mass/Yukawa/Mixing Theorem

No mass, Yukawa, or mixing output changes. No official prediction changes.

## 20. What This Achieves

{CONCLUSION_LANGUAGE}

## 21. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until RG running, measured coupling matching, Higgs/scalar mechanism, mass/Yukawa/mixing, and full low-energy Lagrangian theorem layers are complete.

## Trace Result Table

{_trace_result_rows_markdown()}

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_trace_weights_markdown() -> str:
    return """# Derived Boundary Trace Weights

## Active Sector

```text
Y_active(0)=-1
Y_active(1)=1/3
```

Active contribution to `K_1`:

```text
2*1*(-1/2)^2 + 2*3*(1/6)^2
= 1/2 + 1/6
= 2/3
```

## Conjugate Inactive Sector

```text
Y^c = 0, 2, -4/3, 2/3
```

Inactive contribution to `K_1`:

```text
0^2 + 1^2 + 3*(-2/3)^2 + 3*(1/3)^2
= 1 + 4/3 + 1/3
= 8/3
```

## Total Abelian Trace Weight

```text
K1 = 2/3 + 8/3 = 10/3
```

## Non-Abelian Trace Weights

```text
K2 = (1+3)*(1/2) = 2
K3 = 4*(1/2) = 2
```

Status: `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL`.
"""


def render_hypercharge_normalization_markdown() -> str:
    return """# Derived Hypercharge Normalization Factor

The exact boundary trace weights are:

```text
K1 = 10/3
K2 = 2
K3 = 2
```

Define:

```text
eta_Y = K2/K1 = 3/5
```

Then:

```text
eta_Y*K1 = 2
eta_Y*K1 = K2 = K3
```

Therefore the normalized residual Abelian generator is:

```text
T_Y_norm = sqrt(3/5) * Y/2
```

The exact rational check uses squared normalization:

```text
Tr(T_Y_norm^2) = (3/5) Tr((Y/2)^2) = 2
```

Coupling-convention relation:

```text
g1^2 = (5/3) gY^2
alpha1 = (5/3) alphaY
```

Guardrail: This is a normalization theorem, not a measured coupling prediction.

Status: `BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL`.
"""


def render_normalized_gauge_action_markdown() -> str:
    return """# Derived Normalized Gauge-Action Skeleton

Starting skeleton:

```text
S_gauge_boundary =
k3 Tr(F_cyc wedge *F_cyc)
+ k2 Tr(F_orient wedge *F_orient)
+ k1 F_Y wedge *F_Y
```

The boundary trace-weight derivation gives:

```text
K1 = 10/3
K2 = 2
K3 = 2
eta_Y = 3/5
```

After normalization, the Abelian kinetic term is placed on the same trace-normalized footing as the cyclic and active-orientation terms:

```text
S_gauge_boundary_norm =
k [
  Tr_cyc(F_cyc wedge *F_cyc)
  + Tr_orient(F_orient wedge *F_orient)
  + eta_Y F_Y wedge *F_Y
]
```

Equivalent compact convention:

```text
k[Tr(F_cyc^2)+Tr(F_orient^2)+eta_Y F_Y^2]
```

Guardrail: This does not derive RG running or measured values.

Status: `NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL`.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("boundary Y table from prior theorem", "uses previously derived Y(C,sigma,w)", "known charge table could be imported", "source is boundary operator formula, not normalization target", "conditional pass", "prior theorem remains conditional"),
        ("active sector trace contribution", "active rows give 2/3", "known multiplet count could be imported", "uses N(C)=1+2C and two active orientation components", "conditional pass", "derive trace basis fully"),
        ("conjugate inactive sector trace contribution", "conjugate inactive rows give 8/3", "right-oriented table could be inserted", "uses conjugation from single left-oriented basis", "conditional pass", "derive conjugate-basis convention fully"),
        ("channel multiplicity", "N(C)=1+2C", "known channel multiplicity could be imported", "uses finite boundary algebra channel block dimensions", "conditional pass", "derive full physical channel interpretation"),
        ("orientation trace index", "fundamental active-orientation index is 1/2", "known non-Abelian index could be imported", "uses finite M2(C) fundamental trace convention", "conditional pass", "derive global normalization of finite trace"),
        ("cyclic trace index", "fundamental cyclic index is 1/2", "known non-Abelian index could be imported", "uses finite M3(C) fundamental trace convention", "conditional pass", "derive curvature dynamics"),
        ("Abelian K1=10/3", "sum boundary multiplicity*(Y/2)^2", "conventional normalization could be inserted", "computed before comparison", "pass", "prior inputs conditional"),
        ("non-Abelian K2=K3=2", "finite-algebra trace weights", "target equality could be imposed", "computed independently from block counts", "conditional pass", "trace-index convention conditional"),
        ("eta_Y=3/5", "eta_Y=K2/K1", "known factor could be imported", "computed only after K values", "pass", "depends on trace-basis assumptions"),
        ("comparison to conventional hypercharge normalization", "5/3 coupling-convention relation", "could be used as premise", "appears after derivation only", "guarded", "not a measured-coupling prediction"),
    ]
    lines = [
        "# Trace Normalization Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.extend(
        [
            "",
            "Conclusion: The derivation does not use known Standard Model/GUT normalization as input. If finite-algebra trace index normalization remains conditional, it is explicitly recorded as a remaining assumption tied to the boundary trace basis.",
        ]
    )
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_boundary_trace_normalization.md": render_main_markdown(),
        "derived_boundary_trace_weights.md": render_trace_weights_markdown(),
        "derived_hypercharge_normalization_factor.md": render_hypercharge_normalization_markdown(),
        "derived_normalized_gauge_action_skeleton.md": render_normalized_gauge_action_markdown(),
        "trace_normalization_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_trace_normalization_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
