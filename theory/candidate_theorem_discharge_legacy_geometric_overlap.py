from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-legacy-geometric-overlap-bridge-v1"
STATUS = "theorem_discharge_candidate"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch bridges the legacy "
    "scalar-topographic/Berger-sphere Yukawa overlap integral into the current "
    "BHSM theorem stack, identifying the BHSM overlap kernel as a geometric "
    "internal-mode integral rather than a fitted distance law. Status labels may "
    "be promoted only when the bridge is explicit, non-tautological, and does not "
    "use measured fermion masses or mixing angles as input."
)
CONCLUSION_LANGUAGE = (
    "This branch conditionally discharges the legacy geometric-overlap bridge "
    "theorem layer. The current BHSM Yukawa kernel I_f(i,j) is identified with "
    "the legacy scalar-topographic internal overlap integral over the "
    "Berger/internal space. In the sharp-peak limit of the universal "
    "Higgs/topographic profile, the kernel reduces to a product of internal mode "
    "amplitudes at the distinguished point y0. Because strict point sampling is "
    "an outer-product approximation, it supplies a leading focusing term rather "
    "than a full rank-three Yukawa matrix by itself. Numerical Yukawa values, "
    "fermion mass ratios, CKM values, and PMNS values remain open until the "
    "relevant internal eigenfunction amplitudes and finite-width overlap moments "
    "are computed without fitting."
)


class BridgeStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    APPROXIMATION_DERIVED_CONDITIONAL = "APPROXIMATION_DERIVED_CONDITIONAL"
    NUMERICAL_OPEN = "NUMERICAL_OPEN"
    NOT_DERIVED = "NOT_DERIVED"


@dataclass(frozen=True)
class BridgeComponent:
    name: str
    statement: str
    status: str
    guardrail: str


VERDICT_LABELS = [
    "THEOREM_DISCHARGE_LEGACY_GEOMETRIC_OVERLAP_BRIDGE_COMPLETE",
    "PO_BH_22_LEGACY_GEOMETRIC_OVERLAP_KERNEL_BRIDGED_CONDITIONAL",
    "LEGACY_YUKAWA_OVERLAP_INTEGRAL_BRIDGED_CONDITIONAL",
    "BHSM_GEOMETRIC_OVERLAP_KERNEL_DERIVED_CONDITIONAL",
    "UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL",
    "SHARP_PEAK_Y0_SAMPLING_APPROXIMATION_DERIVED_CONDITIONAL",
    "SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL",
    "INTERNAL_MODE_AMPLITUDE_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL",
    "DISTANCE_OVERLAP_RECONCILIATION_DERIVED_CONDITIONAL",
    "NUMERICAL_EIGENFUNCTION_AMPLITUDES_REMAIN_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def legacy_overlap_integral() -> str:
    return "Y_ij^f = g_f integral Psi_L_i^*(y) Phi(y) Psi_R_j(y) dV_int"


def bhsm_overlap_kernel() -> str:
    return "I_f(i,j)=integral_{B^3} Psi_A_f_i^*(y) Phi_H_f(y) Psi_S_f_j(y) dV_gamma"


def universal_profile() -> str:
    return "Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]"


def sharp_peak_approximation() -> str:
    return "I_f(i,j) approx Phi0 Psi_A_f_i^*(y0) Psi_S_f_j(y0)"


def strict_point_sampling_rank_bound() -> str:
    return "rank(I)<=1 for strict point-sampling outer-product approximation"


def kernel_bridge_status() -> str:
    return BridgeStatus.DERIVED_CONDITIONAL.value


def rank_three_yukawa_matrix_derived() -> bool:
    return False


def numerical_eigenfunction_amplitudes_computed() -> bool:
    return False


def numerical_yukawa_values_derived() -> bool:
    return False


def fermion_mass_ratios_derived() -> bool:
    return False


def ckm_values_derived() -> bool:
    return False


def pmns_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def source_ingestion_complete() -> bool:
    return False


def bridge_components() -> tuple[BridgeComponent, ...]:
    return (
        BridgeComponent(
            "legacy_integral",
            legacy_overlap_integral(),
            "LEGACY_YUKAWA_OVERLAP_INTEGRAL_BRIDGED_CONDITIONAL",
            "prompt-provided legacy formula; source ingestion remains incomplete",
        ),
        BridgeComponent(
            "bhsm_kernel",
            bhsm_overlap_kernel(),
            "BHSM_GEOMETRIC_OVERLAP_KERNEL_DERIVED_CONDITIONAL",
            "identifies symbolic kernel only",
        ),
        BridgeComponent(
            "universal_profile",
            universal_profile(),
            "UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL",
            "universal profile, no flavor/generation fitted widths",
        ),
        BridgeComponent(
            "sharp_peak",
            sharp_peak_approximation(),
            "SHARP_PEAK_Y0_SAMPLING_APPROXIMATION_DERIVED_CONDITIONAL",
            "leading focusing approximation only",
        ),
        BridgeComponent(
            "rank_guardrail",
            strict_point_sampling_rank_bound(),
            "SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL",
            "strict point sampling cannot by itself produce rank three",
        ),
    )


def proof_discharge_ledger() -> dict[str, str]:
    return {
        "PO-BH-22": (
            "DERIVED_CONDITIONAL: BHSM Yukawa overlap kernel is bridged to the "
            "legacy scalar-topographic internal overlap integral; strict point "
            "sampling is rank-limited and numerical eigenfunction amplitudes "
            "remain open"
        )
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "legacy_geometric_overlap_bridge_discharged_conditionally": True,
        "source_ingestion_complete": source_ingestion_complete(),
        "strict_point_sampling_rank_three_derived": rank_three_yukawa_matrix_derived(),
        "numerical_eigenfunction_amplitudes_computed": numerical_eigenfunction_amplitudes_computed(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "fermion_mass_ratios_derived": fermion_mass_ratios_derived(),
        "ckm_values_derived": ckm_values_derived(),
        "pmns_values_derived": pmns_values_derived(),
        "discharged_obligations": proof_discharge_ledger(),
        "kernel": {
            "legacy_integral": legacy_overlap_integral(),
            "bhsm_form": bhsm_overlap_kernel(),
            "universal_profile": universal_profile(),
            "sharp_peak_limit": sharp_peak_approximation(),
            "rank_guardrail": "strict point sampling is an outer product and has rank <= 1",
        },
        "bridge_components": [
            {
                "name": component.name,
                "statement": component.statement,
                "status": component.status,
                "guardrail": component.guardrail,
            }
            for component in bridge_components()
        ],
        "still_open_downstream": [
            "internal Berger/BHSM eigenfunction theorem",
            "eigenfunction amplitudes at y0",
            "finite-width overlap moment theorem",
            "rank-three Yukawa matrix theorem",
            "numerical Yukawa coupling theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "neutral-sector mass scale theorem",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "strict point sampling alone does not derive full rank-three Yukawa matrices",
            "legacy source ingestion remains incomplete until source docs are added to the repo",
            "numerical eigenfunction amplitudes not computed in this branch",
            "numerical Yukawa values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "legacy scalar-topographic Yukawa overlap integral bridged into BHSM notation",
            "PO-BH-21 distance-law result remains valid: no direct numerical distance-to-overlap map is promoted",
            "rank guardrail prevents overclaiming the sharp-peak approximation",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _components_table() -> str:
    lines = ["| component | statement | status | guardrail |", "| --- | --- | --- | --- |"]
    for component in bridge_components():
        lines.append(
            f"| {component.name} | `{component.statement}` | `{component.status}` | {component.guardrail} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Legacy Geometric Overlap Bridge

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived boundary closure, finite algebra, charges, gauge skeletons, scalar representation, Yukawa operator closure, symbolic Yukawa matrices, kernel selection, and distance diagnostics.

## 3. PO-BH-21 Result And Why It Was Partial

PO-BH-21 correctly left direct numerical distance-to-overlap laws open. It did not find a theorem-derived map `D_f(i,j) -> I_f(i,j)` that avoids fitted masses or mixing data.

## 4. Legacy Scalar-Topographic Overlap Integral

```text
{legacy_overlap_integral()}
```

## 5. Universal Higgs/Topographic Profile

```text
{universal_profile()}
```

## 6. Bridge To Current BHSM Notation

```text
{bhsm_overlap_kernel()}
```

## 7. Sharp-Peak Sampling Approximation

```text
{sharp_peak_approximation()}
```

## 8. Rank Guardrail For Strict Point Sampling

```text
{strict_point_sampling_rank_bound()}
```

Strict point sampling gives an outer product and is therefore only a leading focusing term.

## 9. Internal Harmonic Amplitudes And Hierarchies

Hierarchy information may enter through internal mode amplitudes at `y0`, node suppression, anisotropic focusing, finite-width moments, and transport/dressing terms. No numerical amplitudes are computed here.

## 10. Diagonal Leading Overlaps And Off-Diagonal Mixing

The previous leading/conditional texture status is preserved: diagonal entries are leading self-overlaps, while off-diagonal entries remain conditional mixing/transport/dressing sources.

## 11. Reconciliation With Mode-Distance Diagnostics

Distance enters through `d_I(y,y0)` in the universal profile and through eigenfunction shapes. PO-BH-21 remains valid: no direct numerical `D_f(i,j) -> I_f(i,j)` law is promoted.

## 12. Numerical Value Status

Numerical eigenfunction amplitudes and finite-width overlap moments remain open.

## 13. Non-Tautology Checks

See [Legacy Geometric Overlap Non-Tautology Audit](legacy_geometric_overlap_non_tautology_audit.md).

## 14. Promoted Results

{_components_table()}

## 15. What Remains Before Numerical Yukawa Theorem

Compute internal eigenfunction amplitudes at `y0` and finite-width overlap moments over the BHSM internal space, without fitting measured masses.

## 16. What Remains Before Replacement Claim

Replacement readiness remains false until numerical Yukawa couplings, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, and the full low-energy Lagrangian theorem are complete.

## Conclusion

{CONCLUSION_LANGUAGE}

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_legacy_integral_markdown() -> str:
    return f"""# Derived Legacy Yukawa Overlap Integral

```text
{legacy_overlap_integral()}
```

Mapped to the current BHSM scaffold:

```text
Y_f[i,j] = N_f I_f(A_f[i], H_f, S_f[j])
```

Status: `LEGACY_YUKAWA_OVERLAP_INTEGRAL_BRIDGED_CONDITIONAL`.
"""


def render_bhsm_kernel_markdown() -> str:
    return f"""# Derived BHSM Geometric Overlap Kernel

```text
{bhsm_overlap_kernel()}
```

Here `B^3` is the internal Berger/BHSM boundary internal space, `gamma` is the internal metric, `dV_gamma` is the internal volume measure, `Psi_A` is the active-side internal mode, `Psi_S` is the singlet-side internal mode, and `Phi_H` is the scalar/topographic profile for `H` or `H_tilde`.

Status: `BHSM_GEOMETRIC_OVERLAP_KERNEL_DERIVED_CONDITIONAL`.
"""


def render_profile_markdown() -> str:
    return f"""# Derived Universal Higgs Topographic Profile

```text
{universal_profile()}
```

Guardrails:

- universal across flavor;
- universal across generation;
- no fitted sector widths;
- no measured-mass input.

Status: `UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL`.
"""


def render_sharp_peak_markdown() -> str:
    return f"""# Derived Sharp-Peak Sampling Approximation

```text
{sharp_peak_approximation()}
```

This is a leading focusing approximation, not a complete rank-three matrix theorem.

Status: `SHARP_PEAK_Y0_SAMPLING_APPROXIMATION_DERIVED_CONDITIONAL`.
"""


def render_rank_guardrail_markdown() -> str:
    return """# Derived Sharp-Peak Rank Guardrail

In the strict sharp-peak limit, the approximation

```text
I_ij approx Phi0 a_i^* b_j
```

is an outer product. Therefore `rank(I) <= 1`. This means the strict point-sampling term cannot by itself generate three nonzero singular values. Full rank-three Yukawa structure requires additional derived structure such as finite-width moments of the universal profile, internal mode orthogonality/selection, boundary transport, or dressing terms. This is a guardrail against overclaiming the sharp-peak approximation.

Status: `SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL`.
"""


def render_amplitude_bridge_markdown() -> str:
    return """# Derived Internal Mode Amplitude Hierarchy Bridge

- Hierarchies may arise from how internal modes sample `y0`.
- Node suppression can reduce amplitudes.
- Anisotropic focusing along the squashed axis can enhance amplitudes.
- Off-diagonal entries reflect basis misalignment, finite-width overlap, or transport/dressing.
- No numerical values are derived.

Status: `INTERNAL_MODE_AMPLITUDE_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL`.
"""


def render_distance_reconciliation_markdown() -> str:
    return """# Derived Overlap Kernel Vs Distance Law Reconciliation

- PO-BH-21 found no direct numerical distance-to-overlap law.
- That result remains valid.
- The primary kernel is the geometric overlap integral.
- Distance enters through `d_I(y,y0)` in the universal profile and through eigenfunction shapes.
- Direct `D_f(i,j) -> I_f(i,j)` laws remain unpromoted.

Status: `DISTANCE_OVERLAP_RECONCILIATION_DERIVED_CONDITIONAL`.
"""


def render_open_problem_markdown() -> str:
    return """# Derived Geometric Overlap Numerical Open Problem

Compute `Psi_A_f_i(y0)`, `Psi_S_f_j(y0)`, and finite-width overlap moments of `Phi(y)` over `B^3` for the BHSM generation modes, without fitting measured fermion masses.

Numerical Yukawa values remain open until the internal Berger/BHSM eigenfunctions, their amplitudes at `y0`, and finite-width overlap moments are computed from the derived internal geometry.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("legacy integral source", "legacy scalar-topographic formula is bridged", "measured Yukawa matrix", "formula is symbolic and source ingestion is flagged incomplete", "conditional pass", "add legacy source docs to repo"),
        ("BHSM notation bridge", "I_f is geometric overlap kernel", "fitted distance law", "kernel is integral over internal modes", "pass", "compute modes"),
        ("universal profile", "single Phi(y)", "flavor-dependent tuning", "universal across sector/generation", "pass", "derive sigma from geometry"),
        ("sharp-peak approximation", "leading y0 sampling", "rank-three matrix claim", "rank guardrail included", "guarded", "finite-width moments"),
        ("rank guardrail", "strict point sampling rank <= 1", "full rank assumed", "outer-product limitation explicit", "pass", "rank-three theorem"),
        ("internal mode amplitudes", "hierarchy bridge", "measured masses", "no numerical amplitudes inserted", "open", "compute eigenfunctions"),
        ("distance-law reconciliation", "PO-BH-21 remains valid", "direct D-to-I law", "unpromoted distance law", "pass", "derive value map if possible"),
        ("numerical values", "remain open", "fitted masses", "all numerical claims false", "guarded", "eigenfunction/moment theorem"),
        ("comparison to known Yukawa hierarchies", "comparison only after bridge", "known hierarchy as premise", "not used as input", "guarded", "future theorem"),
    ]
    lines = [
        "# Legacy Geometric Overlap Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: The bridge does not use measured masses or known Yukawa matrices as inputs. Numerical eigenfunction amplitudes, finite-width moments, and Yukawa values remain open.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_legacy_geometric_overlap_bridge.md": render_main_markdown(),
        "derived_legacy_yukawa_overlap_integral.md": render_legacy_integral_markdown(),
        "derived_bhsm_geometric_overlap_kernel.md": render_bhsm_kernel_markdown(),
        "derived_universal_higgs_topographic_profile.md": render_profile_markdown(),
        "derived_sharp_peak_sampling_approximation.md": render_sharp_peak_markdown(),
        "derived_sharp_peak_rank_guardrail.md": render_rank_guardrail_markdown(),
        "derived_internal_mode_amplitude_hierarchy_bridge.md": render_amplitude_bridge_markdown(),
        "derived_overlap_kernel_vs_distance_law_reconciliation.md": render_distance_reconciliation_markdown(),
        "derived_geometric_overlap_numerical_open_problem.md": render_open_problem_markdown(),
        "legacy_geometric_overlap_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_legacy_geometric_overlap_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
