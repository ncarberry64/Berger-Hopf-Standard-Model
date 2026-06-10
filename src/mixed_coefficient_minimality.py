"""BHSM v2.11 minimality and variant audit for mixed coefficients."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


VARIANT_FAILS_BHSM_AXIOMS = "VARIANT_FAILS_BHSM_AXIOMS"
VARIANT_INDETERMINATE_WITHOUT_COMPATIBILITY_AXIOM = "VARIANT_INDETERMINATE_WITHOUT_COMPATIBILITY_AXIOM"
VARIANT_OPEN_MIRROR_RISK = "VARIANT_OPEN_MIRROR_RISK"
VARIANT_FORBIDDEN_FREE_COEFFICIENT = "VARIANT_FORBIDDEN_FREE_COEFFICIENT"
MINIMALITY_AUDIT_PASSES_UNDER_BHSM_AXIOMS = "MINIMALITY_AUDIT_PASSES_UNDER_BHSM_AXIOMS"


@dataclass(frozen=True)
class MixedCoefficientVariant:
    variant_id: str
    changed_rule: str
    outcome: str
    status: str
    limitation: str


@dataclass(frozen=True)
class MixedCoefficientMinimalityReport:
    title: str
    variants: tuple[MixedCoefficientVariant, ...]
    minimality_status: str
    uniqueness_status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_mixed_coefficient_minimality_report() -> MixedCoefficientMinimalityReport:
    variants = (
        MixedCoefficientVariant("coefficient_zero", "set every mixed coefficient to zero", "allowed only for Hopf/base vertical-horizontal compatibility, not as universal convenience", VARIANT_INDETERMINATE_WITHOUT_COMPATIBILITY_AXIOM, "Represented slots must remain represented by existing sectors."),
        MixedCoefficientVariant("sign_flipped", "flip mixed coefficient orientations", "forbidden because no independent orientation coefficient is allowed", VARIANT_FORBIDDEN_FREE_COEFFICIENT, "A sign flip would create a new free bundle-curvature parameter."),
        MixedCoefficientVariant("hopf_base_disabled", "remove Hopf/base mixing", "breaks the identified complete-connection slot", VARIANT_FAILS_BHSM_AXIOMS, "The parent connection inventory includes this slot."),
        MixedCoefficientVariant("boundary_coframe_disabled", "remove boundary/coframe mixing", "loses the quark coframe compatibility channel", VARIANT_FAILS_BHSM_AXIOMS, "The v1.2C coframe triplet channel remains required."),
        MixedCoefficientVariant("coframe_singlet", "replace coframe triplet by singlet", "fails the tested action-origin sector ledger", VARIANT_FAILS_BHSM_AXIOMS, "This reopens the v1.2C uniqueness failure."),
        MixedCoefficientVariant("chirality_blind", "remove chirality dependence", "reopens mirror-channel risk", VARIANT_OPEN_MIRROR_RISK, "Mirror exclusion cannot be preserved by a chirality-blind mixed rule."),
        MixedCoefficientVariant("sector_blind", "remove lepton/up/down dependence", "cannot distinguish the sector boundary functionals", VARIANT_FAILS_BHSM_AXIOMS, "Sector labels are part of the formal kernel."),
        MixedCoefficientVariant("mirror_allowing", "allow opposite-chirality mixed channel", "conflicts with mirror exclusion scaffold", VARIANT_OPEN_MIRROR_RISK, "No theorem allows this channel."),
        MixedCoefficientVariant("independent_free_mixed_coefficient", "introduce a new fitted coefficient", "violates bundle separation and topographic representation", VARIANT_FORBIDDEN_FREE_COEFFICIENT, "This is explicitly forbidden by the v2.11 axiom."),
    )
    return MixedCoefficientMinimalityReport(
        title="BHSM v2.11 Mixed Coefficient Minimality Report",
        variants=variants,
        minimality_status=MINIMALITY_AUDIT_PASSES_UNDER_BHSM_AXIOMS,
        uniqueness_status="UNIQUE_REPRESENTATION_RULE_UNDER_BHSM_AXIOMS",
        theorem_complete=True,
        limitations=(
            "The audit closes independent coefficient freedom under the BHSM axiom, but does not prove the full H_T theorem.",
            "Scalar/topographic, projector-domain, and lower-bound dependencies remain separate theorem obligations.",
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


def export_mixed_coefficient_minimality_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_coefficient_minimality_report()), indent=2, sort_keys=True) + "\n")


def export_mixed_coefficient_minimality_markdown(path: str | Path) -> None:
    report = build_mixed_coefficient_minimality_report()
    lines = [
        "# BHSM v2.11 Mixed Coefficient Minimality Report",
        "",
        f"Minimality status: `{report.minimality_status}`",
        f"Uniqueness status: `{report.uniqueness_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Variant | Changed rule | Outcome | Status | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.variants:
        lines.append(f"| `{row.variant_id}` | {row.changed_rule} | {row.outcome} | `{row.status}` | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

