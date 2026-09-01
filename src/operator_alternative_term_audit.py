"""BHSM v2.13 audit of plausible alternative complete-operator terms."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


FORBIDDEN_BY_AXIOMS = "FORBIDDEN_BY_AXIOMS"
EQUIVALENT_TO_EXISTING_TERM = "EQUIVALENT_TO_EXISTING_TERM"
ZERO_BY_SYMMETRY = "ZERO_BY_SYMMETRY"
SCREENED_OR_LIFTED = "SCREENED_OR_LIFTED"
PSD_OR_RELATIVELY_BOUNDED_SAFE = "PSD_OR_RELATIVELY_BOUNDED_SAFE"
OPENS_MIRROR_LEAKAGE = "OPENS_MIRROR_LEAKAGE"
BREAKS_FORMAL_KERNEL = "BREAKS_FORMAL_KERNEL"
BREAKS_LOCAL_SM_BUNDLE_SEPARATION = "BREAKS_LOCAL_SM_BUNDLE_SEPARATION"
REAL_MISSING_TERM = "REAL_MISSING_TERM"
OPEN = "OPEN"

SAFE_OR_FORBIDDEN_CLASSIFICATIONS = {
    FORBIDDEN_BY_AXIOMS,
    EQUIVALENT_TO_EXISTING_TERM,
    ZERO_BY_SYMMETRY,
    SCREENED_OR_LIFTED,
    PSD_OR_RELATIVELY_BOUNDED_SAFE,
    OPENS_MIRROR_LEAKAGE,
    BREAKS_FORMAL_KERNEL,
    BREAKS_LOCAL_SM_BUNDLE_SEPARATION,
}
BLOCKING_CLASSIFICATIONS = {REAL_MISSING_TERM, OPEN}


@dataclass(frozen=True)
class AlternativeOperatorTerm:
    term_id: str
    proposed_term: str
    classification: str
    preserves_formal_kernel: bool
    preserves_local_sm_bundle: bool
    preserves_mirror_exclusion: bool
    equivalent_to: str
    evidence: tuple[str, ...]
    limitation: str


@dataclass(frozen=True)
class OperatorAlternativeTermAuditReport:
    title: str
    alternatives: tuple[AlternativeOperatorTerm, ...]
    all_alternatives_classified: bool
    real_missing_terms: tuple[str, ...]
    open_terms: tuple[str, ...]
    uniqueness_breaking_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def alternative_terms() -> tuple[AlternativeOperatorTerm, ...]:
    return (
        AlternativeOperatorTerm("additional_hopf_base_mixed", "extra Hopf/base mixed term", EQUIVALENT_TO_EXISTING_TERM, True, True, True, "topographic represented sector", ("v2.11/v2.12 represent mixed Hopf/base curvature topographically.",), "No independent coefficient is allowed."),
        AlternativeOperatorTerm("additional_boundary_coframe", "extra boundary/coframe term", EQUIVALENT_TO_EXISTING_TERM, True, True, True, "V_boundary + topographic represented sector", ("boundary/coframe compatibility is already represented.",), ""),
        AlternativeOperatorTerm("additional_chirality_mixing", "extra chirality-mixing term", OPENS_MIRROR_LEAKAGE, False, True, False, "", ("A chirality-mixing perturbation opens mirror leakage.",), "Rejected as theorem-failing, not allowed."),
        AlternativeOperatorTerm("additional_sector_off_diagonal", "extra sector off-diagonal term", BREAKS_FORMAL_KERNEL, False, True, True, "", ("Uncontrolled sector off-diagonal terms break the sector-labeled formal kernel.",), "Only K_sector is allowed."),
        AlternativeOperatorTerm("additional_higgs_u1_mirror", "extra Higgs-U1 mirror term", OPENS_MIRROR_LEAKAGE, False, True, False, "", ("Mirror-opening Higgs-U1 channel violates the mirror guard.",), "Rejected rather than tuned away."),
        AlternativeOperatorTerm("additional_scalar_topographic_leakage", "extra scalar/topographic leakage term", SCREENED_OR_LIFTED, True, True, True, "screened/lifted scalar-topographic sector", ("Scalar/topographic leakage is screened, lifted, or classified as forbidden light scalar.",), "Full scalar theorem remains separately audited."),
        AlternativeOperatorTerm("additional_psd_profile", "extra PSD/profile term", PSD_OR_RELATIVELY_BOUNDED_SAFE, True, True, True, "V_PSD", ("Positive semidefinite/profile additions are already represented by V_PSD.",), "Does not change uniqueness of the minimal package up to represented PSD terms."),
        AlternativeOperatorTerm("torsion_like_term", "torsion-like contribution", ZERO_BY_SYMMETRY, True, True, True, "", ("No torsion-like independent term survives the BHSM torsion-free/represented connection scaffold.",), "A future nonzero torsion axiom would be a different theory."),
        AlternativeOperatorTerm("connection_curvature_remainder", "independent R_bundle remainder", EQUIVALENT_TO_EXISTING_TERM, True, True, True, "topographic represented sector", ("v2.12 classifies R_bundle as represented by the topographic/profile sector.",), ""),
        AlternativeOperatorTerm("independent_free_mixed_coefficient", "free mixed coefficient term", BREAKS_LOCAL_SM_BUNDLE_SEPARATION, True, False, True, "", ("v2.11 forbids free mixed coefficients under local SM bundle separation.",), "Not an allowed BHSM operator deformation."),
    )


def build_operator_alternative_term_audit_report() -> OperatorAlternativeTermAuditReport:
    alternatives = alternative_terms()
    real_missing = tuple(row.term_id for row in alternatives if row.classification == REAL_MISSING_TERM)
    open_terms = tuple(row.term_id for row in alternatives if row.classification == OPEN)
    uniqueness_breaking = tuple(row.term_id for row in alternatives if row.classification in BLOCKING_CLASSIFICATIONS)
    status = "ALTERNATIVE_TERM_AUDIT_CLOSED" if not uniqueness_breaking else "ALTERNATIVE_TERM_AUDIT_BLOCKED"
    return OperatorAlternativeTermAuditReport(
        title="BHSM v2.13 Operator Alternative-Term Audit",
        alternatives=alternatives,
        all_alternatives_classified=all(row.classification for row in alternatives),
        real_missing_terms=real_missing,
        open_terms=open_terms,
        uniqueness_breaking_terms=uniqueness_breaking,
        status=status,
        theorem_complete=not uniqueness_breaking,
        limitations=(
            "Terms classified as mirror-opening, kernel-breaking, or local-SM-breaking are not allowed alternatives.",
            "No empirical prediction residual is used to choose or reject an operator term.",
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


def export_operator_alternative_term_audit_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_operator_alternative_term_audit_report()), indent=2, sort_keys=True) + "\n")


def export_operator_alternative_term_audit_markdown(path: str | Path) -> None:
    report = build_operator_alternative_term_audit_report()
    lines = [
        "# BHSM v2.13 Operator Alternative-Term Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Alternative | Classification | Equivalent to | Kernel | Local SM | Mirror |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.alternatives:
        lines.append(f"| `{row.term_id}` | `{row.classification}` | `{row.equivalent_to}` | `{row.preserves_formal_kernel}` | `{row.preserves_local_sm_bundle}` | `{row.preserves_mirror_exclusion}` |")
    lines.extend(["", "## Real Missing Terms", ""])
    lines.extend(f"- `{item}`" for item in report.real_missing_terms)
    lines.extend(["", "## Open Terms", ""])
    lines.extend(f"- `{item}`" for item in report.open_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
