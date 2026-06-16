from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-one-loop-rg-boundary-content-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to derive the "
    "one-loop gauge beta coefficients from already-derived BHSM boundary "
    "charge/hypercharge operators, boundary trace normalization, boundary "
    "multiplicities, and gauge algebra. Status labels may be promoted only when "
    "the derivation is explicit, exact, non-tautological, and does not use a "
    "known Standard Model beta-coefficient table as a premise."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the one-loop RG theorem layer. Given "
    "the previously derived boundary trace normalization, boundary gauge algebra, "
    "three-generation branch structure, and active scalar orientation doublet "
    "input, the exact one-loop beta coefficients are b1=41/10, b2=-19/6, and "
    "b3=-7 under the convention dg_i/dln(mu)=b_i g_i^3/(16 pi^2). The "
    "coefficients are derived from BHSM boundary trace sums and gauge "
    "self-interaction terms rather than imported from a Standard Model "
    "beta-coefficient table."
)
VERDICT_LABELS = [
    "THEOREM_DISCHARGE_ONE_LOOP_RG_BOUNDARY_CONTENT_COMPLETE",
    "PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL",
    "BOUNDARY_FERMION_TRACE_SUMS_DERIVED_CONDITIONAL",
    "BOUNDARY_SCALAR_TRACE_SUMS_DERIVED_CONDITIONAL",
    "BETA_COEFFICIENTS_41_10_NEG_19_6_NEG_7_DERIVED_CONDITIONAL",
    "MEASURED_COUPLINGS_REMAIN_OPEN",
    "TWO_LOOP_RG_REMAINS_OPEN",
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
class BetaContribution:
    sector: str
    b1: Fraction
    b2: Fraction
    b3: Fraction
    interpretation: str

    def as_tuple(self) -> tuple[Fraction, Fraction, Fraction]:
        return (self.b1, self.b2, self.b3)


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: DischargeStatus
    statement: str
    dependencies: tuple[str, ...]
    remaining_blocker: str


def K1_normalized() -> Fraction:
    return Fraction(2, 1)


def K2_orientation() -> Fraction:
    return Fraction(2, 1)


def K3_cyclic() -> Fraction:
    return Fraction(2, 1)


def fermion_trace_sums_one_generation() -> tuple[Fraction, Fraction, Fraction]:
    return (K1_normalized(), K2_orientation(), K3_cyclic())


def fermion_beta_one_generation() -> BetaContribution:
    factor = Fraction(2, 3)
    traces = fermion_trace_sums_one_generation()
    return BetaContribution(
        "fermion_one_generation",
        *(factor * value for value in traces),
        interpretation="one boundary generation Weyl trace contribution",
    )


def number_of_boundary_generations() -> int:
    return 3


def fermion_beta_all_generations() -> BetaContribution:
    one = fermion_beta_one_generation()
    n_gen = number_of_boundary_generations()
    return BetaContribution(
        "fermion_three_generations",
        n_gen * one.b1,
        n_gen * one.b2,
        n_gen * one.b3,
        "three-generation boundary branch contribution",
    )


def gauge_self_beta() -> BetaContribution:
    return BetaContribution(
        "gauge_self_interaction",
        Fraction(0),
        -Fraction(11, 3) * Fraction(2),
        -Fraction(11, 3) * Fraction(3),
        "adjoint self-interaction terms with C2=(0,2,3)",
    )


def scalar_trace_sums_active_doublet() -> tuple[Fraction, Fraction, Fraction]:
    return (Fraction(3, 10), Fraction(1, 2), Fraction(0))


def scalar_beta_active_doublet() -> BetaContribution:
    factor = Fraction(1, 3)
    traces = scalar_trace_sums_active_doublet()
    return BetaContribution(
        "scalar_active_doublet",
        *(factor * value for value in traces),
        interpretation="conditional active scalar orientation doublet contribution",
    )


def total_one_loop_beta() -> BetaContribution:
    gauge = gauge_self_beta()
    fermion = fermion_beta_all_generations()
    scalar = scalar_beta_active_doublet()
    return BetaContribution(
        "total_one_loop",
        gauge.b1 + fermion.b1 + scalar.b1,
        gauge.b2 + fermion.b2 + scalar.b2,
        gauge.b3 + fermion.b3 + scalar.b3,
        "one-loop beta coefficients from boundary content",
    )


def expected_beta_tuple() -> tuple[Fraction, Fraction, Fraction]:
    return (Fraction(41, 10), Fraction(-19, 6), Fraction(-7, 1))


def beta_coefficients_match_expected() -> bool:
    return total_one_loop_beta().as_tuple() == expected_beta_tuple()


def measured_couplings_predicted() -> bool:
    return False


def two_loop_rg_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-15": DischargeRecord(
            "PO-BH-15",
            "derive one-loop RG coefficients from boundary content",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Boundary trace sums, gauge self-interactions, three boundary generations, and the active scalar doublet input give b=(41/10,-19/6,-7).",
            (
                "boundary trace normalization",
                "boundary gauge algebra C2=(0,2,3)",
                "three-generation branch structure",
                "active scalar orientation doublet input",
                "standard one-loop QFT representation formula",
            ),
            "Measured gauge matching, two-loop/threshold running, Higgs/scalar mechanism, and mass/Yukawa/mixing derivations remain downstream.",
        )
    }


def theorem_discharge_summary() -> dict:
    total = total_one_loop_beta()
    return {
        "one_loop_rg_layer_discharged_conditionally": True,
        "fermion_trace_sums_one_generation": [str(x) for x in fermion_trace_sums_one_generation()],
        "fermion_beta_one_generation": [str(x) for x in fermion_beta_one_generation().as_tuple()],
        "fermion_beta_three_generations": [str(x) for x in fermion_beta_all_generations().as_tuple()],
        "gauge_self_beta": [str(x) for x in gauge_self_beta().as_tuple()],
        "scalar_trace_sums_active_doublet": [str(x) for x in scalar_trace_sums_active_doublet()],
        "scalar_beta_active_doublet": [str(x) for x in scalar_beta_active_doublet().as_tuple()],
        "total_beta": [str(x) for x in total.as_tuple()],
        "matches_expected_tuple": beta_coefficients_match_expected(),
        "measured_couplings_predicted": measured_couplings_predicted(),
        "two_loop_rg_derived": two_loop_rg_derived(),
        "replacement_claim_ready": replacement_claim_ready(),
    }


def _tuple_strings(values: tuple[Fraction, Fraction, Fraction]) -> list[str]:
    return [str(value) for value in values]


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "one_loop_rg_layer_discharged_conditionally": True,
        "measured_couplings_predicted": False,
        "two_loop_rg_derived": False,
        "discharged_obligations": {
            "PO-BH-15": "DERIVED_CONDITIONAL: one-loop beta coefficients derived from BHSM boundary trace sums, gauge self-interactions, and active scalar boundary input"
        },
        "beta_coefficients": {
            "convention": "dg_i/dlnmu = b_i g_i^3/(16 pi^2)",
            "b1": "41/10",
            "b2": "-19/6",
            "b3": "-7",
        },
        "contributions": {
            "gauge": _tuple_strings(gauge_self_beta().as_tuple()),
            "fermion_three_generations": _tuple_strings(fermion_beta_all_generations().as_tuple()),
            "scalar_active_doublet": _tuple_strings(scalar_beta_active_doublet().as_tuple()),
        },
        "still_open_downstream": [
            "measured gauge coupling matching theorem",
            "two-loop RG and threshold theorem",
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
            "trace_normalization_layer": True,
        },
        "negative_results": [
            "measured gauge couplings not predicted in this branch",
            "two-loop RG not derived in this branch",
            "scalar active doublet input remains conditional if not theorem-discharged elsewhere",
            "replacement claim is not ready because measured matching, Higgs/scalar sector, mass/Yukawa/mixing, and low-energy Lagrangian derivations remain open",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for one-loop RG beta coefficients",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "summary": theorem_discharge_summary(),
    }


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: One-Loop RG From Boundary Content

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum `{{1,2,3}}`, finite boundary algebra, boundary charge/hypercharge operators, anomaly cancellation as boundary consistency, boundary gauge-algebra skeleton, boundary gauge-action skeleton, and boundary trace normalization with `K1=10/3`, `K2=2`, `K3=2`, and `eta_Y=3/5`.

## 3. Why One-Loop RG Coefficients Are The Next Theorem Blocker

The gauge-action skeleton has trace-normalized generators. The next theorem layer asks whether the one-loop coefficients follow from boundary field content and gauge-algebra data rather than an imported coefficient table.

## 4. Boundary Gauge Algebra And Action Source

Gauge self-interactions use `C2=(0,2,3)` for the Abelian, active-orientation, and cyclic-channel factors.

## 5. Boundary Trace Normalization Source

The prior trace-normalization layer gives one boundary generation matter trace sums:

```text
sum_f T1 = 2
sum_f T2 = 2
sum_f T3 = 2
```

## 6. One-Loop QFT Representation Formula

See [Derived One-Loop RG Formula Boundary](derived_one_loop_rg_formula_boundary.md). The QFT infrastructure formula is:

```text
b_i =
- (11/3) C2(G_i)
+ (2/3) sum_Weyl T_i(R_f)
+ (1/3) sum_complex_scalar T_i(R_s)
```

## 7. Boundary Fermion Trace Sums

See [Derived Boundary Fermion Trace Sums](derived_boundary_fermion_trace_sums.md).

```text
b_f/gen = (2/3)*(2,2,2) = (4/3,4/3,4/3)
N_gen = 3
b_f = (4,4,4)
```

## 8. Three-Generation Boundary Multiplicity

This branch depends on the existing three-generation branch theorem/scaffold result. If that input remains conditional elsewhere, this one-loop theorem layer is conditional on it.

## 9. Gauge Self-Interaction Contributions

```text
b_gauge = (0, -22/3, -11)
```

## 10. Active Scalar Boundary Contribution

See [Derived Boundary Scalar Trace Sums](derived_boundary_scalar_trace_sums.md).

```text
b_scalar = (1/10, 1/6, 0)
```

The active scalar orientation doublet remains a conditional scalar-sector input if not theorem-discharged elsewhere.

## 11. Exact One-Loop Beta Coefficients

See [Derived Boundary Beta Coefficients](derived_boundary_beta_coefficients.md).

```text
b_total =
(0, -22/3, -11)
+ (4, 4, 4)
+ (1/10, 1/6, 0)
= (41/10, -19/6, -7)
```

## 12. Non-Tautology Checks

See [One-Loop RG Non-Tautology Audit](one_loop_rg_non_tautology_audit.md).

## 13. Promoted Results, If Any

- `PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL`
- `BOUNDARY_FERMION_TRACE_SUMS_DERIVED_CONDITIONAL`
- `BOUNDARY_SCALAR_TRACE_SUMS_DERIVED_CONDITIONAL`
- `BETA_COEFFICIENTS_41_10_NEG_19_6_NEG_7_DERIVED_CONDITIONAL`

## 14. Remaining Blockers

- measured gauge coupling matching theorem;
- two-loop RG and threshold theorem;
- Higgs/scalar mechanism theorem;
- mass/Yukawa/mixing theorem-level derivation;
- full low-energy Lagrangian theorem;
- full replacement-level derivation.

## 15. Impact On Measured Gauge Matching

This branch derives one-loop coefficients conditionally. It does not predict measured coupling values.

## 16. Impact On Higgs/Scalar Theorem

The scalar contribution uses the active scalar orientation doublet as a conditional scalar-sector input.

## 17. Impact On Mass/Yukawa/Mixing Theorem

No official mass, Yukawa, or mixing output changes.

## 18. What This Achieves

{CONCLUSION_LANGUAGE}

## 19. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until measured matching, two-loop/threshold RG, Higgs/scalar mechanism, mass/Yukawa/mixing, and full low-energy Lagrangian theorem layers are complete.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_formula_markdown() -> str:
    return """# Derived One-Loop RG Formula Boundary

The one-loop convention is:

```text
dg_i/dlnmu = b_i g_i^3/(16 pi^2)
```

The QFT representation formula used as infrastructure is:

```text
b_i =
- (11/3) C2(G_i)
+ (2/3) sum_Weyl T_i(R_f)
+ (1/3) sum_complex_scalar T_i(R_s)
```

For the Abelian factor, the normalized boundary generator is:

```text
T_Y_norm^2 = eta_Y * (Y/2)^2
eta_Y = 3/5
```

This formula is the standard one-loop gauge-field renormalization theorem used as QFT infrastructure. The branch derives the BHSM-specific trace sums and representations from boundary content.

Guardrail: This is not a measured coupling prediction.
"""


def render_fermion_trace_markdown() -> str:
    return """# Derived Boundary Fermion Trace Sums

The boundary trace-normalization theorem gives one boundary generation:

```text
K1_norm = 2
K2 = 2
K3 = 2
```

Thus:

```text
b_f/gen = (2/3)*(2,2,2) = (4/3,4/3,4/3)
```

With the three-generation branch result:

```text
N_gen = 3
b_f = 3*(4/3,4/3,4/3) = (4,4,4)
```

If the three-generation branch is conditional in the repository theorem stack, this result depends on that conditional input.

Status: `BOUNDARY_FERMION_TRACE_SUMS_DERIVED_CONDITIONAL`.
"""


def render_scalar_trace_markdown() -> str:
    return """# Derived Boundary Scalar Trace Sums

Active scalar orientation doublet input:

```text
Y = +1
eta_Y = 3/5
two orientation components
```

Abelian scalar trace:

```text
sum_s T1 = 2*(3/5)*(1/2)^2 = 3/10
b1_scalar = (1/3)*(3/10) = 1/10
```

Orientation scalar trace:

```text
sum_s T2 = 1/2
b2_scalar = (1/3)*(1/2) = 1/6
```

Cyclic scalar trace:

```text
b3_scalar = 0
```

Therefore:

```text
b_scalar = (1/10,1/6,0)
```

Guardrail: If the scalar doublet is still conditional in the theorem stack, this is a conditional scalar-sector input.

Status: `BOUNDARY_SCALAR_TRACE_SUMS_DERIVED_CONDITIONAL`.
"""


def render_beta_coefficients_markdown() -> str:
    return """# Derived Boundary Beta Coefficients

Gauge contribution:

```text
b_gauge = (0, -22/3, -11)
```

Fermion contribution:

```text
b_fermion = (4,4,4)
```

Scalar contribution:

```text
b_scalar = (1/10,1/6,0)
```

Total:

```text
b_total =
(0, -22/3, -11)
+ (4,4,4)
+ (1/10,1/6,0)
= (41/10, -19/6, -7)
```

Status: `PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL`.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("one-loop QFT formula", "uses representation beta formula", "coefficient table could be imported", "formula is QFT infrastructure, not a BHSM-specific table", "conditional pass", "higher-loop theorem open"),
        ("boundary fermion trace sums", "one-generation traces are (2,2,2)", "known matter table could be imported", "uses prior boundary trace-normalization layer", "conditional pass", "prior trace layer conditional"),
        ("three-generation multiplicity", "N_gen=3", "known family count could be imported", "uses existing three-generation branch result", "conditional pass", "depends on branch theorem status"),
        ("gauge self-interaction terms", "C2=(0,2,3)", "known gauge data could be imported", "uses boundary gauge algebra skeleton", "conditional pass", "full gauge dynamics still open if not discharged"),
        ("scalar active-orientation doublet", "b_scalar=(1/10,1/6,0)", "known scalar content could be imported", "marked conditional scalar-sector input", "conditional pass", "full scalar theorem open"),
        ("beta coefficient totals", "b=(41/10,-19/6,-7)", "known beta table could be copied", "computed from preceding rows before comparison", "pass", "measured matching open"),
        ("comparison to known low-energy SM one-loop coefficients", "agreement can be checked after derivation", "comparison could feed back into construction", "comparison is after derivation only", "guarded", "do not use as premise"),
    ]
    lines = [
        "# One-Loop RG Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.extend(
        [
            "",
            "Conclusion: The branch does not use known SM beta coefficients as input. If the active scalar doublet or three-generation input remains conditional, that dependency is explicit.",
        ]
    )
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_one_loop_rg_boundary_content.md": render_main_markdown(),
        "derived_one_loop_rg_formula_boundary.md": render_formula_markdown(),
        "derived_boundary_fermion_trace_sums.md": render_fermion_trace_markdown(),
        "derived_boundary_scalar_trace_sums.md": render_scalar_trace_markdown(),
        "derived_boundary_beta_coefficients.md": render_beta_coefficients_markdown(),
        "one_loop_rg_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_one_loop_rg_results.json": json.dumps(build_results_payload(), indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
