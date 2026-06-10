"""BHSM v2.6 complete-operator term inventory."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_audit import (
    REMAINDER_OPEN,
    REMAINDER_PSD_PROFILE_CONTROLLED,
    REMAINDER_REAL_MISSING_TERM,
    REMAINDER_RELATIVELY_BOUNDED_SAFE,
    REMAINDER_REPRESENTED_BY_EXISTING_TERM,
    REMAINDER_SCREENED_OR_LIFTED,
    REMAINDER_ZERO,
)
from curvature_remainder_closure_decision import build_curvature_remainder_closure_decision


DERIVED_AND_INCLUDED = "DERIVED_AND_INCLUDED"
DERIVED_ZERO_OR_CANCELLED = "DERIVED_ZERO_OR_CANCELLED"
DERIVED_SCREENED_OR_LIFTED = "DERIVED_SCREENED_OR_LIFTED"
REPRESENTED_BY_EXISTING_TERM = "REPRESENTED_BY_EXISTING_TERM"
CONDITIONAL_IDENTIFICATION = "CONDITIONAL_IDENTIFICATION"
MISSING_TERM = "MISSING_TERM"
FORBIDDEN_BY_AXIOM = "FORBIDDEN_BY_AXIOM"
OPEN = "OPEN"

SAFE_CLASSIFICATIONS = {
    DERIVED_AND_INCLUDED,
    DERIVED_ZERO_OR_CANCELLED,
    DERIVED_SCREENED_OR_LIFTED,
    REPRESENTED_BY_EXISTING_TERM,
    FORBIDDEN_BY_AXIOM,
}

BLOCKING_CLASSIFICATIONS = {CONDITIONAL_IDENTIFICATION, MISSING_TERM, OPEN}


@dataclass(frozen=True)
class OperatorTerm:
    term_id: str
    role: str
    represented_by: str
    required_for_ht: bool
    classification: str
    evidence: tuple[str, ...]
    limitation: str


@dataclass(frozen=True)
class OperatorTermInventoryReport:
    title: str
    terms: tuple[OperatorTerm, ...]
    all_terms_classified: bool
    required_open_or_missing_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def complete_operator_terms() -> tuple[OperatorTerm, ...]:
    """Return the complete-operator term inventory currently auditable in repo."""

    curvature_decision = build_curvature_remainder_closure_decision()
    curvature_classification = {
        REMAINDER_ZERO: DERIVED_ZERO_OR_CANCELLED,
        REMAINDER_REPRESENTED_BY_EXISTING_TERM: REPRESENTED_BY_EXISTING_TERM,
        REMAINDER_PSD_PROFILE_CONTROLLED: REPRESENTED_BY_EXISTING_TERM,
        REMAINDER_SCREENED_OR_LIFTED: DERIVED_SCREENED_OR_LIFTED,
        REMAINDER_RELATIVELY_BOUNDED_SAFE: CONDITIONAL_IDENTIFICATION,
        REMAINDER_REAL_MISSING_TERM: MISSING_TERM,
        REMAINDER_OPEN: OPEN,
    }[curvature_decision.remainder_classification]
    curvature_represented_by = (
        "not represented by a proven existing term"
        if curvature_classification in BLOCKING_CLASSIFICATIONS
        else "closed by v2.7 curvature remainder decision"
    )
    curvature_evidence = (
        f"v2.7 classification: {curvature_decision.remainder_classification}",
        f"v2.7 final result: {curvature_decision.final_result}",
    )
    curvature_limitation = (
        "Single missing complete-operator identification theorem gap remains: "
        f"{curvature_decision.exact_remaining_gap}."
        if curvature_classification in BLOCKING_CLASSIFICATIONS
        else "Curvature remainder is closed by the v2.7 audit."
    )
    return (
        OperatorTerm("berger_diagonal_kinetic", "Berger/Dirac diagonal kinetic contribution", "A0 = D_diag^2", True, DERIVED_AND_INCLUDED, ("v1.9 diagonal reference operator proven",), "Does not by itself identify all twisted/bundle perturbations."),
        OperatorTerm("hopf_fiber_twist", "Hopf fibration/twist contribution", "V_Hopf", True, DERIVED_AND_INCLUDED, ("v2.1 Hopf/boundary/chirality bound scaffold includes V_Hopf",), "Complete-action derivation is inherited from scaffold terms."),
        OperatorTerm("boundary_functional", "sector boundary functional contribution", "V_boundary", True, DERIVED_AND_INCLUDED, ("v1.2/v2.1 boundary functional represented in perturbation package",), "Global boundary problem remains linked to complete-operator proof."),
        OperatorTerm("chirality_projector", "weak chirality contribution", "V_chi", True, DERIVED_AND_INCLUDED, ("chiral projector channel is represented and tested",), "Mirror exclusion remains a separate theorem dependency."),
        OperatorTerm("sector_coupling", "off-diagonal sector coupling contribution", "K_sector", True, REPRESENTED_BY_EXISTING_TERM, ("v1.3-v2.1 sector coupling bound scaffolds represent this block",), "Complete operator source for the coupling is still tied to action-scaffold assumptions."),
        OperatorTerm("formal_kernel_complement_lift", "formal kernel/complement lift contribution", "P_perp_lift", True, DERIVED_AND_INCLUDED, ("v2.2 complement projector and lift/projector domain scaffold",), "Projector graph-domain stability remains conditional downstream."),
        OperatorTerm("heat_lift", "heat-kernel lift contribution", "P_perp_lift", True, DERIVED_AND_INCLUDED, ("v2.1/v2.4 lift term included",), "Exact heat-kernel construction is represented at scaffold level."),
        OperatorTerm("psd_profile", "positive semidefinite topographic/profile contribution", "V_PSD", True, REPRESENTED_BY_EXISTING_TERM, ("PSD profile construction and scalar/topographic screening scaffolds",), "Full scalar action proof remains separate from H_T operator identification."),
        OperatorTerm("higgs_u1_connection", "Higgs-selected U1 bundle phase contribution", "V_boundary + V_Hopf", True, REPRESENTED_BY_EXISTING_TERM, ("v2.3 Higgs-U1 mirror channel and boundary/Hopf representation",), "Standalone complete mirror channel remains conditional."),
        OperatorTerm("trace_u1_nondynamical", "trace U1 topological/nondynamical channel", "excluded from dynamical H_T", True, FORBIDDEN_BY_AXIOM, ("trace U1 is treated as topological/nondynamical in theorem scaffolds",), "Requires retention of the topological/nondynamical axiom."),
        OperatorTerm("scalar_topographic_leakage", "scalar/topographic leakage into H_T", "V_PSD or screened/lifted scalar sector", True, DERIVED_SCREENED_OR_LIFTED, ("scalar/topographic scaffold screens/lifts non-Higgs modes",), "Full scalar action theorem is not part of this v2.6 operator proof."),
        OperatorTerm("mirror_channel_terms", "mirror-sector contributions", "chiral/Higgs-U1/boundary channels", True, REPRESENTED_BY_EXISTING_TERM, ("v2.3 mirror-channel reports account for generated mirror candidates",), "Full mirror theorem remains conditional."),
        OperatorTerm("lichnerowicz_bundle_curvature_remainder", "possible curvature/remainder term in squaring the complete twisted Dirac/bundle operator", curvature_represented_by, True, curvature_classification, curvature_evidence, curvature_limitation),
    )


def build_operator_term_inventory_report() -> OperatorTermInventoryReport:
    terms = complete_operator_terms()
    all_classified = all(term.classification for term in terms)
    blocking = tuple(term.term_id for term in terms if term.required_for_ht and term.classification in BLOCKING_CLASSIFICATIONS)
    status = "OPERATOR_TERM_INVENTORY_BLOCKED" if blocking else "OPERATOR_TERM_INVENTORY_COMPLETE"
    return OperatorTermInventoryReport(
        title="BHSM v2.7 Complete Operator Term Inventory Report",
        terms=terms,
        all_terms_classified=all_classified,
        required_open_or_missing_terms=blocking,
        status=status,
        theorem_complete=not blocking,
        limitations=(
            "Every listed term has an explicit classification.",
            "The Lichnerowicz/bundle-curvature remainder is not hidden; v2.7 keeps it open until a formula/bound theorem is supplied.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_operator_term_inventory_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_term_inventory_report()), indent=2, sort_keys=True) + "\n")


def export_operator_term_inventory_markdown(path: str | Path) -> None:
    report = build_operator_term_inventory_report()
    lines = [
        "# BHSM v2.7 Complete Operator Term Inventory Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All terms classified: `{report.all_terms_classified}`",
        "",
        "| Term | Required | Represented by | Classification | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for term in report.terms:
        lines.append(f"| `{term.term_id}` | `{term.required_for_ht}` | `{term.represented_by}` | `{term.classification}` | {term.limitation} |")
    lines.extend(["", "## Required Open or Missing Terms", ""])
    lines.extend(f"- `{item}`" for item in report.required_open_or_missing_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
