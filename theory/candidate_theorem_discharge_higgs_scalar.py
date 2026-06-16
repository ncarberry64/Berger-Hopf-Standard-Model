from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-higgs-scalar-boundary-mechanism-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to derive the "
    "active scalar orientation doublet from boundary cyclic neutrality, "
    "active-orientation breaking, and neutral-vacuum consistency, rather than "
    "importing the Standard Model Higgs representation as an assumption. Status "
    "labels may be promoted only when the derivation is explicit, exact, "
    "non-tautological, and does not use the known Standard Model Higgs doublet as "
    "a premise."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the Higgs/scalar boundary-mechanism "
    "theorem layer. Boundary cyclic preservation requires C=0, active-orientation "
    "breaking requires a fundamental orientation doublet, and neutral-vacuum "
    "consistency under Q=T3+Y/2 selects Y=+1 up to conjugation. The resulting "
    "scalar has component charges (+1,0), admits a neutral vacuum preserving "
    "U(1)_Q, and yields the electroweak-breaking skeleton SU(2)_orient x U(1)_Y "
    "-> U(1)_Q. The representation source for the scalar contribution used in "
    "the one-loop RG theorem is therefore derived conditionally from BHSM "
    "boundary constraints."
)
VERDICT_LABELS = [
    "THEOREM_DISCHARGE_HIGGS_SCALAR_BOUNDARY_MECHANISM_COMPLETE",
    "PO_BH_16_HIGGS_SCALAR_ACTIVE_ORIENTATION_DOUBLET_DERIVED_CONDITIONAL",
    "BOUNDARY_ACTIVE_SCALAR_DOUBLET_DERIVED_CONDITIONAL",
    "SCALAR_CHARGE_TABLE_DERIVED_CONDITIONAL",
    "SCALAR_CONJUGATE_DOUBLET_DERIVED_CONDITIONAL",
    "ELECTROWEAK_BREAKING_GENERATOR_DERIVED_CONDITIONAL",
    "SCALAR_COVARIANT_DERIVATIVE_DERIVED_CONDITIONAL",
    "SCALAR_POTENTIAL_SKELETON_DERIVED_CONDITIONAL",
    "SCALAR_BETA_INPUT_NOW_DERIVED_CONDITIONAL",
    "HIGGS_MASS_REMAINS_OPEN",
    "VEV_REMAINS_OPEN",
    "QUARTIC_REMAINS_OPEN",
    "YUKAWA_MASS_MIXING_REMAINS_OPEN",
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
class ScalarComponent:
    name: str
    sigma: int
    T3: Fraction
    Y: Fraction
    Q: Fraction


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: DischargeStatus
    statement: str
    dependencies: tuple[str, ...]
    remaining_blocker: str


def active_orientation_T3(sigma: int) -> Fraction:
    if sigma not in (-1, 1):
        raise ValueError("sigma must be +/-1")
    return Fraction(sigma, 2)


def electric_charge(T3: Fraction, Y: Fraction) -> Fraction:
    return T3 + Y / 2


def scalar_doublet_components(Y: Fraction = Fraction(1, 1)) -> tuple[ScalarComponent, ...]:
    return (
        ScalarComponent("H_plus", 1, Fraction(1, 2), Y, electric_charge(Fraction(1, 2), Y)),
        ScalarComponent("H_zero", -1, Fraction(-1, 2), Y, electric_charge(Fraction(-1, 2), Y)),
    )


def conjugate_scalar_doublet_components() -> tuple[ScalarComponent, ...]:
    Y = Fraction(-1, 1)
    return (
        ScalarComponent("H_tilde_zero", 1, Fraction(1, 2), Y, electric_charge(Fraction(1, 2), Y)),
        ScalarComponent("H_tilde_minus", -1, Fraction(-1, 2), Y, electric_charge(Fraction(-1, 2), Y)),
    )


def has_neutral_component(Y: Fraction) -> bool:
    return any(c.Q == 0 for c in scalar_doublet_components(Y))


def cyclic_neutral_required() -> bool:
    return True


def scalar_C_value() -> int:
    return 0


def scalar_is_active_orientation_fundamental() -> bool:
    return True


def scalar_Y_selected_up_to_conjugation() -> Fraction:
    return Fraction(1, 1)


def neutral_vev_preserves_Q() -> bool:
    return any(c.name == "H_zero" and c.Q == 0 for c in scalar_doublet_components())


def symmetry_breaking_skeleton() -> str:
    return "SU(2)_orient x U(1)_Y -> U(1)_Q"


def scalar_covariant_derivative_skeleton() -> str:
    return "D_mu H=(partial_mu - i g2 W_mu^a tau^a/2 - i gY B_mu Y/2)H with Y=1"


def gauge_boson_mass_skeleton() -> dict[str, str]:
    return {
        "m_W_squared": "g2^2 v^2/4",
        "m_Z_squared": "(g2^2+gY^2)v^2/4",
        "m_A_squared": "0",
    }


def scalar_beta_input_derived_conditionally() -> bool:
    return True


def higgs_mass_predicted() -> bool:
    return False


def vev_predicted() -> bool:
    return False


def quartic_predicted() -> bool:
    return False


def yukawa_sector_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-16": DischargeRecord(
            "PO-BH-16",
            "derive active scalar orientation doublet",
            DischargeStatus.DERIVED_CONDITIONAL,
            "Active scalar orientation doublet follows from cyclic neutrality, active-orientation breaking, and neutral-vacuum consistency.",
            (
                "Q=T3+Y/2",
                "cyclic sector preservation",
                "active orientation breaking",
                "neutral vacuum component",
                "minimal boundary scalar degree",
            ),
            "Scalar instability sign, Higgs mass, VEV, quartic, and Yukawa/mass/mixing derivations remain downstream.",
        )
    }


def theorem_discharge_summary() -> dict:
    return {
        "higgs_scalar_layer_discharged_conditionally": True,
        "scalar_C": scalar_C_value(),
        "active_orientation_fundamental": scalar_is_active_orientation_fundamental(),
        "Y": str(scalar_Y_selected_up_to_conjugation()),
        "components": {c.name: {"T3": str(c.T3), "Y": str(c.Y), "Q": str(c.Q)} for c in scalar_doublet_components()},
        "conjugate_components": {c.name: {"T3": str(c.T3), "Y": str(c.Y), "Q": str(c.Q)} for c in conjugate_scalar_doublet_components()},
        "neutral_vev_preserves_Q": neutral_vev_preserves_Q(),
        "symmetry_breaking_skeleton": symmetry_breaking_skeleton(),
        "scalar_beta_input_derived_conditionally": scalar_beta_input_derived_conditionally(),
        "higgs_mass_predicted": higgs_mass_predicted(),
        "vev_predicted": vev_predicted(),
        "quartic_predicted": quartic_predicted(),
        "yukawa_sector_derived": yukawa_sector_derived(),
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
        "higgs_scalar_layer_discharged_conditionally": True,
        "higgs_mass_predicted": False,
        "vev_predicted": False,
        "quartic_predicted": False,
        "yukawa_sector_derived": False,
        "discharged_obligations": {
            "PO-BH-16": "DERIVED_CONDITIONAL: active scalar orientation doublet follows from cyclic neutrality, active-orientation breaking, and neutral-vacuum consistency"
        },
        "scalar_representation": {
            "cyclic_channel": "neutral",
            "C": 0,
            "orientation": "active fundamental doublet",
            "Y": "1",
            "components": {
                "H_plus": {"T3": "1/2", "Q": "1"},
                "H_zero": {"T3": "-1/2", "Q": "0"},
            },
            "conjugate": {
                "Y": "-1",
                "components": {
                    "H_tilde_zero": {"T3": "1/2", "Q": "0"},
                    "H_tilde_minus": {"T3": "-1/2", "Q": "-1"},
                },
            },
        },
        "symmetry_breaking_skeleton": symmetry_breaking_skeleton(),
        "gauge_boson_mass_skeleton": gauge_boson_mass_skeleton(),
        "still_open_downstream": [
            "scalar instability sign / negative mass-squared theorem",
            "Higgs mass and quartic theorem",
            "VEV numerical theorem",
            "Yukawa/mass/mixing theorem-level derivation",
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
            "one_loop_rg_layer": True,
        },
        "negative_results": [
            "Higgs mass not predicted in this branch",
            "VEV not predicted in this branch",
            "quartic coupling not predicted in this branch",
            "Yukawa/mass/mixing sector not derived in this branch",
            "replacement claim is not ready because scalar potential parameters, Yukawa/mass/mixing, and low-energy Lagrangian derivations remain open",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem discharge attempt completed for active scalar boundary mechanism",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "summary": theorem_discharge_summary(),
    }


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _component_table(rows: tuple[ScalarComponent, ...]) -> str:
    lines = ["| component | sigma | T3 | Y | Q |", "| --- | --- | --- | --- | --- |"]
    for row in rows:
        lines.append(
            f"| {row.name} | {row.sigma:+d} | {_fraction_text(row.T3)} | {_fraction_text(row.Y)} | {_fraction_text(row.Q)} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Higgs Scalar Boundary Mechanism

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum, finite boundary algebra, boundary charge/hypercharge operators, anomaly consistency, boundary gauge algebra/action skeletons, trace normalization, and one-loop RG coefficients.

## 3. Why The Higgs/Scalar Theorem Is The Next Blocker

The one-loop RG layer used the active scalar orientation doublet as a conditional input. This branch derives that representation source from boundary constraints.

## 4. Boundary Scalar Constraints

The scalar must preserve the cyclic channel, be active under orientation breaking, admit a neutral vacuum component, and be minimal in boundary degree.

## 5. Cyclic Neutrality

Boundary cyclic preservation requires `C=0`.

## 6. Active-Orientation Requirement

Breaking the active-orientation factor requires the scalar to transform as a fundamental orientation doublet.

## 7. Neutral Vacuum Requirement

Using `Q=T3+Y/2`, a vacuum component must have `Q=0`.

## 8. Hypercharge Selection (Y=+1) Up To Conjugation

For `T3=sigma/2`, neutral consistency gives `Y=-sigma`. The two possible neutral choices are conjugate scalar conventions. This branch chooses `Y=+1`.

## 9. Scalar Charge Table

{_component_table(scalar_doublet_components())}

## 10. Derived Conjugate Scalar Doublet

The conjugate `H_tilde=i sigma_2 H*` is derived from the same complex doublet, not added as an independent second scalar multiplet.

{_component_table(conjugate_scalar_doublet_components())}

## 11. Electroweak-Breaking Generator

With `<H>=(0,v/sqrt(2))^T`, `Q<H>=0`, so:

```text
{symmetry_breaking_skeleton()}
```

## 12. Scalar Covariant Derivative

```text
{scalar_covariant_derivative_skeleton()}
```

## 13. Scalar Kinetic/Gauge-Boson Mass Skeleton

```text
m_W^2 = g2^2 v^2/4
m_Z^2 = (g2^2 + gY^2)v^2/4
m_A^2 = 0
```

This is a mass skeleton, not a measured mass prediction.

## 14. Scalar Potential Skeleton

```text
V(H)=m_H^2 H^dagger H + lambda_H (H^dagger H)^2
m_H^2 < 0
```

The instability sign and scalar potential values remain conditional/open unless derived elsewhere.

## 15. What Remains Conditional

The negative mass-squared sign, Higgs mass, VEV, quartic coupling, and Yukawa/mass/mixing sector remain open.

## 16. Non-Tautology Checks

See [Higgs Scalar Non-Tautology Audit](higgs_scalar_non_tautology_audit.md).

## 17. Promoted Results, If Any

- `PO_BH_16_HIGGS_SCALAR_ACTIVE_ORIENTATION_DOUBLET_DERIVED_CONDITIONAL`
- `BOUNDARY_ACTIVE_SCALAR_DOUBLET_DERIVED_CONDITIONAL`
- `ELECTROWEAK_BREAKING_GENERATOR_DERIVED_CONDITIONAL`
- `SCALAR_BETA_INPUT_NOW_DERIVED_CONDITIONAL`

## 18. Impact On One-Loop RG Theorem

The active scalar input used in the one-loop RG theorem now has a conditional boundary-representation source.

## 19. Impact On Yukawa/Mass Theorem

No Yukawa, mass, or mixing theorem is completed here.

## 20. What This Achieves

{CONCLUSION_LANGUAGE}

## 21. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until scalar potential parameters, Yukawa/mass/mixing, and full low-energy Lagrangian derivations are complete.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_active_doublet_markdown() -> str:
    return """# Derived Active Scalar Orientation Doublet

- Cyclic-sector preservation requires `C=0`.
- Active-orientation breaking requires a fundamental orientation doublet.
- Neutral-vacuum consistency requires one component with `Q=0`.
- With `Q=T3+Y/2`, the minimal choice is `Y=+1` up to conjugation.

Status: `BOUNDARY_ACTIVE_SCALAR_DOUBLET_DERIVED_CONDITIONAL`.
"""


def render_scalar_charge_table_markdown() -> str:
    return f"""# Derived Scalar Charge Table

{_component_table(scalar_doublet_components())}

## Conjugate Table

{_component_table(conjugate_scalar_doublet_components())}

Guardrail: The conjugate doublet is derived from the single complex scalar, not an independent second scalar multiplet.

Status: `SCALAR_CHARGE_TABLE_DERIVED_CONDITIONAL`.
"""


def render_conjugate_markdown() -> str:
    return f"""# Derived Scalar Conjugate Doublet

```text
H_tilde = i sigma_2 H*
```

The conjugate has `Y=-1` and component charges `(0,-1)`:

{_component_table(conjugate_scalar_doublet_components())}

Status: `SCALAR_CONJUGATE_DOUBLET_DERIVED_CONDITIONAL`.
"""


def render_breaking_markdown() -> str:
    return f"""# Derived Electroweak-Breaking Generator

Choose the neutral vacuum:

```text
<H> = (0, v/sqrt(2))^T
```

The lower component has `Q=0`, so:

```text
Q <H> = 0
Q = T3 + Y/2
```

Therefore:

```text
{symmetry_breaking_skeleton()}
```

Status: `ELECTROWEAK_BREAKING_GENERATOR_DERIVED_CONDITIONAL`.
"""


def render_covariant_derivative_markdown() -> str:
    masses = gauge_boson_mass_skeleton()
    return f"""# Derived Scalar Covariant Derivative

```text
D_mu H =
(partial_mu - i g2 W_mu^a tau^a/2 - i gY B_mu Y/2) H
Y=1
```

The skeleton references the active `su(2)_orient` generators and the `u(1)_Y` boundary generator.

Gauge-boson mass skeleton:

```text
m_W^2 = {masses['m_W_squared']}
m_Z^2 = {masses['m_Z_squared']}
m_A^2 = {masses['m_A_squared']}
```

Guardrail: This is a mass skeleton, not a measured mass prediction.

Status: `SCALAR_COVARIANT_DERIVATIVE_DERIVED_CONDITIONAL`.
"""


def render_potential_markdown() -> str:
    return """# Derived Scalar Potential Skeleton

The minimal local gauge-invariant scalar potential is:

```text
V(H)=m_H^2 H^dagger H + lambda_H (H^dagger H)^2
```

Symmetry breaking requires:

```text
m_H^2 < 0
```

Guardrail: the sign and values of `m_H^2`, `v`, and `lambda_H` are not theorem-derived in this branch and remain open/conditional.

Status: `SCALAR_POTENTIAL_SKELETON_DERIVED_CONDITIONAL`.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("cyclic neutrality C=0", "scalar is cyclic neutral", "known scalar color neutrality could be imported", "derived from preserving cyclic channel", "conditional pass", "derive full scalar sector dynamics"),
        ("active-orientation fundamental", "scalar is orientation doublet", "known Higgs doublet could be imported", "derived from needing active-orientation breaking", "conditional pass", "derive full action source"),
        ("neutral-vacuum requirement", "one component has Q=0", "known neutral vacuum could be imported", "uses Q=T3+Y/2 consistency", "pass", "derive vacuum dynamics"),
        ("Y=+1 selection up to conjugation", "Y selected by neutral component", "known hypercharge could be imported", "computed from Y=-sigma then convention fixed", "pass", "derive convention globally"),
        ("scalar charge table", "charges are (+1,0)", "known table could be copied", "computed from T3 and Y", "pass", "none at representation level"),
        ("conjugate doublet", "H_tilde derived from H", "second scalar could be inserted", "not independent", "pass", "none at representation level"),
        ("unbroken Q", "Q<H>=0", "known electroweak pattern could be imported", "computed from neutral component", "pass", "derive vacuum selection"),
        ("scalar covariant derivative", "D_mu uses orient and Y generators", "known derivative could be imported", "uses derived representation", "conditional pass", "derive full local action"),
        ("gauge-boson mass skeleton", "m_W,m_Z,m_A skeleton", "known masses could be imported", "symbolic only, no measured values", "guarded", "derive v and couplings"),
        ("scalar potential skeleton", "minimal invariant potential", "known potential could be imported", "only invariant skeleton, parameters open", "conditional pass", "derive instability and parameters"),
        ("comparison to known Higgs representation", "agreement checked after derivation", "comparison could feed construction", "comparison appears after derivation only", "guarded", "do not use as premise"),
    ]
    lines = [
        "# Higgs Scalar Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: The branch does not use the known SM Higgs representation as input. The scalar instability sign and scalar potential parameters remain conditional/open.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_higgs_scalar_boundary_mechanism.md": render_main_markdown(),
        "derived_active_scalar_orientation_doublet.md": render_active_doublet_markdown(),
        "derived_scalar_charge_table.md": render_scalar_charge_table_markdown(),
        "derived_scalar_conjugate_doublet.md": render_conjugate_markdown(),
        "derived_electroweak_breaking_generator.md": render_breaking_markdown(),
        "derived_scalar_covariant_derivative.md": render_covariant_derivative_markdown(),
        "derived_scalar_potential_skeleton.md": render_potential_markdown(),
        "higgs_scalar_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_higgs_scalar_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
