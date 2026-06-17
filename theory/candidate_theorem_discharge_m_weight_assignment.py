from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


BRANCH = "bhsm-theorem-discharge-m-weight-assignment-v1"
STATUS = "partial_theorem_scaffold"
MISSION_LANGUAGE = (
    "The purpose of this branch is to move BHSM toward a full derivation of the "
    "Standard Model from Berger-Hopf geometry. This branch audits the missing "
    "Wigner/base/orientation weight `m` needed to promote the raw-mode "
    "Berger/Hopf harmonic scaffold into explicit internal eigenfunctions."
)
CONCLUSION_LANGUAGE = (
    "This branch audits the missing m-weight assignment needed to promote the "
    "raw-mode Berger/Hopf harmonic scaffold into explicit internal eigenfunctions. "
    "The branch checks Wigner/Hopf admissibility conditions, audits candidate "
    "harmonic conventions, and identifies possible BHSM boundary/orientation "
    "sources for m. Because no theorem-derived m assignment is promoted in this "
    "branch, explicit eigenfunctions, local feature values at y0, finite-width "
    "rank-three Yukawa support, numerical Yukawa values, and replacement-level "
    "claims remain open."
)


class AssignmentStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    STRUCTURALLY_MOTIVATED_NOT_DERIVED = "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    FAILED_GUARDRAIL = "FAILED_GUARDRAIL"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class RawMode:
    sector: str
    index: int
    k: int
    j: int


@dataclass(frozen=True)
class HarmonicConvention:
    name: str
    ell_formula: str
    n_formula: str
    status: str
    reason: str


VERDICT_LABELS = [
    "PO_BH_26_M_WEIGHT_ASSIGNMENT_FROM_BOUNDARY_ORIENTATION_PARTIAL",
    "M_WEIGHT_CANDIDATE_SOURCES_AUDITED",
    "WIGNER_HOPF_ADMISSIBILITY_AUDITED",
    "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
    "SELECTED_HARMONIC_CONVENTION_REMAINS_OPEN",
    "EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN",
    "RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN",
    "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
    "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]


def raw_mode_ledgers() -> dict[str, tuple[RawMode, ...]]:
    return {
        "reference_charged": (
            RawMode("reference_charged", 0, 0, 0),
            RawMode("reference_charged", 1, 5, 2),
            RawMode("reference_charged", 2, 9, 3),
        ),
        "reference_neutral": (
            RawMode("reference_neutral", 0, 0, 0),
            RawMode("reference_neutral", 1, 3, 0),
            RawMode("reference_neutral", 2, 3, 1),
        ),
        "cyclic_upper": (
            RawMode("cyclic_upper", 0, 0, 0),
            RawMode("cyclic_upper", 1, 6, 0),
            RawMode("cyclic_upper", 2, 10, 1),
        ),
        "cyclic_lower": (
            RawMode("cyclic_lower", 0, 0, 0),
            RawMode("cyclic_lower", 1, 6, 3),
            RawMode("cyclic_lower", 2, 8, 2),
        ),
    }


def allowed_weight(ell: Fraction, weight: Fraction) -> bool:
    if ell < 0:
        return False
    if abs(weight) > ell:
        return False
    return (ell - weight).denominator == 1


def convention_A_ell_k_over_2_n_j_admissible_for_mode(mode: RawMode) -> bool:
    ell = Fraction(mode.k, 2)
    n = Fraction(mode.j, 1)
    return allowed_weight(ell, n)


def convention_A_failures() -> tuple[RawMode, ...]:
    return tuple(
        mode
        for modes in raw_mode_ledgers().values()
        for mode in modes
        if not convention_A_ell_k_over_2_n_j_admissible_for_mode(mode)
    )


def _admissible(ell_formula: str, n_formula: str, mode: RawMode) -> bool:
    values = {
        "ell=k/2": Fraction(mode.k, 2),
        "ell=k": Fraction(mode.k, 1),
        "n=j": Fraction(mode.j, 1),
        "n=j/2": Fraction(mode.j, 2),
        "n=q/2": Fraction(mode.k - 2 * mode.j, 2),
    }
    return allowed_weight(values[ell_formula], values[n_formula])


def convention_failures(ell_formula: str, n_formula: str) -> tuple[RawMode, ...]:
    return tuple(
        mode
        for modes in raw_mode_ledgers().values()
        for mode in modes
        if not _admissible(ell_formula, n_formula, mode)
    )


def candidate_harmonic_conventions() -> tuple[HarmonicConvention, ...]:
    failures_A = convention_A_failures()
    failures_B = convention_failures("ell=k", "n=j")
    failures_C = convention_failures("ell=k/2", "n=j/2")
    failures_D = convention_failures("ell=k/2", "n=q/2")
    return (
        HarmonicConvention(
            "A: ell=k/2, n=j",
            "ell=k/2",
            "n=j",
            AssignmentStatus.FAILED_GUARDRAIL.value if failures_A else AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "admissibility must hold for all modes; failures recorded" if failures_A else "admissible at label level but not yet derived from BHSM geometry",
        ),
        HarmonicConvention(
            "B: ell=k, n=j",
            "ell=k",
            "n=j",
            AssignmentStatus.FAILED_GUARDRAIL.value if failures_B else AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "may avoid parity issue but must be derived from BHSM harmonic normalization",
        ),
        HarmonicConvention(
            "C: ell=k/2, n=j/2",
            "ell=k/2",
            "n=j/2",
            AssignmentStatus.FAILED_GUARDRAIL.value if failures_C else AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "requires derivation of fiber-weight normalization",
        ),
        HarmonicConvention(
            "D: ell=k/2, n=q/2",
            "ell=k/2",
            "n=q/2",
            AssignmentStatus.FAILED_GUARDRAIL.value if failures_D else AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value,
            "requires derivation tying q to the Wigner fiber/base weight",
        ),
    )


def candidate_m_sources() -> tuple[str, ...]:
    return (
        "weak orientation sigma=2T3",
        "active interface w",
        "active/singlet side",
        "left/right chirality",
        "scalar insertion H or H_tilde",
        "cyclic/reference channel",
        "boundary orientation algebra",
        "charge closure Q,T3,Y",
        "sector orientation",
        "generation index",
    )


def candidate_m_assignments() -> tuple[dict[str, str], ...]:
    return (
        {"assignment": "m=sigma/2", "status": AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value, "reason": "requires deriving Wigner m from weak orientation"},
        {"assignment": "m=T3", "status": AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value, "reason": "same orientation source, not yet harmonic-derived"},
        {"assignment": "m=+/-j", "status": AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value, "reason": "admissibility cannot be the only selection rule"},
        {"assignment": "m=+/-q/2", "status": AssignmentStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value, "reason": "requires boundary proof linking q to base weight"},
        {"assignment": "m=orientation eigenvalue", "status": AssignmentStatus.OPEN.value, "reason": "boundary orientation algebra is not yet mapped to Wigner m"},
        {"assignment": "m=active/singlet orientation label", "status": AssignmentStatus.OPEN.value, "reason": "side labels are not yet harmonic weights"},
        {"assignment": "m=scalar-insertion orientation label", "status": AssignmentStatus.OPEN.value, "reason": "H/H_tilde orientation is not yet a mode weight theorem"},
        {"assignment": "m=sector channel label", "status": AssignmentStatus.OPEN.value, "reason": "channel labels are not yet base weights"},
        {"assignment": "m=generation-index dependent label", "status": AssignmentStatus.FAILED_GUARDRAIL.value, "reason": "would be post-hoc unless derived independently"},
    )


def m_weight_assignment_derived() -> bool:
    return False


def selected_harmonic_convention_derived() -> bool:
    return False


def explicit_eigenfunctions_derived() -> bool:
    return False


def finite_width_rank_three_derived() -> bool:
    return False


def numerical_yukawa_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def proof_discharge_ledger() -> dict[str, str]:
    return {
        "PO-BH-26": (
            "PARTIAL: m-weight candidate sources and Wigner/Hopf admissibility "
            "audited; no theorem-derived m assignment promoted unless found in repo"
        )
    }


def _mode_payload(mode: RawMode) -> dict[str, int | str]:
    return {"sector": mode.sector, "index": mode.index, "k": mode.k, "j": mode.j}


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_ready": False,
        "m_weight_assignment_layer_completed": True,
        "m_weight_assignment_derived": m_weight_assignment_derived(),
        "selected_harmonic_convention_derived": selected_harmonic_convention_derived(),
        "explicit_eigenfunctions_derived": explicit_eigenfunctions_derived(),
        "finite_width_rank_three_derived": finite_width_rank_three_derived(),
        "numerical_yukawa_values_derived": numerical_yukawa_values_derived(),
        "discharged_obligations": proof_discharge_ledger(),
        "raw_mode_ledgers": {
            sector: [_mode_payload(mode) for mode in modes] for sector, modes in raw_mode_ledgers().items()
        },
        "convention_A_failures": [_mode_payload(mode) for mode in convention_A_failures()],
        "candidate_harmonic_conventions": [convention.__dict__ for convention in candidate_harmonic_conventions()],
        "candidate_m_sources": list(candidate_m_sources()),
        "candidate_m_assignments": list(candidate_m_assignments()),
        "still_open_downstream": [
            "derive selected Wigner/Hopf harmonic convention",
            "derive m-weight assignment from BHSM boundary/orientation structure",
            "explicit Berger/BHSM harmonic theorem",
            "eigenfunction amplitudes at y0",
            "finite-width moment contractions",
            "rank-three Yukawa matrix theorem",
            "numerical Yukawa coupling theorem",
            "fermion mass hierarchy theorem",
            "CKM mixing theorem",
            "PMNS mixing theorem",
            "full replacement-level SM derivation",
        ],
        "negative_results": [
            "m-weight assignment not derived in this branch unless found in repo",
            "selected harmonic convention not derived in this branch unless found in repo",
            "explicit eigenfunction values not derived in this branch",
            "rank-three Yukawa theorem not derived in this branch",
            "numerical Yukawa values not derived in this branch",
            "replacement claim is not ready",
        ],
        "verdict_labels": VERDICT_LABELS,
    }


def _convention_table() -> str:
    lines = ["| convention | ell | n | status | reason |", "| --- | --- | --- | --- | --- |"]
    for c in candidate_harmonic_conventions():
        lines.append(f"| {c.name} | `{c.ell_formula}` | `{c.n_formula}` | `{c.status}` | {c.reason} |")
    return "\n".join(lines)


def _failure_table() -> str:
    failures = convention_A_failures()
    if not failures:
        return "No Convention A failures."
    lines = ["| sector | index | k | j |", "| --- | ---: | ---: | ---: |"]
    lines.extend(f"| {m.sector} | {m.index} | {m.k} | {m.j} |" for m in failures)
    return "\n".join(lines)


def _source_list() -> str:
    return "\n".join(f"- {source}" for source in candidate_m_sources())


def _assignment_table() -> str:
    lines = ["| assignment | status | reason |", "| --- | --- | --- |"]
    for row in candidate_m_assignments():
        lines.append(f"| `{row['assignment']}` | `{row['status']}` | {row['reason']} |")
    return "\n".join(lines)


def render_main_markdown() -> str:
    return f"""# Theorem Discharge: M-Weight Assignment

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

{MISSION_LANGUAGE}

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers reached the raw-mode map `k=q+2j` and candidate harmonic notation `psi_{{k,j,m}}`, but left `m`, the selected harmonic convention, and explicit eigenfunctions open.

## 3. PO-BH-25 Raw-Mode Harmonic Map

PO-BH-25 derived raw `(k,j)` labels from `q=k-2j`.

## 4. Why `m` Is The Next Blocker

The local feature-vector and finite-width overlap program requires explicit harmonics. The remaining Wigner/base/orientation weight `m` must be fixed by BHSM structure, not guessed.

## 5. Wigner/Hopf Harmonic Admissibility Conditions

For `D^ell_{{m,n}}`, `ell` must be integer or half-integer; `m,n` must be allowed weights; `|m|<=ell`; `|n|<=ell`; and weights must lie in the correct lattice.

## 6. Audit Of `ell=k/2`, `n=j`

Convention A failures:

{_failure_table()}

## 7. Alternative Harmonic Conventions

{_convention_table()}

## 8. Candidate BHSM Sources For `m`

{_source_list()}

## 9. Boundary Orientation Algebra Audit

The repo contains boundary orientation, `sigma`, `T3`, `w`, charge-closure, and finite-algebra scaffolds. It does not yet contain a theorem mapping those structures to Wigner `m`.

## 10. Charge/Orientation/Chirality Audit

Charge, orientation, chirality, scalar insertion, and cyclic/reference channel data are candidate sources only. None is promoted to a selected `m` assignment here.

## 11. Candidate `m` Assignment Status

{_assignment_table()}

## 12. Harmonic Convention Status

No harmonic convention is selected as theorem-derived.

## 13. Bridge To Local Feature Vectors At `y0`

Once `m` and the convention are derived, the local feature vector is `F_{{k,j,m}}=(psi,d_a psi,d_a d_b psi)|_y0`.

## 14. Numerical Eigenfunction Status

Explicit eigenfunction values are not derived.

## 15. Rank-Three/Yukawa Status

Finite-width rank three and numerical Yukawa values remain open.

## 16. Non-Tautology Audit

See [M-Weight Assignment Non-Tautology Audit](m_weight_assignment_non_tautology_audit.md).

## 17. What This Achieves

This branch audits the candidate harmonic conventions and `m` sources without selecting `m` by admissibility or fit.

## 18. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until the selected harmonic convention, `m`, explicit eigenfunctions, feature values, moment contractions, numerical Yukawa values, and mixing values are derived.

## Conclusion

{CONCLUSION_LANGUAGE}

## Verdict Labels

{chr(10).join(f"- `{label}`" for label in VERDICT_LABELS)}
"""


def _doc(title: str, body: str, status: str) -> str:
    return f"# {title}\n\n{body}\n\nStatus: `{status}`.\n"


def render_non_tautology() -> str:
    rows = [
        ("admissibility", "audits Wigner labels", "chosen convention", "failures reported", "pass", "derive convention"),
        ("m sources", "lists BHSM orientation sources", "guessed m", "no source promoted", "guarded", "derive m"),
        ("candidate assignments", "diagnostic table", "fit/admissibility selection", "candidate-only/open", "pass", "boundary theorem"),
        ("numerics", "remain open", "masses or mixing", "all numerical flags false", "pass", "explicit harmonics"),
    ]
    lines = [
        "# M-Weight Assignment Non-Tautology Audit",
        "",
        "| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")
    lines.append("Conclusion: No `m` assignment is selected to fit masses, mixing values, or admissibility alone.")
    return "\n".join(lines) + "\n"


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    docs = {
        "theorem_discharge_m_weight_assignment.md": render_main_markdown(),
        "derived_wigner_admissibility_audit.md": _doc(
            "Derived Wigner Admissibility Audit",
            "Convention A failures:\n\n" + _failure_table() + "\n\nCandidate conventions:\n\n" + _convention_table(),
            "WIGNER_HOPF_ADMISSIBILITY_AUDITED",
        ),
        "derived_m_weight_candidate_assignments.md": _doc(
            "Derived M Weight Candidate Assignments",
            _assignment_table(),
            "M_WEIGHT_CANDIDATE_SOURCES_AUDITED",
        ),
        "derived_boundary_orientation_sources_for_m.md": _doc(
            "Derived Boundary Orientation Sources For M",
            _source_list(),
            "M_WEIGHT_CANDIDATE_SOURCES_AUDITED",
        ),
        "derived_m_weight_assignment_status.md": _doc(
            "Derived M Weight Assignment Status",
            "| item | status |\n| --- | --- |\n| m assignment | `OPEN` |\n| selected harmonic convention | `OPEN` |\n| explicit eigenfunctions | `OPEN` |\n| finite-width rank three | `False` |",
            "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
        ),
        "derived_harmonic_convention_status.md": _doc(
            "Derived Harmonic Convention Status",
            _convention_table(),
            "SELECTED_HARMONIC_CONVENTION_REMAINS_OPEN",
        ),
        "derived_m_weight_to_feature_vector_bridge.md": _doc(
            "Derived M Weight To Feature Vector Bridge",
            "`F_{k,j,m}(y0)=(psi,d_a psi,d_a d_b psi)|_y0`. This bridge remains symbolic until `m` and explicit harmonics are derived.",
            "EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN",
        ),
        "derived_m_weight_open_problem.md": _doc(
            "Derived M Weight Open Problem",
            "Derive `m` from BHSM boundary/orientation/sector structure without measured masses, CKM values, PMNS values, or admissibility-only selection.",
            "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN",
        ),
        "m_weight_assignment_non_tautology_audit.md": render_non_tautology(),
        "theorem_discharge_m_weight_assignment_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in docs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
