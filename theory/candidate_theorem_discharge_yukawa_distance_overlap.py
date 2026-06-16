from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from candidate_theorem_discharge_yukawa_overlap_kernel import (
    SECTORS,
    all_distance_matrices,
    compact_texture_matrix,
    texture_summary_counts,
)


BRANCH = "bhsm-theorem-discharge-yukawa-distance-overlap-law-v1"
STATUS = "partial_theorem_scaffold"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch attempts to determine "
    "whether the already-derived Yukawa mode-distance scaffold can be promoted "
    "into a theorem-level boundary distance-to-overlap law. Status labels may be "
    "promoted only when the law follows from BHSM boundary action, Hessian, "
    "dressing, or overlap machinery and does not use known fermion masses or "
    "mixing angles as input."
)
SAFE_CONCLUSION = (
    "This branch derives and audits candidate distance-to-overlap laws for the "
    "BHSM Yukawa overlap kernel. The existing mode-distance diagnostics provide a "
    "deterministic scaffold for future hierarchy and mixing calculations, but no "
    "numerical distance-to-overlap law is promoted unless it is derived from "
    "existing BHSM boundary action, Hessian, dressing, or overlap machinery. "
    "Therefore numerical overlap values, fermion mass ratios, CKM values, and "
    "PMNS values remain open."
)


class LawStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    STRUCTURALLY_MOTIVATED_NOT_DERIVED = "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    FAILED_GUARDRAIL = "FAILED_GUARDRAIL"
    REMAINS_OPEN = "REMAINS_OPEN"


@dataclass(frozen=True)
class CandidateOverlapLaw:
    name: str
    formula: str
    required_source: str
    status: str
    reason: str


@dataclass(frozen=True)
class BoundaryActionSearchFinding:
    file: str
    finding: str
    maps_distance_to_overlap: bool
    theorem_derived: bool
    fitting_risk: str


@dataclass(frozen=True)
class DischargeRecord:
    code: str
    target: str
    status: str
    statement: str
    remaining_blocker: str


VERDICT_LABELS = [
    "PO_BH_21_YUKAWA_DISTANCE_OVERLAP_LAW_PARTIAL",
    "YUKAWA_DISTANCE_DIAGNOSTICS_DERIVED_CONDITIONAL",
    "YUKAWA_DISTANCE_TO_OVERLAP_LAW_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
    "NUMERICAL_OVERLAP_LAW_REMAINS_OPEN",
    "NUMERICAL_OVERLAP_VALUES_REMAIN_OPEN",
    "FERMION_MASS_RATIOS_REMAIN_OPEN",
    "CKM_VALUES_REMAIN_OPEN",
    "PMNS_VALUES_REMAIN_OPEN",
    "DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def candidate_overlap_laws() -> tuple[CandidateOverlapLaw, ...]:
    return (
        CandidateOverlapLaw(
            "exponential_L1",
            "I_f(i,j)=A_f exp[-eta_f D_f(i,j)]",
            "boundary action or transport Hessian deriving eta_f",
            LawStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "requires derived eta_f and an action-to-overlap theorem",
        ),
        CandidateOverlapLaw(
            "gaussian_D2",
            "I_f(i,j)=A_f exp[-eta_f D2_f(i,j)]",
            "quadratic boundary Hessian overlap theorem",
            LawStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "requires derived quadratic overlap kernel",
        ),
        CandidateOverlapLaw(
            "power_dressing",
            "I_f(i,j)=A_f Z_f^{D_f(i,j)}",
            "derived sector dressing law",
            LawStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "requires non-fitted Z_f and exponent theorem",
        ),
        CandidateOverlapLaw(
            "boundary_action_hessian",
            "I_f(i,j) proportional to exp[-Delta S_f(i,j)]",
            "explicit BHSM boundary action/Hessian difference",
            LawStatus.REMAINS_OPEN.value,
            "no theorem-derived action difference was found for Yukawa mode-distance overlaps",
        ),
        CandidateOverlapLaw(
            "selection_only",
            "diagonal leading, off-diagonal conditional",
            "already derived overlap-kernel selection theorem",
            LawStatus.DERIVED_CONDITIONAL.value,
            "does not assign numerical values",
        ),
    )


def boundary_action_search_findings() -> tuple[BoundaryActionSearchFinding, ...]:
    return (
        BoundaryActionSearchFinding(
            "theory/theorem_discharge_yukawa_overlap_kernel_selection.md",
            "derives distance diagnostics and diagonal/off-diagonal status",
            False,
            True,
            "none; no numerical values assigned",
        ),
        BoundaryActionSearchFinding(
            "theory/topographic_attractor_boundary_action_bridge.md",
            "records candidate quadratic norm and stochastic dressing language",
            False,
            False,
            "would require a derived action-to-overlap theorem before use",
        ),
        BoundaryActionSearchFinding(
            "theory/virtual_environment_dressing_audit.md",
            "diagnostic virtual dressing formalism",
            False,
            False,
            "candidate-only dressing could become post-hoc if promoted here",
        ),
        BoundaryActionSearchFinding(
            "candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md",
            "non-official charged-lepton dressing candidate",
            False,
            False,
            "eta is candidate/fitted and cannot define official Yukawa kernel law",
        ),
        BoundaryActionSearchFinding(
            "candidates/BHSM_MIXING_DRESSED_V1_CANDIDATE.md",
            "non-official CKM 2-3 mixing dressing candidate",
            False,
            False,
            "uses candidate exponent requiring derivation before promotion",
        ),
    )


def candidate_law_status() -> dict[str, str]:
    return {law.name: law.status for law in candidate_overlap_laws()}


def numerical_overlap_values_derived() -> bool:
    return False


def fermion_mass_ratios_derived() -> bool:
    return False


def ckm_values_derived() -> bool:
    return False


def pmns_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def distance_overlap_law_discharged_conditionally() -> bool:
    return False


def theorem_status() -> str:
    return "PARTIAL: distance diagnostics and candidate laws audited; numerical distance-to-overlap law remains open"


def proof_discharge_ledger() -> dict[str, DischargeRecord]:
    return {
        "PO-BH-21": DischargeRecord(
            "PO-BH-21",
            "derive Yukawa distance-to-overlap law",
            "PARTIAL",
            "Candidate distance-to-overlap laws were audited; selection-only status is conditionally derived, while numerical overlap kernels remain open.",
            "Derive K_f(mode_i, mode_j, H_f) from BHSM boundary action/Hessian/dressing machinery without measured masses.",
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
        "distance_overlap_law_discharged_conditionally": False,
        "distance_diagnostics_preserved": True,
        "candidate_laws_audited": True,
        "numerical_overlap_values_derived": False,
        "fermion_mass_ratios_derived": False,
        "ckm_values_derived": False,
        "pmns_values_derived": False,
        "discharged_obligations": {
            "PO-BH-21": "PARTIAL: candidate distance-to-overlap laws audited; numerical overlap kernel remains open unless an existing BHSM action/Hessian law is found"
        },
        "candidate_law_status": candidate_law_status(),
        "texture_summary_preserved": texture_summary_counts(),
        "distance_matrices_preserved": all_distance_matrices(),
        "boundary_action_search_findings": [
            {
                "file": finding.file,
                "finding": finding.finding,
                "maps_distance_to_overlap": finding.maps_distance_to_overlap,
                "theorem_derived": finding.theorem_derived,
                "fitting_risk": finding.fitting_risk,
            }
            for finding in boundary_action_search_findings()
        ],
        "still_open_downstream": [
            "numerical boundary overlap kernel theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "neutral-sector mass scale theorem",
            "scalar potential numerical theorem",
            "full low-energy SM Lagrangian theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "numerical overlap values not derived in this branch",
            "fermion mass ratios not derived in this branch",
            "CKM values not derived in this branch",
            "PMNS values not derived in this branch",
            "replacement claim is not ready",
        ],
        "summary": {
            "theorem_status": theorem_status(),
            "distance_overlap_law_discharged_conditionally": distance_overlap_law_discharged_conditionally(),
            "candidate_law_status": candidate_law_status(),
            "selection_only_status": candidate_law_status()["selection_only"],
            "all_promoted_laws_are_non_numeric": True,
            "numerical_overlap_values_derived": numerical_overlap_values_derived(),
            "fermion_mass_ratios_derived": fermion_mass_ratios_derived(),
            "ckm_values_derived": ckm_values_derived(),
            "pmns_values_derived": pmns_values_derived(),
            "replacement_claim_ready": replacement_claim_ready(),
        },
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate distance-to-overlap laws audited without fitting masses",
            "mission remains full Standard Model derivation from BHSM",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
    }


def _laws_table() -> str:
    lines = [
        "| candidate_law | formula | required_source | status | reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for law in candidate_overlap_laws():
        lines.append(f"| {law.name} | `{law.formula}` | {law.required_source} | `{law.status}` | {law.reason} |")
    return "\n".join(lines)


def _search_table() -> str:
    lines = [
        "| file | formulas found | maps mode distance to overlap value | theorem derived | fitting risk |",
        "| --- | --- | --- | --- | --- |",
    ]
    for finding in boundary_action_search_findings():
        lines.append(
            f"| {finding.file} | {finding.finding} | {finding.maps_distance_to_overlap} | {finding.theorem_derived} | {finding.fitting_risk} |"
        )
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: Yukawa Distance-To-Overlap Law

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the closure spectrum, finite boundary algebra, charge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, scalar doublet, Yukawa operator closure, symbolic Yukawa matrix scaffolds, and overlap-kernel selection rules.

## 3. Why Distance-To-Overlap Is The Next Blocker

The kernel-selection layer gives exact mode distances and entry statuses. A numerical mass theorem requires a derived map from those distances to overlap values.

## 4. Current Overlap-Kernel Status

The selection-only status is conditionally derived: diagonal entries are leading and off-diagonal entries remain conditional.

## 5. Mode-Distance Diagnostics

The preserved diagnostics are `D_f(i,j)=|q_i-q_j|+|j_i-j_j|` and `D2_f(i,j)=(q_i-q_j)^2+(j_i-j_j)^2`.

## 6. Candidate Distance-To-Overlap Laws

{_laws_table()}

## 7. Boundary Action/Hessian Audit

See [Derived Yukawa Boundary Action Overlap Audit](derived_yukawa_boundary_action_overlap_audit.md).

## 8. Guardrails Against Fitting

See [Derived Yukawa Overlap Value Guardrails](derived_yukawa_overlap_value_guardrails.md).

## 9. Candidate Law Status Table

{_laws_table()}

## 10. Numerical Overlap-Value Status

Numerical overlap values are not derived in this branch.

## 11. Impact On Mass Hierarchy Theorem

The hierarchy theorem remains narrowed to deriving a non-fitted numerical kernel `K_f(mode_i, mode_j, H_f)`.

## 12. Impact On CKM/PMNS Theorem

CKM and PMNS values remain open because no numerical off-diagonal kernel values are derived.

## 13. What This Branch Achieves

{SAFE_CONCLUSION}

## 14. What Remains Before Replacement Claim

Replacement readiness remains false until numerical overlap kernels, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, scalar potential numerics, and the full low-energy Lagrangian theorem are complete.

## Verdict Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def render_candidates_markdown() -> str:
    return f"""# Derived Yukawa Distance-Overlap Candidates

{_laws_table()}
"""


def render_boundary_action_audit_markdown() -> str:
    return f"""# Derived Yukawa Boundary Action Overlap Audit

{_search_table()}

No existing theorem-derived boundary action/Hessian formula was found that maps Yukawa mode distance to numerical overlap values without additional assumptions.
"""


def render_distance_kernel_status_markdown() -> str:
    return """# Derived Yukawa Distance Kernel Status

| object | status |
| --- | --- |
| mode distances | `DERIVED_CONDITIONAL` |
| diagonal leading source | `DERIVED_CONDITIONAL` |
| off-diagonal conditional source | `DERIVED_CONDITIONAL` |
| distance-to-numerical-overlap law | `REMAINS_OPEN` |
| numerical overlap values | `REMAIN_OPEN` |
"""


def render_guardrails_markdown() -> str:
    return """# Derived Yukawa Overlap Value Guardrails

- no fitting measured masses;
- no CKM/PMNS input;
- no changing frozen outputs;
- no sector exponent tuning;
- no hidden post-hoc normalization.
"""


def render_open_problem_markdown() -> str:
    return """# Derived Yukawa Numerical Kernel Open Problem

Find or derive a BHSM boundary functional `K_f` such that:

```text
I_f(i,j)=K_f(mode_i, mode_j, H_f)
```

and `K_f` is derived from boundary action/Hessian/dressing/overlap structure, not from measured masses.
"""


def render_non_tautology_markdown() -> str:
    rows = [
        ("distance diagnostics", "preserve exact q,j distance matrices", "known hierarchies", "distances inherited from mode ledgers", "pass", "derive value map"),
        ("exponential L1 candidate", "structural candidate", "fitted eta_f", "not promoted without derived eta_f", "guarded", "derive action-to-overlap theorem"),
        ("Gaussian D2 candidate", "structural candidate", "fitted quadratic kernel", "not promoted without Hessian theorem", "guarded", "derive quadratic kernel"),
        ("power/dressing candidate", "structural candidate", "candidate dressing factors", "not promoted without non-fitted Z_f", "guarded", "derive sector dressing law"),
        ("boundary-action Hessian candidate", "open action route", "informal Hessian analogy", "reported open", "open", "derive Delta S_f"),
        ("selection-only scaffold", "diagonal leading, off-diagonal conditional", "known diagonal textures", "non-numeric selection only", "conditional pass", "derive numerical kernel"),
    ]
    lines = [
        "# Yukawa Distance-Overlap Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: This branch does not use measured masses, known Yukawa textures, CKM values, or PMNS values as input. Numerical overlap values remain open.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_discharge_yukawa_distance_overlap_law.md": render_main_markdown(),
        "derived_yukawa_distance_overlap_candidates.md": render_candidates_markdown(),
        "derived_yukawa_boundary_action_overlap_audit.md": render_boundary_action_audit_markdown(),
        "derived_yukawa_distance_kernel_status.md": render_distance_kernel_status_markdown(),
        "derived_yukawa_overlap_value_guardrails.md": render_guardrails_markdown(),
        "derived_yukawa_numerical_kernel_open_problem.md": render_open_problem_markdown(),
        "yukawa_distance_overlap_non_tautology_audit.md": render_non_tautology_markdown(),
        "theorem_discharge_yukawa_distance_overlap_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
